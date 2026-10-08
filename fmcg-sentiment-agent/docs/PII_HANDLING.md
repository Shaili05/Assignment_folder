# How reviewer identity data is handled

1. Raw data has synthetic identity columns (reviewer_name, user_email, user_phone).
2. scrub_pii.py masks them (J*** S****, jo***@x.com, XXX-XXX-1234). user_id stays as a pseudonymous reference.
3. Emails, phone numbers and URLs typed inside review_text are fully redacted.
4. Only the scrubbed CSV is loaded by the tools and embedded in ChromaDB. Raw data is never read at runtime.
5. Retrieval and tool outputs never return identity fields. The agent prompt and the privacy guardrail refuse identity questions.
6. Every data-prep run is recorded in logs/run_log.csv; every question and answer in logs/audit_log.jsonl.
