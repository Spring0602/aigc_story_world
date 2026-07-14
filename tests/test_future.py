import unittest

from app import run_pipeline


class FutureTest(unittest.TestCase):
    def test_pipeline_generates_candidate_futures_per_step(self):
        result = run_pipeline("校园监控", steps=1, export=False)

        self.assertEqual(len(result["objective_states"]), 2)
        self.assertEqual(len(result["candidate_futures"]), 4)
        self.assertTrue(result["selected_futures"][0]["future_id"].endswith("secret"))


if __name__ == "__main__":
    unittest.main()
