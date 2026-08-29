import os
import sqlite3
import json
import math
import logging
import re
import hashlib
from typing import List, Dict, Any, Optional
from functools import lru_cache
from dotenv import load_dotenv

from app.ai.embedding_service import generate_embedding, EMBEDDING_DIMENSION
from app.database.supabase import get_supabase_client, get_supabase_admin_client
from app.database.db_service import LOCAL_DB_PATH

load_dotenv()

logger = logging.getLogger("campusai.vector_search")

DEFAULT_TOP_K = int(os.getenv("RAG_TOP_K", "6"))
DEFAULT_SIMILARITY_THRESHOLD = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.05"))

# ─────────────────────────────────────────────
# In-process VECTOR CACHE: stores pre-parsed chunk vectors in RAM so we
# never hit SQLite JSON parsing on hot paths. Warmed once on first search.
# ─────────────────────────────────────────────
_VECTOR_CACHE: List[Dict[str, Any]] = []
_VECTOR_CACHE_LOADED = False

# Similarity search result cache keyed by (query_hash, top_k, threshold)
_SEARCH_RESULT_CACHE: Dict[str, List[Dict[str, Any]]] = {}
_SEARCH_RESULT_CACHE_MAX = 512

def _warm_vector_cache() -> None:
    """
    Pre-loads all chunk vectors from SQLite into RAM on first call.
    Subsequent searches use pure in-memory NumPy-free cosine similarity — no I/O.
    """
    global _VECTOR_CACHE, _VECTOR_CACHE_LOADED
    if _VECTOR_CACHE_LOADED:
        return
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                c.id, c.document_id, c.chunk_index, c.content,
                c.page_number, c.embedding, c.metadata,
                d.title, d.category, d.file_name
            FROM document_chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE c.embedding IS NOT NULL AND c.embedding != ''
            ORDER BY c.document_id, c.chunk_index
        """)
        rows = cursor.fetchall()
        conn.close()

        cache = []
        for r in rows:
            chunk_id, doc_id, chunk_idx, content, page_num, emb_str, meta_str, doc_title, doc_cat, file_name = r
            try:
                vec = json.loads(emb_str)
                if not vec or len(vec) < 10:
                    continue
                # Pre-compute magnitude so cosine sim is just dot product / const
                mag = math.sqrt(sum(x * x for x in vec))
                if mag == 0:
                    continue
                cache.append({
                    "id": chunk_id,
                    "document_id": doc_id,
                    "chunk_index": chunk_idx,
                    "content": content,
                    "page_number": page_num,
                    "metadata": json.loads(meta_str) if meta_str else {},
                    "document_title": doc_title,
                    "document_category": doc_cat,
                    "file_name": file_name,
                    "_vec": vec,
                    "_mag": mag,
                })
            except Exception:
                continue

        _VECTOR_CACHE = cache
        _VECTOR_CACHE_LOADED = True
        logger.info(f"Vector cache warmed: {len(_VECTOR_CACHE)} chunks loaded into RAM.")
    except Exception as e:
        logger.error(f"Vector cache warming failed: {e}")

def invalidate_vector_cache() -> None:
    """Call this after new documents are ingested so cache refreshes."""
    global _VECTOR_CACHE, _VECTOR_CACHE_LOADED, _SEARCH_RESULT_CACHE
    _VECTOR_CACHE = []
    _VECTOR_CACHE_LOADED = False
    _SEARCH_RESULT_CACHE = {}
    logger.info("Vector cache invalidated — will reload on next search.")

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """
    Calculates cosine similarity score between two float vectors.
    Returns float value between 0.0 and 1.0.
    """
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    similarity = dot_product / (mag1 * mag2)
    return max(0.0, min(1.0, float(similarity)))

def _fast_cosine(query_vec: List[float], query_mag: float, chunk: Dict) -> float:
    """
    Fast cosine similarity using pre-computed chunk magnitude.
    Only one dot-product loop needed per comparison.
    """
    dot = sum(a * b for a, b in zip(query_vec, chunk["_vec"]))
    denom = query_mag * chunk["_mag"]
    if denom == 0:
        return 0.0
    return max(0.0, min(1.0, dot / denom))

def search_similar_chunks(
    query: str,
    top_k: Optional[int] = None,
    similarity_threshold: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Performs ultra-fast cosine similarity search over in-RAM vector cache.
    Falls back to Supabase pgvector if configured. Results are cached by query hash.
    """
    if not query or not query.strip():
        return []

    limit = top_k if top_k is not None else DEFAULT_TOP_K
    threshold = similarity_threshold if similarity_threshold is not None else DEFAULT_SIMILARITY_THRESHOLD

    # ── Cache key for search result (not query cache, which is in rag_service) ──
    q_hash = hashlib.md5(f"{query.strip().lower()}{limit}{threshold}".encode()).hexdigest()
    if q_hash in _SEARCH_RESULT_CACHE:
        logger.debug(f"Search result cache HIT for query hash {q_hash[:8]}")
        return _SEARCH_RESULT_CACHE[q_hash]

    # ── Generate Query Embedding (also LRU-cached per text) ──
    query_vector = generate_embedding(query.strip())
    if not query_vector or len(query_vector) < 10:
        logger.warning("Failed to generate valid query embedding.")
        return []

    query_mag = math.sqrt(sum(x * x for x in query_vector))
    if query_mag == 0:
        return []

    # ── Try Supabase pgvector first (cloud, optimised index) ──
    supabase = get_supabase_admin_client() or get_supabase_client()
    if supabase:
        try:
            res = supabase.rpc(
                "match_document_chunks",
                {
                    "query_embedding": query_vector,
                    "match_threshold": threshold,
                    "match_count": limit
                }
            ).execute()
            if res.data:
                _cache_search_result(q_hash, res.data)
                return res.data
        except Exception as e:
            logger.warning(f"Supabase pgvector search failed ({e}); using RAM cache fallback.")

    # ── Fast in-RAM cosine similarity search ──
    _warm_vector_cache()

    if not _VECTOR_CACHE:
        logger.warning("Vector cache is empty — no chunks indexed yet.")
        return []

    scored = []
    for chunk in _VECTOR_CACHE:
        sim = _fast_cosine(query_vector, query_mag, chunk)
        if sim >= threshold:
            scored.append((sim, chunk))

    # Sort descending by similarity, take top_k
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:limit]

    results = [
        {
            "id": c["id"],
            "document_id": c["document_id"],
            "chunk_index": c["chunk_index"],
            "content": c["content"],
            "page_number": c["page_number"],
            "metadata": c["metadata"],
            "similarity": round(sim, 4),
            "document_title": c["document_title"],
            "document_category": c["document_category"],
            "file_name": c["file_name"],
        }
        for sim, c in top
    ]

    # ── Hybrid Fallback: Keyword search over in-RAM chunks if vector sim returned 0 ──
    if not results and _VECTOR_CACHE:
        words = [w for w in re.findall(r"\w+", query.lower()) if len(w) > 2 and w not in ("what", "when", "where", "with", "from", "that", "this", "your")]
        matched_chunks = []
        for c in _VECTOR_CACHE:
            content_lower = c["content"].lower()
            doc_title_lower = c["document_title"].lower()
            cat_lower = c["document_category"].lower()
            
            score = 0
            for w in words:
                if w in doc_title_lower:
                    score += 5
                if w in cat_lower:
                    score += 4
                if w in content_lower:
                    score += 2
            
            if score > 0:
                matched_chunks.append((score, c))
        
        matched_chunks.sort(key=lambda x: x[0], reverse=True)
        results = [
            {
                "id": c["id"],
                "document_id": c["document_id"],
                "chunk_index": c["chunk_index"],
                "content": c["content"],
                "page_number": c["page_number"],
                "metadata": c["metadata"],
                "similarity": round(min(0.95, 0.5 + score * 0.1), 4),
                "document_title": c["document_title"],
                "document_category": c["document_category"],
                "file_name": c["file_name"],
            }
            for score, c in matched_chunks[:limit]
        ]

    _cache_search_result(q_hash, results)
    return results

def _cache_search_result(key: str, data: List[Dict]) -> None:
    """LRU-style eviction: drop oldest 25% when cache is full."""
    global _SEARCH_RESULT_CACHE
    if len(_SEARCH_RESULT_CACHE) >= _SEARCH_RESULT_CACHE_MAX:
        keys = list(_SEARCH_RESULT_CACHE.keys())
        for k in keys[:_SEARCH_RESULT_CACHE_MAX // 4]:
            del _SEARCH_RESULT_CACHE[k]
    _SEARCH_RESULT_CACHE[key] = data
