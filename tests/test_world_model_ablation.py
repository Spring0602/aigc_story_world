import json
import tempfile
import unittest
from pathlib import Path

from app import run_pipeline
from experiments.world_model_ablation import WorldModelAblationExperiment


class WorldModelAblationExperimentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.experiment = WorldModelAblationExperiment()
        cls.result = cls.experiment.run(steps=3)

    def test_controlled_ablation_detects_subjective_model_effects(self):
        comparison = self.result.comparison

        self.assertTrue(self.result.passed)
        self.assertTrue(comparison.objective_control_preserved)
        self.assertTrue(comparison.observation_boundary_preserved)
        self.assertTrue(comparison.subjective_configuration_removed)
        self.assertTrue(comparison.belief_trajectory_changed)
        self.assertTrue(comparison.interpretation_trajectory_changed)
        self.assertTrue(comparison.future_scores_changed)
        self.assertTrue(comparison.action_scores_changed)
        self.assertTrue(comparison.subjective_effect_detected)
        self.assertTrue(comparison.provenance_preserved)

    def test_stable_action_can_survive_even_when_formation_mechanism_changes(self):
        comparison = self.result.comparison
        self.assertFalse(comparison.selected_actions_changed)
        self.assertFalse(comparison.final_state_changed)
        self.assertTrue(comparison.provenance_changed)
        self.assertEqual(
            self.result.with_subjective_model.selected_actions,
            self.result.without_subjective_model.selected_actions,
        )

    def test_no_subjective_model_condition_uses_neutral_agent_carriers(self):
        output = run_pipeline(
            "校园监控",
            steps=1,
            export=False,
            use_subjective_models=False,
        )
        self.assertFalse(output["subjective_models_enabled"])
        for model in output["subjective_models"]:
            self.assertFalse(model["values"])
            self.assertFalse(model["goals"])
        hidden_ids = {
            item["info_id"]
            for item in output["objective_states"][0]["hidden_facts"]
            if item["visibility"] == "hidden"
        }
        observed_ids = {
            item["information_id"] for item in output["observations"]
        }
        self.assertTrue(hidden_ids.isdisjoint(observed_ids))

    def test_experiment_is_deterministic_and_exports_both_formats(self):
        repeated = self.experiment.run(steps=3)
        self.assertEqual(
            self.result.model_dump(mode="json"),
            repeated.model_dump(mode="json"),
        )

        with tempfile.TemporaryDirectory() as directory:
            result = self.experiment.run(
                steps=3,
                export=True,
                output_dir=directory,
            )
            json_path = Path(directory) / "world_model_ablation.json"
            report_path = Path(directory) / "world_model_ablation.md"
            self.assertTrue(json_path.is_file())
            self.assertTrue(report_path.is_file())
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["passed"], result.passed)
            self.assertIn("Passed: True", report_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
