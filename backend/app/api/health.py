from fastapi import APIRouter
from app.database.supabase import get_supabase_client

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint returning application status, vector cache status, and database readiness.
    """
    from app.rag.vector_search import _VECTOR_CACHE
    import os
    
    supabase_client = get_supabase_client()
    return {
        "status": "healthy",
        "service": "CampusAI Backend API",
        "version": "1.0.0",
        "database_connection": "configured" if supabase_client is not None else "unconfigured_or_pending",
        "cached_chunks": len(_VECTOR_CACHE),
        "gemini_api_key_set": bool(os.getenv("GEMINI_API_KEY") and len(os.getenv("GEMINI_API_KEY")) > 10)
    }
