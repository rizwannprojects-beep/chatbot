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

DEFAULT_TOP_K = int(os.getenv("RAG_TOP_K", "4"))
DEFAULT_SIMILARITY_THRESHOLD = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.20"))

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
    Performs Question-Aware hybrid vector search over in-RAM cache.
    Applies topic category boosting, keyword matching, topic mismatch penalization,
    deduplication, and strict score thresholding.
    """
    if not query or not query.strip():
        return []

    limit = top_k if top_k is not None else DEFAULT_TOP_K
    threshold = similarity_threshold if similarity_threshold is not None else DEFAULT_SIMILARITY_THRESHOLD

    q_hash = hashlib.md5(f"{query.strip().lower()}{limit}{threshold}".encode()).hexdigest()
    if q_hash in _SEARCH_RESULT_CACHE:
        return _SEARCH_RESULT_CACHE[q_hash]

    from app.rag.intent_service import analyze_query_intent
    intent = analyze_query_intent(query)
    if intent["is_ambiguous"]:
        return []

    query_vector = generate_embedding(query.strip())
    if not query_vector or len(query_vector) < 10:
        logger.warning("Failed to generate valid query embedding.")
        return []

    query_mag = math.sqrt(sum(x * x for x in query_vector))
    if query_mag == 0:
        return []

    _warm_vector_cache()
    if not _VECTOR_CACHE:
        return []

    scored_chunks = []
    target_cat = intent.get("target_category")
    keywords = intent.get("keywords", set())
    title_kws = intent.get("title_keywords", [])

    for chunk in _VECTOR_CACHE:
        sim = _fast_cosine(query_vector, query_mag, chunk)
        
        # Calculate hybrid boost / penalty
        category_boost = 0.0
        keyword_boost = 0.0
        mismatch_penalty = 0.0

        chunk_cat = chunk.get("document_category", "")
        chunk_title = chunk.get("document_title", "").lower()
        chunk_content = chunk.get("content", "").lower()

        # 1. Category boost
        if target_cat and chunk_cat.lower() == target_cat.lower():
            category_boost = 0.15
        elif target_cat and chunk_cat:
            mismatch_penalty = 0.20  # Penalize unrelated categories when strong domain intent exists

        # 2. Keyword boost
        matching_kws = sum(1 for kw in keywords if kw in chunk_content or kw in chunk_title)
        if matching_kws > 0:
            keyword_boost = min(0.20, matching_kws * 0.05)

        for tk in title_kws:
            if tk in chunk_title:
                keyword_boost += 0.08

        # Composite score
        composite_score = sim + category_boost + keyword_boost - mismatch_penalty

        if composite_score >= threshold or (sim >= 0.45 and mismatch_penalty == 0):
            scored_chunks.append((composite_score, sim, chunk))

    # Sort by composite score descending
    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    # Deduplicate near-identical chunks
    unique_chunks = []
    seen_contents = []

    for score, sim, c in scored_chunks:
        c_text = c["content"].strip()
        # Simple overlap check to avoid returning duplicate snippets
        is_dup = False
        for seen in seen_contents:
            if c_text[:100] == seen[:100] or (len(c_text) > 50 and c_text[:60] in seen):
                is_dup = True
                break
        if not is_dup:
            seen_contents.append(c_text)
            unique_chunks.append((score, sim, c))
            if len(unique_chunks) >= limit:
                break

    results = [
        {
            "id": c["id"],
            "document_id": c["document_id"],
            "chunk_index": c["chunk_index"],
            "content": c["content"],
            "page_number": c["page_number"],
            "metadata": c["metadata"],
            "similarity": round(max(sim, score), 4),
            "document_title": c["document_title"],
            "document_category": c["document_category"],
            "file_name": c["file_name"],
        }
        for score, sim, c in unique_chunks
    ]

    _cache_search_result(q_hash, results)
    return results

def _cache_search_result(key: str, data: List[Dict]) -> None:
    global _SEARCH_RESULT_CACHE
    if len(_SEARCH_RESULT_CACHE) >= _SEARCH_RESULT_CACHE_MAX:
        keys = list(_SEARCH_RESULT_CACHE.keys())
        for k in keys[:_SEARCH_RESULT_CACHE_MAX // 4]:
            del _SEARCH_RESULT_CACHE[k]
    _SEARCH_RESULT_CACHE[key] = data
