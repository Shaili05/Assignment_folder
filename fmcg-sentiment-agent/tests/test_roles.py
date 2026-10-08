import pytest

from src.agents.roles import allowed_tools, audit_access, can_call, get_role
from src.exceptions.exceptions import InvalidRequestError, InvalidRoleError


def test_unknown_role_raises_invalid_role():
    with pytest.raises(InvalidRoleError):
        get_role("intern")


def test_invalid_role_is_a_bad_request_and_a_value_error():
    assert issubclass(InvalidRoleError, InvalidRequestError)
    assert issubclass(InvalidRoleError, ValueError)


def test_brand_manager_has_all_tools():
    assert len(allowed_tools("brand_manager")) == 4


def test_support_team_is_limited():
    assert can_call("support_team", "flagged_reviews")
    assert not can_call("support_team", "sentiment_trend")


def test_audit_access_by_role():
    assert audit_access("brand_manager") == "full"
    assert audit_access("support_team") == "own_summary"


