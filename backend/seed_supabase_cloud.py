"""
Seed script to populate Supabase Cloud Database with CampusAI document knowledge base.
Wipes existing records and inserts all comprehensive college documents & vector embeddings.
"""

import os
import sys
import uuid
import json
import logging
from datetime import datetime, timezone

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(__file__))

from app.database.supabase import get_supabase_admin_client, get_supabase_client
from app.ai.embedding_service import generate_embedding
from seed_comprehensive_college_data import DOCUMENTS

NOW = datetime.now(timezone.utc).isoformat()

def seed_supabase():
    client = get_supabase_admin_client() or get_supabase_client()
    if not client:
        print("❌ Error: Supabase client could not be initialized. Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.", flush=True)
        sys.exit(1)

    print("🚀 Seeding Supabase Cloud Database with Comprehensive College Knowledge...", flush=True)

    # 1. Clean existing records for fresh seed
    try:
        client.table("document_chunks").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        client.table("documents").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print("Cleared existing documents and chunks from Supabase cloud database.", flush=True)
    except Exception as e:
        print(f"Notice during cleanup: {e}", flush=True)

    print(f"Total documents to upload: {len(DOCUMENTS)}", flush=True)

    total_inserted_docs = 0
    total_inserted_chunks = 0

    for idx, doc in enumerate(DOCUMENTS, 1):
        doc_id = str(uuid.uuid4())
        doc_title = doc["title"]
        category = doc["category"]
        description = doc.get("description", "")
        file_name = doc.get("file_name", "campus_doc.pdf")

        print(f"\n[{idx}/{len(DOCUMENTS)}] Processing Document: '{doc_title}' ({category})", flush=True)

        try:
            # Insert Document record
            doc_res = client.table("documents").insert({
                "id": doc_id,
                "title": doc_title,
                "description": description,
                "category": category,
                "file_name": file_name,
                "file_url": f"/uploads/{file_name}",
                "file_size": 1024,
                "mime_type": "application/pdf",
                "status": "COMPLETED",
                "created_at": NOW,
                "updated_at": NOW,
                "processed_at": NOW
            }).execute()

            if doc_res.data:
                total_inserted_docs += 1
        except Exception as e:
            print(f"  ❌ Error inserting document '{doc_title}': {e}", flush=True)
            continue

        # Insert Chunks
        chunks = doc.get("chunks", [])
        for chunk_idx, chunk in enumerate(chunks):
            content = chunk.get("content", "").strip()
            page_num = chunk.get("page", 1)

            print(f"   -> Generating embedding for chunk {chunk_idx + 1}/{len(chunks)} (p.{page_num})...", flush=True)
            try:
                embedding = generate_embedding(content)
                chunk_id = str(uuid.uuid4())
                metadata = {
                    "document_title": doc_title,
                    "category": category,
                    "page_number": page_num,
                    "file_name": file_name
                }

                chunk_res = client.table("document_chunks").insert({
                    "id": chunk_id,
                    "document_id": doc_id,
                    "chunk_index": chunk_idx,
                    "content": content,
                    "page_number": page_num,
                    "embedding": embedding,
                    "metadata": metadata,
                    "created_at": NOW
                }).execute()

                if chunk_res.data:
                    total_inserted_chunks += 1
            except Exception as e:
                print(f"   ❌ Error inserting chunk {chunk_idx + 1}: {e}", flush=True)

    print("\n" + "=" * 60, flush=True)
    print(f"🎉 SUCCESS! Ingested {total_inserted_docs} Documents and {total_inserted_chunks} Chunks into Supabase Cloud Database!", flush=True)
    print("=" * 60, flush=True)

if __name__ == "__main__":
    seed_supabase()
