from src.mcp.tools.summary_report import generate_summary_report, save_report


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


def test_report_compares_with_the_previous_window(sample_reviews):
    result = generate_summary_report(window_days=30, df=sample_reviews)
    assert result["change"] is not None
    assert {"negative_pct_change", "positive_pct_change"} <= set(result["change"])


def test_report_says_when_nothing_was_flagged(sample_reviews):
    result = generate_summary_report(window_days=7, df=sample_reviews)
    assert "No flagged reviews in this period." in result["markdown"]


def test_save_report_writes_a_markdown_file(sample_reviews, tmp_path):
    report = generate_summary_report(window_days=30, df=sample_reviews)
    path = save_report(report, output_dir=tmp_path)
    assert path.name == f"brand_health_report_{report['window']['end']}_30d.md"
    assert path.read_text(encoding="utf-8") == report["markdown"]


