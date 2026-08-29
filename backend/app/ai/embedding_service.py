import os
import re
import math
import httpx
import logging
from functools import lru_cache
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("campusai.embedding_service")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "768"))

GEMINI_EMBED_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_EMBEDDING_MODEL}:embedContent"

# Persistent HTTP Client pool to eliminate TLS handshake latency
_http_client = httpx.Client(timeout=10.0, limits=httpx.Limits(max_keepalive_connections=20, max_connections=50))

def _generate_fallback_vector(text: str, dim: int = EMBEDDING_DIMENSION) -> List[float]:
    """
    Generates a normalized float vector based on word feature hashing
    when Gemini API key is missing or unconfigured in local test environments.
    """
    vector = [0.0] * dim
    words = re.findall(r'\w+', text.lower())
    
    if not words:
        words = ["empty"]
        
    for word in words:
        for idx in range(5):
            bucket = (hash(f"{word}_{idx}") % dim)
            weight = 1.0 / (idx + 1)
            vector[bucket] += weight

    magnitude = math.sqrt(sum(x * x for x in vector)) or 1.0
    return [round(x / magnitude, 6) for x in vector]

@lru_cache(maxsize=1024)
def generate_embedding(text: str) -> List[float]:
    """
    Generates embedding for text using Google Gemini REST API or LRU cache.
    """
    if not text or not text.strip():
        return [0.0] * EMBEDDING_DIMENSION

    cleaned_text = text.strip()

    if not GEMINI_API_KEY or "your-gemini-api-key" in GEMINI_API_KEY or "mock-gemini" in GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY is unconfigured or mock; using deterministic vector generator for testing.")
        return _generate_fallback_vector(cleaned_text, EMBEDDING_DIMENSION)

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_EMBEDDING_MODEL}:embedContent?key={GEMINI_API_KEY}"
        payload = {
            "model": f"models/{GEMINI_EMBEDDING_MODEL}",
            "content": {
                "parts": [
                    {"text": cleaned_text[:2048]}
                ]
            }
        }
        
        response = _http_client.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            embedding_values = data.get("embedding", {}).get("values", [])
            if len(embedding_values) >= EMBEDDING_DIMENSION:
                return embedding_values[:EMBEDDING_DIMENSION]
            elif len(embedding_values) > 0:
                return embedding_values + [0.0] * (EMBEDDING_DIMENSION - len(embedding_values))
            else:
                return _generate_fallback_vector(cleaned_text, EMBEDDING_DIMENSION)
        elif response.status_code in (404, 400) and GEMINI_EMBEDDING_MODEL != "embedding-001":
            # Retry with legacy embedding-001
            retry_url = f"https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent?key={GEMINI_API_KEY}"
            retry_payload = {
                "model": "models/embedding-001",
                "content": {"parts": [{"text": cleaned_text[:2048]}]}
            }
            res2 = _http_client.post(retry_url, json=retry_payload)
            if res2.status_code == 200:
                vals = res2.json().get("embedding", {}).get("values", [])
                if vals:
                    return vals[:EMBEDDING_DIMENSION] if len(vals) >= EMBEDDING_DIMENSION else vals + [0.0]*(EMBEDDING_DIMENSION-len(vals))
            return _generate_fallback_vector(cleaned_text, EMBEDDING_DIMENSION)
        else:
            logger.error(f"Gemini Embedding API returned HTTP {response.status_code}: {response.text[:120]}")
            return _generate_fallback_vector(cleaned_text, EMBEDDING_DIMENSION)
    except Exception as e:
        logger.error(f"Gemini embedding generation failed: {e}")
        return _generate_fallback_vector(cleaned_text, EMBEDDING_DIMENSION)

def generate_batch_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generates embeddings for a list of text chunks.
    """
    return [generate_embedding(text) for text in texts]
