import json


class LLMClient:
    """Thin placeholder for future structured LLM calls."""

    def generate_text(self, prompt: str) -> str:
        return json.dumps(self.generate_json(prompt), ensure_ascii=False, indent=2)

    def generate_json(self, prompt: str) -> dict:
        return {}
