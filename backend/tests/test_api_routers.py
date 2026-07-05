import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.db.models import Base
from app.db.seed import seed_demo_data
from app.db.session import get_db
from app.main import app


@pytest.fixture()
def api_client(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    with TestingSessionLocal() as db:
        ids = seed_demo_data(db)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client, ids
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def _sse_events(text: str) -> list[dict]:
    events = []
    for block in text.split("\n\n"):
        block = block.strip()
        if not block.startswith("data: "):
            continue
        events.append(json.loads(block.removeprefix("data: ")))
    return events


def test_health_and_dashboard_metrics_routes(api_client):
    client, _ids = api_client

    health = client.get("/health", headers={"x-request-id": "req-test"})
    assert health.json() == {"status": "ok"}
    assert health.headers["x-request-id"] == "req-test"
    metrics = client.get("/dashboard/metrics").json()

    assert metrics["count"] >= 0
    assert "avg_latency_ms" in metrics


def test_demo_access_gate_requires_header_when_configured(api_client, monkeypatch):
    client, _ids = api_client
    monkeypatch.setenv("DEMO_ACCESS_KEY", "demo-secret")
    get_settings.cache_clear()

    assert client.get("/health").status_code == 200
    assert client.get("/dashboard/metrics").status_code == 401
    assert client.get("/dashboard/metrics", headers={"x-demo-access-key": "demo-secret"}).status_code == 200

    get_settings.cache_clear()


def test_artist_validation_rejects_blank_name(api_client):
    client, ids = api_client

    response = client.put(f"/artists/{ids['artist_id']}", json={"name": "   "})

    assert response.status_code == 422


def test_prompt_version_crud_routes(api_client):
    client, ids = api_client

    create = client.post(
        f"/artists/{ids['artist_id']}/prompt-versions",
        json={
            "name": "crud-test",
            "system_prompt": "You are LUMI NOA in a focused prompt test.",
            "memory_template": "Use safe memory only.",
            "rag_template": "Use retrieved lore.",
            "safety_template": "No unsafe intimacy.",
            "version_note": "Created by router test.",
        },
    )
    prompt_version = create.json()
    prompt_version_id = prompt_version["id"]

    assert create.status_code == 200
    assert prompt_version["name"] == "crud-test"
    assert any(item["id"] == prompt_version_id for item in client.get(f"/artists/{ids['artist_id']}/prompt-versions").json())
    assert client.get(f"/artists/prompt-versions/{prompt_version_id}").json()["system_prompt"].startswith("You are")

    update = client.put(
        f"/artists/prompt-versions/{prompt_version_id}",
        json={"version_note": "Updated by router test."},
    )

    assert update.status_code == 200
    assert update.json()["version_note"] == "Updated by router test."
    assert client.delete(f"/artists/prompt-versions/{prompt_version_id}").status_code == 204
    assert client.get(f"/artists/prompt-versions/{prompt_version_id}").status_code == 404


def test_conversation_list_and_create_routes(api_client):
    client, ids = api_client

    before = client.get(f"/conversations?artist_id={ids['artist_id']}&fan_id={ids['fan_id']}").json()["items"]
    created = client.post("/conversations", json={"artist_id": ids["artist_id"], "fan_id": ids["fan_id"]}).json()
    after = client.get(f"/conversations?artist_id={ids['artist_id']}&fan_id={ids['fan_id']}").json()["items"]

    assert before
    assert created["id"] != ids["conversation_id"]
    assert any(item["id"] == created["id"] for item in after)


def test_memory_edit_route_updates_source_tracked_memory(api_client):
    client, ids = api_client
    memory = client.post(
        f"/fans/{ids['fan_id']}/memories",
        json={
            "artist_id": ids["artist_id"],
            "memory_type": "preference",
            "content": "Fan likes quiet synth textures.",
            "confidence": 0.7,
            "sensitivity": "low",
        },
    ).json()

    edited = client.put(
        f"/fans/{ids['fan_id']}/memories/{memory['id']}",
        json={"content": "Fan likes quiet synth textures and concise answers.", "confidence": 0.93},
    )

    assert edited.status_code == 200
    assert edited.json()["confidence"] == 0.93
    assert "concise answers" in edited.json()["content"]


def test_sse_chat_stream_includes_latency_and_memory_extraction(api_client):
    client, ids = api_client

    response = client.post(
        "/chat/stream",
        json={
            "artist_id": ids["artist_id"],
            "fan_id": ids["fan_id"],
            "conversation_id": ids["conversation_id"],
            "message": "My favorite LUMI track is Blue Static.",
        },
    )
    events = _sse_events(response.text)
    debug = next(event["payload"] for event in events if event.get("type") == "debug")

    assert response.status_code == 200
    assert any(event.get("type") == "token" for event in events)
    assert debug["latency"]["latency_ms_first_token"] is not None
    assert "rag_search_ms" in debug["latency"]
    assert debug["usage_log"]["stage_timings"]["latency_ms_total"] >= debug["latency_ms"]
    assert debug["memory_extraction"]["stored"][0]["memory_type"] == "preference"
    assert debug["memory_extraction"]["stored"][0]["source_message_id"] is not None


def test_sse_chat_respects_disabled_memory_storage(api_client):
    client, ids = api_client

    response = client.post(
        "/chat/stream",
        json={
            "artist_id": ids["artist_id"],
            "fan_id": ids["fan_id"],
            "conversation_id": ids["conversation_id"],
            "message": "My favorite LUMI track is Blue Static.",
            "allow_memory_storage": False,
        },
    )
    debug = next(event["payload"] for event in _sse_events(response.text) if event.get("type") == "debug")

    assert debug["memory_extraction"]["stored"] == []
    assert debug["memory_extraction"]["skipped"][0]["skip_reason"] == "user_disabled_future_memory"


def test_manual_eval_review_route_updates_comment(api_client):
    client, ids = api_client
    client.post(
        "/chat/stream",
        json={
            "artist_id": ids["artist_id"],
            "fan_id": ids["fan_id"],
            "conversation_id": ids["conversation_id"],
            "message": "What was your debut song?",
        },
    )
    logs = client.get("/eval/logs").json()["items"]
    response_log_id = logs[0]["response_log_id"]

    review = client.post(
        f"/eval/{response_log_id}/manual-review",
        json={"comment": "Reviewed: grounding and boundary are acceptable.", "overall_score": 4.9},
    )

    assert review.status_code == 200
    assert review.json()["comment"].startswith("Reviewed")
    assert review.json()["overall_score"] == 4.9


def test_usage_reconciliation_updates_response_log(api_client):
    client, ids = api_client
    client.post(
        "/chat/stream",
        json={
            "artist_id": ids["artist_id"],
            "fan_id": ids["fan_id"],
            "conversation_id": ids["conversation_id"],
            "message": "What was your debut song?",
        },
    )
    response_log_id = client.get("/eval/logs").json()["items"][0]["response_log_id"]

    reconciled = client.post(
        f"/eval/{response_log_id}/usage-reconcile",
        json={"input_tokens": 120, "output_tokens": 33, "latency_ms": 456, "estimated_cost_usd": 0.0012},
    )

    assert reconciled.status_code == 200
    assert reconciled.json()["input_tokens"] == 120
    assert reconciled.json()["cost_estimate"] == 0.0012


def test_persona_feedback_metrics_routes(api_client):
    client, ids = api_client

    created = client.post(
        "/eval/persona-feedback",
        json={
            "fan_id": ids["fan_id"],
            "artist_id": ids["artist_id"],
            "conversation_id": ids["conversation_id"],
            "persona_mode": "companion-is",
            "rating": 4.5,
            "comment": "Felt warm but bounded.",
        },
    )
    summary = client.get(f"/dashboard/persona-feedback?artist_id={ids['artist_id']}").json()

    assert created.status_code == 200
    assert summary["modes"][0]["persona_mode"] == "companion-is"
    assert summary["modes"][0]["avg_rating"] == 4.5


def test_demo_export_import_routes(api_client):
    client, ids = api_client

    exported = client.get("/demo/export").json()
    imported = client.post("/demo/import", json=exported).json()

    assert exported["version"] == "blue_garage_demo_export_v1"
    assert any(conversation["id"] == ids["conversation_id"] for conversation in exported["conversations"])
    assert imported["imported"] is True
    assert imported["counts"]["artists"] >= 1
