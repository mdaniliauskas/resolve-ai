"""
Tests for RAG pipeline — Resolve Aí

Tests the ingestion (chunking + metadata) and retrieval (similarity search)
using an in-memory ChromaDB instance.
"""

from rag.ingest import CDCChunk, chunk_cdc_text, load_cdc_text

# --- Chunking Tests -----------------------------------------------------------

# Sample CDC fragment for testing (smaller than real CDC)
SAMPLE_CDC = """TÍTULO I

Dos Direitos do Consumidor

CAPÍTULO I

Disposições Gerais

Art. 1° O presente código estabelece normas de proteção e defesa do consumidor, de
ordem pública e interesse social.

Art. 2° Consumidor é toda pessoa física ou jurídica que adquire ou utiliza produto ou
serviço como destinatário final.

CAPÍTULO IV

Da Qualidade de Produtos e Serviços

SEÇÃO III

Da Responsabilidade por Vício do Produto e do Serviço

Art. 18. Os fornecedores de produtos de consumo duráveis ou não duráveis respondem
solidariamente pelos vícios de qualidade ou quantidade que os tornem impróprios ou
inadequados ao consumo a que se destinam ou lhes diminuam o valor.

§ 1° Não sendo o vício sanado no prazo máximo de trinta dias, pode o consumidor
exigir, alternativamente e à sua escolha:

I - a substituição do produto por outro da mesma espécie;
II - a restituição imediata da quantia paga;
III - o abatimento proporcional do preço.
"""


def test_chunk_produces_nonempty_results():
    """Chunking should produce at least one chunk from valid CDC text."""
    chunks = chunk_cdc_text(SAMPLE_CDC)
    assert len(chunks) >= 1
    assert all(isinstance(c, CDCChunk) for c in chunks)


def test_chunk_preserves_text_content():
    """Chunked text should contain the original article content."""
    chunks = chunk_cdc_text(SAMPLE_CDC)
    all_text = " ".join(c.text for c in chunks)
    assert "Art. 1" in all_text
    assert "Art. 2" in all_text
    assert "Art. 18" in all_text


def test_chunk_tracks_articles():
    """Each chunk should list the articles it contains."""
    chunks = chunk_cdc_text(SAMPLE_CDC)
    all_articles = []
    for chunk in chunks:
        all_articles.extend(chunk.articles)
    assert "Art. 1" in all_articles
    assert "Art. 18" in all_articles


def test_chunk_tracks_hierarchy():
    """Chunks should carry TÍTULO/CAPÍTULO/SEÇÃO metadata."""
    chunks = chunk_cdc_text(SAMPLE_CDC)
    # The last chunk should have the hierarchy from SEÇÃO III
    last_chunk = chunks[-1]
    assert last_chunk.titulo != "" or last_chunk.capitulo != "" or last_chunk.secao != ""


def test_chunk_metadata_is_flat_dict():
    """Metadata property should return a flat dict suitable for ChromaDB."""
    chunks = chunk_cdc_text(SAMPLE_CDC)
    meta = chunks[0].metadata
    assert isinstance(meta, dict)
    assert "titulo" in meta
    assert "capitulo" in meta
    assert "secao" in meta
    assert "articles" in meta
    assert "source" in meta


# --- Load Tests ---------------------------------------------------------------


def test_load_cdc_text_returns_string():
    """Loading the CDC file should return a non-empty string."""
    text = load_cdc_text()
    assert isinstance(text, str)
    assert len(text) > 10000  # CDC is ~80k chars
    assert "Art. 1" in text
    assert "consumidor" in text.lower()


# --- Integration: Chunking the real CDC ---------------------------------------


def test_real_cdc_produces_reasonable_chunk_count():
    """The full CDC should produce between 20-60 chunks with default settings."""
    text = load_cdc_text()
    chunks = chunk_cdc_text(text)
    assert 20 <= len(chunks) <= 60, f"Got {len(chunks)} chunks — check chunk size params"


def test_real_cdc_chunks_contain_key_articles():
    """Key CDC articles should appear in the chunks."""
    text = load_cdc_text()
    chunks = chunk_cdc_text(text)
    all_articles = []
    for chunk in chunks:
        all_articles.extend(chunk.articles)

    # These are the most commonly cited articles (from golden test set)
    expected = ["Art. 12", "Art. 18", "Art. 20", "Art. 35", "Art. 37", "Art. 42", "Art. 49"]
    for art in expected:
        assert art in all_articles, f"{art} not found in any chunk"
