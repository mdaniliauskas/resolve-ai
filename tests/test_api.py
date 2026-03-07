"""
Tests for API routes — Resolve Aí

Validates the /api/chat and /api/health endpoints.
Chat tests mock the agent workflow to avoid real LLM calls.
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from agents.legal_analysis import ArticleDetail, LegalAnalysisResult
from agents.strategy import StrategyChannel, StrategyResult
from agents.workflow import ChatResult
from api.main import app

client = TestClient(app)

MOCK_CHAT_RESULT = ChatResult(
    response="Seu caso se enquadra no CDC. Você tem direitos!",
    analysis=LegalAnalysisResult(
        is_cdc_case=True,
        articles=[ArticleDetail(number="Art. 18", title="Vício", relevance="defeito")],
        rights=["Reparo em 30 dias"],
        severity="medium",
        confidence=0.8,
    ),
    strategy=StrategyResult(
        channels=[StrategyChannel(step=1, name="SAC", description="Ligue", link=None)],
        estimated_resolution_time="7 dias",
        tips=["Guarde comprovantes"],
    ),
    sources=["CDC Art. 18"],
    metadata={"intent": "consumer_complaint", "latency_ms": 1200},
)


# --- Health -------------------------------------------------------------------


def test_health_returns_ok():
    """Health check should return status 'ok' and service metadata."""
    response = client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"
    assert "llm_provider" in data
    assert "vector_store" in data


# --- Chat ---------------------------------------------------------------------


@patch("api.routes.run_chat", return_value=MOCK_CHAT_RESULT)
def test_chat_returns_response_for_valid_message(mock_workflow):
    """A valid message should return a 200 with a response string."""
    response = client.post("/api/chat", json={"message": "Meu celular quebrou"})

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0


def test_chat_rejects_empty_message():
    """An empty message should return 422 (validation error)."""
    response = client.post("/api/chat", json={"message": ""})

    assert response.status_code == 422


def test_chat_rejects_missing_message():
    """A request without the 'message' field should return 422."""
    response = client.post("/api/chat", json={})

    assert response.status_code == 422


@patch("api.routes.run_chat", return_value=MOCK_CHAT_RESULT)
def test_chat_response_has_expected_shape(mock_workflow):
    """The response should include all expected top-level fields."""
    response = client.post("/api/chat", json={"message": "Produto com defeito"})

    data = response.json()
    assert "response" in data
    assert "analysis" in data
    assert "strategy" in data
    assert "sources" in data
    assert "metadata" in data


@patch("api.routes.run_chat", return_value=MOCK_CHAT_RESULT)
def test_chat_analysis_has_articles(mock_workflow):
    """The analysis should contain articles when it's a CDC case."""
    response = client.post("/api/chat", json={"message": "Celular defeituoso"})

    data = response.json()
    assert data["analysis"]["is_cdc_case"] is True
    assert len(data["analysis"]["articles"]) > 0
    assert data["analysis"]["articles"][0]["number"] == "Art. 18"

