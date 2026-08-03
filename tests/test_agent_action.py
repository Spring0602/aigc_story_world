import unittest

from pydantic import ValidationError

from app import run_pipeline
from core.agent_action_model import AgentActionModel
from core.cognition_engine import CognitionEngine
from core.economic_engine import EconomicEngine
from core.lens_router import LensRouter
from core.observation_engine import ObservationEngine
from core.possible_world_engine import PossibleWorldEngine
from core.psychology_engine import PsychologyEngine
from core.social_structure_engine import SocialStructureEngine
from core.theory_of_mind import TheoryOfMindEngine
from core.world_initializer import WorldInitializer
from schemas import ActionScoreBreakdown, AgentActionDecision


class AgentActionModelTest(unittest.TestCase):
    def setUp(self):
        self.context = self._build_context()
        self.decisions = self._evaluate(self.context)

    def test_bounded_action_chain_has_complete_ranked_breakdowns(self):
        self.assertEqual(len(self.decisions), 4)
        self.assertEqual(
            [item.consideration_rank for item in self.decisions],
            [1, 2, 3, 4],
        )
        self.assertEqual(sum(item.is_preferred for item in self.decisions), 1)
        self.assertEqual(
            next(item for item in self.decisions if item.is_preferred).action,
            "secretly_collect_network_evidence",
        )
        for decision in self.decisions:
            self.assertTrue(decision.supporting_observation_ids)
            self.assertTrue(decision.supporting_belief_ids)
            self.assertTrue(decision.supporting_goals)
            self.assertTrue(decision.supporting_values)
            self.assertTrue(decision.other_model_ids)
            self.assertTrue(decision.constraint_ids)
            self.assertEqual(
                decision.is_satisficing,
                decision.score_breakdown.weighted_score
                >= decision.satisficing_threshold,
            )

    def test_score_is_the_documented_bounded_rationality_weighting(self):
        decision = self.decisions[0]
        score = decision.score_breakdown
        expected = (
            score.belief_compatibility * 0.20
            + score.possible_world_compatibility * 0.10
            + score.goal_compatibility * 0.12
            + score.value_compatibility * 0.15
            + score.emotional_compatibility * 0.12
            + score.motivation_compatibility * 0.14
            + score.other_model_compatibility * 0.07
            + score.constraint_satisfaction * 0.10
        )
        self.assertAlmostEqual(score.weighted_score, expected)

    def test_action_model_uses_latest_belief_and_visible_observations_only(self):
        latest = max(
            (
                item
                for item in self.context["cognition"].belief_states
                if item.agent_id == "lin_xia"
            ),
            key=lambda item: (item.step, len(item.belief_ids), item.belief_state_id),
        )
        boundary = next(
            item
            for item in self.context["economics"].information_boundaries
            if item.agent_id == "lin_xia"
        )
        for decision in self.decisions:
            self.assertEqual(decision.belief_state_id, latest.belief_state_id)
            self.assertEqual(decision.supporting_belief_ids, latest.belief_ids)
            self.assertTrue(
                set(decision.supporting_observation_ids).issubset(
                    boundary.observation_ids
                )
            )

    def test_removing_environmental_constraints_changes_confrontation_score(self):
        unconstrained = self._evaluate(
            self.context,
            economics=None,
            social=None,
        )
        baseline = next(
            item for item in self.decisions if item.action == "confront_authority"
        )
        counterfactual = next(
            item for item in unconstrained if item.action == "confront_authority"
        )
        self.assertGreater(
            counterfactual.score_breakdown.constraint_satisfaction,
            baseline.score_breakdown.constraint_satisfaction,
        )
        self.assertGreater(
            counterfactual.score_breakdown.weighted_score,
            baseline.score_breakdown.weighted_score,
        )

    def test_possible_world_revision_changes_action_compatibility(self):
        possible_worlds = self.context["possible_worlds"]
        revised_distributions = []
        for distribution in possible_worlds.posterior_distributions:
            if distribution.agent_id != "lin_xia":
                revised_distributions.append(distribution)
                continue
            probabilities = {
                world_id: (
                    0.90 if world_id.endswith("protective_security") else 0.05
                )
                for world_id in distribution.probabilities
            }
            dominant = next(
                world_id
                for world_id in probabilities
                if world_id.endswith("protective_security")
            )
            revised_distributions.append(
                distribution.model_copy(
                    update={
                        "probabilities": probabilities,
                        "dominant_possible_world_id": dominant,
                        "uncertainty": 0.36,
                    },
                    deep=True,
                )
            )
        revised_context = possible_worlds.model_copy(
            update={"posterior_distributions": revised_distributions},
            deep=True,
        )
        revised = self._evaluate(
            {**self.context, "possible_worlds": revised_context}
        )
        baseline_delay = next(
            item for item in self.decisions if item.action == "delay_action"
        )
        revised_delay = next(
            item for item in revised if item.action == "delay_action"
        )
        self.assertEqual(
            revised_delay.score_breakdown.possible_world_compatibility,
            0.90,
        )
        self.assertGreater(
            revised_delay.score_breakdown.weighted_score,
            baseline_delay.score_breakdown.weighted_score,
        )

    def test_pipeline_closes_action_model_future_decision_and_action_references(self):
        result = run_pipeline("校园监控", steps=1, export=False)
        action_decisions = {
            item["action_decision_id"]: item
            for item in result["agent_action_decisions"]
        }
        for future in result["candidate_futures"]:
            self.assertEqual(len(future["source_action_decision_ids"]), 1)
            source = action_decisions[future["source_action_decision_ids"][0]]
            self.assertEqual(source["action"], future["agent_actions"][0]["action"])
            self.assertEqual(
                source["score_breakdown"]["weighted_score"],
                future["bounded_rationality_score"],
            )
        final_decision = result["decisions"][0]
        source = action_decisions[final_decision["agent_action_decision_id"]]
        self.assertEqual(source["action"], final_decision["selected_action"])
        self.assertEqual(
            source["score_breakdown"]["weighted_score"],
            final_decision["bounded_rationality_score"],
        )
        self.assertEqual(result["actions"][0]["decision_id"], final_decision["decision_id"])

    def test_disabled_psychology_lens_does_not_leak_action_components(self):
        result = run_pipeline(
            "校园监控",
            steps=1,
            export=False,
            enabled_lenses={"economic", "social_structure"},
        )
        for decision in result["agent_action_decisions"]:
            self.assertEqual(
                decision["score_breakdown"]["emotional_compatibility"],
                0.5,
            )
            self.assertEqual(
                decision["score_breakdown"]["motivation_compatibility"],
                0.5,
            )
            self.assertIsNone(decision["emotional_appraisal_id"])
            self.assertIsNone(decision["motivation_state_id"])

    def test_schema_rejects_inconsistent_satisficing_state(self):
        breakdown = ActionScoreBreakdown(
            belief_compatibility=0.5,
            possible_world_compatibility=0.5,
            goal_compatibility=0.5,
            value_compatibility=0.5,
            emotional_compatibility=0.5,
            motivation_compatibility=0.5,
            other_model_compatibility=0.5,
            constraint_satisfaction=0.5,
            weighted_score=0.5,
        )
        with self.assertRaises(ValidationError):
            AgentActionDecision(
                action_decision_id="action_decision_invalid",
                agent_id="lin_xia",
                step=1,
                action="delay_action",
                information_boundary_id="boundary_001",
                information_coverage=0.5,
                belief_state_id="belief_state_001",
                dominant_possible_world_belief_id="world_belief_001",
                evaluated_possible_world_id="world_001",
                belief_distribution_id="distribution_001",
                score_breakdown=breakdown,
                satisficing_threshold=0.6,
                consideration_rank=1,
                is_satisficing=True,
                rationale="invalid",
            )

    def _build_context(self):
        state, _, models = WorldInitializer().initialize("校园监控")
        observations = ObservationEngine().observe(state, models)
        psychology_engine = PsychologyEngine()
        perceptions = psychology_engine.perceive(state, observations, models)
        cognition = CognitionEngine().interpret(
            observations,
            models,
            perceptions=perceptions,
        )
        models = cognition.subjective_models
        psychology = psychology_engine.appraise(
            perceptions,
            models,
            cognition.belief_states,
            cognition.interpretations,
        )
        models, other_models = TheoryOfMindEngine().infer(
            state,
            observations,
            models,
        )
        economics = EconomicEngine().assess_context(
            state,
            models,
            observations,
            cognition.belief_states,
        )
        possible_worlds = PossibleWorldEngine().build_context(
            observations,
            cognition.evidence,
            economics.information_boundaries,
            models,
            step=state.step,
        )
        social = SocialStructureEngine().assess_context(
            state,
            observations,
            models,
            cognition.belief_states,
        )
        hypotheses = LensRouter().route(
            state,
            models,
            psychology=psychology,
            economics=economics,
            social=social,
        ).hypotheses
        return {
            "models": models,
            "cognition": cognition,
            "psychology": psychology,
            "economics": economics,
            "possible_worlds": possible_worlds,
            "social": social,
            "other_models": other_models,
            "hypotheses": hypotheses,
        }

    def _evaluate(self, context, economics="default", social="default"):
        return AgentActionModel().evaluate(
            subjective_models=context["models"],
            belief_states=context["cognition"].belief_states,
            possible_worlds=context["possible_worlds"],
            psychology=context["psychology"],
            information_boundaries=context["economics"].information_boundaries,
            other_models=context["other_models"],
            hypotheses=context["hypotheses"],
            step=1,
            economics=(context["economics"] if economics == "default" else economics),
            social=(context["social"] if social == "default" else social),
        )


if __name__ == "__main__":
    unittest.main()
