"""
CDC Ingestion Pipeline — Resolve Aí

Loads the cleaned CDC text, splits it into chunks with hierarchical metadata,
and indexes everything into ChromaDB for similarity search.

Usage:
    uv run python -m rag.ingest
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

import chromadb

from config import settings
from rag.embedder import gemini_embedder

logger = logging.getLogger(__name__)

CDC_FILE = Path("data/cdc/cdc_clean.txt")
COLLECTION_NAME = "cdc_articles"

# Chunking parameters (from TECH_DECISIONS.md ADR-004)
CHUNK_SIZE = 3200  # ~800 tokens (1 token ≈ 4 chars for Portuguese)
CHUNK_OVERLAP = 800  # ~200 tokens


# --- Data Structures ----------------------------------------------------------


@dataclass
class CDCSection:
    """A structural section of the CDC with its hierarchical position."""

    titulo: str = ""
    capitulo: str = ""
    secao: str = ""


@dataclass
class CDCChunk:
    """A chunk of CDC text ready for indexing, with metadata."""

    text: str
    titulo: str = ""
    capitulo: str = ""
    secao: str = ""
    articles: list[str] = field(default_factory=list)
    chunk_index: int = 0

    @property
    def metadata(self) -> dict:
        """Flat metadata dict for ChromaDB storage."""
        return {
            "titulo": self.titulo,
            "capitulo": self.capitulo,
            "secao": self.secao,
            "articles": ", ".join(self.articles),
            "chunk_index": self.chunk_index,
            "source": "CDC - Lei 8.078/1990",
        }


# --- Pipeline Steps -----------------------------------------------------------


def load_cdc_text() -> str:
    """Load the cleaned CDC text from disk."""
    if not CDC_FILE.exists():
        raise FileNotFoundError(
            f"CDC file not found at {CDC_FILE}. "
            "Run 'uv run python -m rag.download_cdc' first."
        )
    text = CDC_FILE.read_text(encoding="utf-8")
    logger.info("Loaded CDC text: %d chars, %d lines", len(text), text.count("\n"))
    return text


def chunk_cdc_text(text: str) -> list[CDCChunk]:
    """Split CDC text into overlapping chunks with hierarchical metadata.

    Tracks the current TÍTULO, CAPÍTULO, and SEÇÃO as context flows through
    the text. Each chunk knows which articles it contains.
    """
    section = CDCSection()
    chunks: list[CDCChunk] = []

    # Split into paragraphs (natural boundaries in the CDC)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    current_text = ""
    current_articles: list[str] = []
    chunk_index = 0

    for paragraph in paragraphs:
        # Track structural hierarchy
        _update_section(section, paragraph)

        # Track article references in this paragraph
        found_articles = re.findall(r"Art\.\s*(\d+)", paragraph)
        for art in found_articles:
            art_ref = f"Art. {art}"
            if art_ref not in current_articles:
                current_articles.append(art_ref)

        # Would adding this paragraph exceed the chunk size?
        candidate = f"{current_text}\n\n{paragraph}".strip() if current_text else paragraph

        if len(candidate) > CHUNK_SIZE and current_text:
            # Save current chunk
            chunks.append(CDCChunk(
                text=current_text,
                titulo=section.titulo,
                capitulo=section.capitulo,
                secao=section.secao,
                articles=current_articles.copy(),
                chunk_index=chunk_index,
            ))
            chunk_index += 1

            # Start new chunk with overlap — keep the tail of the previous chunk
            if len(current_text) > CHUNK_OVERLAP:
                overlap_text = current_text[-CHUNK_OVERLAP:]
            else:
                overlap_text = ""
            current_text = f"{overlap_text}\n\n{paragraph}".strip()

            # Keep only articles that appear in the overlap + new paragraph
            current_articles = re.findall(r"Art\.\s*(\d+)", current_text)
            current_articles = [f"Art. {a}" for a in current_articles]
        else:
            current_text = candidate

    # Don't forget the last chunk
    if current_text.strip():
        chunks.append(CDCChunk(
            text=current_text,
            titulo=section.titulo,
            capitulo=section.capitulo,
            secao=section.secao,
            articles=current_articles,
            chunk_index=chunk_index,
        ))

    logger.info("Created %d chunks (avg %d chars)", len(chunks), _avg_len(chunks))
    return chunks


def index_chunks(chunks: list[CDCChunk]) -> chromadb.Collection:
    """Index chunks into ChromaDB. Idempotent — deletes and recreates the collection."""
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)

    # Delete existing collection if present (idempotent re-indexing)
    try:
        client.delete_collection(COLLECTION_NAME)
        logger.info("Deleted existing collection '%s'", COLLECTION_NAME)
    except Exception:
        pass  # Collection didn't exist

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=gemini_embedder,
        metadata={
            "description": "CDC - Código de Defesa do Consumidor (Lei 8.078/1990)",
            "hnsw:space": "cosine",
        },
    )

    # ChromaDB will use gemini_embedder
    collection.add(
        ids=[f"cdc-chunk-{c.chunk_index}" for c in chunks],
        documents=[c.text for c in chunks],
        metadatas=[c.metadata for c in chunks],
    )

    logger.info("Indexed %d chunks into collection '%s'", len(chunks), COLLECTION_NAME)
    return collection


# --- Helpers ------------------------------------------------------------------


def _update_section(section: CDCSection, paragraph: str) -> None:
    """Update the current section tracker based on structural markers in the text."""
    upper = paragraph.upper().strip()

    if upper.startswith("TÍTULO") or upper.startswith("TITULO"):
        section.titulo = paragraph.strip()
        section.capitulo = ""
        section.secao = ""
    elif upper.startswith("CAPÍTULO") or upper.startswith("CAPITULO"):
        section.capitulo = paragraph.strip()
        section.secao = ""
    elif upper.startswith("SEÇÃO") or upper.startswith("SECAO") or upper.startswith("SEÇÃO"):
        section.secao = paragraph.strip()


def _avg_len(chunks: list[CDCChunk]) -> int:
    """Average character length of chunks."""
    if not chunks:
        return 0
    return sum(len(c.text) for c in chunks) // len(chunks)


# --- Main ---------------------------------------------------------------------


def main() -> None:
    """Run the full CDC ingestion pipeline: load → chunk → index."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    text = load_cdc_text()
    chunks = chunk_cdc_text(text)
    collection = index_chunks(chunks)

    # Quick verification
    sample = collection.query(query_texts=["produto com defeito na garantia"], n_results=3)
    logger.info("Verification query — top 3 results:")
    docs_and_metas = zip(sample["documents"][0], sample["metadatas"][0], strict=False)
    for i, (doc, meta) in enumerate(docs_and_metas):
        logger.info(
            "  [%d] articles=%s | %s...",
            i + 1,
            meta.get("articles", ""),
            doc[:100],
        )


if __name__ == "__main__":
    main()
