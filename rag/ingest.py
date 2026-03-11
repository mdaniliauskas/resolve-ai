"""
CDC Ingestion Pipeline — Resolve Aí

Loads the cleaned CDC text, splits it into chunks with hierarchical metadata,
and indexes everything into ChromaDB for similarity search.

Usage:
    uv run python -m rag.ingest
"""

import logging
import re
from dataclasses import dataclass
from pathlib import Path

import chromadb

from config import settings
from rag.embedder import gemini_embedder

logger = logging.getLogger(__name__)

CDC_FILE = Path("data/cdc/cdc_clean.txt")
STJ_FILE = Path("data/jurisprudencia/stj_summaries.txt")
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
class GenericChunk:
    """A generic chunk of text for indexing."""

    text: str
    source_type: str = "cdc"
    reference: str = ""  # Article or Súmula number
    titulo: str = ""
    capitulo: str = ""
    secao: str = ""
    chunk_index: int = 0

    @property
    def metadata(self) -> dict:
        """Flat metadata dict for ChromaDB storage."""
        return {
            "source_type": self.source_type,
            "reference": self.reference,
            "titulo": self.titulo,
            "capitulo": self.capitulo,
            "secao": self.secao,
            "chunk_index": self.chunk_index,
            "source": f"Resolve Aí - {self.source_type.upper()}",
        }


# --- Pipeline Steps -----------------------------------------------------------


def load_text(file_path: Path) -> str:
    """Load text from a file."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found at {file_path}")
    return file_path.read_text(encoding="utf-8")


def chunk_cdc_text(text: str) -> list[GenericChunk]:
    """Split CDC text into overlapping chunks with hierarchical metadata."""
    section = CDCSection()
    chunks: list[GenericChunk] = []
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    current_text = ""
    current_articles: list[str] = []
    chunk_index = 0

    for paragraph in paragraphs:
        _update_section(section, paragraph)
        found_articles = re.findall(r"Art\.\s*(\d+)", paragraph)
        for art in found_articles:
            art_ref = f"Art. {art}"
            if art_ref not in current_articles:
                current_articles.append(art_ref)

        candidate = f"{current_text}\n\n{paragraph}".strip() if current_text else paragraph

        if len(candidate) > CHUNK_SIZE and current_text:
            chunks.append(GenericChunk(
                text=current_text,
                source_type="cdc",
                reference=", ".join(current_articles),
                titulo=section.titulo,
                capitulo=section.capitulo,
                secao=section.secao,
                chunk_index=chunk_index,
            ))
            chunk_index += 1
            overlap_text = current_text[-CHUNK_OVERLAP:] if len(current_text) > CHUNK_OVERLAP else ""
            current_text = f"{overlap_text}\n\n{paragraph}".strip()
            current_articles = [f"Art. {a}" for a in re.findall(r"Art\.\s*(\d+)", current_text)]
        else:
            current_text = candidate

    if current_text.strip():
        chunks.append(GenericChunk(
            text=current_text,
            source_type="cdc",
            reference=", ".join(current_articles),
            titulo=section.titulo,
            capitulo=section.capitulo,
            secao=section.secao,
            chunk_index=chunk_index,
        ))
    return chunks


def chunk_stj_text(text: str) -> list[GenericChunk]:
    """Split STJ jurisprudence into chunks. Each entry (Súmula/Tema) is a chunk."""
    chunks: list[GenericChunk] = []
    # Split by lines, filtering empty ones
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    chunk_index = 1000  # Offset index for jurisprudence
    for line in lines:
        if any(line.startswith(prefix) for prefix in ["Súmula", "Tema", "REsp"]):
            # Extract the reference (e.g., "Súmula 130")
            match = re.match(r"(Súmula\s+\d+|Tema\s+\d+|REsp\s+[\d\.]+)", line)
            ref = match.group(1) if match else "STJ"
            
            chunks.append(GenericChunk(
                text=line,
                source_type="stj",
                reference=ref,
                chunk_index=chunk_index
            ))
            chunk_index += 1
            
    return chunks


def index_chunks(chunks: list[GenericChunk]) -> chromadb.Collection:
    """Index chunks into ChromaDB."""
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)

    try:
        client.delete_collection(COLLECTION_NAME)
        logger.info("Deleted existing collection '%s'", COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=gemini_embedder,
        metadata={"hnsw:space": "cosine"},
    )

    # Add in batches to avoid large request issues
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        collection.add(
            ids=[f"chunk-{c.source_type}-{c.chunk_index}" for c in batch],
            documents=[c.text for c in batch],
            metadatas=[c.metadata for c in batch],
        )

    logger.info("Indexed %d chunks into collection '%s'", len(chunks), COLLECTION_NAME)
    return collection


def _update_section(section: CDCSection, paragraph: str) -> None:
    upper = paragraph.upper().strip()
    if upper.startswith("TÍTULO") or upper.startswith("TITULO"):
        section.titulo, section.capitulo, section.secao = paragraph.strip(), "", ""
    elif upper.startswith("CAPÍTULO") or upper.startswith("CAPITULO"):
        section.capitulo, section.secao = paragraph.strip(), ""
    elif upper.startswith("SEÇÃO") or upper.startswith("SECAO"):
        section.secao = paragraph.strip()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    all_chunks = []
    
    # Ingest CDC
    logger.info("Ingesting CDC...")
    cdc_text = load_text(CDC_FILE)
    all_chunks.extend(chunk_cdc_text(cdc_text))
    
    # Ingest STJ Jurisprudence
    logger.info("Ingesting STJ Jurisprudence...")
    stj_text = load_text(STJ_FILE)
    all_chunks.extend(chunk_stj_text(stj_text))

    collection = index_chunks(all_chunks)

    # Verification
    logger.info("Verifying retrieval with mixed sources...")
    q = "estacionamento de shopping"
    results = collection.query(query_texts=[q], n_results=3)
    for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
        logger.info("[%d] %s | %s: %s...", i+1, meta["source_type"], meta["reference"], doc[:100])


if __name__ == "__main__":
    main()
