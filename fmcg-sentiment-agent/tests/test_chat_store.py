from src.frontend import chat_store


def make_messages():
    return [
        {"role": "user", "content": "How is packaging doing?"},
        {
            "role": "assistant",
            "content": "Mostly positive.",
            "record": {
                "interaction_id": "i1",
                "status": "answered",
                "latency_sec": 1.2,
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "cost_usd": 0.001,
                "checks": {"invalid_citations": []},
                "tool_calls": [
                    {"name": "sentiment_trend", "arguments": {"aspect": "packaging"}, "output_text": "raw review text"}
                ],
            },
        },
    ]


def entry(session_id, role, updated_at):
    return {"session_id": session_id, "role": role, "updated_at": updated_at, "messages": []}


def test_save_and_load_round_trip(tmp_path):
    path = tmp_path / "chats.json"
    chat_store.save_conversation("s1", "brand_manager", make_messages(), path)
    loaded = chat_store.load_conversation("s1", path)
    assert len(loaded) == 2
    assert loaded[0]["content"] == "How is packaging doing?"
    assert loaded[1]["record"]["tool_calls"] == [{"name": "sentiment_trend", "arguments": {"aspect": "packaging"}}]


def test_tool_output_is_not_stored(tmp_path):
    path = tmp_path / "chats.json"
    chat_store.save_conversation("s1", "brand_manager", make_messages(), path)
    assert "raw review text" not in path.read_text(encoding="utf-8")


def test_save_ignores_empty_input(tmp_path):
    path = tmp_path / "chats.json"
    chat_store.save_conversation("", "brand_manager", make_messages(), path)
    chat_store.save_conversation("s1", "brand_manager", [], path)
    assert not path.exists()


def test_saving_same_session_overwrites(tmp_path):
    path = tmp_path / "chats.json"
    chat_store.save_conversation("s1", "brand_manager", make_messages(), path)
    chat_store.save_conversation("s1", "brand_manager", make_messages()[:1], path)
    items = chat_store.list_conversations(path=path)
    assert len(items) == 1
    assert items[0]["message_count"] == 1


def test_strip_message_without_record():
    assert chat_store.strip_message({"role": "user", "content": "hi"}) == {
        "role": "user", "content": "hi", "record": None,
    }


def test_make_title_short_and_whitespace():
    assert chat_store.make_title([{"role": "user", "content": "  hello   world "}]) == "hello world"


def test_make_title_long_is_truncated():
    title = chat_store.make_title([{"role": "user", "content": "word " * 30}])
    assert title.endswith("...")
    assert len(title) == chat_store.CHAT_TITLE_CHARS + 3


def test_make_title_without_user_message():
    assert chat_store.make_title([{"role": "assistant", "content": "hi"}]) == "New conversation"


def test_list_conversations_filters_by_role(tmp_path):
    path = tmp_path / "chats.json"
    chat_store.save_conversation("s1", "brand_manager", make_messages(), path)
    chat_store.save_conversation("s2", "support_team", make_messages(), path)
    assert len(chat_store.list_conversations(path=path)) == 2
    support = chat_store.list_conversations(role="support_team", path=path)
    assert [c["session_id"] for c in support] == ["s2"]
    assert support[0]["message_count"] == 2


def test_list_conversations_newest_first(tmp_path):
    path = tmp_path / "chats.json"
    data = {"a": entry("a", "r", "2026-01-01T00:00:00"), "b": entry("b", "r", "2026-02-01T00:00:00")}
    chat_store._write_all(data, path)
    ids = [c["session_id"] for c in chat_store.list_conversations(path=path)]
    assert ids == ["b", "a"]
    assert chat_store.list_conversations(path=path)[0]["title"] == "Conversation"


def test_load_missing_conversation(tmp_path):
    assert chat_store.load_conversation("nope", tmp_path / "chats.json") == []


def test_delete_conversation(tmp_path):
    path = tmp_path / "chats.json"
    chat_store.save_conversation("s1", "brand_manager", make_messages(), path)
    chat_store.delete_conversation("s1", path)
    assert chat_store.load_conversation("s1", path) == []
    chat_store.delete_conversation("missing", path)


def test_clear_all_for_one_role(tmp_path):
    path = tmp_path / "chats.json"
    chat_store.save_conversation("s1", "brand_manager", make_messages(), path)
    chat_store.save_conversation("s2", "support_team", make_messages(), path)
    chat_store.clear_all(role="support_team", path=path)
    assert [c["session_id"] for c in chat_store.list_conversations(path=path)] == ["s1"]


def test_clear_all_removes_everything(tmp_path):
    path = tmp_path / "chats.json"
    chat_store.save_conversation("s1", "brand_manager", make_messages(), path)
    chat_store.clear_all(path=path)
    assert chat_store.list_conversations(path=path) == []


def test_corrupt_file_is_treated_as_empty(tmp_path):
    path = tmp_path / "chats.json"
    path.write_text("{not json", encoding="utf-8")
    assert chat_store.list_conversations(path=path) == []


def test_non_object_json_is_treated_as_empty(tmp_path):
    path = tmp_path / "chats.json"
    path.write_text("[1, 2]", encoding="utf-8")
    assert chat_store.list_conversations(path=path) == []


def test_trim_keeps_newest(monkeypatch):
    monkeypatch.setattr(chat_store, "CHAT_MAX_CONVERSATIONS", 2)
    data = {
        "a": entry("a", "r", "2026-01-01T00:00:00"),
        "b": entry("b", "r", "2026-02-01T00:00:00"),
        "c": entry("c", "r", "2026-03-01T00:00:00"),
    }
    assert set(chat_store._trim(data)) == {"b", "c"}


def test_trim_leaves_small_store_untouched():
    data = {"a": entry("a", "r", "2026-01-01T00:00:00")}
    assert chat_store._trim(data) is data

