import os
import logging
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

logger = logging.getLogger("campusai.database")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

_supabase_client: Optional[Client] = None
_supabase_admin_client: Optional[Client] = None

def get_supabase_client() -> Optional[Client]:
    """
    Returns an initialized Supabase Client using anonymous key.
    Handles configuration errors gracefully.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if not SUPABASE_URL or not SUPABASE_ANON_KEY or "your-supabase-project" in SUPABASE_URL:
        logger.warning("Supabase URL or Anon Key is unconfigured in environment variables.")
        return None

    try:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        logger.info("Supabase client initialized successfully.")
        return _supabase_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        return None

def get_supabase_admin_client() -> Optional[Client]:
    """
    Returns an initialized Supabase Client using service role key for backend admin tasks.
    """
    global _supabase_admin_client
    if _supabase_admin_client is not None:
        return _supabase_admin_client

    key = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY
    if not SUPABASE_URL or not key or "your-supabase-project" in SUPABASE_URL:
        logger.warning("Supabase configuration missing for admin client.")
        return None

    try:
        _supabase_admin_client = create_client(SUPABASE_URL, key)
        return _supabase_admin_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase admin client: {e}")
        return None
