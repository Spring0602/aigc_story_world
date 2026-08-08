import unittest

from pydantic import ValidationError

from app import run_pipeline
from core.narrative_engine import NarrativeEngine
from schemas import (
    Focalization,
    InformationEffect,
    NarrativeEvent,
    NarrativePlan,
    ObjectiveWorldState,
)


class NarrativeEngineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = run_pipeline("校园监控", steps=3, export=False)

    def test_beats_close_the_expression_reference_chain(self):
        events = {
            item["narrative_event_id"]: item
            for item in self.output["narrative_events"]
        }
        focalizations = {
            item["focalization_id"]: item
            for item in self.output["focalizations"]
        }
        for sequence, beat in enumerate(self.output["narrative_beats"], start=1):
            event = events[beat["narrative_event_id"]]
            focalization = focalizations[beat["focalization_id"]]
            self.assertEqual(beat["sequence"], sequence)
            self.assertEqual(beat["source_event_id"], event["source_event_id"])
            self.assertEqual(
                beat["source_fabula_event_id"],
                event["source_fabula_event_id"],
            )
            self.assertEqual(
                set(beat["source_information_ids"]),
                set(focalization["audience_information_ids"]),
            )

    def test_story_text_is_composed_in_syuzhet_order(self):
        story = self.output["story_outputs"][0]
        beats = self.output["narrative_beats"]
        self.assertEqual(
            story["narrative_beat_ids"],
            [item["narrative_beat_id"] for item in beats],
        )
        self.assertEqual(
            story["rendered_text"],
            "\n\n".join(item["rendered_text"] for item in beats),
        )

    def test_rendered_story_does_not_leak_withheld_fact_content(self):
        information = {
            item["info_id"]: item["content"]
            for item in [
                *self.output["objective_states"][0]["public_information"],
                *self.output["objective_states"][0]["hidden_facts"],
            ]
        }
        for beat in self.output["narrative_beats"]:
            withheld_contents = {
                information[item]
                for item in beat["information_effect"][
                    "withheld_information_ids"
                ]
            }
            self.assertTrue(
                all(item not in beat["rendered_text"] for item in withheld_contents)
            )
            self.assertIn("仍有信息", beat["rendered_text"])

    def test_information_effect_is_derived_from_disjoint_partitions(self):
        for beat in self.output["narrative_beats"]:
            effect = beat["information_effect"]
            partitions = [
                set(effect[name])
                for name in (
                    "shared_information_ids",
                    "audience_only_information_ids",
                    "character_only_information_ids",
                    "withheld_information_ids",
                )
            ]
            for index, left in enumerate(partitions):
                for right in partitions[index + 1 :]:
                    self.assertTrue(left.isdisjoint(right))
            self.assertEqual(effect["dominant_effect"], "suspense")
            self.assertGreater(effect["tension_score"], 0.0)

    def test_information_effect_rejects_inconsistent_label(self):
        with self.assertRaises(ValidationError):
            InformationEffect(
                effect_id="effect_invalid",
                focalization_id="focalization_invalid",
                withheld_information_ids=["secret"],
                dominant_effect="alignment",
                tension_score=1.0,
                rationale="invalid fixture",
            )

    def test_information_gap_selects_all_supported_effects(self):
        cases = (
            ([], [], [], "alignment"),
            ([], [], ["withheld"], "suspense"),
            (["character_only"], [], [], "mystery"),
            ([], ["audience_only"], [], "dramatic_irony"),
        )
        engine = NarrativeEngine()
        for character_known, audience_known, withheld, expected in cases:
            with self.subTest(effect=expected):
                focalization = Focalization(
                    focalization_id=f"focalization_{expected}",
                    syuzhet_id="syuzhet_test",
                    fabula_event_id="fabula_event_test",
                    mode="third_person_limited",
                    focal_agent_id="lin_xia",
                    character_known_information_ids=character_known,
                    audience_information_ids=audience_known,
                    withheld_information_ids=withheld,
                    rationale="controlled information gap",
                )
                effect = engine.analyze_information_effect(focalization)
                self.assertEqual(effect.dominant_effect, expected)

    def test_rendering_does_not_modify_objective_world(self):
        state = ObjectiveWorldState.model_validate(
            self.output["objective_states"][1]
        )
        event = NarrativeEvent.model_validate(self.output["narrative_events"][0])
        plan = NarrativePlan.model_validate(self.output["narrative_plans"][0])
        focalization = Focalization.model_validate(
            self.output["focalizations"][0]
        )
        before = state.model_dump()

        NarrativeEngine().render_beat(1, state, event, plan, focalization)

        self.assertEqual(state.model_dump(), before)


if __name__ == "__main__":
    unittest.main()
