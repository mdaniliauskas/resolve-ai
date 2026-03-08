"""
Gemini Embedding Function — Resolve Aí

Provides a custom embedding function for ChromaDB that uses
Google's text-embedding-004 via the google-genai SDK.
"""

from typing import cast
from chromadb import Documents, EmbeddingFunction, Embeddings
from google import genai
from config import settings

class GeminiEmbeddingFunction(EmbeddingFunction[Documents]):
    """ChromaDB embedding function using Google's Gemini models."""

    def __init__(self, model_name: str = "gemini-embedding-001"):
        self.client = genai.Client(api_key=settings.google_api_key)
        self.model_name = model_name

    def __call__(self, input: Documents) -> Embeddings:
        """Embeds a list of texts using the Gemini API."""
        # Process in batches if necessary, but GenAI SDK usually handles arrays
        response = self.client.models.embed_content(
            model=self.model_name,
            contents=list(input),
            config={"task_type": "RETRIEVAL_DOCUMENT"}
        )
        # response.embeddings is a list of objects with a 'values' attribute (list of floats)
        return cast(Embeddings, [e.values for e in response.embeddings])

gemini_embedder = GeminiEmbeddingFunction()
