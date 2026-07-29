import unittest

from pydantic import ValidationError

from app import run_pipeline
from core.cognition_engine import CognitionEngine
from core.future_generator import FutureGenerator
from core.lens_router import LensRouter
from core.observation_engine import ObservationEngine
from core.psychology_engine import PsychologyEngine
from core.social_structure_engine import SocialStructureEngine
from core.world_initializer import WorldInitializer
from schemas import RoleAssessment


class SocialStructureLensTest(unittest.TestCase):
    def test_world_observation_and_belief_produce_social_context(self):
        result = run_pipeline("校园监控", steps=1, export=False)
        observation_ids = {
            item["observation_id"] for item in result["observations"]
        }
        belief_state_ids = {
            item["belief_state_id"] for item in result["belief_states"]
        }

        self.assertEqual(len(result["role_assessments"]), 2)
        self.assertEqual(len(result["norm_pressures"]), 2)
        self.assertEqual(len(result["institution_powers"]), 2)
        for role in result["role_assessments"]:
            self.assertIn("student", role["roles"])
            self.assertTrue(set(role["observation_ids"]) <= observation_ids)
            self.assertIn(role["belief_state_id"], belief_state_ids)
            self.assertGreater(role["role_constraint"], 0.5)
        for norm in result["norm_pressures"]:
            self.assertEqual(norm["norm_id"], "student_network_policy")
            self.assertGreater(norm["compliance_pressure"], 0.4)
        for power in result["institution_powers"]:
            self.assertEqual(
                power["institution_id"],
                "university_it_office",
            )
            self.assertGreater(power["power_asymmetry"], 0.7)

    def test_social_lens_is_agent_specific_and_has_provenance(self):
        result = run_pipeline("校园监控", steps=1, export=False)
        role_ids = {
            item["role_assessment_id"]
            for item in result["role_assessments"]
        }
        norm_ids = {
            item["norm_pressure_id"] for item in result["norm_pressures"]
        }
        power_ids = {
            item["institution_power_id"]
            for item in result["institution_powers"]
        }
        hypotheses = [
            item
            for item in result["hypotheses"]
            if item["lens"] == "social_structure"
        ]

        self.assertEqual(len(hypotheses), 2)
        self.assertNotEqual(hypotheses[0]["claim"], hypotheses[1]["claim"])
        for item in hypotheses:
            self.assertTrue(
                set(item["supporting_role_assessment_ids"]) <= role_ids
            )
            self.assertTrue(
                set(item["supporting_norm_pressure_ids"]) <= norm_ids
            )
            self.assertTrue(
                set(item["supporting_institution_power_ids"]) <= power_ids
            )

    def test_social_action_evaluations_close_both_branches(self):
        result = run_pipeline("校园监控", steps=1, export=False)
        roles = {
            item["role_assessment_id"]
            for item in result["role_assessments"]
        }
        norms = {
            item["norm_pressure_id"] for item in result["norm_pressures"]
        }
        powers = {
            item["institution_power_id"]
            for item in result["institution_powers"]
        }
        beliefs = {
            item["belief_state_id"] for item in result["belief_states"]
        }
        motivations = {
            item["motivation_state_id"]
            for item in result["motivation_states"]
        }
        emotions = {
            item["emotional_appraisal_id"]
            for item in result["emotional_appraisals"]
        }
        biases = {
            item["bias_filter_id"] for item in result["bias_filter_results"]
        }

        self.assertEqual(len(result["social_action_evaluations"]), 4)
        for item in result["social_action_evaluations"]:
            self.assertIn(item["role_assessment_id"], roles)
            self.assertTrue(set(item["norm_pressure_ids"]) <= norms)
            self.assertTrue(set(item["institution_power_ids"]) <= powers)
            self.assertIn(item["belief_state_id"], beliefs)
            self.assertIn(item["motivation_state_id"], motivations)
            self.assertIn(item["emotional_appraisal_id"], emotions)
            self.assertTrue(set(item["bias_filter_ids"]) <= biases)

    def test_social_compatibility_enters_decision_and_action(self):
        result = run_pipeline("校园监控", steps=1, export=False)
        social = {
            item["social_evaluation_id"]: item
            for item in result["social_action_evaluations"]
        }
        values = {
            item["value_assessment_id"]: item
            for item in result["value_assessments"]
        }
        decision = result["decisions"][0]
        value = values[decision["value_assessment_id"]]
        evaluation = social[value["social_evaluation_id"]]

        self.assertEqual(
            decision["social_evaluation_id"],
            evaluation["social_evaluation_id"],
        )
        self.assertEqual(
            value["social_compatibility"],
            evaluation["compatibility"],
        )
        self.assertTrue(
            any(
                item["decision_id"] == decision["decision_id"]
                for item in result["actions"]
            )
        )

        base_value = sum(value["value_contributions"].values()) / len(
            value["value_contributions"]
        )
        psychology_score = min(
            1.0,
            max(
                0.0,
                (base_value * 0.7)
                + (value["motivation_alignment"] * 0.3)
                + value["stress_adjustment"],
            ),
        )
        economic_score = (psychology_score * 0.75) + (
            value["economic_utility"] * 0.25
        )
        expected = (economic_score * 0.8) + (
            value["social_compatibility"] * 0.2
        )
        self.assertAlmostEqual(value["score"], expected)

    def test_lower_institutional_power_raises_confrontation_compatibility(self):
        state, _, models = WorldInitializer().initialize("校园监控")
        observations = ObservationEngine().observe(state, models)
        cognition = CognitionEngine().interpret(observations, models)
        models = cognition.subjective_models
        psychology_engine = PsychologyEngine()
        perceptions = psychology_engine.perceive(
            state,
            observations,
            models,
        )
        psychology = psychology_engine.appraise(
            perceptions,
            models,
            cognition.belief_states,
            cognition.interpretations,
        )
        engine = SocialStructureEngine()
        baseline_context = engine.assess_context(
            state,
            observations,
            models,
            cognition.belief_states,
        )
        hypotheses = LensRouter().analyze(
            state,
            models,
            psychology=psychology,
            social=baseline_context,
        )
        futures = FutureGenerator().generate(state, models, hypotheses)
        baseline = engine.evaluate_actions(
            baseline_context,
            state,
            futures,
            psychology,
            cognition.bias_results,
            cognition.mental_models,
            step=1,
        )

        weak_state = state.model_copy(deep=True)
        for institution in weak_state.institutions.values():
            institution.authority_scope = []
            institution.resources_controlled = []
            institution.transparency = 1.0
        for norm in weak_state.norms.values():
            norm.clarity = 0.0
            norm.sanctions = []
        weak_context = engine.assess_context(
            weak_state,
            observations,
            models,
            cognition.belief_states,
        )
        weak = engine.evaluate_actions(
            weak_context,
            weak_state,
            futures,
            psychology,
            cognition.bias_results,
            cognition.mental_models,
            step=1,
        )

        baseline_confront = next(
            item
            for item in baseline.action_evaluations
            if item.action == "confront_authority"
        )
        weak_confront = next(
            item
            for item in weak.action_evaluations
            if item.action == "confront_authority"
        )
        self.assertLess(
            weak_confront.institutional_risk,
            baseline_confront.institutional_risk,
        )
        self.assertGreater(
            weak_confront.compatibility,
            baseline_confront.compatibility,
        )

    def test_social_scores_reject_invalid_ranges(self):
        with self.assertRaises(ValidationError):
            RoleAssessment(
                role_assessment_id="role_invalid",
                agent_id="lin_xia",
                step=0,
                observation_ids=[],
                belief_state_id="belief_state_001",
                roles=["student"],
                expected_behaviors=["comply"],
                role_constraint=1.2,
                role_conflict=0.5,
            )


if __name__ == "__main__":
    unittest.main()
