import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.routers import assistant_router, audit_router, dashboard_router, overview_router

OVERVIEW = {
    "tool": "generate_summary_report", "window": {"days": 7}, "filters": {}, "overall": {"n_reviews": 5},
    "previous_overall": {"n_reviews": 4}, "change": None, "aspects": [], "flagged": {"total": 2},
    "products": [], "notes": [], "markdown": "Weekly report",
}
STATS = {
    "total_reviews": 5, "overall": {"n_reviews": 5}, "flagged_total": 2, "start_date": "2023-01-05",
    "end_date": "2023-02-10", "aspects": [{"aspect": "price", "n_reviews": 1}],
    "severity_counts": {"low": 1, "medium": 0, "high": 1}, "issue_type_counts": {"safety": 1, "quality": 1},
}


@pytest.fixture
def client():
    return TestClient(app)


def test_assistant_post_passes_the_payload_to_the_service(client, monkeypatch):
    seen = {}

    def fake_ask(question, role, session_id, model):
        seen["args"] = (question, role, session_id, model)
        return {"session_id": "s1", "role": role, "status": "answered", "answer": "Fine.", "checks": {}}

    monkeypatch.setattr(assistant_router, "ask_assistant", fake_ask)
    response = client.post("/assistant", json={"question": "How is packaging?", "role": "support_team", "session_id": "s1"})
    assert response.status_code == 200
    assert response.json()["answer"] == "Fine."
    assert seen["args"] == ("How is packaging?", "support_team", "s1", None)


def test_assistant_status_passes_the_model(client, monkeypatch):
    monkeypatch.setattr(
        assistant_router, "get_assistant_status",
        lambda model: {"started": True, "ready": True, "error": None, "model": model},
    )
    response = client.get("/assistant/status", params={"model": "groq:test"})
    assert response.status_code == 200
    assert response.json()["model"] == "groq:test"


def test_assistant_progress_returns_the_stages(client, monkeypatch):
    stages = [{"stage": "question_received", "detail": "q", "timestamp": "2023-03-21T10:00:00+00:00"}]
    monkeypatch.setattr(assistant_router, "get_progress", lambda session_id: {"stages": stages})
    response = client.get("/assistant/progress", params={"session_id": "s1"})
    assert response.status_code == 200
    assert response.json() == {"stages": stages}


def test_assistant_progress_needs_a_session_id(client):
    assert client.get("/assistant/progress").status_code == 422


def test_audit_logs_use_the_role_and_session(client, monkeypatch):
    seen = {}

    def fake_read_log(role, session_id=None):
        seen["args"] = (role, session_id)
        return [{"interaction_id": "i1"}]

    monkeypatch.setattr(audit_router, "read_log", fake_read_log)
    response = client.get("/audit/logs", params={"role": "support_team", "session_id": "s1"})
    assert response.status_code == 200
    assert response.json() == [{"interaction_id": "i1"}]
    assert seen["args"] == ("support_team", "s1")


def test_audit_logs_default_to_the_brand_manager(client, monkeypatch):
    seen = {}
    monkeypatch.setattr(audit_router, "read_log", lambda role, session_id=None: seen.update(role=role) or [])
    assert client.get("/audit/logs").status_code == 200
    assert seen["role"] == "brand_manager"


def test_dashboard_stats_are_returned(client, monkeypatch):
    monkeypatch.setattr(dashboard_router, "get_all_time_stats", lambda: STATS)
    response = client.get("/dashboard/stats")
    assert response.status_code == 200
    assert response.json()["total_reviews"] == 5


def test_dashboard_products_are_listed(client, monkeypatch):
    monkeypatch.setattr(dashboard_router, "get_product_options", lambda: ["Test Cleanser", "Test Moisturizer"])
    response = client.get("/dashboard/products")
    assert response.status_code == 200
    assert response.json() == {"products": ["Test Cleanser", "Test Moisturizer"]}


def test_dashboard_product_span_is_returned(client, monkeypatch):
    monkeypatch.setattr(
        dashboard_router, "get_product_span", lambda name: {"count": 2, "first": "2023-01-15", "last": "2023-02-01"},
    )
    response = client.get("/dashboard/products/span", params={"product_name": "Test Cleanser"})
    assert response.status_code == 200
    assert response.json()["count"] == 2


def test_overview_passes_the_query_values(client, monkeypatch):
    seen = {}

    def fake_overview(window_days, as_of, product_name, brand_name):
        seen["args"] = (window_days, as_of, product_name, brand_name)
        return OVERVIEW

    monkeypatch.setattr(overview_router, "get_overview", fake_overview)
    response = client.get("/overview", params={"window_days": 14, "as_of": "2023-02-01"})
    assert response.status_code == 200
    assert response.json()["markdown"] == "Weekly report"
    assert seen["args"] == (14, "2023-02-01", None, None)


