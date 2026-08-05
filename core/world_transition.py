from copy import deepcopy
from typing import Any

from pydantic import BaseModel

from schemas import (
    Action,
    AgentActionDecision,
    CandidateFuture,
    Decision,
    Event,
    FutureEvaluation,
    ObjectiveWorldState,
    StateProvenance,
    ValueAssessment,
)


class TransitionValidationError(ValueError):
    """Raised before a candidate transition can mutate a world snapshot."""


class WorldTransition:
    PROTECTED_ROOTS = {"state_id", "step", "timestamp", "events", "history"}

    def apply(
        self,
        state: ObjectiveWorldState,
        future: CandidateFuture,
        actions: list[Action] | None = None,
        decisions: list[Decision] | None = None,
        action_decisions: list[AgentActionDecision] | None = None,
        value_assessments: list[ValueAssessment] | None = None,
        future_evaluation: FutureEvaluation | None = None,
    ) -> ObjectiveWorldState:
        actions = actions or []
        decisions = decisions or []
        action_decisions = action_decisions or []
        value_assessments = value_assessments or []
        self._validate(
            state,
            future,
            actions,
            decisions,
            action_decisions,
            value_assessments,
            future_evaluation,
        )

        next_state = state.model_copy(deep=True)
        next_state.step = state.step + 1
        next_state.state_id = f"state_{next_state.step:03d}"
        next_state.timestamp = f"day_1_step_{next_state.step:02d}"
        event_id = f"event_{next_state.step:03d}_{future.future_id}"
        provenance_ids = [
            f"prov_{next_state.step:03d}_{index:03d}"
            for index in range(1, len(future.expected_state_changes) + 1)
        ]
        action_ids = self._action_ids(future, actions)
        decision_ids = [item.decision_id for item in decisions]
        source_observation_ids = self._collect(decisions, "source_observation_ids")
        other_model_ids = self._collect(decisions, "other_model_ids")
        supporting_belief_ids = self._collect(decisions, "supporting_belief_ids")
        source_action_decisions = self._source_action_decisions(
            future,
            action_decisions,
        )
        selected_value_ids = {
            item.value_assessment_id for item in decisions
        }
        selected_value_assessments = [
            item
            for item in value_assessments
            if item.value_assessment_id in selected_value_ids
        ]
        relation_ids = self._evaluation_relation_ids(future_evaluation)

        for index, change in enumerate(future.expected_state_changes):
            self._set_path(next_state, change.path, change.new_value)
            next_state.history.append(
                StateProvenance(
                    provenance_id=provenance_ids[index],
                    step=next_state.step,
                    timestamp=next_state.timestamp,
                    source="world_transition",
                    source_state_id=state.state_id,
                    target_state_id=next_state.state_id,
                    path=change.path,
                    old_value=change.old_value,
                    new_value=change.new_value,
                    cause=change.reason,
                    future_id=future.future_id,
                    future_evaluation_id=(
                        future_evaluation.evaluation_id
                        if future_evaluation
                        else None
                    ),
                    event_id=event_id,
                    action_ids=action_ids,
                    decision_ids=decision_ids,
                    agent_action_decision_ids=[
                        item.action_decision_id for item in source_action_decisions
                    ],
                    value_assessment_ids=[
                        item.value_assessment_id
                        for item in selected_value_assessments
                    ],
                    supporting_hypothesis_ids=future.supporting_hypotheses,
                    opposing_hypothesis_ids=future.opposing_hypotheses,
                    hypothesis_relation_ids=relation_ids,
                    supporting_lens_names=(
                        future.mechanism.lens_names if future.mechanism else []
                    ),
                    mechanism_id=(
                        future.mechanism.mechanism_id
                        if future.mechanism
                        else None
                    ),
                    source_observation_ids=source_observation_ids,
                    supporting_belief_ids=supporting_belief_ids,
                    supporting_goals=self._collect(
                        source_action_decisions,
                        "supporting_goals",
                    ),
                    emotional_appraisal_ids=self._optional_ids(
                        decisions,
                        "emotional_appraisal_id",
                    ),
                    motivation_state_ids=self._optional_ids(
                        decisions,
                        "motivation_state_id",
                    ),
                    constraint_ids=self._collect(
                        source_action_decisions,
                        "constraint_ids",
                    ),
                    supporting_other_model_ids=other_model_ids,
                    source_possible_world_ids=future.source_possible_world_ids,
                    source_belief_distribution_ids=(
                        future.source_belief_distribution_ids
                    ),
                )
            )

        effective_actions = actions or future.agent_actions
        event_visibility = (
            "hidden"
            if any("secretly" in item.action for item in effective_actions)
            else "public"
        )
        actor_ids = sorted({item.agent_id for item in effective_actions})
        next_state.events.append(
            Event(
                event_id=event_id,
                event_type="agent_action_outcome",
                timestamp=next_state.timestamp,
                description=future.summary,
                visibility=event_visibility,
                participant_ids=actor_ids,
                actor_ids=actor_ids,
                cause_ids=decision_ids,
                effect_paths=[
                    change.path for change in future.expected_state_changes
                ],
                decision_ids=decision_ids,
                action_ids=action_ids,
                source_belief_ids=supporting_belief_ids,
                source_observation_ids=source_observation_ids,
                source_other_model_ids=other_model_ids,
                provenance_ids=provenance_ids,
            )
        )
        return ObjectiveWorldState.model_validate(next_state.model_dump(mode="python"))

    def _validate(
        self,
        state: ObjectiveWorldState,
        future: CandidateFuture,
        actions: list[Action],
        decisions: list[Decision],
        action_decisions: list[AgentActionDecision],
        value_assessments: list[ValueAssessment],
        future_evaluation: FutureEvaluation | None,
    ) -> None:
        if future.source_state_id != state.state_id:
            raise TransitionValidationError(
                "candidate future source_state_id does not match current state"
            )
        if not future.expected_state_changes:
            raise TransitionValidationError(
                "candidate future must contain at least one StateChange"
            )
        paths = [item.path for item in future.expected_state_changes]
        if len(paths) != len(set(paths)):
            raise TransitionValidationError(
                "candidate future cannot change the same path more than once"
            )
        for change in future.expected_state_changes:
            if change.future_id != future.future_id:
                raise TransitionValidationError(
                    "StateChange future_id does not match candidate future"
                )
            root = change.path.split(".", maxsplit=1)[0]
            if root in self.PROTECTED_ROOTS:
                raise TransitionValidationError(
                    f"StateChange cannot modify protected path {change.path!r}"
                )
            found, current_value = self._read_path(state, change.path)
            if not found:
                raise TransitionValidationError(
                    f"StateChange path does not exist: {change.path!r}"
                )
            if current_value != change.old_value:
                raise TransitionValidationError(
                    f"StateChange old_value is stale for {change.path!r}"
                )
            if current_value == change.new_value:
                raise TransitionValidationError(
                    f"StateChange is a no-op for {change.path!r}"
                )

        self._validate_actions(state, future, actions, decisions)
        self._validate_supporting_artifacts(
            state,
            future,
            decisions,
            action_decisions,
            value_assessments,
            future_evaluation,
        )

    def _validate_actions(
        self,
        state: ObjectiveWorldState,
        future: CandidateFuture,
        actions: list[Action],
        decisions: list[Decision],
    ) -> None:
        next_step = state.step + 1
        decisions_by_id = {item.decision_id: item for item in decisions}
        if len(decisions_by_id) != len(decisions):
            raise TransitionValidationError("duplicate decision_id")
        future_actions = {(item.agent_id, item.action) for item in future.agent_actions}
        for decision in decisions:
            if decision.step != next_step:
                raise TransitionValidationError(
                    "decision step does not match transition target step"
                )
            if (decision.agent_id, decision.selected_action) not in future_actions:
                raise TransitionValidationError(
                    "decision does not implement the selected candidate future"
                )
        for action in actions:
            decision = decisions_by_id.get(action.decision_id)
            if decision is None:
                raise TransitionValidationError(
                    "executed action must reference a supplied decision"
                )
            if action.status != "executed":
                raise TransitionValidationError(
                    "only executed actions can change objective world state"
                )
            if action.step != next_step:
                raise TransitionValidationError(
                    "action step does not match transition target step"
                )
            if (action.agent_id, action.action) != (
                decision.agent_id,
                decision.selected_action,
            ):
                raise TransitionValidationError(
                    "action does not match its source decision"
                )
        if actions and len(actions) != len(decisions):
            raise TransitionValidationError(
                "each supplied decision must have one executed action"
            )

    def _validate_supporting_artifacts(
        self,
        state: ObjectiveWorldState,
        future: CandidateFuture,
        decisions: list[Decision],
        action_decisions: list[AgentActionDecision],
        value_assessments: list[ValueAssessment],
        future_evaluation: FutureEvaluation | None,
    ) -> None:
        action_decisions_by_id = {
            item.action_decision_id: item for item in action_decisions
        }
        values_by_id = {
            item.value_assessment_id: item for item in value_assessments
        }
        for decision in decisions:
            if (
                decision.agent_action_decision_id
                and decision.agent_action_decision_id
                not in future.source_action_decision_ids
            ):
                raise TransitionValidationError(
                    "decision action model provenance does not match future"
                )
            if action_decisions and (
                not decision.agent_action_decision_id
                or decision.agent_action_decision_id not in action_decisions_by_id
            ):
                raise TransitionValidationError(
                    "decision references a missing AgentActionDecision"
                )
            if value_assessments and decision.value_assessment_id not in values_by_id:
                raise TransitionValidationError(
                    "decision references a missing ValueAssessment"
                )
        if future_evaluation is not None:
            if future_evaluation.future_id != future.future_id:
                raise TransitionValidationError(
                    "FutureEvaluation does not reference the selected future"
                )
            if future_evaluation.evaluated_state_id != state.state_id:
                raise TransitionValidationError(
                    "FutureEvaluation was computed against a different state"
                )

    def _read_path(
        self,
        state: ObjectiveWorldState,
        path: str,
    ) -> tuple[bool, Any]:
        current: Any = state
        for part in path.split("."):
            if isinstance(current, BaseModel):
                if not hasattr(current, part):
                    return False, None
                current = getattr(current, part)
            elif isinstance(current, dict):
                if part not in current:
                    return False, None
                current = current[part]
            elif isinstance(current, list) and part.isdigit():
                index = int(part)
                if index >= len(current):
                    return False, None
                current = current[index]
            else:
                return False, None
        return True, current

    def _set_path(
        self,
        state: ObjectiveWorldState,
        path: str,
        value: Any,
    ) -> None:
        target: Any = state
        parts = path.split(".")
        for part in parts[:-1]:
            if isinstance(target, BaseModel):
                target = getattr(target, part)
            elif isinstance(target, dict):
                target = target[part]
            elif isinstance(target, list) and part.isdigit():
                target = target[int(part)]
        final = parts[-1]
        if isinstance(target, BaseModel):
            setattr(target, final, deepcopy(value))
        elif isinstance(target, dict):
            target[final] = deepcopy(value)
        elif isinstance(target, list) and final.isdigit():
            target[int(final)] = deepcopy(value)
        else:
            raise TransitionValidationError(
                f"unsupported StateChange target for {path!r}"
            )

    def _action_ids(
        self,
        future: CandidateFuture,
        actions: list[Action],
    ) -> list[str]:
        if actions:
            return [item.action_id for item in actions]
        return [f"{item.agent_id}:{item.action}" for item in future.agent_actions]

    def _source_action_decisions(
        self,
        future: CandidateFuture,
        action_decisions: list[AgentActionDecision],
    ) -> list[AgentActionDecision]:
        source_ids = set(future.source_action_decision_ids)
        return [
            item
            for item in action_decisions
            if item.action_decision_id in source_ids
        ]

    def _evaluation_relation_ids(
        self,
        evaluation: FutureEvaluation | None,
    ) -> list[str]:
        if evaluation is None:
            return []
        return sorted(
            set(
                evaluation.supporting_relation_ids
                + evaluation.contradicting_relation_ids
                + evaluation.conditioning_relation_ids
            )
        )

    def _collect(self, items: list[Any], field: str) -> list[str]:
        return sorted(
            {
                value
                for item in items
                for value in getattr(item, field)
            }
        )

    def _optional_ids(self, items: list[Any], field: str) -> list[str]:
        return sorted(
            {
                value
                for item in items
                if (value := getattr(item, field)) is not None
            }
        )
