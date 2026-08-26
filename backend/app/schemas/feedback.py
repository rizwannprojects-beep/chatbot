from pydantic import BaseModel, Field
from typing import Optional

class FeedbackRequest(BaseModel):
    message_id: str = Field(..., description="ID of the assistant message being rated")
    rating: str = Field(..., description="Rating: 'helpful' or 'unhelpful'")
    comment: Optional[str] = Field(None, description="Optional text comment describing feedback")

class FeedbackResponse(BaseModel):
    success: bool
    message: str
    id: str
