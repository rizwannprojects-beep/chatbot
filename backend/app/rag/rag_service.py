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

# ══════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════

FALLBACK_RESPONSE = (
    "I searched the official campus documents, but I couldn't find specific details for your query right now.\n\n"
    "You can ask me about:\n"
    "• **Admissions & Eligibility**: B.Tech, PG courses, required documents\n"
    "• **Hostel Rules & Curfew**: Gate times (8:30 PM girls / 9:30 PM boys), gate passes\n"
    "• **Fees & Scholarships**: Tuition fees, government scholarship portals\n"
    "• **Exams & Grading**: Internal marks, 10-point CGPA scale, revaluation\n"
    "• **Placements**: TPC rules, company eligibility, campus drives"
)

SYSTEM_PROMPT = """You are CampusAI, the official college assistant.

CRITICAL ANSWERING RULES:
1. Answer the student's EXACT question directly and specifically.
2. Rely strictly on facts, percentages, fees, deadlines, and rules provided in the OFFICIAL DOCUMENT CONTEXT.
3. Do NOT include unrelated topics (e.g., if asked about attendance, do NOT include scholarships, hostel rules, or Wi-Fi info).
4. Do NOT use generic introductory filler or greetings like "Hello! 😊 Based on official campus documents...". Start directly with the answer.
5. Keep your response clear, concise, professional, and well-structured.
6. If the context does not contain the answer, state clearly that the document does not provide that information. Do not invent policies.
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
# ══════════════════════════════════════════════════════════════

_RESPONSE_CACHE: Dict[str, Dict[str, Any]] = {}
_CACHE_MAX_SIZE = 1000

def _normalize(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r"[?!.,;:'\"\-]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def _cache_get(key: str) -> Optional[Dict[str, Any]]:
    return _RESPONSE_CACHE.get(key)

def _cache_set(key: str, value: Dict[str, Any]) -> None:
    if len(_RESPONSE_CACHE) >= _CACHE_MAX_SIZE:
        evict_keys = list(_RESPONSE_CACHE.keys())[:_CACHE_MAX_SIZE // 5]
        for k in evict_keys:
            del _RESPONSE_CACHE[k]
    _RESPONSE_CACHE[key] = value

def prewarm_rag_system() -> None:
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
    t0 = time.perf_counter()

    cleaned = question.strip()
    if not cleaned:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question cannot be empty.")

    norm_q  = _normalize(cleaned)
    short_q = cleaned[:40] + ("..." if len(cleaned) > 40 else "")

    try:
        conv = None
        if conversation_id:
            conv = get_conversation_by_id(conversation_id)
            if not conv or conv.get("user_id") != user_id:
                conv = None

        if not conv:
            conv = create_conversation(user_id=user_id, title=short_q)
            conversation_id = conv["id"]

        add_message(conversation_id=conversation_id, sender="user", content=cleaned, sources=None)

        # 1. Greetings
        if norm_q in _GREETINGS:
            answer = _GREETINGS[norm_q]
            return _save_and_return(conversation_id, answer, [], t0)

        for greeting_key, greeting_val in _GREETINGS.items():
            if norm_q.startswith(greeting_key) and len(norm_q) < len(greeting_key) + 8:
                return _save_and_return(conversation_id, greeting_val, [], t0)

        # 2. Intent & Ambiguity Check
        from app.rag.intent_service import analyze_query_intent
        intent = analyze_query_intent(cleaned)
        if intent["is_ambiguous"]:
            answer = intent["clarification_message"]
            return _save_and_return(conversation_id, answer, [], t0)

        # 3. Vector search
        raw_thresh = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.10"))
        threshold = min(0.10, raw_thresh)

        t_vec = time.perf_counter()
        retrieved = search_similar_chunks(query=cleaned, top_k=top_k, similarity_threshold=threshold)
        logger.info(f"Vector search: {len(retrieved)} chunks in {(time.perf_counter()-t_vec)*1000:.1f}ms")

        # 4. Prompt & Answer Generation
        context_blocks = []
        context_snippets = []
        sources = []

        if retrieved:
            for idx, chunk in enumerate(retrieved, 1):
                doc_title = chunk.get("document_title", "Campus Document")
                page_num  = chunk.get("page_number", 1)
                content   = chunk.get("content", "")
                sim       = chunk.get("similarity", 0.0)

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

            context_text = "\n\n".join(context_blocks)
            prompt = (
                f"{SYSTEM_PROMPT}\n\n"
                f"=== OFFICIAL DOCUMENT CONTEXT ===\n{context_text}\n\n"
                f"=== STUDENT QUESTION ===\n{cleaned}\n\n"
                f"Question-Specific Answer:"
            )
            t_llm = time.perf_counter()
            answer = generate_grounded_answer(prompt, context_snippets, question=cleaned)
            logger.info(f"LLM generation: {(time.perf_counter()-t_llm)*1000:.1f}ms")
        else:
            # Fallback when official documents do not contain relevant details
            fallback_prompt = (
                f"SYSTEM: You are CampusAI, an official campus assistant. You MUST stay strictly grounded in official documents.\n"
                f"CRITICAL INSTRUCTION: Do not invent, fabricate, or estimate any specific figures, fee amounts, dates, or campus rules under any circumstances.\n\n"
                f"=== STUDENT QUESTION ===\n{cleaned}\n\n"
                f"State clearly that official details regarding '{cleaned}' were not found in the campus knowledge base and direct the student to the Campus Support Desk."
            )
            t_llm = time.perf_counter()
            answer = generate_grounded_answer(fallback_prompt, [], question=cleaned)
            logger.info(f"Fallback LLM generation: {(time.perf_counter()-t_llm)*1000:.1f}ms")
            sources = []

        total_ms = (time.perf_counter() - t0) * 1000
        logger.info(f"Total RAG pipeline: {total_ms:.1f}ms for '{short_q}'")

        return _save_and_return(conversation_id, answer, sources, t0)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in execute_rag_pipeline: {type(e).__name__}: {e}")
        fallback_prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"=== STUDENT QUESTION ===\n{cleaned}\n\n"
            f"Provide a clear, accurate, structured, and comprehensive answer detailing the policies, rules, placement statistics, procedures, or guidelines for this topic."
        )
        answer = generate_grounded_answer(fallback_prompt, [], question=cleaned)
        cid = conversation_id or str(uuid.uuid4())
        return _save_and_return(cid, answer, [], t0)


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
