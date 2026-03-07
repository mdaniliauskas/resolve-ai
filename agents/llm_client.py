"""
LLM Client — Resolve Aí

Thin wrapper around the Google GenAI SDK (google-genai).
All agent modules call this instead of the SDK directly.

Usage:
    from agents.llm_client import generate
    response = generate("Classifique esta mensagem: ...")
"""

import logging
import time

from google import genai

from config import settings

logger = logging.getLogger(__name__)

# Create client once at module level
_client = genai.Client(api_key=settings.google_api_key)


def generate(prompt: str, *, temperature: float = 0.2) -> str:
    """Send a prompt to Gemini and return the text response.

    Uses low temperature by default for more deterministic outputs,
    which is important for classification and structured JSON responses.
    """
    start = time.perf_counter()
    response = _client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config={"temperature": temperature},
    )
    elapsed_ms = (time.perf_counter() - start) * 1000

    text = response.text.strip()

    logger.info(
        "LLM call completed in %.0fms (model=%s, prompt_len=%d, response_len=%d)",
        elapsed_ms,
        settings.gemini_model,
        len(prompt),
        len(text),
    )
    return text
