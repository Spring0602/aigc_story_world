import unittest

from pydantic import ValidationError

from app import run_pipeline
from core.narrative_importance import NarrativeImportance
from core.world_transition import WorldTransition
from schemas import (
    CandidateFuture,
    FutureEvaluation,
    NARRATIVE_IMPORTANCE_WEIGHTS,
    NarrativeImportanceAssessment,
    NarrativeImportanceBreakdown,
    ObjectiveWorldState,
    SubjectiveWorldModel,
)


class NarrativeImportanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = run_pipeline("校园监控", steps=1, export=False)
        cls.old_state = ObjectiveWorldState.model_validate(
            cls.output["objective_states"][0]
        )
        cls.models = [
            SubjectiveWorldModel.model_validate(item)
            for item in cls.output["subjective_models"]
        ]
        cls.futures = {
            item["future_id"].rsplit("_", maxsplit=1)[-1]:
            CandidateFuture.model_validate(item)
            for item in cls.output["candidate_futures"]
        }
        cls.evaluations = {
            item["future_id"].rsplit("_", maxsplit=1)[-1]:
            FutureEvaluation.model_validate(item)
            for item in cls.output["future_evaluations"]
        }
        cls.engine = NarrativeImportance()
        cls.assessments = {
            suffix: cls._assess_branch(suffix)
            for suffix in cls.futures
        }

    @classmethod
    def _assess_branch(cls, suffix: str) -> NarrativeImportanceAssessment:
        future = cls.futures[suffix]
        new_state = WorldTransition().apply(cls.old_state, future)
        event = new_state.events[len(cls.old_state.events)]
        return cls.engine.assess(
            cls.old_state,
            new_state,
            event,
            future,
            cls.models,
            cls.evaluations[suffix],
        )

    def test_pipeline_closes_world_event_assessment_and_narrative_event(self):
        assessment = NarrativeImportanceAssessment.model_validate(
            self.output["narrative_importance_assessments"][0]
        )
        narrative = self.output["narrative_events"][0]
        event = self.output["world_events"][0]

        self.assertEqual(assessment.source_event_id, event["event_id"])
        self.assertEqual(assessment.action_ids, event["action_ids"])
        self.assertEqual(assessment.decision_ids, event["decision_ids"])
        self.assertEqual(assessment.provenance_ids, event["provenance_ids"])
        self.assertEqual(
            narrative["importance_assessment_id"],
            assessment.assessment_id,
        )
        self.assertEqual(narrative["source_event_id"], event["event_id"])
        self.assertEqual(
            narrative["narrative_importance"],
            assessment.score_breakdown.weighted_score,
        )

    def test_weighted_score_uses_all_documented_dimensions(self):
        breakdown = self.assessments["secret"].score_breakdown
        expected = round(
            sum(
                getattr(breakdown, field) * weight
                for field, weight in NARRATIVE_IMPORTANCE_WEIGHTS.items()
            ),
            3,
        )
        self.assertEqual(breakdown.weighted_score, expected)
        self.assertEqual(
            set(self.assessments["secret"].dimension_rationales),
            set(NARRATIVE_IMPORTANCE_WEIGHTS),
        )

    def test_mechanically_distinct_events_activate_distinct_dimensions(self):
        secret = self.assessments["secret"].score_breakdown
        roommate = self.assessments["roommate"].score_breakdown
        confront = self.assessments["confront"].score_breakdown
        ignore = self.assessments["ignore"].score_breakdown

        self.assertGreater(secret.information_gain, ignore.information_gain)
        self.assertGreater(roommate.relationship_change, ignore.relationship_change)
        self.assertGreater(confront.conflict_change, ignore.conflict_change)
        self.assertGreater(confront.irreversibility, ignore.irreversibility)
        self.assertGreater(secret.visual_potential, ignore.visual_potential)

    def test_score_does_not_depend_on_dramatic_keywords(self):
        future = self.futures["secret"]
        rewritten = future.model_copy(
            update={
                "future_id": "future_plain_identifier",
                "summary": "A neutral description of the same structured change.",
            },
            deep=True,
        )
        self.assertEqual(
            self.engine.score(future),
            self.engine.score(rewritten),
        )

    def test_rank_is_descending_and_deterministic(self):
        values = list(self.assessments.values())
        first = self.engine.rank(values)
        second = self.engine.rank(list(reversed(values)))
        self.assertEqual(
            [item.source_event_id for item in first],
            [item.source_event_id for item in second],
        )
        scores = [item.score_breakdown.weighted_score for item in first]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_assessment_rejects_mismatched_world_event(self):
        future = self.futures["secret"]
        new_state = WorldTransition().apply(self.old_state, future)
        event = new_state.events[len(self.old_state.events)].model_copy(
            update={"effect_paths": ["agents.lin_xia.status"]},
            deep=True,
        )
        with self.assertRaisesRegex(ValueError, "effects do not match"):
            self.engine.assess(
                self.old_state,
                new_state,
                event,
                future,
                self.models,
            )

    def test_schema_rejects_an_incorrect_weighted_score(self):
        with self.assertRaises(ValidationError):
            NarrativeImportanceBreakdown(
                conflict_change=0.5,
                information_gain=0.5,
                character_decision=0.5,
                relationship_change=0.5,
                irreversibility=0.5,
                theme_relevance=0.5,
                visual_potential=0.5,
                weighted_score=0.9,
            )


if __name__ == "__main__":
    unittest.main()
