from copy import deepcopy


class WorldStateManager:
    def __init__(self, initial_state: dict):
        self.current_state = deepcopy(initial_state)
        self.history = [deepcopy(initial_state)]

    def get_current_state(self) -> dict:
        return deepcopy(self.current_state)

    def update_state(self, new_state: dict) -> None:
        self.current_state = deepcopy(new_state)
        self.history.append(deepcopy(new_state))

    def get_history(self) -> list[dict]:
        return deepcopy(self.history)

