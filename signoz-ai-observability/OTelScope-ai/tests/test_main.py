"""Tests for the main FastAPI endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_returns_project_information() -> None:
    response = client.get("/")

    assert response.status_code == 200

    body = response.json()

    assert body["project"] == "OTelScope AI"
    assert body["service"] == "otelscope-ai-api"
    assert body["documentation"] == "/docs"


def test_health_returns_healthy_status() -> None:
    response = client.get("/health")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "healthy"
    assert body["service"] == "otelscope-ai-api"


def test_ask_runs_complete_agent_workflow() -> None:
    response = client.post(
        "/ask",
        json={
            "question": "Why is my API slow?",
            "session_id": "test-session",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["provider"] == "simulated"
    assert body["model"] == "demo-model"
    assert body["session_id"] == "test-session"
    assert body["request_id"]
    assert "Why is my API slow?" in body["answer"]


def test_ask_generates_session_id_when_missing() -> None:
    response = client.post(
        "/ask",
        json={
            "question": "How do traces work?",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["request_id"]
    assert body["session_id"]


def test_ask_strips_surrounding_whitespace() -> None:
    response = client.post(
        "/ask",
        json={
            "question": "   How do traces work?   ",
            "session_id": "test-session",
        },
    )

    assert response.status_code == 200
    assert "How do traces work?" in response.json()["answer"]


def test_ask_rejects_whitespace_only_question() -> None:
    response = client.post(
        "/ask",
        json={
            "question": "   ",
        },
    )

    assert response.status_code == 422


def test_ask_rejects_missing_question() -> None:
    response = client.post(
        "/ask",
        json={},
    )

    assert response.status_code == 422


def test_ask_rejects_blank_session_id() -> None:
    response = client.post(
        "/ask",
        json={
            "question": "How do traces work?",
            "session_id": "   ",
        },
    )

    assert response.status_code == 422

def test_ask_returns_safe_error_for_simulated_llm_failure() -> None:
    response = client.post(
        "/ask",
        json={
            "question": "Test an LLM provider failure.",
            "session_id": "test-session",
            "scenario": "failure",
        },
    )

    assert response.status_code == 503

    assert response.json() == {
        "detail": "A simulated downstream operation failed."
    }

def test_ask_defaults_to_normal_scenario() -> None:
    response = client.post(
        "/ask",
        json={
            "question": "Why is my API slow?"
        },
    )

    assert response.status_code == 200
    assert response.json()["scenario"] == "normal"


def test_retrieval_empty_scenario_succeeds() -> None:
    response = client.post(
        "/ask",
        json={
            "question": "Find diagnostic context.",
            "scenario": "retrieval-empty",
        },
    )

    assert response.status_code == 200
    assert response.json()["scenario"] == "retrieval-empty"


def test_high_token_scenario_returns_large_answer() -> None:
    response = client.post(
        "/ask",
        json={
            "question": "Explain observability.",
            "scenario": "high-token",
        },
    )

    assert response.status_code == 200
    assert len(response.json()["answer"]) > 5_000


def test_llm_failure_scenario_returns_503() -> None:
    response = client.post(
        "/ask",
        json={
            "question": "Test provider failure.",
            "scenario": "failure",
        },
    )

    assert response.status_code == 503

    assert response.json() == {
        "detail": "A simulated downstream operation failed."
    }


def test_tool_failure_scenario_returns_503() -> None:
    response = client.post(
        "/ask",
        json={
            "question": "Check service health.",
            "scenario": "tool-failure",
        },
    )

    assert response.status_code == 503


def test_unknown_scenario_is_rejected() -> None:
    response = client.post(
        "/ask",
        json={
            "question": "Test invalid scenario.",
            "scenario": "random",
        },
    )

    assert response.status_code == 422   