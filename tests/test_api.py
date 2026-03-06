"""
Tests for API routes — Resolve Aí

Validates the /api/chat and /api/health endpoints.
"""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


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


# --- Chat (stub) -------------------------------------------------------------


def test_chat_returns_response_for_valid_message():
    """A valid message should return a 200 with a response string."""
    response = client.post("/api/chat", json={"message": "Meu celular quebrou"})

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0


def test_chat_echoes_user_message_in_stub():
    """The stub should echo back the user's message (proves it was received)."""
    user_msg = "Cobrança indevida no cartão de crédito"
    response = client.post("/api/chat", json={"message": user_msg})

    data = response.json()
    assert user_msg in data["response"]


def test_chat_rejects_empty_message():
    """An empty message should return 422 (validation error)."""
    response = client.post("/api/chat", json={"message": ""})

    assert response.status_code == 422


def test_chat_rejects_missing_message():
    """A request without the 'message' field should return 422."""
    response = client.post("/api/chat", json={})

    assert response.status_code == 422


def test_chat_response_has_expected_shape():
    """The response should include all expected top-level fields."""
    response = client.post("/api/chat", json={"message": "Produto com defeito"})

    data = response.json()
    assert "response" in data
    assert "analysis" in data
    assert "sources" in data
    assert "metadata" in data
