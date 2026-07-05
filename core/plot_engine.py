import json


class PlotEngine:
    def __init__(self, llm_client):
        self.llm = llm_client

    def generate_event(self, world_state: dict, step: int) -> dict:
        return self.llm.generate_json(self.build_prompt(world_state, step))

    def build_prompt(self, world_state: dict, step: int) -> str:
        payload = json.dumps(world_state, ensure_ascii=False)
        return f"TASK: generate_event\nSTEP:\n{step}\nWORLD_STATE:\n{payload}"

