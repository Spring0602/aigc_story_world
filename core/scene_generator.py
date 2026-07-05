import json


class SceneGenerator:
    def __init__(self, llm_client):
        self.llm = llm_client

    def generate_scene(self, world_state: dict, event_card: dict) -> dict:
        return self.llm.generate_json(self.build_prompt(world_state, event_card))

    def build_prompt(self, world_state: dict, event_card: dict) -> str:
        state_payload = json.dumps(world_state, ensure_ascii=False)
        event_payload = json.dumps(event_card, ensure_ascii=False)
        return (
            "TASK: generate_scene\n"
            f"WORLD_STATE:\n{state_payload}\n"
            f"EVENT_CARD:\n{event_payload}"
        )

