from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.auth.dependencies import get_current_user, require_admin
from app.database.db_service import (
    get_message_by_id,
    get_conversation_by_id,
    save_feedback_record,
    get_admin_dashboard_stats
)

bonus_router = APIRouter(prefix="/api", tags=["Bonus Features"])

def _get_user_id(user: Any) -> str:
    return getattr(user, "id", None) or (user.get("id") if isinstance(user, dict) else str(user))

@bonus_router.post("/feedback", response_model=FeedbackResponse)
def submit_answer_feedback(
    payload: FeedbackRequest,
    current_user: Any = Depends(get_current_user)
):
    """
    POST /api/feedback
    Submit user feedback (helpful/unhelpful + comment) for an assistant message.
    Verifies that the message belongs to a conversation owned by the authenticated student.
    """
    user_id = _get_user_id(current_user)
    
    # 1. Fetch target message
    msg = get_message_by_id(payload.message_id)
    if not msg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with ID '{payload.message_id}' not found."
        )

    # 2. Fetch parent conversation to verify user authorization
    conv_id = msg.get("conversation_id")
    conv = get_conversation_by_id(conv_id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parent conversation for message not found."
        )

    if conv.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You cannot submit feedback for another user's conversation."
        )

    # 3. Normalize rating value
    rating_val = payload.rating.lower()
    if rating_val not in ["helpful", "unhelpful", "positive", "negative"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be 'helpful' or 'unhelpful'."
        )

    # 4. Save feedback
    record = save_feedback_record(
        user_id=user_id,
        message_id=payload.message_id,
        rating="helpful" if rating_val in ["helpful", "positive"] else "unhelpful",
        comment=payload.comment
    )

    return {
        "success": True,
        "message": "Feedback submitted successfully. Thank you!",
        "id": record["id"]
    }

@bonus_router.get("/admin/stats", response_model=Dict[str, Any])
def get_admin_stats(current_user: Any = Depends(require_admin)):
    """
    GET /api/admin/stats
    Admin-only endpoint providing dashboard metrics for users, documents, chats, and feedback sentiment.
    """
    return get_admin_dashboard_stats()
