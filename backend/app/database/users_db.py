import sqlite3
import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from app.database.supabase import get_supabase_admin_client, get_supabase_client
from app.database.db_service import LOCAL_DB_PATH

logger = logging.getLogger("campusai.users_db")

def create_user_record(name: str, email: str, password_hash: str, role: str = "student") -> Dict[str, Any]:
    """
    Creates a new user record in Supabase or local persistent database.
    """
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    supabase = get_supabase_admin_client() or get_supabase_client()
    if supabase:
        try:
            res = supabase.table("users").insert({
                "id": user_id,
                "name": name,
                "email": email.lower().strip(),
                "password_hash": password_hash,
                "role": role,
                "created_at": now,
                "updated_at": now
            }).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.warning(f"Supabase insert failed ({e}); falling back to local persistent store.")

    # Local persistent fallback
    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (id, name, email, password_hash, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, name, email.lower().strip(), password_hash, role, now, now))
        conn.commit()
        return {
            "id": user_id,
            "name": name,
            "email": email.lower().strip(),
            "password_hash": password_hash,
            "role": role,
            "created_at": now,
            "updated_at": now
        }
    finally:
        conn.close()

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a user by email address.
    """
    normalized_email = email.lower().strip()
    supabase = get_supabase_admin_client() or get_supabase_client()
    if supabase:
        try:
            res = supabase.table("users").select("*").eq("email", normalized_email).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.warning(f"Supabase query failed ({e}); falling back to local persistent store.")

    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, email, password_hash, role, created_at, updated_at FROM users WHERE email = ?", (normalized_email,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "password_hash": row[3],
                "role": row[4],
                "created_at": row[5],
                "updated_at": row[6]
            }
        return None
    finally:
        conn.close()

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a user by user ID.
    """
    supabase = get_supabase_admin_client() or get_supabase_client()
    if supabase:
        try:
            res = supabase.table("users").select("*").eq("id", user_id).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.warning(f"Supabase query failed ({e}); falling back to local persistent store.")

    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, email, password_hash, role, created_at, updated_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "password_hash": row[3],
                "role": row[4],
                "created_at": row[5],
                "updated_at": row[6]
            }
        return None
    finally:
        conn.close()
