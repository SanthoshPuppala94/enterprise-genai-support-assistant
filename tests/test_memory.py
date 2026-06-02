from app.memory.preference_store import PreferenceStore


def test_memory_save_and_read(tmp_path):
    store = PreferenceStore(tmp_path / "memory.db")
    store.save_preferences(
        "user-1",
        response_style="bullet",
        preferred_agent="rag_agent",
        preferred_detail_level="high",
    )
    prefs = store.get_preferences("user-1")
    assert prefs["response_style"] == "bullet"
    assert prefs["preferred_agent"] == "rag_agent"
    assert prefs["preferred_detail_level"] == "high"

