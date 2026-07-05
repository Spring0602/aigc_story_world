class InputParser:
    def __init__(self, llm_client):
        self.llm = llm_client

    def parse(self, user_input: str) -> dict:
        return self.llm.generate_json(self.build_prompt(user_input))

    def build_prompt(self, user_input: str) -> str:
        return f"TASK: parse_input\nUSER_INPUT:\n{user_input}"

