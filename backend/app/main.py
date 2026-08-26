import os
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

app = FastAPI(
    title="CampusAI Backend API",
    description="RAG-Based College Chatbot Backend Service",
    version="1.0.0"
)

# CORS Configuration
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
origins = [
    frontend_url,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(document_router, prefix="/api", tags=["Document Management"])
app.include_router(chat_router)
app.include_router(conv_router)
app.include_router(bonus_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to CampusAI API",
        "docs": "/docs",
        "health": "/api/health"
    }
