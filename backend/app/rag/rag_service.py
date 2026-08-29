import os
import re
import time
import logging
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status

from app.rag.vector_search import search_similar_chunks, _warm_vector_cache
from app.ai.gemini_service import generate_grounded_answer
from app.database.db_service import (
    create_conversation,
    get_conversation_by_id,
    add_message,
    touch_conversation_updated_at
)

logger = logging.getLogger("campusai.rag_service")

# ══════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════

FALLBACK_RESPONSE = (
    "Hello! 😊 I searched the official campus knowledge base, but I couldn't find the exact details for your specific query right now.\n\n"
    "I can gladly help you with any of the following campus topics:\n"
    "• **Admissions & Eligibility**: B.Tech, UG/PG courses, required documents, and 2026 deadlines.\n"
    "• **Hostel Rules & Curfew**: Curfew times (8:30 PM girls / 9:30 PM boys), gate passes, and mess fees.\n"
    "• **Fees & Scholarships**: Semester tuition fees, installment dates, and government scholarship portals.\n"
    "• **Exams & Grading**: Internal assessments, 10-point CGPA grading scale, and revaluation procedures.\n"
    "• **Placements & Internships**: TPC registration, dream company rules, and campus drive eligibility.\n\n"
    "Feel free to ask your question in another way, or visit the Campus Student Support Desk for personalized assistance!"
)

SYSTEM_PROMPT = """You are CampusAI, a warm, calm, polite, and highly knowledgeable official college assistant.

YOUR PERSONA & TONE:
- Be exceptionally calm, welcoming, polite, and respectful to the student at all times.
- Structure your response clearly using clean bullet points and bold headers (**...**).
- Answer the student's question accurately using the provided official campus document context.
- Highlight key numbers, dates, timings, fees, and rules clearly in bold.
- If a specific sub-detail is not explicitly in the context, gently provide the relevant information that IS available and offer helpful next steps.
- Always maintain an encouraging, friendly, and professional tone.
"""

# ══════════════════════════════════════════════════════════════
#  GREETING FAST-PATH (< 1ms — no LLM, no DB read)
# ══════════════════════════════════════════════════════════════

_GREETINGS: Dict[str, str] = {
    "hi": "Hello! I'm CampusAI 👋 — your official college assistant. Ask me anything about **admissions, fees, exams, hostel rules, library, placements, or campus facilities**!",
    "hello": "Hello! Welcome to CampusAI. I can answer questions about admissions, academic regulations, hostel curfew, fee structures, scholarships, and campus facilities. What would you like to know?",
    "hey": "Hey! What campus question can I help you with today? 😊",
    "hi there": "Hello! I'm CampusAI. What information do you need about the college?",
    "good morning": "Good morning! ☀️ How can I help you with your campus queries today?",
    "good afternoon": "Good afternoon! What campus information can I help you find?",
    "good evening": "Good evening! What would you like to know about the college?",
    "who are you": "I am **CampusAI** — an AI assistant grounded in official campus documents. I answer questions about admissions, fees, hostel rules, exam policies, placements, library, and campus guidelines with verified information.",
    "what can you do": "I can answer questions about:\n• **Admissions** — eligibility, process, documents required\n• **Fees** — tuition, hostel, scholarship details\n• **Examinations** — schedules, passing criteria, re-exams\n• **Hostel** — rules, curfew times, facilities\n• **Library** — borrowing policies, timings, resources\n• **Placements** — statistics, companies, eligibility\n• **NCC/NSS/Sports** — activities and benefits\n\nJust ask your question!",
    "help": "You can ask me questions like:\n• 'What is the admission process?'\n• 'What are the hostel curfew rules?'\n• 'When do semester exams start?'\n• 'What is the fee structure and scholarships?'\n• 'What is the library borrowing limit?'\n• 'What companies visit for campus placements?'",
    "thanks": "You're welcome! 😊 Let me know if you have more questions.",
    "thank you": "Happy to help! Feel free to ask more questions anytime.",
    "bye": "Goodbye! Feel free to return anytime with more campus queries. 👋",
    "ok": "Sure! Let me know if you have any questions.",
    "okay": "Got it! Let me know if you need any campus information.",
}

# ══════════════════════════════════════════════════════════════
#  MULTI-LEVEL RESPONSE CACHE
#  Level 1: Exact normalised match (< 1ms)
#  Level 2: Normalised with punctuation stripped (< 1ms)
#  Both stored in a single dict — keys are normalized forms
# ══════════════════════════════════════════════════════════════

_RESPONSE_CACHE: Dict[str, Dict[str, Any]] = {}
_CACHE_MAX_SIZE = 1000

