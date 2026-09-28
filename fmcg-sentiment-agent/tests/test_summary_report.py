"""
test_summary_report.py

Tests for src/mcp/tools/summary_report.py using an in-memory sample
DataFrame.
"""

from src.mcp.tools.summary_report import generate_summary_report


def test_basic_report_structure(sample_reviews):
    result = generate_summary_report(window_days=90, df=sample_reviews)
    assert "error" not in result
    assert "markdown" in result
    assert "overall" in result
    assert "aspects" in result
    assert "flagged" in result


def test_invalid_window_days_returns_error(sample_reviews):
    result = generate_summary_report(window_days=0, df=sample_reviews)
    assert "error" in result
    result = generate_summary_report(window_days=99999, df=sample_reviews)
    assert "error" in result


def test_product_filter_applies(sample_reviews):
    result = generate_summary_report(window_days=90, product_name="Test Cleanser", df=sample_reviews)
    assert "error" not in result
    assert result["overall"]["n_reviews"] == 2


