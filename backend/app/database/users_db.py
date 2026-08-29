import sqlite3
import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from app.database.supabase import get_supabase_admin_client, get_supabase_client
LOCAL_DB_PATH = os.path.join(os.path.dirname(__file__), "local_campusai.db")

logger = logging.getLogger("campusai.users_db")

def ensure_user_in_sqlite(user_id: str, name: str = "Student", email: str = "", role: str = "student") -> None:
    """
    Guarantees that a user_id exists in the local SQLite users table to satisfy
    foreign key constraints for conversations and messages.
    """
    if not user_id:
        return
    now = datetime.now(timezone.utc).isoformat()
    user_email = email.lower().strip() if email else f"user_{user_id[:8]}@campusai.local"
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO users (id, name, email, password_hash, role, created_at, updated_at)
            VALUES (?, ?, ?, 'managed_auth', ?, ?, ?)
        """, (user_id, name, user_email, role, now, now))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"ensure_user_in_sqlite warning: {e}")

def create_user_record(name: str, email: str, password_hash: str, role: str = "student") -> Dict[str, Any]:
    """
    Creates a new user record in Supabase and local persistent database.
    """
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    clean_email = email.lower().strip()
    
    # Always write to local SQLite first to guarantee local FK integrity
    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (id, name, email, password_hash, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, name, clean_email, password_hash, role, now, now))
        conn.commit()
    except Exception as e:
        logger.warning(f"Local SQLite user insert exception: {e}")
    finally:
        conn.close()

    # Try Supabase sync if configured
    supabase = get_supabase_admin_client() or get_supabase_client()
    if supabase:
        try:
            supabase.table("users").insert({
                "id": user_id,
                "name": name,
                "email": clean_email,
                "password_hash": password_hash,
                "role": role,
                "created_at": now,
                "updated_at": now
            }).execute()
        except Exception as e:
            logger.warning(f"Supabase insert sync failed ({e}); local persistent store active.")

    return {
        "id": user_id,
        "name": name,
        "email": clean_email,
        "password_hash": password_hash,
        "role": role,
        "created_at": now,
        "updated_at": now
    }

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

def ensure_demo_users() -> None:
    """
    Ensures that default demo users (Student and Admin) exist in SQLite and Supabase
    so the demo credentials shown on the login UI function seamlessly out of the box.
    """
    from app.auth.security import hash_password, verify_password
    
    demo_users = [
        {
            "name": "Demo Student",
            "email": "student_test@college.edu",
            "password": "studentpass123",
            "role": "student"
        },
        {
            "name": "Demo Admin",
            "email": "admin_test@college.edu",
            "password": "adminpass123",
            "role": "admin"
        }
    ]

    for demo in demo_users:
        existing = get_user_by_email(demo["email"])
        if not existing:
            pwd_hash = hash_password(demo["password"])
            create_user_record(
                name=demo["name"],
                email=demo["email"],
                password_hash=pwd_hash,
                role=demo["role"]
            )
            logger.info(f"Demo user created: {demo['email']} ({demo['role']})")
        else:
            if not verify_password(demo["password"], existing.get("password_hash", "")):
                new_hash = hash_password(demo["password"])
                try:
                    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
                    c = conn.cursor()
                    c.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_hash, demo["email"]))
                    conn.commit()
                    conn.close()
                    logger.info(f"Demo user password updated: {demo['email']}")
                except Exception as e:
                    logger.warning(f"Failed to update demo user password hash in SQLite: {e}")
                
                supabase = get_supabase_admin_client() or get_supabase_client()
                if supabase:
                    try:
                        supabase.table("users").update({"password_hash": new_hash}).eq("email", demo["email"]).execute()
                    except Exception as e:
                        logger.warning(f"Failed to update demo user password hash in Supabase: {e}")

