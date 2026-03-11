"""
Golden Test Set — Resolve Aí

The 10 core scenarios from MVP_SPEC.md, used to measure retrieval quality.
Each case has a consumer query and the expected CDC article(s) that should
appear in the top-K results.

Usage:
    uv run python -m evaluation.golden_test_set
"""

import logging
from dataclasses import dataclass

from rag.retrieval import retrieve

logger = logging.getLogger(__name__)


@dataclass
class GoldenCase:
    """A test case with a consumer query and expected CDC article."""

    id: int
    query: str
    expected_article: str
    severity: str
    description: str


# From MVP_SPEC.md — Section 6
GOLDEN_CASES: list[GoldenCase] = [
    GoldenCase(
        id=1,
        query="Comprei um celular e a tela quebrou com 10 dias de uso",
        expected_article="Art. 18",
        severity="medium",
        description="Produto com defeito dentro da garantia",
    ),
    GoldenCase(
        id=2,
        query="Cobrança indevida no meu cartão de crédito, não reconheço essa compra",
        expected_article="Art. 42",
        severity="medium",
        description="Cobrança indevida no cartão de crédito",
    ),
    GoldenCase(
        id=3,
        query="O produto que recebi é completamente diferente do que anunciaram no site",
        expected_article="Art. 37",
        severity="medium",
        description="Propaganda enganosa",
    ),
    GoldenCase(
        id=4,
        query="Paguei por um serviço de internet que nunca foi instalado",
        expected_article="Art. 20",
        severity="high",
        description="Serviço não prestado após pagamento",
    ),
    GoldenCase(
        id=5,
        query="A empresa se recusa a cancelar meu contrato de academia",
        expected_article="Art. 49",
        severity="medium",
        description="Negativa de cancelamento de contrato",
    ),
    GoldenCase(
        id=6,
        query="A loja anunciou uma promoção e na hora de pagar cobrou preço diferente",
        expected_article="Art. 35",
        severity="low",
        description="Descumprimento de oferta/promoção",
    ),
    GoldenCase(
        id=7,
        query="Meu filho tomou um remédio com defeito e passou mal, precisou ir ao hospital",
        expected_article="Art. 12",
        severity="high",
        description="Produto perigoso causou dano à saúde",
    ),
    GoldenCase(
        id=8,
        query="O contrato tem uma cláusula dizendo que a empresa não se responsabiliza por nada",
        expected_article="Art. 51",
        severity="medium",
        description="Cláusula abusiva em contrato",
    ),
    GoldenCase(
        id=9,
        query="Comprei online há 3 dias e a loja se recusa a aceitar a devolução",
        expected_article="Art. 49",
        severity="low",
        description="Recusa de troca em compra online (7 dias)",
    ),
    GoldenCase(
        id=10,
        query="Meu nome foi colocado no SPC indevidamente por uma dívida que já paguei",
        expected_article="Art. 43",
        severity="high",
        description="Negativação indevida (SPC/Serasa)",
    ),
]


def evaluate_retrieval(top_k: int = 5) -> dict:
    """Run all golden cases through the retrieval pipeline and measure precision.

    Returns a dict with per-case results and overall precision score.
    """
    results = []

    for case in GOLDEN_CASES:
        chunks = retrieve(case.query, top_k=top_k)

        # Check if the expected article appears in any of the retrieved chunks
        all_articles_text = " ".join(c.reference for c in chunks)
        hit = case.expected_article in all_articles_text

        # Find the best matching chunk's position (1-indexed)
        hit_position = None
        for i, chunk in enumerate(chunks):
            if case.expected_article in chunk.reference:
                hit_position = i + 1
                break

        results.append({
            "id": case.id,
            "description": case.description,
            "expected": case.expected_article,
            "hit": hit,
            "hit_position": hit_position,
            "chunks_returned": len(chunks),
            "top_score": chunks[0].score if chunks else 0.0,
        })

    # Calculate metrics
    hits = sum(1 for r in results if r["hit"])
    precision = hits / len(results) if results else 0.0

    return {
        "cases": results,
        "total": len(results),
        "hits": hits,
        "precision": precision,
        "target_precision": 0.70,  # Sprint 1 target: 70%
    }


def print_report(evaluation: dict) -> None:
    """Print a human-readable evaluation report."""
    print("\n" + "=" * 72)
    print("  GOLDEN TEST SET -- Retrieval Quality Report")
    print("=" * 72)

    for r in evaluation["cases"]:
        status = "[HIT] " if r["hit"] else "[MISS]"
        pos = f"(position {r['hit_position']})" if r["hit_position"] else ""
        print(
            f"  [{r['id']:2d}] {status} {pos:15s} "
            f"| {r['expected']:8s} | {r['description']}"
        )

    print("-" * 72)
    precision_pct = evaluation["precision"] * 100
    target_pct = evaluation["target_precision"] * 100
    passed = evaluation["precision"] >= evaluation["target_precision"]
    status = "PASS" if passed else "FAIL"

    print(f"  Precision: {evaluation['hits']}/{evaluation['total']} = {precision_pct:.0f}%")
    print(f"  Target:    {target_pct:.0f}%")
    print(f"  Status:    {status}")
    print("=" * 72 + "\n")


def main() -> None:
    """Run the golden test set evaluation and print results."""
    logging.basicConfig(level=logging.WARNING)  # Suppress retrieval logs
    evaluation = evaluate_retrieval()
    print_report(evaluation)


if __name__ == "__main__":
    main()
