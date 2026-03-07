"""
Tests for LangGraph Workflow — Resolve Aí

Integration tests for the full agent pipeline with mocked LLM calls.
"""

from unittest.mock import patch

from agents.workflow import run_chat

LLM_CLIENT = "agents.llm_client.generate"

# Ordered mock responses for the pipeline: orchestrator → legal → strategy → response
MOCK_LEGAL_JSON = (
    '{"is_cdc_case": true, "articles": [{"number": "Art. 18", "title": "Vício",'
    ' "relevance": "defeito"}], "rights": ["Reparo"], "severity": "medium",'
    ' "confidence": 0.8, "reasoning": "ok"}'
)
MOCK_STRATEGY_JSON = (
    '{"channels": [{"step": 1, "name": "SAC", "description": "Ligue", "link": null}],'
    ' "estimated_resolution_time": "7 dias", "tips": ["Guarde notas"]}'
)
CDC_CASE_RESPONSES = [
    "consumer_complaint",  # orchestrator: classify intent
    MOCK_LEGAL_JSON,  # legal analysis
    MOCK_STRATEGY_JSON,  # strategy
    "Entendemos sua situação. Você tem direitos!",  # response formatting
]


@patch(LLM_CLIENT)
def test_cdc_case_runs_full_pipeline(mock_llm):
    """A consumer complaint should go through all 4 agents."""
    mock_llm.side_effect = CDC_CASE_RESPONSES
    result = run_chat("Meu celular quebrou com 10 dias")

    assert result["response"] == "Entendemos sua situação. Você tem direitos!"
    assert result["analysis"] is not None
    assert result["analysis"].is_cdc_case is True
    assert result["strategy"] is not None
    assert len(result["strategy"].channels) == 1
    assert mock_llm.call_count == 4  # All 4 agents called


@patch(LLM_CLIENT)
def test_greeting_skips_analysis(mock_llm):
    """A greeting should only call orchestrator and return static response."""
    mock_llm.return_value = "greeting"
    result = run_chat("Olá!")

    assert "Resolve Aí" in result["response"]
    assert result["analysis"] is None
    assert result["strategy"] is None
    mock_llm.assert_called_once()  # Only orchestrator


@patch(LLM_CLIENT)
def test_out_of_scope_skips_analysis(mock_llm):
    """An out-of-scope message should only call orchestrator and return info."""
    mock_llm.return_value = "out_of_scope"
    result = run_chat("Qual a previsão do tempo?")

    assert "fora do escopo" in result["response"].lower()
    assert result["analysis"] is None
    mock_llm.assert_called_once()  # Only orchestrator
