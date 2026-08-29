import sqlite3
import os
import uuid
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from app.database.supabase import get_supabase_admin_client, get_supabase_client

logger = logging.getLogger("campusai.db_service")

LOCAL_DB_PATH = os.path.join(os.path.dirname(__file__), "local_campusai.db")

def init_db():
    """
    Initializes all 6 database tables, indexes, and cascading foreign keys.
    """
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
        cursor = conn.cursor()
        try:
            cursor.execute("PRAGMA journal_mode = WAL;")
        except Exception:
            pass
        cursor.execute("PRAGMA foreign_keys = ON;")

        # 1. users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'admin')),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """)

        # 2. documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL DEFAULT 'General',
                file_name TEXT NOT NULL,
                file_url TEXT,
                file_size INTEGER NOT NULL DEFAULT 0,
                mime_type TEXT NOT NULL DEFAULT 'application/pdf',
                status TEXT NOT NULL DEFAULT 'UPLOADED' CHECK (status IN ('UPLOADED', 'PROCESSING', 'COMPLETED', 'FAILED')),
                error_message TEXT,
                uploaded_by TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                processed_at TEXT,
                FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
            );
        """)

        # 3. document_chunks table (with embedding vector array JSON representation)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                page_number INTEGER,
                embedding TEXT, -- JSON array string of 768 dimensions
                metadata TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
            );
        """)

        # 4. conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL DEFAULT 'New Conversation',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # 5. messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                sources TEXT DEFAULT '[]',
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );
        """)

        # 6. feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                message_id TEXT NOT NULL,
                rating TEXT NOT NULL CHECK (rating IN ('positive', 'negative')),
                comment TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
            );
        """)

        # Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_uploaded_by ON documents(uploaded_by);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_message_id ON feedback(message_id);")

        conn.commit()
        conn.close()

        try:
            from app.database.users_db import ensure_demo_users
            ensure_demo_users()
        except Exception as e:
            logger.warning(f"ensure_demo_users error: {e}")
    except Exception as e:
        logger.warning(f"init_db exception: {e}")

# Run initialization
init_db()

# --- Helper Functions for Database Verification & Operations ---

def get_db_tables() -> List[str]:
    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def create_document_record(
    title: str,
    file_name: str,
    uploaded_by: str,
    category: str = "General",
    description: Optional[str] = None,
    file_url: Optional[str] = None,
    file_size: int = 0,
    mime_type: str = "application/pdf"
) -> Dict[str, Any]:
    doc_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    supabase = get_supabase_admin_client() or get_supabase_client()
    if supabase:
        try:
            res = supabase.table("documents").insert({
                "id": doc_id,
                "title": title,
                "description": description,
                "category": category,
                "file_name": file_name,
                "file_url": file_url,
                "file_size": file_size,
                "mime_type": mime_type,
                "status": "UPLOADED",
                "uploaded_by": uploaded_by,
                "created_at": now,
                "updated_at": now
            }).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.warning(f"Supabase document insert failed ({e}); falling back to local store.")

    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO documents (id, title, description, category, file_name, file_url, file_size, mime_type, status, uploaded_by, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'UPLOADED', ?, ?, ?)
    """, (doc_id, title, description, category, file_name, file_url, file_size, mime_type, uploaded_by, now, now))
    conn.commit()
    conn.close()
    
    return {
        "id": doc_id,
        "title": title,
        "description": description,
        "category": category,
        "file_name": file_name,
        "file_url": file_url,
        "file_size": file_size,
        "mime_type": mime_type,
        "status": "UPLOADED",
        "error_message": None,
        "uploaded_by": uploaded_by,
        "created_at": now,
        "updated_at": now,
        "processed_at": None
    }

def get_documents(category: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    supabase = get_supabase_admin_client() or get_supabase_client()
    if supabase:
        try:
            query = supabase.table("documents").select("*")
            if category:
                query = query.eq("category", category)
            if status:
                query = query.eq("status", status)
            res = query.order("created_at", desc=True).execute()
            if res.data is not None:
                return res.data
        except Exception as e:
            logger.warning(f"Supabase documents fetch failed ({e}); falling back to local store.")

    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    cursor = conn.cursor()
    sql = "SELECT id, title, description, category, file_name, file_url, file_size, mime_type, status, error_message, uploaded_by, created_at, updated_at, processed_at FROM documents WHERE 1=1"
    params = []
    if category:
        sql += " AND category = ?"
        params.append(category)
    if status:
        sql += " AND status = ?"
        params.append(status)
    sql += " ORDER BY created_at DESC"
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [{
        "id": r[0],
        "title": r[1],
        "description": r[2],
        "category": r[3],
        "file_name": r[4],
        "file_url": r[5],
        "file_size": r[6],
        "mime_type": r[7],
        "status": r[8],
        "error_message": r[9],
        "uploaded_by": r[10],
        "created_at": r[11],
        "updated_at": r[12],
        "processed_at": r[13]
    } for r in rows]

def get_document_by_id(document_id: str) -> Optional[Dict[str, Any]]:
    supabase = get_supabase_admin_client() or get_supabase_client()
    if supabase:
        try:
            res = supabase.table("documents").select("*").eq("id", document_id).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.warning(f"Supabase document fetch failed ({e}); falling back to local store.")

    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, description, category, file_name, file_url, file_size, mime_type, status, error_message, uploaded_by, created_at, updated_at, processed_at
        FROM documents WHERE id = ?
    """, (document_id,))
    r = cursor.fetchone()
    conn.close()
    if not r:
        return None
    return {
        "id": r[0],
        "title": r[1],
        "description": r[2],
        "category": r[3],
        "file_name": r[4],
        "file_url": r[5],
        "file_size": r[6],
        "mime_type": r[7],
        "status": r[8],
        "error_message": r[9],
        "uploaded_by": r[10],
        "created_at": r[11],
        "updated_at": r[12],
        "processed_at": r[13]
    }

