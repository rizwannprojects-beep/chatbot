import os
import re
import math
import httpx
import logging
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("campusai.embedding_service")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
EMBEDDING_DIMENSION = 768

GEMINI_EMBED_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_EMBEDDING_MODEL}:embedContent"

def _generate_fallback_vector(text: str, dim: int = EMBEDDING_DIMENSION) -> List[float]:
    """
    Generates a normalized 768-dimensional float vector based on word feature hashing
    when Gemini API key is missing or unconfigured in local test environments.
    """
    vector = [0.0] * dim
    words = re.findall(r'\w+', text.lower())
    
    if not words:
        words = ["empty"]
        
    for word in words:
        # Hash each word into multiple vector dimension buckets
        for idx in range(5):
            bucket = (hash(f"{word}_{idx}") % dim)
            weight = 1.0 / (idx + 1)
            vector[bucket] += weight

    # Normalize vector to unit length
    magnitude = math.sqrt(sum(x * x for x in vector)) or 1.0
    return [round(x / magnitude, 6) for x in vector]

def generate_embedding(text: str) -> List[float]:
    """
    Calls Google Gemini REST API to generate a 768-dimensional text embedding.
    """
    if not text or not text.strip():
        return [0.0] * EMBEDDING_DIMENSION

    cleaned_text = text.strip()

    if not GEMINI_API_KEY or "your-gemini-api-key" in GEMINI_API_KEY or "mock-gemini" in GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY is unconfigured or mock; using deterministic 768-dim vector generator for testing.")
        return _generate_fallback_vector(cleaned_text, EMBEDDING_DIMENSION)

    try:
        url = f"{GEMINI_EMBED_URL}?key={GEMINI_API_KEY}"
        payload = {
            "model": f"models/{GEMINI_EMBEDDING_MODEL}",
            "content": {
                "parts": [
                    {"text": cleaned_text[:2048]}  # Truncate safe context length
                ]
            }
        }
        
        with httpx.Client(timeout=15.0) as client:
            response = client.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                embedding_values = data.get("embedding", {}).get("values", [])
                if len(embedding_values) == EMBEDDING_DIMENSION:
                    return embedding_values
                else:
                    logger.warning(f"Unexpected embedding dimension {len(embedding_values)}; expected {EMBEDDING_DIMENSION}")
                    return embedding_values[:EMBEDDING_DIMENSION]
            else:
                logger.error(f"Gemini Embedding API returned HTTP {response.status_code}: {response.text}")
                return _generate_fallback_vector(cleaned_text, EMBEDDING_DIMENSION)
    except Exception as e:
        logger.error(f"Gemini embedding generation failed: {e}")
        return _generate_fallback_vector(cleaned_text, EMBEDDING_DIMENSION)

def generate_batch_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generates 768-dimensional embeddings for a list of text chunks.
    """
    return [generate_embedding(text) for text in texts]
