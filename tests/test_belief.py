import unittest

from core.cognition_engine import CognitionEngine
from core.observation_engine import ObservationEngine
from core.world_initializer import WorldInitializer


class BeliefTest(unittest.TestCase):
    def test_same_world_produces_different_interpretations(self):
        state, agents, models = WorldInitializer().initialize("校园监控")
        observations = ObservationEngine().observe(state, models)
        models, interpretations = CognitionEngine().interpret(observations, models)

        lin_claims = [item.claim for item in interpretations if item.agent_id == "lin_xia"]
        wang_claims = [item.claim for item in interpretations if item.agent_id == "wang_chen"]

        self.assertTrue(any("监控" in claim for claim in lin_claims))
        self.assertTrue(any("安全升级" in claim for claim in wang_claims))


if __name__ == "__main__":
    unittest.main()
