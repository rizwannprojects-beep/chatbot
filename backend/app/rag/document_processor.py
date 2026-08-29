import os
import re
import fitz  # PyMuPDF
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from fastapi import HTTPException, status

from app.database.db_service import (
    get_document_by_id,
    update_document_status,
    add_document_chunk,
    LOCAL_DB_PATH
)
from app.database.supabase import get_supabase_admin_client, get_supabase_client
import sqlite3

load_dotenv()

logger = logging.getLogger("campusai.document_processor")

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

def clean_text(text: str) -> str:
    """
    Normalizes extracted PDF text, cleans irregular whitespace and unprintable artifacts.
    """
    if not text:
        return ""
    # Replace non-breaking spaces and control characters
    text = text.replace('\xa0', ' ').replace('\r\n', '\n').replace('\r', '\n')
    # Collapse multiple vertical spaces while preserving paragraph breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Collapse horizontal spaces
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.split('\n')]
    cleaned = '\n'.join(lines).strip()
    return cleaned

def extract_text_by_pages(file_path: str) -> List[Dict[str, Any]]:
    """
    Extracts text page-by-page from a PDF using PyMuPDF.
    Preserves page number for each page.
    """
    if not os.path.exists(file_path):
        raise ValueError(f"Physical file '{file_path}' not found on server.")

    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise ValueError(f"Corrupted or invalid PDF document: {e}")

    if doc.page_count == 0:
        doc.close()
        raise ValueError("PDF document contains 0 pages.")

    pages_data = []
    total_length = 0

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        raw_text = page.get_text("text") or ""
        cleaned = clean_text(raw_text)
        total_length += len(cleaned)
        
        pages_data.append({
            "page_number": page_num + 1,
            "text": cleaned
        })

    doc.close()

    if total_length == 0:
        raise ValueError("No readable text found in PDF document (possibly empty or scanned image PDF).")

    return pages_data

def chunk_page_text(
    pages: List[Dict[str, Any]],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> List[Dict[str, Any]]:
    """
    Divides page text into page-aware sequential chunks.
    Ensures sequential chunk indexing and preserves page numbers.
    """
    chunks = []
    global_chunk_index = 0

    for page in pages:
        page_num = page["page_number"]
        page_text = page["text"]
        
        if not page_text:
            continue

        # If page text is within chunk_size limit, create single chunk
        if len(page_text) <= chunk_size:
            chunks.append({
                "chunk_index": global_chunk_index,
                "content": page_text,
                "page_number": page_num
            })
            global_chunk_index += 1
            continue

        # Split page text into overlapping windows
        start = 0
        text_len = len(page_text)

        while start < text_len:
            end = start + chunk_size
            chunk_content = page_text[start:end].strip()

            if chunk_content:
                chunks.append({
                    "chunk_index": global_chunk_index,
                    "content": chunk_content,
                    "page_number": page_num
                })
                global_chunk_index += 1

            start += (chunk_size - chunk_overlap)

    return chunks

def delete_chunks_for_document(document_id: str):
    """
    Deletes all existing document_chunks for a document to support idempotent reprocessing.
    """
    supabase = get_supabase_admin_client() or get_supabase_client()
    if supabase:
        try:
            supabase.table("document_chunks").delete().eq("document_id", document_id).execute()
        except Exception as e:
            logger.warning(f"Supabase delete chunks failed ({e}); deleting local chunks.")

    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM document_chunks WHERE document_id = ?", (document_id,))
    conn.commit()
    conn.close()

def process_document(document_id: str) -> Dict[str, Any]:
    """
    Complete document processing pipeline:
    FETCH -> STATUS(PROCESSING) -> DELETE OLD CHUNKS -> PYMUPDF EXTRACT -> CLEAN -> CHUNK -> STORE CHUNKS -> STATUS(COMPLETED)
    Handles exceptions safely by setting status to FAILED and logging error message.
    """
    doc = get_document_by_id(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found."
        )

    # 1. Update status to PROCESSING
    update_document_status(document_id, status="PROCESSING")

    try:
        # 2. Delete existing chunks (reprocessing safety)
        delete_chunks_for_document(document_id)

        # 3. Locate physical file
        file_name = doc.get("file_name", "")
        file_path = os.path.join(UPLOAD_DIR, file_name)

        # 4. Extract page text
        pages_data = extract_text_by_pages(file_path)

        # 5. Generate page-aware chunks
        chunks = chunk_page_text(pages_data, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

        if not chunks:
            raise ValueError("No valid document chunks generated from extracted text.")

        # 6. Generate embeddings and store chunks in document_chunks table
        from app.ai.embedding_service import generate_embedding

        for chunk in chunks:
            chunk_metadata = {
                "document_id": document_id,
                "document_title": doc.get("title"),
                "category": doc.get("category"),
                "file_name": doc.get("file_name"),
                "page_number": chunk["page_number"],
                "chunk_size": len(chunk["content"])
            }
            
            # Generate 768-dim vector embedding
            embedding_vector = generate_embedding(chunk["content"])

            add_document_chunk(
                document_id=document_id,
                chunk_index=chunk["chunk_index"],
                content=chunk["content"],
                page_number=chunk["page_number"],
                embedding=embedding_vector
            )

        # 7. Update status to COMPLETED & invalidate vector cache
        from app.rag.vector_search import invalidate_vector_cache
        invalidate_vector_cache()

        updated_doc = update_document_status(document_id, status="COMPLETED", error_message=None)
        logger.info(f"Document '{document_id}' successfully processed into {len(chunks)} chunks.")
        return updated_doc or doc

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Document processing failed for '{document_id}': {error_msg}")
        # Safeguard: never leave document in PROCESSING on failure
        update_document_status(document_id, status="FAILED", error_message=error_msg)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document processing failed: {error_msg}"
        )