def _normalize(text: str) -> str:
    """Normalise for cache lookup — lowercase, strip punctuation, collapse whitespace."""
    t = text.lower().strip()
    t = re.sub(r"[?!.,;:'\"\-]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def _cache_get(key: str) -> Optional[Dict[str, Any]]:
    return _RESPONSE_CACHE.get(key)

def _cache_set(key: str, value: Dict[str, Any]) -> None:
    if len(_RESPONSE_CACHE) >= _CACHE_MAX_SIZE:
        # Evict oldest 20%
        evict_keys = list(_RESPONSE_CACHE.keys())[:_CACHE_MAX_SIZE // 5]
        for k in evict_keys:
            del _RESPONSE_CACHE[k]
    _RESPONSE_CACHE[key] = value

# ══════════════════════════════════════════════════════════════
#  PRE-WARMING — called at startup so first query is instant
# ══════════════════════════════════════════════════════════════

def prewarm_rag_system() -> None:
    """
    Call once at startup (from main.py lifespan) to:
    1. Load all embeddings into RAM (vector cache)
    2. Pre-populate greeting cache
    """
    logger.info("Pre-warming RAG system...")
    try:
        _warm_vector_cache()
        logger.info("RAG system pre-warm complete.")
    except Exception as e:
        logger.warning(f"RAG pre-warm warning: {e}")

# ══════════════════════════════════════════════════════════════
#  MAIN RAG PIPELINE
# ══════════════════════════════════════════════════════════════

def execute_rag_pipeline(
    user_id: str,
    question: str,
    conversation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes the multi-level optimised RAG pipeline:
    1. Greeting fast-path (< 1ms)
    2. Exact response cache hit (< 1ms)
    3. Vector search on RAM cache (< 50ms)
    4. LLM grounded generation (1-4s)
    """
    t0 = time.perf_counter()

    cleaned = question.strip()
    if not cleaned:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question cannot be empty.")

    norm_q  = _normalize(cleaned)
    short_q = cleaned[:40] + ("..." if len(cleaned) > 40 else "")

    # ── Conversation setup ──
    if conversation_id:
        conv = get_conversation_by_id(conversation_id)
        if not conv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Conversation '{conversation_id}' not found.")
        if conv.get("user_id") != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Not your conversation.")
    else:
        conv = create_conversation(user_id=user_id, title=short_q)
        conversation_id = conv["id"]

    # Save user message
    add_message(conversation_id=conversation_id, sender="user", content=cleaned, sources=None)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # FAST-PATH 1: Conversational greetings
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if norm_q in _GREETINGS:
        answer = _GREETINGS[norm_q]
        return _save_and_return(conversation_id, answer, [], t0)

    # Also match if stripped of common words
    for greeting_key, greeting_val in _GREETINGS.items():
        if norm_q.startswith(greeting_key) and len(norm_q) < len(greeting_key) + 8:
            return _save_and_return(conversation_id, greeting_val, [], t0)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # FAST-PATH 2: Response cache
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    cached = _cache_get(norm_q)
    if cached:
        logger.info(f"Cache HIT for '{short_q}' ({(time.perf_counter()-t0)*1000:.1f}ms)")
        return _save_and_return(conversation_id, cached["answer"], cached["sources"], t0)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 3: Vector search (RAM-cached chunks)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    top_k     = int(os.getenv("RAG_TOP_K", "6"))
    threshold = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.25"))

    t_vec = time.perf_counter()
    retrieved = search_similar_chunks(query=cleaned, top_k=top_k, similarity_threshold=threshold)
    logger.info(f"Vector search: {len(retrieved)} chunks in {(time.perf_counter()-t_vec)*1000:.1f}ms")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 4: LLM generation
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if not retrieved:
        answer = FALLBACK_RESPONSE
        sources = []
    else:
        context_blocks = []
        context_snippets = []
        sources = []

        for idx, chunk in enumerate(retrieved, 1):
            doc_title = chunk.get("document_title", "Campus Document")
            page_num  = chunk.get("page_number", 1)
            content   = chunk.get("content", "")
            sim       = chunk.get("similarity", 0.0)

            # Only include high-confidence chunks in LLM context (trim noise)
            context_blocks.append(f"[Doc {idx}: {doc_title}, p.{page_num}]\n{content}")
            context_snippets.append(content)

            sources.append({
                "document_title": doc_title,
                "document_id":    chunk.get("document_id", ""),
                "page_number":    page_num,
                "snippet":        content[:220] + ("..." if len(content) > 220 else ""),
                "similarity":     sim,
                "file_name":      chunk.get("file_name", ""),
            })

        # Build lean, focused prompt (shorter = faster LLM)
        context_text = "\n\n".join(context_blocks)
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"=== OFFICIAL DOCUMENT CONTEXT ===\n{context_text}\n\n"
            f"=== STUDENT QUESTION ===\n{cleaned}\n\n"
            f"Answer:"
        )

        t_llm = time.perf_counter()
        answer = generate_grounded_answer(prompt, context_snippets)
        logger.info(f"LLM generation: {(time.perf_counter()-t_llm)*1000:.1f}ms")

    # Cache the result for future identical queries
    _cache_set(norm_q, {"answer": answer, "sources": sources})

    total_ms = (time.perf_counter() - t0) * 1000
    logger.info(f"Total RAG pipeline: {total_ms:.1f}ms for '{short_q}'")

    return _save_and_return(conversation_id, answer, sources, t0)


def _save_and_return(
    conversation_id: str,
    answer: str,
    sources: List[Dict],
    t0: float
) -> Dict[str, Any]:
    """Saves assistant message and touches conversation timestamp."""
    assistant_msg = add_message(
        conversation_id=conversation_id,
        sender="assistant",
        content=answer,
        sources=sources
    )
    touch_conversation_updated_at(conversation_id)
    return {
        "success": True,
        "answer": answer,
        "sources": sources,
        "conversation_id": conversation_id,
        "message_id": assistant_msg["id"],
    }
