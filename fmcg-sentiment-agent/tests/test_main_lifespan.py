from fastapi.testclient import TestClient

from src import main


def test_the_assistant_starts_and_stops_with_the_app(monkeypatch):
    events = []
    monkeypatch.setattr(main, "get_runtime", lambda: events.append("start"))
    monkeypatch.setattr(main, "close_runtimes", lambda: events.append("stop"))
    with TestClient(main.app) as client:
        assert events == ["start"]
        assert client.get("/health").status_code == 200
    assert events == ["start", "stop"]


