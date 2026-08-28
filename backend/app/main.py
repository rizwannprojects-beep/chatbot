import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api.health import router as health_router
from app.api.auth_routes import router as auth_router
from app.api.document_routes import router as document_router
from app.api.chat_routes import chat_router
from app.api.conversation_routes import conv_router
from app.api.bonus_routes import bonus_router

load_dotenv()

logger = logging.getLogger("campusai.main")

# ── Startup / Shutdown lifecycle ──────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-warm vector cache and auto-seed database on startup if fresh
    logger.info("CampusAI startup: checking database knowledge base status...")
    try:
        import sqlite3
        from app.database.db_service import LOCAL_DB_PATH, init_db
        init_db()
        conn = sqlite3.connect(LOCAL_DB_PATH, timeout=10.0)
        c = conn.cursor()
        c.execute("SELECT count(*) FROM documents")
        count = c.fetchone()[0]
        conn.close()
        if count == 0:
            logger.info("Fresh production database detected — auto-seeding 12 comprehensive college policy documents...")
            from seed_comprehensive_college_data import seed_database
            seed_database()
    except Exception as e:
        logger.warning(f"Auto-seed check warning: {e}")

    try:
        from app.rag.rag_service import prewarm_rag_system
        prewarm_rag_system()
        logger.info("RAG pre-warm complete — system ready.")
    except Exception as e:
        logger.warning(f"RAG pre-warm failed (non-fatal): {e}")
    yield
    logger.info("CampusAI shutdown complete.")

app = FastAPI(
    title="CampusAI Backend API",
    description="RAG-Based College Chatbot Backend Service",
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
origins = [
    frontend_url,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://frontend-red-nine-67.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(document_router, prefix="/api", tags=["Document Management"])
app.include_router(chat_router)
app.include_router(conv_router)
app.include_router(bonus_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to CampusAI API v2.0",
        "docs": "/docs",
        "health": "/api/health",
        "status": "optimised RAG pipeline active"
    }
