import unittest

from pydantic import ValidationError

from app import run_pipeline
from core.world_transition import TransitionValidationError, WorldTransition
from schemas import (
    Action,
    CandidateFuture,
    Decision,
    FutureEvaluation,
    ObjectiveWorldState,
    StateProvenance,
)


class WorldTransitionProvenanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_pipeline("校园监控", steps=1, export=False)
        cls.state = ObjectiveWorldState.model_validate(
            cls.result["objective_states"][0]
        )
        cls.future = next(
            CandidateFuture.model_validate(item)
            for item in cls.result["candidate_futures"]
            if item["future_id"] == cls.result["selected_futures"][0]["future_id"]
        )
        cls.decision = Decision.model_validate(cls.result["decisions"][0])
        cls.action = Action.model_validate(cls.result["actions"][0])
        cls.evaluation = next(
            FutureEvaluation.model_validate(item)
            for item in cls.result["future_evaluations"]
            if item["future_id"] == cls.future.future_id
        )

    def test_pipeline_provenance_closes_the_complete_causal_chain(self):
        provenance = StateProvenance.model_validate(
            self.result["state_provenance"][-1]
        )
        event = self.result["world_events"][0]

        self.assertEqual(provenance.source_state_id, "state_000")
        self.assertEqual(provenance.target_state_id, "state_001")
        self.assertEqual(provenance.future_id, self.future.future_id)
        self.assertEqual(
            provenance.future_evaluation_id,
            self.evaluation.evaluation_id,
        )
        self.assertEqual(provenance.action_ids, [self.action.action_id])
        self.assertEqual(provenance.decision_ids, [self.decision.decision_id])
        self.assertEqual(
            provenance.agent_action_decision_ids,
            [self.decision.agent_action_decision_id],
        )
        self.assertEqual(
            provenance.value_assessment_ids,
            [self.decision.value_assessment_id],
        )
        self.assertTrue(provenance.supporting_hypothesis_ids)
        self.assertTrue(provenance.hypothesis_relation_ids)
        self.assertTrue(provenance.supporting_lens_names)
        self.assertTrue(provenance.source_observation_ids)
        self.assertTrue(provenance.supporting_belief_ids)
        self.assertTrue(provenance.supporting_goals)
        self.assertTrue(provenance.emotional_appraisal_ids)
        self.assertTrue(provenance.motivation_state_ids)
        self.assertTrue(provenance.constraint_ids)
        self.assertIn(provenance.provenance_id, event["provenance_ids"])
        self.assertEqual(provenance.event_id, event["event_id"])

    def test_transition_preserves_source_snapshot_and_records_real_values(self):
        source_dump = self.state.model_dump(mode="python")
        next_state = WorldTransition().apply(self.state, self.future)
        change = self.future.expected_state_changes[0]
        provenance = next_state.history[-1]

        self.assertEqual(self.state.model_dump(mode="python"), source_dump)
        self.assertEqual(provenance.old_value, change.old_value)
        self.assertEqual(provenance.new_value, change.new_value)
        self.assertEqual(self._read(next_state, change.path), change.new_value)
        self.assertEqual(self._read(self.state, change.path), change.old_value)

    def test_rejects_stale_source_state_before_applying_changes(self):
        stale = self.future.model_copy(
            update={"source_state_id": "state_stale"},
            deep=True,
        )
        self._assert_rejected_without_mutation(stale, "source_state_id")

    def test_rejects_missing_path_stale_value_noop_and_duplicate_path(self):
        change = self.future.expected_state_changes[0]
        cases = {
            "does not exist": change.model_copy(
                update={"path": "agents.unknown.status"},
                deep=True,
            ),
            "old_value is stale": change.model_copy(
                update={"old_value": "stale"},
                deep=True,
            ),
            "no-op": change.model_copy(
                update={"new_value": change.old_value},
                deep=True,
            ),
        }
        for message, invalid_change in cases.items():
            with self.subTest(message=message):
                future = self.future.model_copy(
                    update={"expected_state_changes": [invalid_change]},
                    deep=True,
                )
                self._assert_rejected_without_mutation(future, message)

        duplicate = self.future.model_copy(
            update={"expected_state_changes": [change, change]},
            deep=True,
        )
        self._assert_rejected_without_mutation(duplicate, "same path")

    def test_rejects_protected_world_metadata_changes(self):
        change = self.future.expected_state_changes[0].model_copy(
            update={
                "path": "state_id",
                "old_value": self.state.state_id,
                "new_value": "state_injected",
            },
            deep=True,
        )
        future = self.future.model_copy(
            update={"expected_state_changes": [change]},
            deep=True,
        )
        self._assert_rejected_without_mutation(future, "protected path")

    def test_rejects_action_that_does_not_match_its_decision(self):
        mismatched = self.action.model_copy(
            update={"action": "confront_authority"},
            deep=True,
        )
        source_dump = self.state.model_dump(mode="python")
        with self.assertRaisesRegex(
            TransitionValidationError,
            "action does not match",
        ):
            WorldTransition().apply(
                self.state,
                self.future,
                actions=[mismatched],
                decisions=[self.decision],
            )
        self.assertEqual(self.state.model_dump(mode="python"), source_dump)

    def test_rejects_evaluation_computed_for_another_world(self):
        stale_evaluation = self.evaluation.model_copy(
            update={"evaluated_state_id": "state_stale"},
            deep=True,
        )
        with self.assertRaisesRegex(
            TransitionValidationError,
            "different state",
        ):
            WorldTransition().apply(
                self.state,
                self.future,
                future_evaluation=stale_evaluation,
            )

    def test_schema_rejects_incomplete_transition_provenance(self):
        with self.assertRaises(ValidationError):
            StateProvenance(
                provenance_id="prov_invalid",
                step=1,
                timestamp="step_1",
                source="world_transition",
                source_state_id="state_000",
                target_state_id="state_001",
                path="agents.lin_xia.status",
                future_id="future_001",
                event_id="event_001",
            )

    def _assert_rejected_without_mutation(
        self,
        future: CandidateFuture,
        message: str,
    ) -> None:
        source_dump = self.state.model_dump(mode="python")
        with self.assertRaisesRegex(TransitionValidationError, message):
            WorldTransition().apply(self.state, future)
        self.assertEqual(self.state.model_dump(mode="python"), source_dump)

    def _read(self, state: ObjectiveWorldState, path: str):
        current = state
        for part in path.split("."):
            current = current[part] if isinstance(current, dict) else getattr(current, part)
        return current


if __name__ == "__main__":
    unittest.main()
