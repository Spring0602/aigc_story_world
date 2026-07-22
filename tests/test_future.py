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

    def test_world_to_event_chain_has_closed_references(self):
        result = run_pipeline("校园监控", steps=1, export=False)
        observation_ids = {item["observation_id"] for item in result["observations"]}
        evidence_by_id = {item["evidence_id"]: item for item in result["evidence"]}
        updates_by_id = {item["update_id"]: item for item in result["belief_updates"]}
        belief_states_by_id = {item["belief_state_id"]: item for item in result["belief_states"]}
        assessments_by_id = {
            item["value_assessment_id"]: item for item in result["value_assessments"]
        }
        decisions_by_id = {item["decision_id"]: item for item in result["decisions"]}
        actions_by_id = {item["action_id"]: item for item in result["actions"]}
        other_models_by_id = {
            item["other_model_id"]: item for item in result["beliefs_about_others"]
        }

        self.assertEqual(len(result["value_assessments"]), len(result["candidate_futures"]))
        self.assertEqual(
            {item["action"] for item in result["value_assessments"]},
            {
                action["action"]
                for future in result["candidate_futures"]
                for action in future["agent_actions"]
            },
        )

        for update in updates_by_id.values():
            evidence = evidence_by_id[update["evidence_id"]]
            self.assertIn(evidence["observation_id"], observation_ids)
            self.assertGreaterEqual(update["posterior"], 0.0)
            self.assertLessEqual(update["posterior"], 1.0)

        for state in belief_states_by_id.values():
            self.assertIn(state["source_update_id"], updates_by_id)

        for decision in decisions_by_id.values():
            assessment = assessments_by_id[decision["value_assessment_id"]]
            self.assertEqual(assessment["belief_state_id"], decision["belief_state_id"])
            self.assertIn(decision["belief_state_id"], belief_states_by_id)
            self.assertTrue(decision["other_model_ids"])
            self.assertTrue(all(item in other_models_by_id for item in decision["other_model_ids"]))
            self.assertNotEqual(decision["other_model_adjustment"], 0.0)

        event = result["world_events"][0]
        self.assertTrue(event["decision_ids"])
        self.assertTrue(event["action_ids"])
        self.assertTrue(event["source_belief_ids"])
        self.assertTrue(event["source_observation_ids"])
        self.assertEqual(event["source_other_model_ids"], result["decisions"][0]["other_model_ids"])
        self.assertTrue(all(item in decisions_by_id for item in event["decision_ids"]))
        self.assertTrue(all(item in actions_by_id for item in event["action_ids"]))
        for action_id in event["action_ids"]:
            self.assertIn(actions_by_id[action_id]["decision_id"], event["decision_ids"])

        provenance = result["objective_states"][-1]["history"][-1]
        self.assertEqual(provenance["action_ids"], event["action_ids"])
        self.assertEqual(provenance["source_observation_ids"], event["source_observation_ids"])
        self.assertEqual(
            provenance["supporting_other_model_ids"],
            event["source_other_model_ids"],
        )

    def test_hidden_action_event_is_not_used_for_another_agents_other_model(self):
        result = run_pipeline("校园监控", steps=2, export=False)
        secret_event_id = result["world_events"][0]["event_id"]
        self.assertEqual(result["world_events"][0]["visibility"], "hidden")

        wang_about_lin = [
            item
            for item in result["beliefs_about_others"]
            if item["observer_agent_id"] == "wang_chen"
            and item["target_agent_id"] == "lin_xia"
        ]
        self.assertTrue(wang_about_lin)
        self.assertTrue(
            all(secret_event_id not in item["evidence_event_ids"] for item in wang_about_lin)
        )


if __name__ == "__main__":
    unittest.main()
