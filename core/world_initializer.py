import json


class WorldInitializer:
    def __init__(self, llm_client):
        self.llm = llm_client

    def init(self, story_setting: dict) -> tuple[dict, list[dict]]:
        result = self.llm.generate_json(self.build_prompt(story_setting))
        return result["world_state"], result["character_cards"]

    def build_prompt(self, story_setting: dict) -> str:
        payload = json.dumps(story_setting, ensure_ascii=False)
        return f"TASK: init_world\nSTORY_SETTING:\n{payload}"

