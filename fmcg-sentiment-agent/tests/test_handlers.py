from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel


from src.exceptions.exceptions import RateLimitError, ReviewsNotFoundError
from src.exceptions.handlers import register_exception_handlers


class Body(BaseModel):
    question: str

def make_client():
    app = FastAPI()
    register_exception_handlers(app)


    @app.get("/missing")
    def missing():
        raise ReviewsNotFoundError("No reviews for Oat Balm")


    @app.get("/limited")
    def limited():
        raise RateLimitError()


    @app.post("/echo")
    def echo(body: Body):
        return {"ok": True}


    @app.get("/boom")
    def boom():
        raise RuntimeError("internal detail with gsk_secret")


    return TestClient(app, raise_server_exceptions=False)




def test_app_error_becomes_json_with_its_status():
    response = make_client().get("/missing")
    assert response.status_code == 404
    assert response.json() == {"error": {"code": "reviews_not_found", "message": "No reviews for Oat Balm"}}




def test_rate_limit_maps_to_429():
    response = make_client().get("/limited")
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "rate_limited"




def test_validation_error_lists_the_bad_field():
    response = make_client().post("/echo", json={})
    assert response.status_code == 422
    body = response.json()["error"]
    assert body["code"] == "validation_error"
    assert body["details"][0]["field"] == "question"




def test_unexpected_error_hides_internal_details():
    response = make_client().get("/boom")
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_error"
    assert "gsk_secret" not in response.text
    assert "RuntimeError" not in response.text



