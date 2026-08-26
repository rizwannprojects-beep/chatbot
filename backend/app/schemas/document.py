from pydantic import BaseModel, Field
from typing import Optional

class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    category: str = Field("General", min_length=2, max_length=100)
    description: Optional[str] = None

class DocumentResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    category: str
    file_name: str
    file_url: Optional[str] = None
    file_size: int
    mime_type: str
    status: str
    error_message: Optional[str] = None
    uploaded_by: Optional[str] = None
    created_at: str
    updated_at: str
    processed_at: Optional[str] = None

    class Config:
        from_attributes = True
