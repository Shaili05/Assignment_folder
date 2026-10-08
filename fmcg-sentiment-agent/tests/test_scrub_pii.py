import pandas as pd

from src.data_prep import scrub_pii


def test_mask_name():
    assert scrub_pii.mask_name("John Smith") == "J*** S****"
    assert scrub_pii.mask_name("A Smith") == "A S****"
    assert scrub_pii.mask_name("") == ""
    assert scrub_pii.mask_name(None) is None


def test_mask_email():
    assert scrub_pii.mask_email("john.smith@x.com") == "jo********@x.com"
    assert scrub_pii.mask_email("ab@x.com") == "a*@x.com"
    assert scrub_pii.mask_email("a@x.com") == "a*@x.com"
    assert scrub_pii.mask_email("not-an-email") == "not-an-email"
    assert scrub_pii.mask_email(None) is None


def test_mask_phone():
    assert scrub_pii.mask_phone("415-555-1234") == "XXX-XXX-1234"
    assert scrub_pii.mask_phone("12") == "**"
    assert scrub_pii.mask_phone(None) is None


def test_scrub_text_redacts_all_three_types():
    audit = []
    text = "mail a@b.com, call 415-555-1234 or see https://x.com/page"
    result = scrub_pii.scrub_text(text, 7, audit)
    assert "[REDACTED_EMAIL]" in result
    assert "[REDACTED_PHONE]" in result
    assert "[REDACTED_URL]" in result
    assert "a@b.com" not in result
    assert {row["pii_type"] for row in audit} == {"EMAIL", "PHONE", "URL"}
    assert all(row["row_id"] == 7 and row["action"] == "text_redaction" for row in audit)


def test_scrub_text_leaves_clean_text_alone():
    audit = []
    assert scrub_pii.scrub_text("Great cream, loved it.", 1, audit) == "Great cream, loved it."
    assert audit == []


def test_scrub_text_ignores_non_strings():
    assert scrub_pii.scrub_text(None, 1, []) is None


def test_scrub_dataframe_masks_columns_and_logs():
    df = pd.DataFrame({
        "review_text": ["Contact me at a@b.com"],
        "reviewer_name": ["John Smith"],
        "user_email": ["john.smith@x.com"],
        "user_phone": ["415-555-1234"],
    })
    scrubbed, audit, masked = scrub_pii.scrub_dataframe(df)
    assert masked == ["reviewer_name", "user_email", "user_phone"]
    assert scrubbed.loc[0, "reviewer_name"] == "J*** S****"
    assert scrubbed.loc[0, "review_text"] == "Contact me at [REDACTED_EMAIL]"
    assert int((audit["action"] == "column_mask").sum()) == 3
    assert int((audit["action"] == "text_redaction").sum()) == 1
    assert df.loc[0, "reviewer_name"] == "John Smith"


def test_scrub_dataframe_without_identity_columns():
    df = pd.DataFrame({"review_text": ["fine"]})
    scrubbed, audit, masked = scrub_pii.scrub_dataframe(df)
    assert masked == []
    assert audit.empty
    assert list(scrubbed.columns) == ["review_text"]


def test_run_writes_scrubbed_file(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(scrub_pii, "log_run", lambda **kwargs: calls.append(kwargs))
    source = tmp_path / "labeled.csv"
    target = tmp_path / "out" / "scrubbed.csv"
    pd.DataFrame({
        "review_text": ["write to a@b.com"],
        "reviewer_name": ["John Smith"],
        "user_email": ["john.smith@x.com"],
        "user_phone": ["415-555-1234"],
    }).to_csv(source, index=False)

    scrub_pii.run(str(source), str(target))

    result = pd.read_csv(target)
    assert result.loc[0, "review_text"] == "write to [REDACTED_EMAIL]"
    assert result.loc[0, "reviewer_name"] == "J*** S****"
    assert result.loc[0, "user_phone"] == "XXX-XXX-1234"
    assert len(calls) == 1
    assert calls[0]["script_name"] == "scrub_pii.py"

