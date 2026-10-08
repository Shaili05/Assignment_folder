import pytest

from src.exceptions.exceptions import VectorStoreUnavailableError
from src.rag import retriever


def test_missing_vector_store_raises(monkeypatch, tmp_path):
    monkeypatch.setattr(retriever, "_state", {})
    monkeypatch.setattr(retriever, "VECTORSTORE_DIR", tmp_path / "no_such_store")
    with pytest.raises(VectorStoreUnavailableError):
        retriever.get_collection()


def test_bad_aspect_still_returns_error_dict_for_the_agent():
    result = retriever.search_reviews("packaging complaints", aspect="colour")
    assert "error" in result
    assert "Unknown aspect" in result["error"]


