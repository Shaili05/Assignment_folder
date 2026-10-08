from src.mcp import registry

TOOL_NAMES = {"sentiment_trend", "flagged_reviews", "generate_summary_report", "search_reviews"}


def test_list_specs_covers_all_tools():
    specs = registry.list_specs()
    assert {spec["name"] for spec in specs} == TOOL_NAMES
    for spec in specs:
        assert spec["description"]
        assert spec["input_schema"]["type"] == "object"


def test_search_reviews_requires_question():
    assert registry.TOOLS["search_reviews"]["schema"]["required"] == ["question"]


def test_unknown_tool_returns_error():
    result = registry.call_tool("nope")
    assert "Unknown tool 'nope'" in result["error"]


def test_unknown_argument_returns_error():
    result = registry.call_tool("sentiment_trend", {"colour": "red"})
    assert "Unknown arguments for sentiment_trend: colour" in result["error"]


def test_empty_arguments_are_dropped(monkeypatch):
    monkeypatch.setitem(registry.TOOLS["sentiment_trend"], "handler", lambda **kwargs: kwargs)
    result = registry.call_tool("sentiment_trend", {"aspect": "price", "product_name": None, "brand_name": ""})
    assert result == {"aspect": "price"}


def test_call_tool_without_arguments(monkeypatch):
    monkeypatch.setitem(registry.TOOLS["flagged_reviews"], "handler", lambda **kwargs: {"seen": kwargs})
    assert registry.call_tool("flagged_reviews") == {"seen": {}}


def test_type_error_becomes_error_dict(monkeypatch):
    def broken(**kwargs):
        raise TypeError("boom")

    monkeypatch.setitem(registry.TOOLS["sentiment_trend"], "handler", broken)
    result = registry.call_tool("sentiment_trend", {"aspect": "price"})
    assert result == {"error": "Invalid arguments for sentiment_trend: boom"}


def test_run_summary_report_passes_arguments(monkeypatch):
    monkeypatch.setattr(registry, "generate_summary_report", lambda **kwargs: {"ok": kwargs})
    assert registry.run_summary_report(window_days=7) == {"ok": {"window_days": 7}}


def test_run_search_reviews_keeps_stdout_clean(monkeypatch, capsys):
    import src.rag.retriever as retriever

    def fake_search(**kwargs):
        print("noise")
        return {"hits": [], "args": kwargs}

    monkeypatch.setattr(retriever, "search_reviews", fake_search)
    result = registry.run_search_reviews(question="packaging")
    captured = capsys.readouterr()
    assert result["args"] == {"question": "packaging"}
    assert "noise" not in captured.out
    assert "noise" in captured.err


def test_warm_up_loads_collection_and_embedder(monkeypatch):
    import src.rag.retriever as retriever

    loaded = []
    monkeypatch.setattr(retriever, "get_collection", lambda: loaded.append("collection"))
    monkeypatch.setattr(retriever, "get_embedder", lambda: loaded.append("embedder"))
    registry.warm_up()
    assert loaded == ["collection", "embedder"]