def update_document_status(document_id: str, status: str, error_message: Optional[str] = None) -> Optional[Dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    processed_at = now if status in ["COMPLETED", "FAILED"] else None

    supabase = get_supabase_admin_client() or get_supabase_client()
    if supabase:
        try:
            payload = {"status": status, "updated_at": now}
            if error_message is not None:
                payload["error_message"] = error_message
            if processed_at:
                payload["processed_at"] = processed_at
            res = supabase.table("documents").update(payload).eq("id", document_id).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.warning(f"Supabase update failed ({e}); falling back to local store.")

    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE documents SET status = ?, error_message = ?, updated_at = ?, processed_at = COALESCE(?, processed_at)
        WHERE id = ?
    """, (status, error_message, now, processed_at, document_id))
    conn.commit()
    conn.close()
    return get_document_by_id(document_id)

def delete_document_record(document_id: str) -> bool:
    supabase = get_supabase_admin_client() or get_supabase_client()
    if supabase:
        try:
            supabase.table("documents").delete().eq("id", document_id).execute()
        except Exception as e:
            logger.warning(f"Supabase document deletion failed ({e}); falling back to local store.")

    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    conn.commit()
    conn.close()
    return True

def add_document_chunk(document_id: str, chunk_index: int, content: str, page_number: int = 1, embedding: Optional[List[float]] = None) -> Dict[str, Any]:
    chunk_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    emb_json = json.dumps(embedding) if embedding else None
    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO document_chunks (id, document_id, chunk_index, content, page_number, embedding, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (chunk_id, document_id, chunk_index, content, page_number, emb_json, now))
    conn.commit()
    conn.close()
    return {"id": chunk_id, "document_id": document_id, "chunk_index": chunk_index}

def get_chunks_for_document(document_id: str) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    cursor = conn.cursor()
    cursor.execute("SELECT id, chunk_index, content FROM document_chunks WHERE document_id = ?", (document_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "chunk_index": r[1], "content": r[2]} for r in rows]

def create_conversation(user_id: str, title: str = "New Chat") -> Dict[str, Any]:
    conv_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    supabase = get_supabase_client()
    if supabase:
        try:
            res = supabase.table("conversations").insert({
                "id": conv_id,
                "user_id": user_id,
                "title": title,
                "created_at": now,
                "updated_at": now
            }).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.warning(f"Supabase conversation create failed ({e}); using local database.")

    # Guarantee user record exists in SQLite before conversation insert (prevents FK IntegrityError)
    from app.database.users_db import ensure_user_in_sqlite
    ensure_user_in_sqlite(user_id)

    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO conversations (id, user_id, title, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
    """, (conv_id, user_id, title, now, now))
    conn.commit()
    conn.close()
    return {"id": conv_id, "user_id": user_id, "title": title, "created_at": now, "updated_at": now}

