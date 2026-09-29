from fastapi import APIRouter, Query

from src.schemas.response_schema import AllTimeStatsResponse, ProductListResponse, ProductSpanResponse
from src.services.review_service import get_all_time_stats, get_data_as_of, get_product_options, get_product_span

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=AllTimeStatsResponse)
def stats():
    return get_all_time_stats()


@router.get("/products", response_model=ProductListResponse)
def products():
    return {"products": get_product_options()}


@router.get("/products/span", response_model=ProductSpanResponse)
def product_span(product_name: str = Query(None)):
    return get_product_span(product_name)


@router.get("/as-of")
def as_of():
    return {"as_of_date": get_data_as_of()}
