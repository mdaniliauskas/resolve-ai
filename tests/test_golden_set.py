"""
Tests for golden test set evaluation — Resolve Aí

Validates retrieval quality using the golden test set from MVP_SPEC.md.
These are integration tests that require an indexed ChromaDB.
"""

from evaluation.golden_test_set import evaluate_retrieval


def test_retrieval_precision_meets_target():
    """Overall precision should meet the Sprint 1 target (70%)."""
    result = evaluate_retrieval()
    assert result["precision"] >= result["target_precision"], (
        f"Precision {result['precision']:.0%} is below "
        f"target {result['target_precision']:.0%}"
    )


def test_all_golden_cases_return_results():
    """Every golden case should return at least 1 chunk (not empty)."""
    result = evaluate_retrieval()
    for case in result["cases"]:
        assert case["chunks_returned"] > 0, (
            f"Case {case['id']} ({case['description']}) returned 0 chunks"
        )
