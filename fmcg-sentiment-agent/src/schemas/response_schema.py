from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class TrendResponse(BaseModel):
    tool: str
    filters: Dict[str, Any]
    granularity: str
    as_of_date: str
    series: List[Any]
    overall: Dict[str, Any]
    latest_vs_previous: Optional[Dict[str, Any]] = None
    notes: List[str]

class FlaggedReviewsResponse(BaseModel):
    tool: str
    window: Dict[str, Any]
    total_matches: int
    returned: int
    counts_by_level: Dict[str, int]
    counts_by_issue_type: Dict[str, int]
    reviews: List[Dict[str, Any]]

class OverviewResponse(BaseModel):
    tool: str
    window: Dict[str, Any]
    filters: Dict[str, Any]
    overall: Dict[str, Any]
    previous_overall: Dict[str, Any]
    change: Optional[Dict[str, Any]] = None
    aspects: List[Any]
    flagged: Dict[str, Any]
    products: List[Any]
    notes: List[str]
    markdown: str

class AssistantResponse(BaseModel):
    session_id: str
    role: str
    status: str
    answer: str
    interaction_id: Optional[str] = None
    checks: Dict[str, Any] = {}

class AllTimeStatsResponse(BaseModel):
    total_reviews: int
    overall: Dict[str, Any]
    flagged_total: int
    start_date: str
    end_date: str
    aspects: List[Dict[str, Any]]
    severity_counts: Dict[str, int]
    issue_type_counts: Dict[str, int]

class ProductListResponse(BaseModel):
    products: List[str]

class ProductSpanResponse(BaseModel):
    count: int
    first: str
    last: str
