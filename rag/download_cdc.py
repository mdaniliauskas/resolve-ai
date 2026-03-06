"""
CDC Downloader — Resolve Aí

Downloads the full text of the Código de Defesa do Consumidor (Law 8.078/1990)
from planalto.gov.br and saves a clean plaintext version.

Usage:
    uv run python -m rag.download_cdc
"""

import logging
import re
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

CDC_URL = "https://www.planalto.gov.br/ccivil_03/leis/l8078compilado.htm"
OUTPUT_DIR = Path("data/cdc")
RAW_FILE = OUTPUT_DIR / "cdc_raw.html"
CLEAN_FILE = OUTPUT_DIR / "cdc_clean.txt"


def download_cdc() -> str:
    """Download the CDC HTML from planalto.gov.br.

    Uses a browser-like User-Agent because planalto blocks bot requests.
    The site serves pages as ISO-8859-1 (Latin-1), so we decode manually.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "pt-BR,pt;q=0.9",
    }

    logger.info("Downloading CDC from %s", CDC_URL)
    response = httpx.get(CDC_URL, headers=headers, follow_redirects=True, timeout=30)
    response.raise_for_status()

    # Planalto uses ISO-8859-1 — decode from raw bytes to get proper Portuguese chars
    html = response.content.decode("iso-8859-1")

    # Save raw HTML for reference
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_FILE.write_text(html, encoding="utf-8")
    logger.info("Raw HTML saved to %s (%d bytes)", RAW_FILE, len(html))

    return html


def clean_html(html: str) -> str:
    """Extract the CDC body text from HTML and clean it.

    Removes HTML tags, normalizes whitespace, and preserves the article structure.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style elements
    for tag in soup(["script", "style", "head"]):
        tag.decompose()

    # Get text content
    text = soup.get_text(separator="\n")

    # Normalize line breaks — collapse 3+ empty lines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Normalize whitespace within lines (but preserve line breaks)
    lines = []
    for line in text.split("\n"):
        cleaned = " ".join(line.split())  # collapse multiple spaces/tabs
        lines.append(cleaned)
    text = "\n".join(lines)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def save_clean_text(text: str) -> Path:
    """Save the cleaned CDC text to disk."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CLEAN_FILE.write_text(text, encoding="utf-8")
    logger.info("Clean text saved to %s (%d chars)", CLEAN_FILE, len(text))
    return CLEAN_FILE


def main() -> None:
    """Download, clean, and save the CDC text. Idempotent — safe to re-run."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if CLEAN_FILE.exists():
        logger.info("CDC already downloaded at %s — delete it to re-download", CLEAN_FILE)
        return

    html = download_cdc()
    clean_text = clean_html(html)
    save_clean_text(clean_text)

    # Quick stats
    article_count = len(re.findall(r"Art\.\s*\d+", clean_text))
    logger.info("Done! Found ~%d article references in the CDC text", article_count)


if __name__ == "__main__":
    main()
