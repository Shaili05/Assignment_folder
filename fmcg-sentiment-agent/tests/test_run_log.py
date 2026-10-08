import csv

from src.utils.run_log import log_run


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.reader(handle))


def test_first_run_writes_a_header_and_a_row(tmp_path):
    path = tmp_path / "logs" / "run_log.csv"
    log_run("apply_label_rules", "--limit 10", "10 rows labelled", log_path=path)
    rows = read_rows(path)
    assert rows[0] == ["timestamp", "script", "params", "summary"]
    assert rows[1][1:] == ["apply_label_rules", "--limit 10", "10 rows labelled"]


def test_second_run_appends_without_a_second_header(tmp_path):
    path = tmp_path / "run_log.csv"
    log_run("scrub_pii", "", "done", log_path=path)
    log_run("recompute_safety_flags", "", "done", log_path=path)
    rows = read_rows(path)
    assert len(rows) == 3
    assert [row[1] for row in rows[1:]] == ["scrub_pii", "recompute_safety_flags"]


