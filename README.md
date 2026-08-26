# 🎓 CampusAI — RAG-Based College Chatbot System

CampusAI is a production-grade, Retrieval-Augmented Generation (RAG) conversational platform designed to deliver instant, accurate, and grounded answers for college students, faculty, and administrators. Powered by **Vite + React**, **FastAPI**, **Supabase PostgreSQL (with pgvector)**, and **Google Gemini LLM**, CampusAI ensures zero hallucinations by strictly anchoring answers to official college documents with page citations.

---

## 📌 Problem Statement & Solution

- **Problem**: College websites and student portals host information across dozens of fragmented PDFs (e.g., Academic Handbooks, Hostel Rules, Examination Guidelines, Admission Criteria). Students spend hours searching for accurate facts, while administrative staff are inundated with repetitive queries.
- **Solution**: CampusAI indexes official PDFs into semantic 768-dimensional vector embeddings stored in Supabase `pgvector`. When a student asks a question, CampusAI performs high-speed cosine similarity search, retrieves the top-K relevant chunks, and prompts Gemini to synthesize a grounded answer accompanied by exact document titles and page references.

---

## ✨ Key Features

- 💬 **Grounded RAG Chat**: Instant answers bound to official college document context.
- 📄 **Page-Aware PDF Chunking**: PyMuPDF page text extraction preserving exact page numbers.
- 🔍 **Vector Similarity Search**: Cosine distance similarity search using Supabase `pgvector` HNSW index.
- 🛡️ **Zero Hallucination Guarantee**: Fallback response when relevant information is not in the knowledge base.
- 📚 **Source Citations**: Displays document title, page number, similarity percentage, and snippet text.
- 👨‍💼 **Admin Control Dashboard**: PDF upload, validation, document status lifecycle (`UPLOADED` → `PROCESSING` → `COMPLETED` / `FAILED`), category filtering, search, sorting, and document deletion.
- 📊 **Analytics & Feedback**: Statistics for registered users, processed PDFs, conversation metrics, and 👍/👎 student answer feedback.
- 🔒 **Secure Authentication**: Bcrypt password hashing, HS256 JWT token authorization, and role-based access control (Student vs Admin).
- 🌐 **Multilingual & Responsive**: Mobile-friendly sidebar drawer and native Gemini multilingual query understanding.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend SPA** | React 18, Vite 5, Tailwind CSS, Lucide Icons, Axios |
| **Backend API** | Python 3.13, FastAPI, Pydantic v2, PyMuPDF, Bcrypt, PyJWT |
| **Vector Database** | Supabase PostgreSQL, `pgvector` extension, HNSW Index |
| **File Storage** | Supabase Storage (`college-documents` bucket) |
| **AI Models** | Google Gemini (`gemini-1.5-flash` & `text-embedding-004`) |
| **Deployment** | Vercel (Frontend), Render (Backend) |

---

## 📐 RAG Pipeline Architecture

```
[ Student Question ]
        │
        ▼
[ Query Embedding (Gemini text-embedding-004) ]
        │
        ▼
[ Supabase pgvector Similarity Search (match_document_chunks RPC) ]
        │
        ▼
[ Top-K Relevant Chunks (Cosine Similarity >= 0.7) ]
        │
        ▼
[ Grounded Context Assembly ]
        │
        ▼
[ Gemini 1.5 Flash LLM Answer Generation ]
        │
        ▼
[ Grounded Answer + Source Cards (Title, Page #, Snippet) ]
```

---

## 🗄️ Database Schema & RPC Setup

Execute `schema_full.sql` in your Supabase SQL Editor:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'admin')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Documents Table
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
    uploaded_by TEXT REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- 3. Document Chunks Table
CREATE TABLE IF NOT EXISTS document_chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    page_number INTEGER,
    embedding vector(768),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_document_chunks_hnsw ON document_chunks USING hnsw (embedding vector_cosine_ops);

-- 4. Vector Match RPC Function
CREATE OR REPLACE FUNCTION match_document_chunks(
    query_embedding vector(768),
    match_threshold float,
    match_count int
)
RETURNS TABLE (
    id TEXT,
    document_id TEXT,
    chunk_index INT,
    content TEXT,
    page_number INT,
    similarity float,
    metadata JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id,
        dc.document_id,
        dc.chunk_index,
        dc.content,
        dc.page_number,
        1 - (dc.embedding <=> query_embedding) AS similarity,
        dc.metadata
    FROM document_chunks dc
    WHERE 1 - (dc.embedding <=> query_embedding) >= match_threshold
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

---

## ⚡ Environment Variables Guide

Copy `.env.example` to `.env` in the root and backend folders:

```env
# Supabase Configuration
SUPABASE_URL=https://your-supabase-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
SUPABASE_STORAGE_BUCKET=college-documents

# Authentication
JWT_SECRET=your-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI Configuration (Google Gemini)
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-flash
EMBEDDING_MODEL=text-embedding-004

# Application Parameters
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
MAX_FILE_SIZE_MB=10
RAG_TOP_K=4
RAG_SIMILARITY_THRESHOLD=0.7
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

---

## 🚀 Local Development Setup

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Automated Testing

Run complete unit and integration tests:

```bash
# Backend Automated Unit Tests (45 tests)
cd backend
python -m unittest discover -s tests

# Frontend Production SPA Build Validation
cd frontend
npm run build
```

---

## ☁️ Deployment Instructions

### Frontend Deployment (Vercel)
1. Import repository into Vercel dashboard.
2. Set Root Directory to `frontend`.
3. Set Build Command to `npm run build` and Output Directory to `dist`.
4. Add Environment Variable:
   - `VITE_API_URL=https://campusai-backend.onrender.com`

### Backend Deployment (Render)
1. Create a new Web Service on Render from the GitHub repo.
2. Set Root Directory to `backend`.
3. Set Environment to `Python 3`.
4. Set Build Command: `pip install -r requirements.txt`.
5. Set Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
6. Add Environment Variables: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `GEMINI_API_KEY`, `JWT_SECRET`, `FRONTEND_URL`.

---

## 📄 License & Attribution

CampusAI is open-source software built for educational institutions. Built with FastAPI, Supabase, and Google Gemini.
