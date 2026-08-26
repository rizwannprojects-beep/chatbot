from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any

from app.auth.dependencies import get_current_user
from app.database.db_service import (
    get_user_conversations,
    get_conversation_by_id,
    get_messages_by_conversation,
    delete_conversation_record
)

conv_router = APIRouter(prefix="/api/conversations", tags=["Conversations"])

def _get_user_id(user: Any) -> str:
    return getattr(user, "id", None) or (user.get("id") if isinstance(user, dict) else str(user))

@conv_router.get("", response_model=List[Dict[str, Any]])
def list_user_conversations(current_user: Any = Depends(get_current_user)):
    """
    GET /api/conversations
    Returns all conversations owned by the authenticated student, sorted by updated_at DESC.
    """
    user_id = _get_user_id(current_user)
    return get_user_conversations(user_id)

@conv_router.get("/{id}", response_model=Dict[str, Any])
def get_single_conversation(id: str, current_user: Any = Depends(get_current_user)):
    """
    GET /api/conversations/{id}
    Returns details of a specific conversation owned by the authenticated student.
    """
    user_id = _get_user_id(current_user)
    conv = get_conversation_by_id(id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID '{id}' not found."
        )
    if conv.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not own this conversation."
        )
    return conv

@conv_router.get("/{id}/messages", response_model=List[Dict[str, Any]])
def get_conversation_messages(id: str, current_user: Any = Depends(get_current_user)):
    """
    GET /api/conversations/{id}/messages
    Returns all message history for a conversation thread owned by the student.
    """
    user_id = _get_user_id(current_user)
    conv = get_conversation_by_id(id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID '{id}' not found."
        )
    if conv.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not own this conversation."
        )
    return get_messages_by_conversation(id)

@conv_router.delete("/{id}")
def delete_user_conversation(id: str, current_user: Any = Depends(get_current_user)):
    """
    DELETE /api/conversations/{id}
    Deletes a conversation and its messages via cascading deletion.
    """
    user_id = _get_user_id(current_user)
    conv = get_conversation_by_id(id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID '{id}' not found."
        )
    if conv.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You cannot delete another user's conversation."
        )
    
    success = delete_conversation_record(id)
    return {"success": success, "message": "Conversation deleted successfully."}
