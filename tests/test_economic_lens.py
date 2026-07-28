import unittest

from pydantic import ValidationError

from app import run_pipeline
from core.economic_engine import EconomicEngine
from core.future_generator import FutureGenerator
from core.lens_router import LensRouter
from core.observation_engine import ObservationEngine
from core.world_initializer import WorldInitializer
from schemas import BeliefState, ScarcityAssessment


class EconomicLensTest(unittest.TestCase):
    def test_world_resources_produce_scarcity_and_information_asymmetry(self):
        result = run_pipeline("校园监控", steps=1, export=False)
        scarcity = {
            item["agent_id"]: item for item in result["scarcity_assessments"]
        }
        asymmetries = {
            item["agent_id"]: item
            for item in result["information_asymmetries"]
        }

        self.assertEqual(set(scarcity), {"lin_xia", "wang_chen"})
        self.assertEqual(set(asymmetries), {"lin_xia", "wang_chen"})
        for item in scarcity.values():
            self.assertEqual(item["resource_id"], "campus_network_access")
            self.assertGreater(item["scarcity_level"], 0.5)
            self.assertIn("student_network_policy", item["constraint_ids"])
        for item in asymmetries.values():
            self.assertGreater(item["asymmetry_level"], 0.4)
            self.assertEqual(
                item["informed_party_ids"],
                ["university_it_office"],
            )
            self.assertIn(
                "info_hidden_scope_unclear",
                item["hidden_information_ids"],
            )

    def test_information_boundary_closes_world_to_action_provenance(self):
        result = run_pipeline("校园监控", steps=1, export=False)
        boundaries = {
            item["information_boundary_id"]: item
            for item in result["information_boundaries"]
        }
        belief_ids = {
            item["belief_state_id"] for item in result["belief_states"]
        }
        motivation_ids = {
            item["motivation_state_id"]
            for item in result["motivation_states"]
        }
        evaluations = {
            item["economic_evaluation_id"]: item
            for item in result["economic_action_evaluations"]
        }
        values = {
            item["value_assessment_id"]: item
            for item in result["value_assessments"]
        }

        self.assertEqual(len(boundaries), 2)
        for boundary in boundaries.values():
            self.assertTrue(boundary["observation_ids"])
            self.assertIn(
                "info_hidden_scope_unclear",
                boundary["inaccessible_information_ids"],
            )
            self.assertNotIn(
                "info_hidden_scope_unclear",
                boundary["visible_information_ids"],
            )
        for evaluation in evaluations.values():
            self.assertIn(evaluation["information_boundary_id"], boundaries)
            self.assertIn(evaluation["belief_state_id"], belief_ids)
            self.assertIn(
                evaluation["motivation_state_id"],
                motivation_ids,
            )
        for decision in result["decisions"]:
            value = values[decision["value_assessment_id"]]
            evaluation = evaluations[value["economic_evaluation_id"]]
            self.assertEqual(
                decision["belief_state_id"],
                evaluation["belief_state_id"],
            )
            self.assertEqual(
                decision["motivation_state_id"],
                evaluation["motivation_state_id"],
            )
            self.assertTrue(
                any(
                    action["decision_id"] == decision["decision_id"]
                    for action in result["actions"]
                )
            )

    def test_role_information_boundaries_change_economic_beliefs(self):
        state, _, models = WorldInitializer().initialize("校园监控")
        observations = ObservationEngine().observe(state, models)
        lin_observations = [
            item for item in observations if item.agent_id == "lin_xia"
        ]
        belief_states = [
            BeliefState(
                belief_state_id=f"belief_boundary_{model.agent_id}",
                agent_id=model.agent_id,
                step=state.step,
                belief_ids=[f"belief_boundary_input_{model.agent_id}"],
                dominant_belief_id=f"belief_boundary_input_{model.agent_id}",
                source_update_id="boundary_test",
                uncertainty=0.2 if model.agent_id == "lin_xia" else 0.8,
            )
            for model in models
        ]

        context = EconomicEngine().assess_context(
            state,
            models,
            observations=lin_observations,
            belief_states=belief_states,
        )
        boundaries = {
            item.agent_id: item for item in context.information_boundaries
        }
        asymmetries = {
            item.agent_id: item for item in context.information_asymmetries
        }

        self.assertGreater(
            boundaries["lin_xia"].coverage,
            boundaries["wang_chen"].coverage,
        )
        self.assertLess(
            asymmetries["lin_xia"].asymmetry_level,
            asymmetries["wang_chen"].asymmetry_level,
        )

    def test_candidate_actions_have_closed_economic_evaluations(self):
        result = run_pipeline("校园监控", steps=1, export=False)
        incentives = {
            item["incentive_assessment_id"]: item
            for item in result["incentive_assessments"]
        }
        opportunity_costs = {
            item["opportunity_cost_id"]: item
            for item in result["opportunity_costs"]
        }
        scarcity_ids = {
            item["scarcity_assessment_id"]
            for item in result["scarcity_assessments"]
        }
        asymmetry_ids = {
            item["information_asymmetry_id"]
            for item in result["information_asymmetries"]
        }
        evaluations = result["economic_action_evaluations"]

        self.assertEqual(len(evaluations), 4)
        self.assertEqual(
            {item["action"] for item in evaluations},
            {
                action["action"]
                for future in result["candidate_futures"]
                for action in future["agent_actions"]
            },
        )
        for item in evaluations:
            self.assertIn(item["incentive_assessment_id"], incentives)
            self.assertIn(item["opportunity_cost_id"], opportunity_costs)
            self.assertIn(item["scarcity_assessment_id"], scarcity_ids)
            self.assertIn(
                item["information_asymmetry_id"],
                asymmetry_ids,
            )

    def test_economic_lens_outputs_agent_specific_provenance(self):
        result = run_pipeline("校园监控", steps=1, export=False)
        scarcity_ids = {
            item["scarcity_assessment_id"]
            for item in result["scarcity_assessments"]
        }
        asymmetry_ids = {
            item["information_asymmetry_id"]
            for item in result["information_asymmetries"]
        }
        hypotheses = [
            item for item in result["hypotheses"] if item["lens"] == "economic"
        ]

        self.assertEqual(len(hypotheses), 2)
        self.assertNotEqual(hypotheses[0]["claim"], hypotheses[1]["claim"])
        for hypothesis in hypotheses:
            self.assertTrue(
                set(hypothesis["supporting_scarcity_assessment_ids"])
                <= scarcity_ids
            )
            self.assertTrue(
                set(hypothesis["supporting_information_asymmetry_ids"])
                <= asymmetry_ids
            )

    def test_economic_utility_is_included_in_value_assessment_score(self):
        result = run_pipeline("校园监控", steps=1, export=False)
        evaluations = {
            item["economic_evaluation_id"]: item
            for item in result["economic_action_evaluations"]
        }
        selected = next(
            item
            for item in result["value_assessments"]
            if item["value_assessment_id"]
            == result["decisions"][0]["value_assessment_id"]
        )

        evaluation = evaluations[selected["economic_evaluation_id"]]
        self.assertEqual(selected["economic_utility"], evaluation["utility"])
        self.assertEqual(
            selected["action"],
            "secretly_collect_network_evidence",
        )
        value_score = sum(selected["value_contributions"].values()) / len(
            selected["value_contributions"]
        )
        psychological_score = min(
            1.0,
            max(
                0.0,
                (value_score * 0.7)
                + (selected["motivation_alignment"] * 0.3)
                + selected["stress_adjustment"],
            ),
        )
        expected = (psychological_score * 0.75) + (
            selected["economic_utility"] * 0.25
        )
        self.assertAlmostEqual(selected["score"], expected)

    def test_abundance_and_transparency_reduce_cost_of_public_action(self):
        state, _, models = WorldInitializer().initialize("校园监控")
        hypotheses = LensRouter().analyze(state, models)
        futures = FutureGenerator().generate(state, models, hypotheses)
        engine = EconomicEngine()
        baseline = engine.evaluate_actions(
            engine.assess_context(state, models),
            futures,
            models,
            step=1,
        )

        transparent_state = state.model_copy(deep=True)
        resource = transparent_state.resources["campus_network_access"]
        resource.quantity = 10
        resource.owner_id = None
        resource.access_rules = []
        transparent_state.hidden_facts = []
        for institution in transparent_state.institutions.values():
            institution.transparency = 1.0
        transparent = engine.evaluate_actions(
            engine.assess_context(transparent_state, models),
            futures,
            models,
            step=1,
        )

        baseline_confront = next(
            item.utility
            for item in baseline.action_evaluations
            if item.action == "confront_authority"
        )
        transparent_confront = next(
            item.utility
            for item in transparent.action_evaluations
            if item.action == "confront_authority"
        )
        self.assertGreater(transparent_confront, baseline_confront)
        self.assertLess(
            transparent.scarcity_assessments[0].scarcity_level,
            baseline.scarcity_assessments[0].scarcity_level,
        )
        self.assertLess(
            transparent.information_asymmetries[0].asymmetry_level,
            baseline.information_asymmetries[0].asymmetry_level,
        )

    def test_economic_scores_reject_values_outside_valid_ranges(self):
        with self.assertRaises(ValidationError):
            ScarcityAssessment(
                scarcity_assessment_id="scarcity_invalid",
                agent_id="lin_xia",
                step=0,
                resource_id="campus_network_access",
                available_quantity=1,
                access_level=0.4,
                physical_scarcity=0.5,
                access_scarcity=0.6,
                scarcity_level=1.2,
            )


if __name__ == "__main__":
    unittest.main()
