"""
scrub_pii.py
Day 2 PII-scrubbing step.

Two kinds of PII are handled here, in different ways:

1. Column-level PII (reviewer_name, user_email, user_phone). These are
   synthetic identity columns added on top of the raw Sephora dataset.
   Per team decision, these are MASKED, not dropped, so the column
   stays in the output but the value is obscured:
     reviewer_name : "John Smith"       -> "J*** S****"
     user_email    : "john.smith@x.com" -> "jo***@x.com"
     user_phone    : "415-555-1234"     -> "XXX-XXX-1234"
   user_id stays as the pseudonymous reviewer reference either way.

2. Text-level PII: emails/phone numbers/URLs accidentally typed inside
   review_text. This gets fully redacted (not masked) with a placeholder
   token, since a partial mask in the middle of a sentence reads oddly
   and there's no reason to keep any of it.

Run:
    python src/data_prep/scrub_pii.py --input data/labeled/labeled_reviews.csv --output data/labeled/reviews_scrubbed.csv
"""

import logging
import re
from pathlib import Path


import pandas as pd


from src.config.settings import LABELED_REVIEWS_PATH, REVIEWS_PATH
from src.utils.output import write_line
from src.utils.run_log import log_run


logger = logging.getLogger(__name__)

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
URL_PATTERN = re.compile(r"(?:https?://\S+|www\.\S+)")

REDACTION_MAP = {
    "EMAIL": ("[REDACTED_EMAIL]", EMAIL_PATTERN),
    "URL": ("[REDACTED_URL]", URL_PATTERN),
    "PHONE": ("[REDACTED_PHONE]", PHONE_PATTERN),
}


def mask_name(name):
    if not isinstance(name, str) or not name.strip():
        return name
    parts = name.split()
    masked_parts = [p[0] + "*" * (len(p) - 1) if len(p) > 1 else p for p in parts]
    return " ".join(masked_parts)


def mask_email(email):
    if not isinstance(email, str) or "@" not in email:
        return email
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = local[0] + "*" * max(len(local) - 1, 1)
    else:
        masked_local = local[:2] + "*" * (len(local) - 2)
    return f"{masked_local}@{domain}"


def mask_phone(phone):
    if not isinstance(phone, str):
        return phone
    digits_only = re.sub(r"\D", "", phone)
    if len(digits_only) < 4:
        return "*" * len(digits_only)
    return f"XXX-XXX-{digits_only[-4:]}"


MASKING_FUNCTIONS = {
    "reviewer_name": mask_name,
    "user_email": mask_email,
    "user_phone": mask_phone,
}


def scrub_text(text, row_id, audit_rows):
    if not isinstance(text, str):
        return text

    scrubbed = text
    for pii_type, (placeholder, pattern) in REDACTION_MAP.items():
        matches = pattern.findall(scrubbed)
        if matches:
            audit_rows.append(
                {"row_id": row_id, "pii_type": pii_type, "action": "text_redaction", "matches_found": len(matches)}
            )
            scrubbed = pattern.sub(placeholder, scrubbed)

    return scrubbed


def log_column_masking(df, col, audit_rows):
    for row_id in df.index:
        audit_rows.append({"row_id": row_id, "pii_type": col, "action": "column_mask", "matches_found": 1})


def scrub_dataframe(df):
    audit_rows = []

    df = df.copy()
    df["review_text"] = [
        scrub_text(text, row_id, audit_rows)
        for row_id, text in zip(df.index, df["review_text"])
    ]

    masked_columns = []
    for col, mask_fn in MASKING_FUNCTIONS.items():
        if col in df.columns:
            log_column_masking(df, col, audit_rows)
            df[col] = df[col].apply(mask_fn)
            masked_columns.append(col)

    audit_df = pd.DataFrame(audit_rows, columns=["row_id", "pii_type", "action", "matches_found"])
    return df, audit_df, masked_columns


def run(input_path=None, output_path=None):
    input_path = input_path or str(LABELED_REVIEWS_PATH)
    output_path = output_path or str(REVIEWS_PATH)


    df = pd.read_csv(input_path, low_memory=False)
    write_line(f"Loaded {len(df)} labeled rows from {input_path}")


    scrubbed_df, audit_df, masked_columns = scrub_dataframe(df)


    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    scrubbed_df.to_csv(output_path, index=False)


    text_redactions = int((audit_df["action"] == "text_redaction").sum())
    column_masks = int((audit_df["action"] == "column_mask").sum())


    write_line(f"Masked identity columns: {masked_columns}")
    write_line(f"Text-level redactions: {text_redactions}")
    write_line(f"Column-level masking actions: {column_masks}")
    write_line(f"Wrote {output_path} ({scrubbed_df.shape[0]} rows, {scrubbed_df.shape[1]} cols)")


    log_run(
        script_name="scrub_pii.py",
        params=f"input={input_path}, output={output_path}",
        summary=(
            f"rows={scrubbed_df.shape[0]}, cols={scrubbed_df.shape[1]}, "
            f"masked_columns={masked_columns}, text_redactions={text_redactions}, "
            f"column_masks={column_masks}"
        ),
    )



