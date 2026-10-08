import requests
import streamlit as st
from src.config.constants import API_TIMEOUT_SEC
from src.config.settings import API_BASE_URL


def _get(path, params=None):
    response = requests.get(f"{API_BASE_URL}{path}", params=params, timeout=API_TIMEOUT_SEC)
    response.raise_for_status()
    return response.json()


def _post(path, json=None):
    response = requests.post(f"{API_BASE_URL}{path}", json=json, timeout=API_TIMEOUT_SEC)
    response.raise_for_status()
    return response.json()


@st.cache_data(show_spinner=False)
def get_dashboard_stats():
    return _get("/dashboard/stats")


@st.cache_data(show_spinner=False)
def get_product_options():
    data = _get("/dashboard/products")
    return ["All products"] + data["products"]


@st.cache_data(show_spinner=False)
def get_data_profile():
    return _get("/dashboard/profile")


@st.cache_data(show_spinner=False)
def get_product_span(product_name):
    try:
        return _get("/dashboard/products/span", params={"product_name": product_name})
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 404:
            return None
        raise


def get_trends(product_name=None, granularity="month", periods=6, as_of=None):
    params = {"granularity": granularity, "periods": periods}
    if product_name:
        params["product_name"] = product_name
    if as_of:
        params["as_of"] = as_of
    return _get("/trends", params=params)


def get_flagged(last_n_days=365, limit=10, full_text=False):
    return _get("/flagged", params={"last_n_days": last_n_days, "limit": limit, "full_text": full_text})


def get_assistant_status(model=None):
    params = {"model": model} if model else None
    return _get("/assistant/status", params=params)


def ask_assistant(question, role, session_id=None, model=None):
    payload = {"question": question, "role": role}
    if session_id:
        payload["session_id"] = session_id
    if model:
        payload["model"] = model
    return _post("/assistant", json=payload)


def get_audit_logs(role, session_id=None):
    params = {"role": role}
    if session_id:
        params["session_id"] = session_id
    return _get("/audit/logs", params=params)


def get_progress(session_id):
    return _get("/assistant/progress", params={"session_id": session_id})


