import json
from pathlib import Path
from typing import Any

from schemas import AgentProfile, ObjectiveWorldState, SubjectiveWorldModel


DEFAULT_EXAMPLE_PATH = Path(__file__).resolve().parents[1] / "data" / "examples" / "campus_monitoring.json"


class WorldInitializer:
    def __init__(self, example_path: str | Path = DEFAULT_EXAMPLE_PATH) -> None:
        self.example_path = Path(example_path)

    def initialize(self, setting: str) -> tuple[ObjectiveWorldState, list[AgentProfile], list[SubjectiveWorldModel]]:
        payload = self._load_example()
        objective_state = ObjectiveWorldState.model_validate(payload["objective_state"])
        agents = [AgentProfile.model_validate(item) for item in payload["agent_profiles"]]
        subjective_models = [SubjectiveWorldModel.model_validate(item) for item in payload["subjective_models"]]

        seed = next((item for item in objective_state.history if item.get("fact") == "scenario_seed"), None)
        if seed is None:
            objective_state.history.append({"step": 0, "fact": "scenario_seed", "value": setting})
        else:
            seed["value"] = setting

        return objective_state, agents, subjective_models

    def _load_example(self) -> dict[str, Any]:
        with self.example_path.open(encoding="utf-8") as file:
            return json.load(file)
