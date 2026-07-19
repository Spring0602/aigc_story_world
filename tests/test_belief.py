import unittest

from core.cognition_engine import CognitionEngine
from core.observation_engine import ObservationEngine
from core.world_initializer import WorldInitializer


class BeliefTest(unittest.TestCase):
    def test_same_world_produces_different_interpretations(self):
        state, agents, models = WorldInitializer().initialize("校园监控")
        observations = ObservationEngine().observe(state, models)
        models, interpretations = CognitionEngine().interpret(observations, models)

        lin_beliefs = [claim for item in interpretations if item.agent_id == "lin_xia" for claim in item.belief_basis]
        wang_beliefs = [claim for item in interpretations if item.agent_id == "wang_chen" for claim in item.belief_basis]

        self.assertTrue(any("监控" in claim for claim in lin_beliefs))
        self.assertTrue(any("安全升级" in claim for claim in wang_beliefs))

        lin_monitoring = next(item for item in interpretations if "监控" in item.belief_basis[0])
        wang_authority = next(item for item in interpretations if item.agent_id == "wang_chen")
        self.assertEqual(lin_monitoring.meaning, "institution threatens autonomy")
        self.assertEqual(lin_monitoring.action_implication, "collect evidence secretly")
        self.assertGreater(lin_monitoring.emotional_response.anger, wang_authority.emotional_response.anger)
        self.assertEqual(wang_authority.action_implication, "follow institutional guidance")


if __name__ == "__main__":
    unittest.main()
