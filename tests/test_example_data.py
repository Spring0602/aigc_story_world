import unittest

from core.world_initializer import WorldInitializer
from schemas import AgentProfile, ObjectiveWorldState, SubjectiveWorldModel


class CampusMonitoringExampleTest(unittest.TestCase):
    def test_day6_example_has_required_world_elements(self):
        state, profiles, subjective_models = WorldInitializer().initialize("校园监控")

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

        seed = next(item for item in state.history if item.fact == "scenario_seed")
        self.assertEqual(seed.new_value, "自定义校园监控设定")
        self.assertEqual(len(profiles), 2)
        self.assertEqual(len(subjective_models), 2)
        self.assertTrue(all(isinstance(item, AgentProfile) for item in profiles))
        self.assertTrue(all(isinstance(item, SubjectiveWorldModel) for item in subjective_models))
        self.assertIsInstance(state, ObjectiveWorldState)


if __name__ == "__main__":
    unittest.main()
