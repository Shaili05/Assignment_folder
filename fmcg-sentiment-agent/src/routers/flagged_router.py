from fastapi import APIRouter, HTTPException

from src.schemas.response_schema import FlaggedReviewsResponse
from src.services.review_service import get_flagged_reviews

router = APIRouter(prefix="/flagged", tags=["flagged"])

@router.get("", response_model=FlaggedReviewsResponse)
def get_flagged(
    severity_level: str = None,
    issue_type: str = None,
    last_n_days: int = None,
    start_date: str = None,
    end_date: str = None,
    product_name: str = None,
    brand_name: str = None,
    limit: int = 10,
    as_of: str = None,
    full_text: bool = False,
):
    try:
        return get_flagged_reviews(
            severity_level, issue_type, last_n_days, start_date, end_date,
            product_name, brand_name, limit, as_of, full_text,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
