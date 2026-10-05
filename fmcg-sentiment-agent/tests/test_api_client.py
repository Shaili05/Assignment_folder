import pytest
import requests
import streamlit as st

from src.config.constants import API_TIMEOUT_SEC
from src.config.settings import API_BASE_URL
from src.frontend import api_client


class FakeResponse:
    def __init__(self, payload=None, status_code=200):
        self.payload = payload if payload is not None else {}
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"status {self.status_code}", response=self)

    def json(self):
        return self.payload


@pytest.fixture(autouse=True)
def clear_cache():
    st.cache_data.clear()
    yield
    st.cache_data.clear()


@pytest.fixture
def http(monkeypatch):
    state = {"calls": [], "response": FakeResponse()}

    def fake_get(url, params=None, timeout=None):
        state["calls"].append({"method": "GET", "url": url, "params": params, "timeout": timeout})
        return state["response"]

    def fake_post(url, json=None, timeout=None):
        state["calls"].append({"method": "POST", "url": url, "json": json, "timeout": timeout})
        return state["response"]

    monkeypatch.setattr(api_client.requests, "get", fake_get)
    monkeypatch.setattr(api_client.requests, "post", fake_post)
    return state


def test_dashboard_stats_calls_endpoint(http):
    http["response"] = FakeResponse({"total": 6000})
    assert api_client.get_dashboard_stats() == {"total": 6000}
    call = http["calls"][0]
    assert call["url"] == f"{API_BASE_URL}/dashboard/stats"
    assert call["timeout"] == API_TIMEOUT_SEC


def test_product_options_start_with_all_products(http):
    http["response"] = FakeResponse({"products": ["A", "B"]})
    assert api_client.get_product_options() == ["All products", "A", "B"]


def test_product_span_returns_payload(http):
    http["response"] = FakeResponse({"first": "2023-01-01"})
    assert api_client.get_product_span("Oat Balm") == {"first": "2023-01-01"}
    assert http["calls"][0]["params"] == {"product_name": "Oat Balm"}


def test_product_span_returns_none_on_404(http):
    http["response"] = FakeResponse(status_code=404)
    assert api_client.get_product_span("Unknown") is None


def test_product_span_raises_on_server_error(http):
    http["response"] = FakeResponse(status_code=500)
    with pytest.raises(requests.HTTPError):
        api_client.get_product_span("Oat Balm")


def test_trends_default_params(http):
    api_client.get_trends()
    assert http["calls"][0]["params"] == {"granularity": "month", "periods": 6}
    assert http["calls"][0]["url"] == f"{API_BASE_URL}/trends"


def test_trends_with_optional_params(http):
    api_client.get_trends(product_name="Oat", granularity="week", periods=3, as_of="2023-03-21")
    assert http["calls"][0]["params"] == {
        "granularity": "week", "periods": 3, "product_name": "Oat", "as_of": "2023-03-21",
    }


def test_flagged_params(http):
    api_client.get_flagged()
    assert http["calls"][0]["params"] == {"last_n_days": 365, "limit": 10, "full_text": False}


def test_assistant_status_without_model(http):
    api_client.get_assistant_status()
    assert http["calls"][0]["params"] is None


def test_assistant_status_with_model(http):
    api_client.get_assistant_status(model="groq:openai/gpt-oss-120b")
    assert http["calls"][0]["params"] == {"model": "groq:openai/gpt-oss-120b"}


def test_ask_assistant_minimal_payload(http):
    http["response"] = FakeResponse({"answer": "ok"})
    assert api_client.ask_assistant("How is price?", "brand_manager") == {"answer": "ok"}
    call = http["calls"][0]
    assert call["method"] == "POST"
    assert call["url"] == f"{API_BASE_URL}/assistant"
    assert call["json"] == {"question": "How is price?", "role": "brand_manager"}


def test_ask_assistant_full_payload(http):
    api_client.ask_assistant("q", "support_team", session_id="s1", model="m")
    assert http["calls"][0]["json"] == {"question": "q", "role": "support_team", "session_id": "s1", "model": "m"}


def test_audit_logs_params(http):
    api_client.get_audit_logs("support_team")
    api_client.get_audit_logs("brand_manager", session_id="s1")
    assert http["calls"][0]["params"] == {"role": "support_team"}
    assert http["calls"][1]["params"] == {"role": "brand_manager", "session_id": "s1"}



def test_progress_asks_for_the_session(http):
    http["response"] = FakeResponse({"stages": []})
    assert api_client.get_progress("s1") == {"stages": []}
    assert http["calls"][0]["url"] == f"{API_BASE_URL}/assistant/progress"
    assert http["calls"][0]["params"] == {"session_id": "s1"}


