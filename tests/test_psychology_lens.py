import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError

from app import run_pipeline
from core.output_exporter import OutputExporter
from schemas import StressState


class PsychologyLensTest(unittest.TestCase):
    def test_world_event_to_action_psychology_chain_has_closed_references(self):
        result = run_pipeline("校园监控", steps=1, export=False)
        initial_event_ids = {
            item["event_id"] for item in result["objective_states"][0]["events"]
        }
        observations = {
            item["observation_id"]: item for item in result["observations"]
        }
        belief_states = {
            item["belief_state_id"]: item for item in result["belief_states"]
        }
        beliefs = {
            belief["belief_id"]: belief
            for model in result["subjective_models"]
            for belief in model["beliefs"]
        }
        perceptions = {
            item["perception_id"]: item for item in result["perceptions"]
        }
        emotions = {
            item["emotional_appraisal_id"]: item
            for item in result["emotional_appraisals"]
        }
        stress_states = {
            item["stress_state_id"]: item for item in result["stress_states"]
        }
        motivations = {
            item["motivation_state_id"]: item
            for item in result["motivation_states"]
        }
        assessments = {
            item["value_assessment_id"]: item
            for item in result["value_assessments"]
        }
        decisions = {
            item["decision_id"]: item for item in result["decisions"]
        }

        decision = result["decisions"][0]
        action = result["actions"][0]
        assessment = assessments[decision["value_assessment_id"]]
        motivation = motivations[decision["motivation_state_id"]]
        stress = stress_states[decision["stress_state_id"]]
        emotion = emotions[decision["emotional_appraisal_id"]]
        perception = perceptions[decision["perception_id"]]
        belief_state = belief_states[emotion["belief_state_id"]]

        self.assertIn(perception["source_event_id"], initial_event_ids)
        self.assertTrue(
            all(item in observations for item in perception["observation_ids"])
        )
        self.assertTrue(
            all(
                perception["perception_id"]
                in beliefs[belief_id]["source_perception_ids"]
                for belief_id in emotion["belief_ids"]
            )
        )
        self.assertEqual(emotion["belief_ids"], belief_state["belief_ids"])
        self.assertEqual(stress["emotional_appraisal_id"], emotion["emotional_appraisal_id"])
        self.assertEqual(motivation["stress_state_id"], stress["stress_state_id"])
        self.assertEqual(
            assessment["motivation_state_id"],
            motivation["motivation_state_id"],
        )
        self.assertEqual(decision["value_assessment_id"], assessment["value_assessment_id"])
        self.assertEqual(action["decision_id"], decision["decision_id"])
        self.assertIn(decision["decision_id"], decisions)

    def test_agents_form_different_stress_and_motivation_from_same_public_event(self):
        result = run_pipeline("校园监控", steps=1, export=False)
        perceptions = {item["agent_id"]: item for item in result["perceptions"]}
        stress = {item["agent_id"]: item for item in result["stress_states"]}
        motivations = {
            item["agent_id"]: item for item in result["motivation_states"]
        }

        self.assertEqual(
            perceptions["lin_xia"]["source_event_id"],
            perceptions["wang_chen"]["source_event_id"],
        )
        self.assertGreater(
            perceptions["lin_xia"]["threat"],
            perceptions["wang_chen"]["threat"],
        )
        self.assertGreater(stress["lin_xia"]["level"], stress["wang_chen"]["level"])
        self.assertEqual(motivations["lin_xia"]["motive"], "verify_threat")
        self.assertEqual(motivations["wang_chen"]["motive"], "preserve_stability")

    def test_psychology_hypotheses_reference_the_dynamic_chain(self):
        result = run_pipeline("校园监控", steps=1, export=False)
        event_ids = {
            item["event_id"] for item in result["objective_states"][0]["events"]
        }
        perception_ids = {item["perception_id"] for item in result["perceptions"]}
        emotion_ids = {
            item["emotional_appraisal_id"]
            for item in result["emotional_appraisals"]
        }
        stress_ids = {item["stress_state_id"] for item in result["stress_states"]}
        motivation_ids = {
            item["motivation_state_id"] for item in result["motivation_states"]
        }
        hypotheses = [
            item for item in result["hypotheses"] if item["lens"] == "psychology"
        ]

        self.assertEqual(len(hypotheses), 2)
        for hypothesis in hypotheses:
            self.assertTrue(set(hypothesis["supporting_event_ids"]) <= event_ids)
            self.assertTrue(
                set(hypothesis["supporting_perception_ids"]) <= perception_ids
            )
            self.assertTrue(
                set(hypothesis["supporting_emotional_appraisal_ids"]) <= emotion_ids
            )
            self.assertTrue(
                set(hypothesis["supporting_stress_state_ids"]) <= stress_ids
            )
            self.assertTrue(
                set(hypothesis["supporting_motivation_state_ids"]) <= motivation_ids
            )

    def test_hidden_action_event_is_perceived_only_by_its_actor(self):
        result = run_pipeline("校园监控", steps=2, export=False)
        hidden_event_id = result["world_events"][0]["event_id"]
        step_one_perceptions = {
            item["agent_id"]: item
            for item in result["perceptions"]
            if item["step"] == 1
        }

        self.assertEqual(
            step_one_perceptions["lin_xia"]["source_event_id"],
            hidden_event_id,
        )
        self.assertNotEqual(
            step_one_perceptions["wang_chen"]["source_event_id"],
            hidden_event_id,
        )

    def test_psychology_scores_reject_values_outside_unit_interval(self):
        with self.assertRaises(ValidationError):
            StressState(
                stress_state_id="stress_invalid",
                agent_id="lin_xia",
                step=0,
                emotional_appraisal_id="emotion_001",
                perception_id="perception_001",
                stressors=["ambiguity"],
                level=1.2,
                band="high",
                coping_capacity=0.4,
            )

    def test_full_export_contains_psychology_chain_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            exporter = OutputExporter(Path(directory))
            with patch("app.OutputExporter", return_value=exporter):
                result = run_pipeline("校园监控", steps=1, export=True)

            run_dir = Path(result["run_dir"])
            json_files = list(run_dir.glob("*.json"))
            self.assertEqual(len(json_files), 52)
            for filename in (
                "perceptions.json",
                "emotional_appraisals.json",
                "stress_states.json",
                "motivation_states.json",
                "information_boundaries.json",
                "possible_worlds.json",
                "world_evidence_assessments.json",
                "prior_belief_distributions.json",
                "world_revisions.json",
                "posterior_belief_distributions.json",
                "possible_world_beliefs.json",
                "value_assessments.json",
                "decisions.json",
                "actions.json",
                "agent_action_decisions.json",
                "future_evaluations.json",
                "state_provenance.json",
                "narrative_importance_assessments.json",
                "fabulas.json",
                "narrative_plans.json",
                "syuzhets.json",
                "focalizations.json",
                "story_outputs.json",
                "narrative_beats.json",
                "scarcity_assessments.json",
                "information_asymmetries.json",
                "incentive_assessments.json",
                "opportunity_costs.json",
                "economic_action_evaluations.json",
                "role_assessments.json",
                "norm_pressures.json",
                "institution_powers.json",
                "social_action_evaluations.json",
                "hypothesis_relations.json",
            ):
                self.assertTrue((run_dir / filename).is_file())


if __name__ == "__main__":
    unittest.main()
