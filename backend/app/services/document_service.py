import os
import re
import uuid
import logging
from typing import Optional, List, Dict, Any
from fastapi import UploadFile, HTTPException, status
from app.database.db_service import (
    create_document_record,
    get_documents,
    get_document_by_id,
    update_document_status,
    delete_document_record
)

logger = logging.getLogger("campusai.document_service")

# Upload directory
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

ALLOWED_MIME_TYPES = {"application/pdf"}
ALLOWED_EXTENSIONS = {".pdf"}

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes user file names to prevent path traversal and shell execution risks.
    """
    # Remove directory paths
    base_name = os.path.basename(filename)
    # Strip dangerous characters
    cleaned = re.sub(r'[^a-zA-Z0-9_.-]', '_', base_name)
    # Ensure extension is lowercase
    name_part, ext = os.path.splitext(cleaned)
    return f"{name_part[:50]}{ext.lower()}"

async def save_uploaded_pdf(
    file: UploadFile,
    title: str,
    category: str,
    uploaded_by: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validates PDF file, enforces file size & MIME limits, saves file securely to disk,
    and stores metadata in database.
    """
    # 1. Validate extension
    file_ext = os.path.splitext(file.filename or "")[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{file_ext}'. Only PDF (.pdf) documents are accepted."
        )

    # 2. Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid MIME type '{file.content_type}'. File must be an application/pdf."
        )

    # 3. Read and validate file size
    contents = await file.read()
    file_size = len(contents)
    
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size ({file_size / (1024*1024):.2f} MB) exceeds maximum limit of {MAX_FILE_SIZE_MB} MB."
        )

    # 4. Generate safe stored file name
    safe_name = sanitize_filename(file.filename or "uploaded.pdf")
    unique_prefix = uuid.uuid4().hex[:8]
    stored_filename = f"{unique_prefix}_{safe_name}"
    file_path = os.path.join(UPLOAD_DIR, stored_filename)

    # 5. Write file safely to disk
    with open(file_path, "wb") as f:
        f.write(contents)

    file_url = f"/uploads/{stored_filename}"

    # Try uploading to Supabase Storage bucket if configured
    from app.database.supabase import get_supabase_admin_client
    supabase_admin = get_supabase_admin_client()
    if supabase_admin:
        try:
            bucket = os.getenv("SUPABASE_STORAGE_BUCKET", "college-documents")
            supabase_admin.storage.from_(bucket).upload(stored_filename, contents, {"content-type": "application/pdf"})
            file_url = f"/storage/v1/object/public/{bucket}/{stored_filename}"
            logger.info(f"Uploaded file '{stored_filename}' to Supabase Storage bucket '{bucket}'")
        except Exception as e:
            logger.warning(f"Supabase Storage upload warning ({e}); utilizing local storage path.")

    # 6. Save metadata record in DB
    doc_record = create_document_record(
        title=title,
        description=description,
        category=category,
        file_name=stored_filename,
        file_url=file_url,
        file_size=file_size,
        mime_type="application/pdf",
        uploaded_by=uploaded_by
    )

    return doc_record

def list_all_documents(category: Optional[str] = None, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    return get_documents(category=category, status=status_filter)

def fetch_document_details(document_id: str) -> Dict[str, Any]:
    doc = get_document_by_id(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found."
        )
    return doc

def remove_document(document_id: str) -> bool:
    doc = get_document_by_id(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found."
        )

    # Delete disk file if present
    file_name = doc.get("file_name")
    if file_name:
        file_path = os.path.join(UPLOAD_DIR, file_name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Could not delete physical file {file_path}: {e}")

        # Remove from Supabase Storage if configured
        from app.database.supabase import get_supabase_admin_client
        supabase_admin = get_supabase_admin_client()
        if supabase_admin:
            try:
                bucket = os.getenv("SUPABASE_STORAGE_BUCKET", "college-documents")
                supabase_admin.storage.from_(bucket).remove([file_name])
                logger.info(f"Removed file '{file_name}' from Supabase Storage bucket '{bucket}'")
            except Exception as e:
                logger.warning(f"Supabase Storage file deletion warning: {e}")

    # Delete database record
    return delete_document_record(document_id)

def start_document_processing_status(document_id: str) -> Dict[str, Any]:
    from app.rag.document_processor import process_document
    return process_document(document_id)
