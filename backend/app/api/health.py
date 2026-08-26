from fastapi import APIRouter
from app.database.supabase import get_supabase_client

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint returning application status and database readiness.
    """
    supabase_status = "configured" if get_supabase_client() is not None else "unconfigured_or_pending"
    return {
        "status": "healthy",
        "service": "CampusAI Backend API",
        "version": "1.0.0",
        "database_connection": supabase_status
    }
