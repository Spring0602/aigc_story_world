import json
import tempfile
import unittest
from pathlib import Path

from app import run_pipeline
from experiments.lens_ablation import (
    ALL_LENSES,
    LensAblationExperiment,
)


class LensAblationExperimentTest(unittest.TestCase):
    def test_four_conditions_share_the_same_objective_world(self):
        result = LensAblationExperiment().run()
        conditions = [result.baseline, *result.ablations]

        self.assertEqual(len(conditions), 4)
        self.assertEqual(
            len(
                {
                    item.objective_world_fingerprint
                    for item in conditions
                }
            ),
            1,
        )
        self.assertEqual(set(result.baseline.enabled_lenses), ALL_LENSES)

    def test_each_ablation_removes_exactly_one_lens_and_its_relations(self):
        result = LensAblationExperiment().run()

        self.assertEqual(len(result.baseline.hypothesis_ids), 6)
        self.assertEqual(len(result.baseline.relation_ids), 6)
        for condition in result.ablations:
            self.assertIsNotNone(condition.removed_lens)
            self.assertNotIn(
                condition.removed_lens,
                condition.enabled_lenses,
            )
            self.assertEqual(len(condition.enabled_lenses), 2)
            self.assertEqual(len(condition.hypothesis_ids), 4)
            self.assertEqual(len(condition.relation_ids), 2)

    def test_ablation_changes_future_and_action_scores(self):
        result = LensAblationExperiment().run()

        self.assertTrue(result.passed)
        self.assertEqual(len(result.comparisons), 3)
        for comparison in result.comparisons:
            self.assertTrue(comparison.passed)
            self.assertTrue(comparison.world_control_preserved)
            self.assertTrue(comparison.removed_lens_absent)
            self.assertTrue(comparison.hypothesis_pool_changed)
            self.assertTrue(comparison.relation_graph_changed)
            self.assertTrue(comparison.future_scores_changed)
            self.assertTrue(comparison.action_scores_changed)

    def test_disabled_lens_does_not_leak_into_value_assessment(self):
        without_psychology = run_pipeline(
            "校园监控",
            steps=1,
            export=False,
            enabled_lenses=ALL_LENSES - {"psychology"},
        )
        without_economic = run_pipeline(
            "校园监控",
            steps=1,
            export=False,
            enabled_lenses=ALL_LENSES - {"economic"},
        )
        without_social = run_pipeline(
            "校园监控",
            steps=1,
            export=False,
            enabled_lenses=ALL_LENSES - {"social_structure"},
        )

        self.assertTrue(
            all(
                item["motivation_state_id"] is None
                for item in without_psychology["value_assessments"]
            )
        )
        self.assertTrue(
            all(
                item["economic_evaluation_id"] is None
                for item in without_economic["value_assessments"]
            )
        )
        self.assertTrue(
            all(
                item["social_evaluation_id"] is None
                for item in without_social["value_assessments"]
            )
        )

    def test_current_selection_is_robust_but_mechanism_sensitive(self):
        result = LensAblationExperiment().run()

        self.assertTrue(
            all(
                not item.selected_future_changed
                and not item.selected_action_changed
                for item in result.comparisons
            )
        )
        self.assertTrue(
            all(item.final_state_changed for item in result.comparisons)
        )
        self.assertTrue(
            all(
                item.future_scores_changed and item.action_scores_changed
                for item in result.comparisons
            )
        )

    def test_experiment_is_deterministic_and_exports_both_formats(self):
        experiment = LensAblationExperiment()
        first = experiment.run()
        second = experiment.run()
        self.assertEqual(
            first.model_dump(mode="json"),
            second.model_dump(mode="json"),
        )

        with tempfile.TemporaryDirectory() as directory:
            result = experiment.run(export=True, output_dir=directory)
            json_path = Path(directory) / "lens_ablation.json"
            report_path = Path(directory) / "lens_ablation.md"
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            report = report_path.read_text(encoding="utf-8")

            self.assertTrue(result.passed)
            self.assertEqual(payload["experiment_id"], result.experiment_id)
            self.assertIn("Experiment 02: Lens Ablation", report)
            self.assertIn("最终选择对单 Lens 移除具有稳健性", report)


if __name__ == "__main__":
    unittest.main()
