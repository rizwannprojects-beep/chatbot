from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import Optional, List
from app.auth.dependencies import require_admin
from app.schemas.auth import UserResponse
from app.schemas.document import DocumentResponse
from app.services.document_service import (
    save_uploaded_pdf,
    list_all_documents,
    fetch_document_details,
    remove_document,
    start_document_processing_status
)

router = APIRouter(prefix="/documents", tags=["Document Management"])

@router.get("", response_model=List[DocumentResponse])
async def get_documents_endpoint(
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    admin_user: UserResponse = Depends(require_admin)
):
    """
    Returns list of all uploaded college documents.
    Only accessible by authenticated administrators.
    """
    return list_all_documents(category=category, status_filter=status_filter)

@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document_endpoint(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("General"),
    description: Optional[str] = Form(None),
    admin_user: UserResponse = Depends(require_admin)
):
    """
    Uploads a new college PDF document.
    Enforces MIME validation, extension check, file size limit, and safe filename sanitization.
    Only accessible by authenticated administrators.
    """
    doc_record = await save_uploaded_pdf(
        file=file,
        title=title,
        category=category,
        uploaded_by=admin_user.id,
        description=description
    )
    return doc_record

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document_by_id_endpoint(
    document_id: str,
    admin_user: UserResponse = Depends(require_admin)
):
    """
    Returns metadata and processing status for a specific document.
    Only accessible by authenticated administrators.
    """
    return fetch_document_details(document_id)

@router.delete("/{document_id}")
async def delete_document_endpoint(
    document_id: str,
    admin_user: UserResponse = Depends(require_admin)
):
    """
    Deletes a document and its stored physical file.
    Only accessible by authenticated administrators.
    """
    remove_document(document_id)
    return {"success": True, "message": f"Document '{document_id}' successfully deleted."}

@router.post("/{document_id}/process", response_model=DocumentResponse)
async def process_document_endpoint(
    document_id: str,
    admin_user: UserResponse = Depends(require_admin)
):
    """
    Triggers document status update to PROCESSING.
    Only accessible by authenticated administrators.
    """
    return start_document_processing_status(document_id)
