# 🚀 CampusAI Production Deployment Guide

This guide provides step-by-step instructions for deploying CampusAI to production using **Vercel** (Frontend), **Render** (Backend), **Supabase** (Database & Storage), and **Google Gemini** (Embeddings & LLM).

---

## 1. Supabase Setup (Database & Vector Search)

1. Sign in to [Supabase Console](https://supabase.com) and create a new project.
2. Open the **SQL Editor** tab and run the script located at `backend/app/database/schema_full.sql`.
3. Confirm that:
   - `vector` extension is enabled (`CREATE EXTENSION IF NOT EXISTS vector;`).
   - All 6 core tables are created (`users`, `documents`, `document_chunks`, `conversations`, `messages`, `feedback`).
   - `match_document_chunks` RPC function is created.
4. Navigate to **Storage** in Supabase and create a new bucket named `college-documents` (Private or Public depending on requirements).
5. Copy your **Project URL**, **Anon Key**, and **Service Role Key** from **Project Settings → API**.

---

## 2. Google Gemini API Setup

1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Generate an API Key with access to:
   - Embedding Model: `text-embedding-004`
   - LLM Model: `gemini-1.5-flash`
3. Save the key as `GEMINI_API_KEY`.

---

## 3. Backend Deployment (Render)

1. Log in to [Render Console](https://render.com) and create a **New Web Service**.
2. Connect your GitHub Repository.
3. Configure the service settings:
   - **Name**: `campusai-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add the following **Environment Variables** in Render:
   - `SUPABASE_URL`: `https://<your-project-ref>.supabase.co`
   - `SUPABASE_ANON_KEY`: `<your-anon-key>`
   - `SUPABASE_SERVICE_ROLE_KEY`: `<your-service-role-key>`
   - `SUPABASE_STORAGE_BUCKET`: `college-documents`
   - `GEMINI_API_KEY`: `<your-gemini-api-key>`
   - `GEMINI_MODEL`: `gemini-1.5-flash`
   - `EMBEDDING_MODEL`: `text-embedding-004`
   - `JWT_SECRET`: `<secure-random-jwt-secret>`
   - `JWT_ALGORITHM`: `HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: `1440`
   - `FRONTEND_URL`: `https://campusai-frontend.vercel.app` (your Vercel URL)
   - `RAG_TOP_K`: `4`
   - `RAG_SIMILARITY_THRESHOLD`: `0.7`
5. Deploy Web Service and copy your public Render URL (e.g. `https://campusai-backend.onrender.com`).
6. Test Health Endpoint: `GET https://campusai-backend.onrender.com/api/health`.

---

## 4. Frontend Deployment (Vercel)

1. Log in to [Vercel Console](https://vercel.com) and click **Add New Project**.
2. Select your GitHub repository.
3. Configure Project Settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add Environment Variable:
   - `VITE_API_URL`: `https://campusai-backend.onrender.com` (your Render backend URL)
5. Click **Deploy**.
6. Once deployed, update the `FRONTEND_URL` on Render to match your exact Vercel production domain.

---

## 5. Post-Deployment Verification Checklist

- [ ] `GET /api/health` returns `{"status": "healthy"}`.
- [ ] Student registration and login function cleanly.
- [ ] Admin document PDF upload succeeds and saves to Supabase Storage.
- [ ] Document processing extracts text, chunks page-by-page, and inserts vector embeddings.
- [ ] Student chat queries retrieve relevant chunks and output grounded answers with page citations.
- [ ] Conversation history and answer feedback persist correctly.
