import json
import tempfile
import unittest
from pathlib import Path

from experiments.multi_step_simulation import MultiStepSimulation


class MultiStepSimulationTest(unittest.TestCase):
    def setUp(self):
        self.simulation = MultiStepSimulation()

    def test_three_step_rollout_preserves_state_and_provenance_continuity(self):
        result = self.simulation.run(steps=3)

        self.assertTrue(result.passed)
        self.assertEqual(
            result.state_ids,
            ["state_000", "state_001", "state_002", "state_003"],
        )
        self.assertTrue(result.continuity_preserved)
        self.assertTrue(result.snapshots_immutable)
        self.assertTrue(result.provenance_complete)
        self.assertTrue(result.no_noop_changes)
        for index, trace in enumerate(result.traces):
            self.assertEqual(trace.source_state_id, result.state_ids[index])
            self.assertEqual(trace.target_state_id, result.state_ids[index + 1])
            self.assertEqual(len(trace.candidate_future_ids), 4)
            self.assertTrue(trace.references_closed)
            self.assertTrue(trace.source_values_match)
            self.assertTrue(trace.target_values_match)

    def test_supports_the_full_planned_three_to_five_step_range(self):
        result = self.simulation.run(steps=5)
        self.assertTrue(result.passed)
        self.assertEqual(len(result.traces), 5)
        self.assertEqual(result.final_state_id, "state_005")

        for invalid_steps in (2, 6):
            with self.subTest(steps=invalid_steps):
                with self.assertRaises(ValueError):
                    self.simulation.run(steps=invalid_steps)

    def test_simulation_is_deterministic_and_exports_both_formats(self):
        first = self.simulation.run(steps=3)
        second = self.simulation.run(steps=3)
        self.assertEqual(
            first.model_dump(mode="json"),
            second.model_dump(mode="json"),
        )

        with tempfile.TemporaryDirectory() as directory:
            result = self.simulation.run(
                steps=3,
                export=True,
                output_dir=directory,
            )
            json_path = Path(directory) / "multi_step_simulation.json"
            report_path = Path(directory) / "multi_step_simulation.md"
            self.assertTrue(json_path.is_file())
            self.assertTrue(report_path.is_file())
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["passed"], result.passed)
            self.assertIn("state_000 -> state_001", report_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
