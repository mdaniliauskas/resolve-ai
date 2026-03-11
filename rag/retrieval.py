"""
CDC Retrieval — Resolve Aí

Similarity search against the indexed CDC chunks in ChromaDB.

Usage:
    from rag.retrieval import retrieve
    results = retrieve("produto com defeito na garantia")
"""

import logging

import chromadb
from pydantic import BaseModel

from config import settings
from rag.embedder import gemini_embedder

logger = logging.getLogger(__name__)

COLLECTION_NAME = "cdc_articles"

# Retrieval parameters (from MVP_SPEC.md)
DEFAULT_TOP_K = 7
# NOTE: Threshold is calibrated for cosine distance with Gemini's text-embedding-004.
# High-dimensional embeddings usually present high cosine similarities (0.6 ~ 0.8+).
SCORE_THRESHOLD = 0.6


class RetrievedChunk(BaseModel):
    """A chunk retrieved from the vector store with its similarity score."""

    text: str
    score: float
    source_type: str = "cdc"
    reference: str = ""  # Article number or Súmula number
    titulo: str = ""
    capitulo: str = ""
    secao: str = ""
    chunk_index: int = 0


def retrieve(query: str, top_k: int = DEFAULT_TOP_K) -> list[RetrievedChunk]:
    """Search the CDC vector store for chunks relevant to the query.

    Returns chunks sorted by relevance, filtered by SCORE_THRESHOLD.
    ChromaDB returns distances (lower = more similar), so we convert to
    similarity scores (higher = more similar) for consistency.
    """
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)

    try:
        collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=gemini_embedder,
        )
    except ValueError:
        logger.error(
            "Collection '%s' not found. Run 'uv run python -m rag.ingest' first.",
            COLLECTION_NAME,
        )
        return []

    results = collection.query(query_texts=[query], n_results=top_k)

    chunks = []
    for doc, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
        strict=False,
    ):
        # ChromaDB configured for 'cosine' returns cosine distance.
        # similarity = 1 - distance
        score = max(0.0, 1.0 - distance)

        if score < SCORE_THRESHOLD:
            logger.debug("Skipping chunk (score %.3f < threshold %.2f)", score, SCORE_THRESHOLD)
            continue

        chunks.append(RetrievedChunk(
            text=doc,
            score=round(score, 4),
            source_type=meta.get("source_type", "cdc"),
            reference=meta.get("reference") or meta.get("articles", ""),
            titulo=meta.get("titulo", ""),
            capitulo=meta.get("capitulo", ""),
            secao=meta.get("secao", ""),
            chunk_index=meta.get("chunk_index", 0),
        ))

    logger.info(
        "Query '%s...' → %d results (of %d before threshold)",
        query[:50],
        len(chunks),
        len(results["documents"][0]),
    )
    return chunks
