from fastapi.testclient import TestClient
from fastapi.exceptions import RequestValidationError


from src.exceptions.exceptions import AppError
from src.main import app




def test_health_endpoint_works():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}




def test_exception_handlers_are_registered():
    assert AppError in app.exception_handlers
    assert RequestValidationError in app.exception_handlers
    assert Exception in app.exception_handlers


def test_bad_assistant_payload_returns_structured_error():
    response = TestClient(app).post("/assistant", json={})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
