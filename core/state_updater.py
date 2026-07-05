import json


class StateUpdater:
    def __init__(self, llm_client):
        self.llm = llm_client

    def update(self, old_world_state: dict, event_card: dict) -> dict:
        return self.llm.generate_json(self.build_prompt(old_world_state, event_card))

    def build_prompt(self, old_world_state: dict, event_card: dict) -> str:
        state_payload = json.dumps(old_world_state, ensure_ascii=False)
        event_payload = json.dumps(event_card, ensure_ascii=False)
        return (
            "TASK: update_state\n"
            f"OLD_WORLD_STATE:\n{state_payload}\n"
            f"EVENT_CARD:\n{event_payload}"
        )

