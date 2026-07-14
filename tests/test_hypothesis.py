import unittest

from core.lens_router import LensRouter
from core.world_initializer import WorldInitializer


class HypothesisTest(unittest.TestCase):
    def test_lenses_return_explicit_hypotheses(self):
        state, agents, models = WorldInitializer().initialize("校园监控")
        hypotheses = LensRouter().analyze(state, models)

        self.assertEqual({hyp.lens for hyp in hypotheses}, {"psychology", "economic", "social_structure"})
        self.assertTrue(all(hyp.claim and hyp.drivers and hyp.mediators and hyp.constraints for hyp in hypotheses))


if __name__ == "__main__":
    unittest.main()
