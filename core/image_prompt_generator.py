import json


class ImagePromptGenerator:
    def __init__(self, llm_client):
        self.llm = llm_client

    def generate(self, scene_card: dict) -> dict:
        return self.llm.generate_json(self.build_prompt(scene_card))

    def build_prompt(self, scene_card: dict) -> str:
        payload = json.dumps(scene_card, ensure_ascii=False)
        return f"TASK: generate_image_prompt\nSCENE_CARD:\n{payload}"

