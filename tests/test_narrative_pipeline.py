import unittest

from app import run_pipeline


class NarrativePipelineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = run_pipeline("校园监控", steps=3, export=False)

    def test_world_simulation_builds_a_chronological_causal_fabula(self):
        fabula = self.output["fabulas"][0]
        states = self.output["objective_states"]
        world_events = {
            item["event_id"]: item for item in self.output["world_events"]
        }

        self.assertTrue(fabula["chronology_valid"])
        self.assertTrue(fabula["causality_preserved"])
        self.assertEqual(fabula["state_ids"], [item["state_id"] for item in states])
        self.assertEqual(len(fabula["events"]), 3)
        for index, event in enumerate(fabula["events"]):
            self.assertEqual(event["source_state_id"], states[index]["state_id"])
            self.assertEqual(event["target_state_id"], states[index + 1]["state_id"])
            self.assertIn(event["world_event_id"], world_events)
            self.assertEqual(
                event["provenance_ids"],
                world_events[event["world_event_id"]]["provenance_ids"],
            )

    def test_narrative_planner_selects_assessed_fabula_events(self):
        fabula = self.output["fabulas"][0]
        plan = self.output["narrative_plans"][0]
        assessments = {
            item["assessment_id"]: item
            for item in self.output["narrative_importance_assessments"]
        }
        fabula_ids = {item["fabula_event_id"] for item in fabula["events"]}

        self.assertEqual(plan["fabula_id"], fabula["fabula_id"])
        self.assertTrue(plan["selected_items"])
        for item in plan["selected_items"]:
            self.assertIn(item["fabula_event_id"], fabula_ids)
            assessment = assessments[item["importance_assessment_id"]]
            self.assertEqual(
                assessment["source_fabula_event_id"],
                item["fabula_event_id"],
            )
            self.assertEqual(
                assessment["score_breakdown"]["weighted_score"],
                item["importance_score"],
            )

    def test_syuzhet_is_separate_from_fabula_and_preserves_first_version_order(self):
        fabula = self.output["fabulas"][0]
        plan = self.output["narrative_plans"][0]
        syuzhet = self.output["syuzhets"][0]
        selected_ids = {
            item["fabula_event_id"] for item in plan["selected_items"]
        }
        expected = [
            item["fabula_event_id"]
            for item in fabula["events"]
            if item["fabula_event_id"] in selected_ids
        ]

        self.assertEqual(syuzhet["arrangement"], "chronological")
        self.assertEqual(syuzhet["ordered_fabula_event_ids"], expected)
        self.assertEqual(syuzhet["narrative_plan_id"], plan["narrative_plan_id"])

    def test_focalization_enforces_third_person_limited_information_boundary(self):
        hidden_ids = {
            item["info_id"]
            for item in self.output["objective_states"][0]["hidden_facts"]
            if item["visibility"] == "hidden"
        }
        observations = {
            item["observation_id"]: item for item in self.output["observations"]
        }
        for focalization in self.output["focalizations"]:
            self.assertEqual(focalization["mode"], "third_person_limited")
            self.assertTrue(
                hidden_ids.isdisjoint(focalization["audience_information_ids"])
            )
            self.assertTrue(
                hidden_ids.issubset(focalization["withheld_information_ids"])
            )
            for observation_id in focalization["observation_ids"]:
                self.assertEqual(
                    observations[observation_id]["agent_id"],
                    focalization["focal_agent_id"],
                )

    def test_story_output_closes_plan_syuzhet_focalization_and_expression(self):
        story = self.output["story_outputs"][0]
        fabula = self.output["fabulas"][0]
        plan = self.output["narrative_plans"][0]
        syuzhet = self.output["syuzhets"][0]
        focalization_ids = {
            item["focalization_id"] for item in self.output["focalizations"]
        }
        narrative_ids = {
            item["narrative_event_id"] for item in self.output["narrative_events"]
        }
        beat_ids = {
            item["narrative_beat_id"] for item in self.output["narrative_beats"]
        }

        self.assertEqual(story["fabula_id"], fabula["fabula_id"])
        self.assertEqual(story["narrative_plan_id"], plan["narrative_plan_id"])
        self.assertEqual(story["syuzhet_id"], syuzhet["syuzhet_id"])
        self.assertEqual(set(story["focalization_ids"]), focalization_ids)
        self.assertEqual(set(story["narrative_event_ids"]), narrative_ids)
        self.assertEqual(set(story["narrative_beat_ids"]), beat_ids)
        self.assertTrue(story["rendered_text"])
        self.assertEqual(story["source_state_ids"], fabula["state_ids"])
        for event in self.output["narrative_events"]:
            self.assertTrue(event["source_fabula_event_id"])
            self.assertEqual(event["narrative_plan_id"], plan["narrative_plan_id"])
            self.assertEqual(event["syuzhet_id"], syuzhet["syuzhet_id"])
            self.assertTrue(event["focalization_id"])

    def test_complete_narrative_pipeline_is_deterministic(self):
        repeated = run_pipeline("校园监控", steps=3, export=False)
        fields = (
            "fabulas",
            "narrative_importance_assessments",
            "narrative_plans",
            "syuzhets",
            "focalizations",
            "narrative_beats",
            "story_outputs",
        )
        for field in fields:
            self.assertEqual(self.output[field], repeated[field])


if __name__ == "__main__":
    unittest.main()