def touch_conversation_updated_at(conversation_id: str):
    now = datetime.now(timezone.utc).isoformat()
    supabase = get_supabase_client()
    if supabase:
        try:
            supabase.table("conversations").update({"updated_at": now}).eq("id", conversation_id).execute()
        except Exception as e:
            logger.warning(f"Supabase update conversation timestamp failed ({e}); using local store.")

    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    cursor = conn.cursor()
    cursor.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conversation_id))
    conn.commit()
    conn.close()

def get_user_conversations(user_id: str) -> List[Dict[str, Any]]:
    supabase = get_supabase_client()
    if supabase:
        try:
            res = supabase.table("conversations").select("*").eq("user_id", user_id).order("updated_at", desc=True).execute()
            if res.data is not None:
                return res.data
        except Exception as e:
            logger.warning(f"Supabase user conversations fetch failed ({e}); using local database.")

    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, title, created_at, updated_at FROM conversations WHERE user_id = ? ORDER BY updated_at DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{
        "id": r[0],
        "user_id": r[1],
        "title": r[2],
        "created_at": r[3],
        "updated_at": r[4]
    } for r in rows]

def get_conversation_by_id(conversation_id: str) -> Optional[Dict[str, Any]]:
    supabase = get_supabase_client()
    if supabase:
        try:
            res = supabase.table("conversations").select("*").eq("id", conversation_id).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.warning(f"Supabase conversation fetch failed ({e}); using local database.")

    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, title, created_at, updated_at FROM conversations WHERE id = ?", (conversation_id,))
    r = cursor.fetchone()
    conn.close()
    if r:
        return {"id": r[0], "user_id": r[1], "title": r[2], "created_at": r[3], "updated_at": r[4]}
    return None

def add_message(
    conversation_id: str,
    sender: Optional[str] = None,
    role: Optional[str] = None,
    content: str = "",
    sources: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    msg_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    msg_role = role or sender or "user"
    sources_json = json.dumps(sources) if sources else None

    supabase = get_supabase_client()
    if supabase:
        try:
            res = supabase.table("messages").insert({
                "id": msg_id,
                "conversation_id": conversation_id,
                "role": msg_role,
                "content": content,
                "sources": sources,
                "created_at": now
            }).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.warning(f"Supabase message insert failed ({e}); using local database.")

    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (id, conversation_id, role, content, sources, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (msg_id, conversation_id, msg_role, content, sources_json, now))
    conn.commit()
    conn.close()
    return {
        "id": msg_id,
        "conversation_id": conversation_id,
        "role": msg_role,
        "sender": msg_role,
        "content": content,
        "sources": sources,
        "created_at": now
    }

def get_messages_by_conversation(conversation_id: str) -> List[Dict[str, Any]]:
    supabase = get_supabase_client()
    if supabase:
        try:
            res = supabase.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at", desc=False).execute()
            if res.data is not None:
                return res.data
        except Exception as e:
            logger.warning(f"Supabase messages fetch failed ({e}); using local database.")

    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    cursor = conn.cursor()
    cursor.execute("SELECT id, conversation_id, role, content, sources, created_at FROM messages WHERE conversation_id = ? ORDER BY created_at ASC", (conversation_id,))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        try:
            srcs = json.loads(r[4]) if r[4] else []
        except Exception:
            srcs = []
        results.append({
            "id": r[0],
            "conversation_id": r[1],
            "role": r[2],
            "sender": r[2],
            "content": r[3],
            "sources": srcs,
            "created_at": r[5]
        })
    return results

def delete_conversation_record(conversation_id: str) -> bool:
    supabase = get_supabase_client()
    if supabase:
        try:
            supabase.table("conversations").delete().eq("id", conversation_id).execute()
        except Exception as e:
            logger.warning(f"Supabase conversation deletion failed ({e}); using local database.")

    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
    conn.commit()
    conn.close()
    return True

def get_message_by_id(message_id: str) -> Optional[Dict[str, Any]]:
    supabase = get_supabase_client()
    if supabase:
        try:
            res = supabase.table("messages").select("*").eq("id", message_id).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.warning(f"Supabase message fetch failed ({e}); using local database.")

    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    cursor = conn.cursor()
    cursor.execute("SELECT id, conversation_id, role, content, sources, created_at FROM messages WHERE id = ?", (message_id,))
    r = cursor.fetchone()
    conn.close()
    if r:
        return {"id": r[0], "conversation_id": r[1], "role": r[2], "content": r[3], "sources": r[4], "created_at": r[5]}
    return None

def save_feedback_record(user_id: str, message_id: str, rating: str, comment: Optional[str] = None) -> Dict[str, Any]:
    fb_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    norm_rating = "positive" if rating.lower() in ["helpful", "positive"] else "negative"

    supabase = get_supabase_client()
    if supabase:
        try:
            res = supabase.table("feedback").insert({
                "id": fb_id,
                "user_id": user_id,
                "message_id": message_id,
                "rating": norm_rating,
                "comment": comment,
                "created_at": now
            }).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.warning(f"Supabase feedback insert failed ({e}); using local database.")

    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO feedback (id, user_id, message_id, rating, comment, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fb_id, user_id, message_id, norm_rating, comment, now))
    conn.commit()
    conn.close()
    return {
        "id": fb_id,
        "user_id": user_id,
        "message_id": message_id,
        "rating": norm_rating,
        "comment": comment,
        "created_at": now
    }

