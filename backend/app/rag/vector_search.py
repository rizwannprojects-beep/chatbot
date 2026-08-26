import os
import sqlite3
import json
import math
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from app.ai.embedding_service import generate_embedding, EMBEDDING_DIMENSION
from app.database.supabase import get_supabase_client
from app.database.db_service import LOCAL_DB_PATH

load_dotenv()

logger = logging.getLogger("campusai.vector_search")

DEFAULT_TOP_K = int(os.getenv("RAG_TOP_K", "4"))
DEFAULT_SIMILARITY_THRESHOLD = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.7"))

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

def search_similar_chunks(
    query: str,
    top_k: Optional[int] = None,
    similarity_threshold: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Performs pgvector cosine similarity search over stored document chunks.
    Filters by similarity_threshold and respects top_k limits.
    """
    if not query or not query.strip():
        return []

    limit = top_k if top_k is not None else DEFAULT_TOP_K
    threshold = similarity_threshold if similarity_threshold is not None else DEFAULT_SIMILARITY_THRESHOLD

    # 1. Generate Query Vector Embedding
    query_vector = generate_embedding(query.strip())
    if not query_vector or len(query_vector) != EMBEDDING_DIMENSION:
        logger.warning(f"Failed to generate valid {EMBEDDING_DIMENSION}-dim query embedding.")
        return []

    # 2. Try Supabase pgvector RPC search
    supabase = get_supabase_client()
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
            if res.data is not None:
                return res.data
        except Exception as e:
            logger.warning(f"Supabase RPC vector search failed ({e}); using local vector search fallback.")

    # 3. Fallback Local Cosine Similarity Search over SQLite vectors
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            c.id, c.document_id, c.chunk_index, c.content, c.page_number, c.embedding, c.metadata,
            d.title, d.category, d.file_name
        FROM document_chunks c
        JOIN documents d ON d.id = c.document_id
        WHERE c.embedding IS NOT NULL AND c.embedding != ''
    """)
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        chunk_id, doc_id, chunk_idx, content, page_num, emb_str, meta_str, doc_title, doc_cat, file_name = r
        try:
            chunk_vector = json.loads(emb_str)
        except Exception:
            continue

        sim = cosine_similarity(query_vector, chunk_vector)
        if sim >= threshold:
            try:
                meta = json.loads(meta_str) if meta_str else {}
            except Exception:
                meta = {}
                
            results.append({
                "id": chunk_id,
                "document_id": doc_id,
                "chunk_index": chunk_idx,
                "content": content,
                "page_number": page_num,
                "metadata": meta,
                "similarity": round(sim, 4),
                "document_title": doc_title,
                "document_category": doc_cat,
                "file_name": file_name
            })

    # Sort by similarity descending and limit to top_k
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:limit]
