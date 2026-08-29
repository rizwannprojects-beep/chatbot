import os
import re
import time
import httpx
import logging
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("campusai.gemini_service")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ─────────────────────────────────────────────────────────────
# HTTP client factory — creates a fresh client when needed.
# We keep a module-level client but recreate it on connection errors
# to clear stale TCP keepalive connections (Windows WSARECV issue).
# ─────────────────────────────────────────────────────────────
def _make_client() -> httpx.Client:
    return httpx.Client(
        timeout=httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0),
        limits=httpx.Limits(
            max_keepalive_connections=5,
            max_connections=10,
            keepalive_expiry=15.0      # Shorter expiry to avoid stale connections
        ),
        headers={"Connection": "keep-alive"},
    )

_gemini_client: Optional[httpx.Client] = None

def _get_client() -> httpx.Client:
    global _gemini_client
    if _gemini_client is None or _gemini_client.is_closed:
        _gemini_client = _make_client()
    return _gemini_client

def _reset_client() -> httpx.Client:
    """Force-recreate the HTTP client — called after connection errors."""
    global _gemini_client
    try:
        if _gemini_client and not _gemini_client.is_closed:
            _gemini_client.close()
    except Exception:
        pass
    _gemini_client = _make_client()
    logger.info("HTTP client recreated after connection error.")
    return _gemini_client

# Ordered model fallback chain — valid active Google AI models
_MODELS_TO_TRY = [
    GEMINI_MODEL,
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-pro",
]

# Connection-level errors that require client recreation
_CONNECTION_ERRORS = (
    httpx.RemoteProtocolError,
    httpx.ConnectError,
    httpx.LocalProtocolError,
    ConnectionAbortedError,
    ConnectionResetError,
    BrokenPipeError,
    OSError,
)


def generate_grounded_answer(prompt: str, context_snippets: List[str]) -> str:
    """
    Calls Google Gemini LLM with automatic retry and connection recovery.
    Handles stale TCP keepalive connections (Windows WSARECV error) gracefully.
    """
    if not prompt or not prompt.strip():
        return "Please ask a valid question."

    if not GEMINI_API_KEY or "your-gemini-api-key" in GEMINI_API_KEY or "mock-gemini" in GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY unconfigured — using context synthesis.")
        return _synthesize_from_context(context_snippets)

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 700,
            "topK": 20,
            "topP": 0.85,
            "candidateCount": 1,
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ],
    }

    max_retries = 3

    for model_name in _MODELS_TO_TRY:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model_name}:generateContent?key={GEMINI_API_KEY}"
        )

        for attempt in range(1, max_retries + 1):
            try:
                client = _get_client()
                response = client.post(url, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            text = parts[0].get("text", "").strip()
                            if text:
                                logger.info(f"Gemini OK [{model_name}] attempt {attempt}: {len(text)} chars")
                                return text
                    logger.warning(f"Gemini [{model_name}] returned 200 but empty content.")
                    break  # Don't retry same model if it worked but gave empty

                elif response.status_code == 429:
                    logger.warning(f"Gemini [{model_name}] rate limited (429). Moving to next model.")
                    break  # Try next model immediately

                elif response.status_code in (500, 503, 502):
                    wait = attempt * 0.5
                    logger.warning(f"Gemini [{model_name}] server error {response.status_code}. Retry {attempt}/{max_retries} in {wait}s...")
                    time.sleep(wait)
                    continue

                else:
                    logger.error(f"Gemini [{model_name}] HTTP {response.status_code}: {response.text[:150]}")
                    break

            except httpx.TimeoutException:
                logger.warning(f"Gemini [{model_name}] timeout on attempt {attempt}/{max_retries}.")
                if attempt < max_retries:
                    time.sleep(0.3)
                    continue
                break

            except _CONNECTION_ERRORS as e:
                # Stale TCP connection (Windows WSARECV / connection aborted)
                logger.warning(
                    f"Gemini [{model_name}] connection error on attempt {attempt}/{max_retries}: "
                    f"{type(e).__name__}: {str(e)[:80]}. Recreating HTTP client..."
                )
                _reset_client()  # Force fresh TCP connection
                if attempt < max_retries:
                    time.sleep(0.2 * attempt)
                    continue
                break

            except Exception as e:
                logger.error(f"Gemini [{model_name}] unexpected exception: {type(e).__name__}: {e}")
                break

    # All models exhausted — synthesise from context
    logger.info("All Gemini models failed — falling back to context synthesis.")
    return _synthesize_from_context(context_snippets)


def _synthesize_from_context(context_snippets: List[str]) -> str:
    """
    Produces a clean, deduplicated, well-formatted answer directly from retrieved context chunks
    when the LLM API is unavailable. Bulletproof against exceptions.
    """
    if not context_snippets:
        return (
            "Hello! 😊 I'm CampusAI, your official college assistant. I am here to help you with all campus queries including **admissions, eligibility, fee structures, hostel curfew rules, examination schedules, placements, and library policies**.\n\n"
            "Please ask your specific question (for example: *'What is the admission process?'* or *'What are the hostel curfew rules?'*) and I will gladly provide full details!"
        )

    try:
        intro = "Hello! 😊 Based on official campus documents, here is the relevant information for you:\n\n"
        seen_lines = set()
        unique_bullets = []

        for snippet in context_snippets:
            cleaned = str(snippet).strip()
            if not cleaned:
                continue
            lines = [l.strip() for l in cleaned.split('\n') if l.strip()]
            for line in lines:
                if len(line) < 4:
                    continue
                norm = re.sub(r'^[0-9.#•*\-\s]+', '', line).strip().lower()
                if norm not in seen_lines:
                    seen_lines.add(norm)
                    formatted = re.sub(r'^[0-9.#•*\-\s]+', '', line).strip()
                    if formatted:
                        unique_bullets.append(f"• {formatted}")

        if unique_bullets:
            return (
                intro
                + "\n".join(unique_bullets[:25])
                + "\n\n*If you need further details or have additional questions, feel free to ask anytime!*"
            )
    except Exception as e:
        logger.error(f"Error during context synthesis: {e}")

    bullets = [f"• {s.strip()[:300]}" for s in context_snippets if s.strip()]
    if bullets:
        return "Hello! 😊 Based on official campus documents:\n\n" + "\n\n".join(bullets)
    return "Hello! 😊 I'm here to help! Please ask me about admissions, fees, hostel rules, or exams!"
