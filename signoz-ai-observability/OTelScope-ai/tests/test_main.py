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