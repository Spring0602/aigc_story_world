import unittest

from app import run_pipeline


class FutureTest(unittest.TestCase):
    def test_pipeline_generates_candidate_futures_per_step(self):
        result = run_pipeline("校园监控", steps=1, export=False)

        self.assertEqual(len(result["objective_states"]), 2)
        self.assertEqual(len(result["candidate_futures"]), 4)
        self.assertTrue(result["selected_futures"][0]["future_id"].endswith("secret"))

    def test_pipeline_exposes_a_closed_cognitive_interpretation_chain(self):
        result = run_pipeline("校园监控", steps=2, export=False)
        mental_models = result["mental_models"]
        bias_results = result["bias_filter_results"]
        interpretations = result["interpretations"]

        self.assertEqual(len(mental_models), len(interpretations))
        self.assertEqual(len(bias_results), len(interpretations))
        self.assertEqual(len({item["mental_model_id"] for item in mental_models}), len(mental_models))
        self.assertEqual(len({item["bias_filter_id"] for item in bias_results}), len(bias_results))
        self.assertEqual(len({item["interpretation_id"] for item in interpretations}), len(interpretations))

        mental_model_ids = {item["mental_model_id"] for item in mental_models}
        bias_results_by_id = {item["bias_filter_id"]: item for item in bias_results}
        for interpretation in interpretations:
            self.assertIn(interpretation["mental_model_id"], mental_model_ids)
            self.assertIn(interpretation["bias_filter_id"], bias_results_by_id)
            self.assertEqual(
                bias_results_by_id[interpretation["bias_filter_id"]]["mental_model_id"],
                interpretation["mental_model_id"],
            )


if __name__ == "__main__":
    unittest.main()
