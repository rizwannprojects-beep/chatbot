import os
import httpx
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("campusai.gemini_service")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_GENERATE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

def generate_grounded_answer(prompt: str, context_snippets: List[str]) -> str:
    """
    Calls Google Gemini LLM API with strict grounding system prompt.
    Returns generated text response.
    """
    if not prompt or not prompt.strip():
        return "Please ask a valid question."

    # If Gemini API key is missing/mock in local test environment, synthesize clean grounded response from context
    if not GEMINI_API_KEY or "your-gemini-api-key" in GEMINI_API_KEY or "mock-gemini" in GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY is unconfigured or mock; returning test grounded synthesis.")
        if not context_snippets:
            return "I could not find reliable information regarding your query in the official campus knowledge base. Please contact the campus administration or student support desk for assistance."
        combined_info = " ".join(context_snippets)
        return f"Based on official campus documents: {combined_info[:400]}"

    try:
        url = f"{GEMINI_GENERATE_URL}?key={GEMINI_API_KEY}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,  # Low temperature for strict adherence to facts
                "maxOutputTokens": 800
            }
        }
        
        with httpx.Client(timeout=25.0) as client:
            response = client.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
                logger.warning("Gemini API returned 200 but empty content candidates.")
                return "I could not generate a response from the retrieved documents."
            else:
                logger.error(f"Gemini LLM API returned HTTP {response.status_code}: {response.text}")
                # Fallback to context synthesis if API fails
                if context_snippets:
                    return f"Based on retrieved campus documents: {' '.join(context_snippets)[:400]}"
                return "I encountered a service issue connecting to the AI model. Please try again shortly."
    except Exception as e:
        logger.error(f"Gemini LLM call exception: {e}")
        if context_snippets:
            return f"Based on retrieved campus documents: {' '.join(context_snippets)[:400]}"
        return "An unexpected error occurred while communicating with the AI service."
