import json
import unittest
from pathlib import Path

from core.world_initializer import DEFAULT_EXAMPLE_PATH, WorldInitializer
from schemas import AgentProfile, ObjectiveWorldState, SubjectiveWorldModel


class CampusMonitoringExampleTest(unittest.TestCase):
    def test_day6_example_has_required_world_elements(self):
        payload = json.loads(Path(DEFAULT_EXAMPLE_PATH).read_text(encoding="utf-8"))
        state = ObjectiveWorldState.model_validate(payload["objective_state"])
        profiles = [AgentProfile.model_validate(item) for item in payload["agent_profiles"]]
        subjective_models = [SubjectiveWorldModel.model_validate(item) for item in payload["subjective_models"]]

        self.assertEqual(len(state.institutions), 1)
        self.assertEqual(next(iter(state.institutions.values())).institution_type, "university")
        self.assertEqual(len(state.agents), 2)
        self.assertEqual(len(state.active_processes), 1)
        self.assertEqual(len(state.hidden_facts), 2)
        self.assertEqual(len(state.public_information), 1)
        self.assertEqual({profile.agent_id for profile in profiles}, set(state.agents))
        self.assertEqual({model.agent_id for model in subjective_models}, set(state.agents))

    def test_initializer_loads_example_and_preserves_input_seed(self):
        state, profiles, subjective_models = WorldInitializer().initialize("自定义校园监控设定")

        seed = next(item for item in state.history if item.get("fact") == "scenario_seed")
        self.assertEqual(seed["value"], "自定义校园监控设定")
        self.assertEqual(len(profiles), 2)
        self.assertEqual(len(subjective_models), 2)


if __name__ == "__main__":
    unittest.main()
