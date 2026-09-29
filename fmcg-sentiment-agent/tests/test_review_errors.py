import pandas as pd
import pytest
from fastapi.testclient import TestClient


from src.exceptions.exceptions import DataFileMissingError, InvalidRequestError, ReviewsNotFoundError
from src.main import app
from src.repositories.review_repository import apply_filters, load_reviews, parse_date, window_bounds
from src.routers import dashboard_router, flagged_router, trends_router
from src.services.review_service import check_result




def test_missing_data_file_raises(tmp_path):
    with pytest.raises(DataFileMissingError):
        load_reviews(tmp_path / "no_such_file.csv")




def test_invalid_date_raises_invalid_request():
    with pytest.raises(InvalidRequestError):
        parse_date("not-a-date", "start_date")




def test_valid_date_is_normalised():
    assert parse_date("2023-03-21 14:30") == pd.Timestamp("2023-03-21")




def test_start_after_end_raises():
    with pytest.raises(InvalidRequestError):
        window_bounds(pd.Timestamp("2023-03-21"), start_date="2023-03-10", end_date="2023-03-01")




def test_unknown_aspect_raises_invalid_request():
    frame = pd.DataFrame({"aspects": ["price"], "product_name": ["a"], "brand_name": ["b"]})
    with pytest.raises(InvalidRequestError):
        apply_filters(frame, aspect="colour")




def test_check_result_raises_on_tool_error():
    with pytest.raises(InvalidRequestError):
        check_result({"error": "Unknown aspect 'colour'."})




def test_check_result_passes_good_result():
    assert check_result({"tool": "sentiment_trend"}) == {"tool": "sentiment_trend"}




def test_trends_router_maps_service_error_to_400(monkeypatch):
    def fail(*args):
        raise InvalidRequestError("Unknown aspect 'colour'.")


    monkeypatch.setattr(trends_router, "get_sentiment_trend", fail)
    response = TestClient(app).get("/trends?aspect=colour")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_request"




def test_flagged_router_maps_service_error_to_400(monkeypatch):
    def fail(*args):
        raise InvalidRequestError("Invalid start_date 'x'.")


    monkeypatch.setattr(flagged_router, "get_flagged_reviews", fail)
    response = TestClient(app).get("/flagged?start_date=x")
    assert response.status_code == 400




def test_dashboard_router_maps_not_found_to_404(monkeypatch):
    def fail(name):
        raise ReviewsNotFoundError(f"No reviews found for {name}")


    monkeypatch.setattr(dashboard_router, "get_product_span", fail)
    response = TestClient(app).get("/dashboard/products/span?product_name=Nothing")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "reviews_not_found"

