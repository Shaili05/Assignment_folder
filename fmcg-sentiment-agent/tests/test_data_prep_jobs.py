import sys
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

import src.data_prep.apply_label_rules as apply_module
import src.data_prep.build_vectorstore as build_module
import src.data_prep.recompute_safety_flags as recompute_module
from src.config.constants import FLAG_BACKUP_SUFFIX, FLAG_COLUMNS, VECTOR_DISTANCE_METRIC
from src.data_prep.label_rules import rating_to_sentiment, rule_aspects
from src.exceptions.exceptions import DataFileMissingError


def review_frame():
    return pd.DataFrame({
        "review_text": [
            "Caused a burning rash on my skin.", "Lovely cream, works well.", "The pump arrived broken and leaking.",
        ],
        "sentiment": ["negative", "positive", "negative"],
        "rating": [1, 5, 2],
        "submission_time": ["2023-01-10", "2023-01-05", "2023-02-01"],
        "product_id": ["p1", "p1", "p2"],
        "product_name": ["Cream A", "Cream A", "Cleanser B"],
        "brand_name": ["TestBrand", "TestBrand", "TestBrand"],
        "user_id": ["u1", "u2", "u3"],
        "aspects": ["texture_effectiveness", "packaging", "packaging"],
    })


def flagged_frame():
    frame = review_frame()
    frame["is_safety_issue"] = [True, False, True]
    frame["severity_score"] = [0.85, 0.0, 0.35]
    frame["issue_type"] = ["safety", "none", "quality"]
    frame["severity_level"] = ["high", "none", "low"]
    frame["matched_terms"] = ["burning|rash", None, "damaged|leaking"]
    return frame


class FakeCollection:
    def __init__(self, size=0):
        self.size = size
        self.added = []
        self.updated = []

    def add(self, ids, embeddings, documents, metadatas):
        self.added.append(ids)
        self.size += len(ids)

    def update(self, ids, metadatas):
        self.updated.append(ids)

    def count(self):
        return self.size


def install_fake_chroma(monkeypatch, collection, existing=()):
    state = {"deleted": [], "created": [], "paths": []}

    class FakeClient:
        def __init__(self, path):
            state["paths"].append(path)

        def get_collection(self, name):
            return collection

        def list_collections(self):
            return [SimpleNamespace(name=name) for name in existing]

        def delete_collection(self, name):
            state["deleted"].append(name)

        def create_collection(self, name, metadata):
            state["created"].append((name, metadata))
            return collection

    monkeypatch.setitem(sys.modules, "chromadb", SimpleNamespace(PersistentClient=FakeClient))
    return state


@pytest.fixture
def output(monkeypatch):
    captured = []
    for module in (recompute_module, apply_module, build_module):
        monkeypatch.setattr(module, "write_line", captured.append)
        monkeypatch.setattr(module, "log_run", lambda **kwargs: captured.append(("logged", kwargs["script_name"])))
    return captured


def test_recompute_file_adds_the_flag_columns_and_keeps_a_backup(tmp_path):
    path = tmp_path / "reviews.csv"
    review_frame().to_csv(path, index=False)
    frame, old_flagged = recompute_module.recompute_file(path)
    backup = path.with_name(path.stem + FLAG_BACKUP_SUFFIX + ".csv")
    assert old_flagged == 0
    assert set(FLAG_COLUMNS) <= set(frame.columns)
    assert bool(frame.loc[0, "is_safety_issue"]) is True
    assert bool(frame.loc[1, "is_safety_issue"]) is False
    assert backup.exists()


def test_recompute_file_never_overwrites_the_first_backup(tmp_path):
    path = tmp_path / "reviews.csv"
    review_frame().to_csv(path, index=False)
    recompute_module.recompute_file(path)
    backup = path.with_name(path.stem + FLAG_BACKUP_SUFFIX + ".csv")
    backup.write_text("original", encoding="utf-8")
    recompute_module.recompute_file(path)
    assert backup.read_text(encoding="utf-8") == "original"


def test_recompute_file_reports_the_old_flag_count(tmp_path):
    path = tmp_path / "reviews.csv"
    frame = review_frame()
    frame["is_safety_issue"] = [True, False, True]
    frame.to_csv(path, index=False)
    assert recompute_module.recompute_file(path)[1] == 2


def test_build_metadata_converts_every_value():
    frame = flagged_frame()
    frame.loc[2, "submission_time"] = "not a date"
    records = recompute_module.build_metadata(frame)
    assert records[0]["rating"] == 1
    assert records[0]["is_safety_issue"] is True
    assert records[0]["severity_score"] == 0.85
    assert records[0]["submission_ts"] == 20230110
    assert records[1]["matched_terms"] == ""
    assert records[2]["submission_ts"] == 0


def test_sync_chroma_updates_in_batches(monkeypatch):
    collection = FakeCollection(size=3)
    state = install_fake_chroma(monkeypatch, collection)
    monkeypatch.setattr(recompute_module, "CHROMA_INSERT_BATCH_SIZE", 2)
    recompute_module.sync_chroma(flagged_frame(), "store-dir", "reviews")
    assert state["paths"] == ["store-dir"]
    assert collection.updated == [["0", "1"], ["2"]]


def test_sync_chroma_stops_when_the_row_counts_differ(monkeypatch):
    install_fake_chroma(monkeypatch, FakeCollection(size=5))
    with pytest.raises(SystemExit):
        recompute_module.sync_chroma(flagged_frame(), "store-dir", "reviews")


