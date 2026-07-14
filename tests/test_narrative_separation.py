import unittest

from app import run_pipeline


class NarrativeSeparationTest(unittest.TestCase):
    def test_narrative_event_does_not_reveal_hidden_fact_as_objective_change(self):
        result = run_pipeline("校园监控", steps=1, export=False)

        narrative = result["narrative_events"][0]
        state_history = result["objective_states"][-1]["history"]

        self.assertIn("检测系统的真实功能边界", narrative["hidden_information"])
        self.assertTrue(all("真实功能边界" not in str(item.get("new_value", "")) for item in state_history))


if __name__ == "__main__":
    unittest.main()
