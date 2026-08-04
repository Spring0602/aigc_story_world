import unittest

from app import run_pipeline
from core.future_evaluator import FutureEvaluator
from schemas import (
    AgentActionDecision,
    CandidateFuture,
    CausalHypothesis,
    FutureEvaluation,
    HypothesisRelation,
    ObjectiveWorldState,
    SubjectiveWorldModel,
)


class FutureEvaluatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_pipeline("校园监控", steps=1, export=False)
        cls.state = ObjectiveWorldState.model_validate(
            cls.result["objective_states"][0]
        )
        cls.models = [
            SubjectiveWorldModel.model_validate(item)
            for item in cls.result["subjective_models"]
        ]
        cls.hypotheses = [
            CausalHypothesis.model_validate(item)
            for item in cls.result["hypotheses"]
        ]
        cls.relations = [
            HypothesisRelation.model_validate(item)
            for item in cls.result["hypothesis_relations"]
        ]
        cls.futures = [
            CandidateFuture.model_validate(item)
            for item in cls.result["candidate_futures"]
        ]
        cls.action_decisions = [
            AgentActionDecision.model_validate(item)
            for item in cls.result["agent_action_decisions"]
        ]
        cls.evaluator = FutureEvaluator()

    def test_pipeline_emits_structured_evaluation_for_every_future(self):
        evaluations = [
            FutureEvaluation.model_validate(item)
            for item in self.result["future_evaluations"]
        ]
        self.assertEqual(len(evaluations), len(self.futures))
        self.assertEqual(
            {item.future_id for item in evaluations},
            {item.future_id for item in self.futures},
        )
        for evaluation in evaluations:
            score = evaluation.score_breakdown
            self.assertTrue(
                set(evaluation.supporting_hypothesis_ids).issubset(
                    {item.hypothesis_id for item in self.hypotheses}
                )
            )
            self.assertTrue(evaluation.action_decision_ids)
            self.assertTrue(evaluation.state_change_paths)
            self.assertGreaterEqual(score.causal_support, 0.0)
            self.assertGreaterEqual(score.agent_consistency, 0.0)
            self.assertGreaterEqual(score.constraint_satisfaction, 0.0)
            self.assertGreaterEqual(score.compatibility, 0.0)

    def test_final_score_uses_documented_weighting_and_penalty(self):
        score = FutureEvaluation.model_validate(
            self.result["future_evaluations"][0]
        ).score_breakdown
        expected = max(
            0.0,
            min(
                1.0,
                score.estimated_plausibility * 0.15
                + score.causal_support * 0.20
                + score.agent_consistency * 0.20
                + score.constraint_satisfaction * 0.15
                + score.compatibility * 0.20
                + score.cross_lens_support * 0.10
                - score.contradiction_penalty * 0.15,
            ),
        )
        self.assertAlmostEqual(score.final_score, expected, places=2)

    def test_action_constraint_score_is_inherited_from_source_decision(self):
        future = self.futures[0]
        source = next(
            item
            for item in self.action_decisions
            if item.action_decision_id in future.source_action_decision_ids
        )
        evaluation = self._evaluate(future)
        self.assertAlmostEqual(
            evaluation.score_breakdown.constraint_satisfaction,
            source.score_breakdown.constraint_satisfaction,
            places=3,
        )
        self.assertEqual(
            evaluation.evaluated_constraint_ids,
            sorted(source.constraint_ids),
        )

    def test_stale_source_and_state_change_reduce_compatibility(self):
        future = self.futures[0]
        baseline = self._evaluate(future)
        stale_change = future.expected_state_changes[0].model_copy(
            update={"old_value": "value_that_is_not_in_the_world"},
            deep=True,
        )
        stale = future.model_copy(
            update={
                "source_state_id": "state_stale",
                "expected_state_changes": [stale_change],
            },
            deep=True,
        )
        stale_evaluation = self._evaluate(stale)
        self.assertEqual(stale_evaluation.source_state_id, "state_stale")
        self.assertEqual(
            stale_evaluation.evaluated_state_id,
            self.state.state_id,
        )
        self.assertLess(
            stale_evaluation.score_breakdown.state_compatibility,
            baseline.score_breakdown.state_compatibility,
        )
        self.assertLess(
            stale_evaluation.score_breakdown.compatibility,
            baseline.score_breakdown.compatibility,
        )

    def test_opposing_hypotheses_create_an_explicit_score_penalty(self):
        future = next(item for item in self.futures if item.opposing_hypotheses)
        baseline = self._evaluate(future)
        unopposed = future.model_copy(
            update={"opposing_hypotheses": []},
            deep=True,
        )
        unopposed_evaluation = self._evaluate(unopposed)
        self.assertGreater(
            baseline.score_breakdown.contradiction_penalty,
            unopposed_evaluation.score_breakdown.contradiction_penalty,
        )
        self.assertLess(
            baseline.score_breakdown.final_score,
            unopposed_evaluation.score_breakdown.final_score,
        )

    def test_flat_scores_are_the_compatible_view_of_evaluations(self):
        flat_scores = {
            item["future_id"]: item["score"]
            for item in self.result["future_scores"]
        }
        structured_scores = {
            item["future_id"]: item["score_breakdown"]["final_score"]
            for item in self.result["future_evaluations"]
        }
        self.assertEqual(flat_scores, structured_scores)

    def _evaluate(self, future: CandidateFuture) -> FutureEvaluation:
        return self.evaluator.evaluate(
            future,
            self.state,
            self.models,
            self.hypotheses,
            self.relations,
            self.action_decisions,
        )


if __name__ == "__main__":
    unittest.main()
