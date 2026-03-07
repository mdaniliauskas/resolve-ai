"""
Tests for Agent modules — Resolve Aí

All tests mock the LLM client to avoid real API calls.
Each agent is tested in isolation with controlled responses.
"""

from unittest.mock import patch

from agents.legal_analysis import LegalAnalysisResult, analyze_case
from agents.orchestrator import classify_intent
from agents.response import format_greeting, format_out_of_scope, format_response
from agents.strategy import StrategyResult, plan_strategy
from rag.retrieval import RetrievedChunk

LLM_CLIENT = "agents.llm_client.generate"


# --- Orchestrator Tests -------------------------------------------------------


@patch(LLM_CLIENT)
def test_orchestrator_classifies_consumer_complaint(mock_llm):
    """A product defect message should be classified as consumer_complaint."""
    mock_llm.return_value = "consumer_complaint"
    result = classify_intent("Comprei um celular e a tela quebrou")
    assert result == "consumer_complaint"


@patch(LLM_CLIENT)
def test_orchestrator_classifies_general_question(mock_llm):
    """A question about CDC should be classified as general_question."""
    mock_llm.return_value = "general_question"
    result = classify_intent("O que é o CDC?")
    assert result == "general_question"


@patch(LLM_CLIENT)
def test_orchestrator_classifies_greeting(mock_llm):
    """A simple greeting should be classified as greeting."""
    mock_llm.return_value = "greeting"
    result = classify_intent("Olá, boa tarde!")
    assert result == "greeting"


@patch(LLM_CLIENT)
def test_orchestrator_classifies_out_of_scope(mock_llm):
    """A non-consumer topic should be classified as out_of_scope."""
    mock_llm.return_value = "out_of_scope"
    result = classify_intent("Qual a previsão do tempo hoje?")
    assert result == "out_of_scope"


@patch(LLM_CLIENT)
def test_orchestrator_falls_back_on_unexpected_response(mock_llm):
    """An unexpected LLM response should fall back to out_of_scope."""
    mock_llm.return_value = "some_random_thing"
    result = classify_intent("teste")
    assert result == "out_of_scope"


# --- Legal Analysis Tests -----------------------------------------------------


MOCK_ANALYSIS_JSON = """{
    "is_cdc_case": true,
    "articles": [
        {"number": "Art. 18", "title": "Vício do Produto", "relevance": "Defeito na garantia"}
    ],
    "rights": ["Reparo em 30 dias", "Substituição", "Devolução"],
    "severity": "medium",
    "confidence": 0.85,
    "reasoning": "Produto com defeito dentro da garantia legal"
}"""


@patch(LLM_CLIENT)
def test_legal_analysis_parses_valid_response(mock_llm):
    """A valid JSON response should be parsed into LegalAnalysisResult."""
    mock_llm.return_value = MOCK_ANALYSIS_JSON
    chunks = [RetrievedChunk(text="Art. 18 ...", score=0.8, articles="Art. 18")]
    result = analyze_case("celular quebrou", chunks)

    assert result.is_cdc_case is True
    assert len(result.articles) == 1
    assert result.articles[0].number == "Art. 18"
    assert result.severity == "medium"
    assert result.confidence == 0.85


@patch(LLM_CLIENT)
def test_legal_analysis_handles_markdown_fenced_json(mock_llm):
    """JSON wrapped in markdown code fences should still parse correctly."""
    mock_llm.return_value = f"```json\n{MOCK_ANALYSIS_JSON}\n```"
    chunks = [RetrievedChunk(text="Art. 18 ...", score=0.8)]
    result = analyze_case("celular quebrou", chunks)

    assert result.is_cdc_case is True
    assert len(result.articles) == 1


@patch(LLM_CLIENT)
def test_legal_analysis_handles_invalid_json(mock_llm):
    """Invalid JSON should return an empty result without crashing."""
    mock_llm.return_value = "this is not json at all"
    result = analyze_case("teste", [])

    assert result.is_cdc_case is False
    assert "Erro" in result.reasoning


# --- Strategy Tests -----------------------------------------------------------


MOCK_STRATEGY_JSON = """{
    "channels": [
        {"step": 1, "name": "SAC", "description": "Ligue para o SAC", "link": null},
        {"step": 2, "name": "PROCON", "description": "Procure o PROCON", "link": null}
    ],
    "estimated_resolution_time": "7-15 dias",
    "tips": ["Guarde os comprovantes"]
}"""


@patch(LLM_CLIENT)
def test_strategy_parses_valid_response(mock_llm):
    """A valid JSON response should be parsed into StrategyResult."""
    mock_llm.return_value = MOCK_STRATEGY_JSON
    analysis = LegalAnalysisResult(is_cdc_case=True, severity="medium")
    result = plan_strategy(analysis)

    assert len(result.channels) == 2
    assert result.channels[0].name == "SAC"
    assert result.estimated_resolution_time == "7-15 dias"


@patch(LLM_CLIENT)
def test_strategy_falls_back_on_invalid_json(mock_llm):
    """Invalid JSON should return the default resolution ladder."""
    mock_llm.return_value = "broken response"
    analysis = LegalAnalysisResult(is_cdc_case=True)
    result = plan_strategy(analysis)

    # Should return the default strategy with 3 channels
    assert len(result.channels) >= 3
    assert result.channels[0].step == 1


# --- Response Tests -----------------------------------------------------------


def test_greeting_returns_static_message():
    """Greeting response should be static (no LLM call)."""
    text = format_greeting()
    assert "Resolve Aí" in text
    assert "direito do consumidor" in text.lower()


def test_out_of_scope_returns_static_message():
    """Out-of-scope response should be static (no LLM call)."""
    text = format_out_of_scope()
    assert "fora do escopo" in text.lower()
    assert "Defensoria" in text


@patch(LLM_CLIENT)
def test_response_formats_with_llm(mock_llm):
    """CDC case response should call the LLM for formatting."""
    mock_llm.return_value = "Entendemos sua situação. Você tem direitos!"
    analysis = LegalAnalysisResult(is_cdc_case=True, severity="medium")
    strategy = StrategyResult(channels=[], tips=[])
    result = format_response("celular quebrou", analysis, strategy)

    assert "direitos" in result.lower()
    mock_llm.assert_called_once()