def get_admin_dashboard_stats() -> Dict[str, Any]:
    supabase = get_supabase_client()
    if supabase:
        try:
            users_cnt = supabase.table("users").select("id", count="exact").execute().count or 0
            docs_cnt = supabase.table("documents").select("id", count="exact").execute().count or 0
            completed_cnt = supabase.table("documents").select("id", count="exact").eq("status", "COMPLETED").execute().count or 0
            failed_cnt = supabase.table("documents").select("id", count="exact").eq("status", "FAILED").execute().count or 0
            convs_cnt = supabase.table("conversations").select("id", count="exact").execute().count or 0
            msgs_cnt = supabase.table("messages").select("id", count="exact").execute().count or 0
            pos_fb_cnt = supabase.table("feedback").select("id", count="exact").eq("rating", "helpful").execute().count or 0
            neg_fb_cnt = supabase.table("feedback").select("id", count="exact").eq("rating", "unhelpful").execute().count or 0

            return {
                "total_students": users_cnt,
                "total_documents": docs_cnt,
                "completed_documents": completed_cnt,
                "failed_documents": failed_cnt,
                "total_conversations": convs_cnt,
                "total_messages": msgs_cnt,
                "positive_feedback": pos_fb_cnt,
                "negative_feedback": neg_fb_cnt
            }
        except Exception as e:
            logger.warning(f"Supabase stats fetch failed ({e}); using local database.")

    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    users_cnt = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM documents")
    docs_cnt = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM documents WHERE status = 'COMPLETED'")
    completed_cnt = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM documents WHERE status = 'FAILED'")
    failed_cnt = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM conversations")
    convs_cnt = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM messages")
    msgs_cnt = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feedback WHERE rating = 'helpful' OR rating = 'positive'")
    pos_fb_cnt = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feedback WHERE rating = 'unhelpful' OR rating = 'negative'")
    neg_fb_cnt = cursor.fetchone()[0]

    conn.close()

    return {
        "total_students": users_cnt,
        "total_documents": docs_cnt,
        "completed_documents": completed_cnt,
        "failed_documents": failed_cnt,
        "total_conversations": convs_cnt,
        "total_messages": msgs_cnt,
        "positive_feedback": pos_fb_cnt,
        "negative_feedback": neg_fb_cnt
    }

# Backward compatibility aliases for test suite
create_conversation_record = create_conversation
add_message_record = add_message
get_messages_for_conversation = get_messages_by_conversation
