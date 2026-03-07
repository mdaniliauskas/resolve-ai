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

logger = logging.getLogger(__name__)

COLLECTION_NAME = "cdc_articles"

# Retrieval parameters (from MVP_SPEC.md)
DEFAULT_TOP_K = 7
# NOTE: Threshold is calibrated for L2 distance with all-MiniLM-L6-v2 (dev).
# Portuguese legal text scores ~0.45-0.55 similarity with this model.
# Re-calibrate when switching to Gemini text-embedding-004 (production).
SCORE_THRESHOLD = 0.3


class RetrievedChunk(BaseModel):
    """A chunk retrieved from the CDC vector store with its similarity score."""

    text: str
    score: float
    articles: str = ""
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
        collection = client.get_collection(COLLECTION_NAME)
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
        # ChromaDB default distance is L2; convert to similarity score (0-1 range)
        # For cosine distance: similarity = 1 - distance/2
        # For L2 distance: we use a simple inverse scaling
        score = max(0.0, 1.0 - distance / 2.0)

        if score < SCORE_THRESHOLD:
            logger.debug("Skipping chunk (score %.3f < threshold %.2f)", score, SCORE_THRESHOLD)
            continue

        chunks.append(RetrievedChunk(
            text=doc,
            score=round(score, 4),
            articles=meta.get("articles", ""),
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
