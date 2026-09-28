from typing import Optional
from pydantic import BaseModel

class TrendQuery(BaseModel):
    aspect: Optional[str] = None
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    granularity: str = "month"
    periods: int = 6
    as_of: Optional[str] = None


class FlaggedQuery(BaseModel):
    severity_level: Optional[str] = None
    issue_type: Optional[str] = None
    last_n_days: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    limit: int = 10
    as_of: Optional[str] = None


class OverviewQuery(BaseModel):
    window_days: int = 7
    as_of: Optional[str] = None
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
