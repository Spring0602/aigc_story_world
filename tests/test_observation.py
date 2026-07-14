import unittest

from core.observation_engine import ObservationEngine
from core.world_initializer import WorldInitializer


class ObservationTest(unittest.TestCase):
    def test_hidden_facts_are_not_public_observations(self):
        state, agents, models = WorldInitializer().initialize("校园监控")
        observations = ObservationEngine().observe(state, models)

        contents = [observation.content for observation in observations]
        self.assertNotIn("检测系统的功能边界并不透明。", contents)
        self.assertIn("部分 DNS 请求被重定向。", contents)


if __name__ == "__main__":
    unittest.main()
