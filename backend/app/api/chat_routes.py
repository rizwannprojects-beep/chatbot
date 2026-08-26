from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.schemas.chat import ChatRequest, ChatResponse
from app.auth.dependencies import get_current_user
from app.rag.rag_service import execute_rag_pipeline

chat_router = APIRouter(prefix="/api/chat", tags=["Chat"])

@chat_router.post("", response_model=ChatResponse)
def handle_chat_query(
    payload: ChatRequest,
    current_user: Any = Depends(get_current_user)
):
    """
    POST /api/chat
    Executes end-to-end RAG query pipeline for authenticated students/admins.
    """
    user_id = getattr(current_user, "id", None) or (current_user.get("id") if isinstance(current_user, dict) else str(current_user))
    result = execute_rag_pipeline(
        user_id=user_id,
        question=payload.question,
        conversation_id=payload.conversation_id
    )
    return result
