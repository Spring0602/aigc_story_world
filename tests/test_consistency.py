from core.state_updater import StateUpdater
from core.llm_client import LLMClient


def test_state_update_preserves_known_facts():
    old_state = {
        "state_id": "state_000",
        "step": 0,
        "known_facts": ["林夏收到异常邮件"],
        "unknowns": [],
        "unresolved_conflicts": [],
        "events_happened": [],
        "characters": {"林夏": {}},
    }
    event = {
        "event_id": "event_001",
        "step": 1,
        "summary": "林夏发现未来时间戳",
        "new_clues": ["邮件来自未来"],
        "new_conflicts": [],
    }

    new_state = StateUpdater(LLMClient()).update(old_state, event)

    assert "林夏收到异常邮件" in new_state["known_facts"]
    assert "邮件来自未来" in new_state["known_facts"]

