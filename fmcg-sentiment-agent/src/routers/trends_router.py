from fastapi import APIRouter


from src.schemas.response_schema import TrendResponse
from src.services.review_service import get_sentiment_trend


router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("", response_model=TrendResponse)
def get_trends(
    aspect: str = None,
    product_name: str = None,
    brand_name: str = None,
    granularity: str = "month",
    periods: int = 6,
    as_of: str = None,
):
    return get_sentiment_trend(aspect, product_name, brand_name, granularity, periods, as_of)
