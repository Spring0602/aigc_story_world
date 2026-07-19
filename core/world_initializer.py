import json
from pathlib import Path
from typing import Any

from schemas import AgentProfile, ObjectiveWorldState, StateProvenance, SubjectiveWorldModel


DEFAULT_EXAMPLE_PATH = Path(__file__).resolve().parents[1] / "data" / "examples" / "campus_monitoring.json"


class WorldInitializer:
    def __init__(self, example_path: str | Path = DEFAULT_EXAMPLE_PATH) -> None:
        self.example_path = Path(example_path)

    def initialize(self, setting: str) -> tuple[ObjectiveWorldState, list[AgentProfile], list[SubjectiveWorldModel]]:
        payload = self._load_example()
        objective_payload = self._load_section(payload, "objective_world_file", "objective_state")
        profile_payload = self._load_section(payload, "agent_profiles_file", "agent_profiles")

        objective_state = ObjectiveWorldState.model_validate(objective_payload)
        agents = [AgentProfile.model_validate(item) for item in profile_payload]
        profiles_by_agent = {profile.agent_id: profile for profile in agents}
        subjective_models = []
        for item in payload["subjective_models"]:
            agent_id = item["agent_id"]
            if agent_id not in profiles_by_agent:
                raise ValueError(f"No AgentProfile found for subjective model {agent_id!r}")
            profile = profiles_by_agent[agent_id]
            model_payload = {
                "values": profile.values,
                "goals": profile.goals,
                "identity": profile.identity,
                "roles": profile.roles,
                "epistemology": profile.epistemology,
                "human_nature_model": profile.human_nature_model,
                "theory_of_change": profile.theory_of_change,
                "methodology": profile.methodology,
                **item,
            }
            subjective_models.append(SubjectiveWorldModel.model_validate(model_payload))

        seed = next((item for item in objective_state.history if item.fact == "scenario_seed"), None)
        if seed is None:
            objective_state.history.append(
                StateProvenance(
                    provenance_id="prov_000_scenario_seed",
                    step=objective_state.step,
                    timestamp=objective_state.timestamp,
                    source="world_initializer",
                    target_state_id=objective_state.state_id,
                    fact="scenario_seed",
                    new_value=setting,
                    cause="User-provided scenario setting",
                )
            )
        else:
            seed.new_value = setting

        return objective_state, agents, subjective_models

    def _load_example(self) -> dict[str, Any]:
        with self.example_path.open(encoding="utf-8") as file:
            return json.load(file)

    def _load_section(self, payload: dict[str, Any], file_key: str, inline_key: str) -> Any:
        if file_key not in payload:
            return payload[inline_key]
        section_path = self.example_path.parent / payload[file_key]
        with section_path.open(encoding="utf-8") as file:
            return json.load(file)