def test_recompute_run_processes_both_files_and_skips_chroma(tmp_path, output):
    labeled, scrubbed = tmp_path / "labeled.csv", tmp_path / "scrubbed.csv"
    review_frame().to_csv(labeled, index=False)
    review_frame().to_csv(scrubbed, index=False)
    recompute_module.run(str(labeled), str(scrubbed), str(tmp_path / "store"), "reviews", skip_chroma=True)
    assert "Chroma sync skipped" in output
    assert ("logged", "recompute_safety_flags.py") in output
    assert any(isinstance(line, str) and line.startswith("scrubbed.csv: flagged 0 ->") for line in output)


def test_recompute_run_syncs_chroma_when_asked(tmp_path, output, monkeypatch):
    synced = []
    monkeypatch.setattr(recompute_module, "sync_chroma", lambda *args: synced.append(args[1:]))
    scrubbed = tmp_path / "scrubbed.csv"
    review_frame().to_csv(scrubbed, index=False)
    recompute_module.run(str(tmp_path / "missing.csv"), str(scrubbed), "store-dir", "reviews")
    assert synced == [("store-dir", "reviews")]


def test_recompute_run_needs_the_scrubbed_file(tmp_path, output):
    with pytest.raises(SystemExit):
        recompute_module.run(str(tmp_path / "a.csv"), str(tmp_path / "b.csv"), "store-dir", "reviews", True)


def labeled_csv(path):
    frame = review_frame()
    frame["is_safety_issue"] = [False, False, False]
    frame["sentiment_confidence"] = [0.9, 0.9, 0.9]
    frame.to_csv(path, index=False)


def test_apply_rules_rewrites_sentiment_aspects_and_flags(tmp_path):
    path = tmp_path / "reviews.csv"
    labeled_csv(path)
    frame, old_sentiment, old_flagged = apply_module.apply_rules(path)
    assert frame["sentiment"].tolist() == [rating_to_sentiment(r) for r in frame["rating"]]
    assert frame["aspects"].tolist() == [rule_aspects(t) for t in frame["review_text"]]
    assert "sentiment_confidence" not in frame.columns
    assert set(FLAG_COLUMNS) <= set(frame.columns)
    assert old_sentiment == {"negative": 2, "positive": 1}
    assert old_flagged == 0
    assert path.with_name("reviews_before_label_fix.csv").exists()


def test_apply_run_skips_the_chroma_sync(tmp_path, output):
    labeled, scrubbed = tmp_path / "labeled.csv", tmp_path / "scrubbed.csv"
    labeled_csv(labeled)
    labeled_csv(scrubbed)
    apply_module.run(str(labeled), str(scrubbed), str(tmp_path / "store"), "reviews", skip_chroma=True)
    assert "Chroma sync skipped" in output
    assert ("logged", "apply_label_rules.py") in output
    assert any(isinstance(line, str) and line.startswith("Aspect counts:") for line in output)


def test_apply_run_syncs_chroma_when_asked(tmp_path, output, monkeypatch):
    synced = []
    monkeypatch.setattr(apply_module, "sync_chroma", lambda *args: synced.append(args[1:]))
    scrubbed = tmp_path / "scrubbed.csv"
    labeled_csv(scrubbed)
    apply_module.run(str(tmp_path / "missing.csv"), str(scrubbed), "store-dir", "reviews")
    assert synced == [("store-dir", "reviews")]


def test_apply_run_needs_the_scrubbed_file(tmp_path, output):
    with pytest.raises(SystemExit):
        apply_module.run(str(tmp_path / "a.csv"), str(tmp_path / "b.csv"), "store-dir", "reviews", True)


def test_indexing_needs_the_scrubbed_file(tmp_path):
    with pytest.raises(DataFileMissingError):
        build_module.load_reviews_for_indexing(tmp_path / "missing.csv")


def test_indexing_names_the_missing_columns(tmp_path):
    path = tmp_path / "reviews.csv"
    review_frame().to_csv(path, index=False)
    with pytest.raises(DataFileMissingError) as raised:
        build_module.load_reviews_for_indexing(path)
    assert "severity_score" in raised.value.message


def test_indexing_loads_a_complete_file(tmp_path):
    path = tmp_path / "reviews.csv"
    flagged_frame().to_csv(path, index=False)
    assert len(build_module.load_reviews_for_indexing(path)) == 3


def install_fake_model(monkeypatch):
    class FakeModel:
        def __init__(self, model_id):
            self.model_id = model_id

        def encode(self, texts, batch_size, show_progress_bar, convert_to_numpy, normalize_embeddings):
            return np.ones((len(texts), 2))

    monkeypatch.setitem(sys.modules, "sentence_transformers", SimpleNamespace(SentenceTransformer=FakeModel))


def test_build_vectorstore_replaces_the_old_collection(tmp_path, output, monkeypatch):
    path = tmp_path / "reviews.csv"
    flagged_frame().to_csv(path, index=False)
    collection = FakeCollection()
    state = install_fake_chroma(monkeypatch, collection, existing=["reviews"])
    install_fake_model(monkeypatch)
    monkeypatch.setattr(build_module, "CHROMA_INSERT_BATCH_SIZE", 2)
    build_module.run(str(path), str(tmp_path / "store"), "reviews")
    assert state["deleted"] == ["reviews"]
    assert state["created"] == [("reviews", {"hnsw:space": VECTOR_DISTANCE_METRIC})]
    assert collection.added == [["0", "1"], ["2"]]
    assert (tmp_path / "store").is_dir()
    assert ("logged", "build_vectorstore") in output


def test_build_vectorstore_creates_a_new_collection(tmp_path, output, monkeypatch):
    path = tmp_path / "reviews.csv"
    flagged_frame().to_csv(path, index=False)
    state = install_fake_chroma(monkeypatch, FakeCollection())
    install_fake_model(monkeypatch)
    build_module.run(str(path), str(tmp_path / "store"), "reviews")
    assert state["deleted"] == []
    assert len(state["created"]) == 1

