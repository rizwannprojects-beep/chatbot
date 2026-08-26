from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class SourceItem(BaseModel):
    document_title: str
    document_id: str
    page_number: Optional[int] = None
    snippet: str
    similarity: float
    file_name: Optional[str] = None

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Student query text")
    conversation_id: Optional[str] = Field(None, description="Existing conversation UUID")

class ChatResponse(BaseModel):
    success: bool = True
    answer: str
    sources: List[SourceItem] = []
    conversation_id: str
    message_id: str
