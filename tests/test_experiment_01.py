import json
import tempfile
import unittest
from pathlib import Path

from experiments.same_world_different_minds import SameWorldDifferentMindsExperiment


class SameWorldDifferentMindsExperimentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.experiment = SameWorldDifferentMindsExperiment()
        cls.result = cls.experiment.run()

    def test_main_control_changes_only_cognitive_configuration(self) -> None:
        result = self.result
        self.assertEqual(len(result.trials), 3)
        self.assertEqual(
            {trial.objective_world_fingerprint for trial in result.trials},
            {result.objective_world_fingerprint},
        )

        signatures = {
            json.dumps(
                self.experiment._observation_signature(trial.observation),
                sort_keys=True,
            )
            for trial in result.trials
        }
        self.assertEqual(len(signatures), 1)

    def test_three_conditions_produce_distinct_beliefs_interpretations_and_actions(self) -> None:
        trials = {trial.condition.condition_id: trial for trial in self.result.trials}
        self.assertEqual(len({trial.belief.proposition for trial in trials.values()}), 3)
        self.assertEqual(len({trial.interpretation.meaning for trial in trials.values()}), 3)
        self.assertEqual(len({trial.action.action for trial in trials.values()}), 3)

        self.assertEqual(
            trials["dataist"].action.action,
            "secretly_collect_network_evidence",
        )
        self.assertEqual(
            trials["institutionalist"].action.action,
            "follow_institutional_guidance",
        )
        self.assertEqual(
            trials["skeptic"].action.action,
            "seek_additional_evidence",
        )

    def test_differences_have_explicit_parameter_and_bias_attribution(self) -> None:
        trials = {trial.condition.condition_id: trial for trial in self.result.trials}
        self.assertGreater(
            trials["dataist"].condition.epistemology.trust_data,
            trials["institutionalist"].condition.epistemology.trust_data,
        )
        self.assertGreater(
            trials["institutionalist"].condition.epistemology.trust_authority,
            trials["skeptic"].condition.epistemology.trust_authority,
        )
        self.assertGreater(
            trials["skeptic"].condition.epistemology.tolerance_for_uncertainty,
            trials["dataist"].condition.epistemology.tolerance_for_uncertainty,
        )
        self.assertEqual(
            {
                trial.bias_filter_result.applied_biases[0].bias_type
                for trial in trials.values()
            },
            {
                "autonomy_threat_sensitivity",
                "authority_deference",
                "evidential_skepticism",
            },
        )

    def test_epistemology_swap_changes_explanation_and_action(self) -> None:
        self.assertEqual(len(self.result.epistemology_swap), 2)
        self.assertTrue(
            all(item.changed_as_predicted for item in self.result.epistemology_swap)
        )

    def test_partial_observability_is_a_separate_passing_control(self) -> None:
        control = self.result.partial_observability_control
        self.assertTrue(control.boundary_preserved)
        self.assertEqual(
            set(control.public_information_ids_by_agent["lin_xia"]),
            set(control.public_information_ids_by_agent["wang_chen"]),
        )
        self.assertIn(
            "info_private_dns_redirect",
            control.private_information_ids_by_agent["lin_xia"],
        )
        self.assertNotIn(
            "info_private_dns_redirect",
            control.private_information_ids_by_agent["wang_chen"],
        )
        self.assertEqual(control.hidden_information_ids_observed, [])

    def test_export_contains_machine_and_human_readable_results(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            json_path, report_path = self.experiment.export(self.result, directory)
            self.assertEqual(json_path.name, "experiment_01.json")
            self.assertEqual(report_path.name, "experiment_01.md")
            self.assertIn('"passed": true', json_path.read_text(encoding="utf-8"))
            report = report_path.read_text(encoding="utf-8")
            self.assertIn("实验状态：PASS", report)
            self.assertIn("参数交换实验", report)
            self.assertIn("Partial Observability", report)


if __name__ == "__main__":
    unittest.main()
