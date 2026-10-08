from fastapi import APIRouter

from src.schemas.response_schema import OverviewResponse
from src.services.review_service import get_overview

router = APIRouter(prefix="/overview", tags=["overview"])

@router.get("", response_model=OverviewResponse)
def get_overview_report(
    window_days: int = 7,
    as_of: str = None,
    product_name: str = None,
    brand_name: str = None,
):
    return get_overview(window_days, as_of, product_name, brand_name)

