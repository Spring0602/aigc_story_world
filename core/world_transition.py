from copy import deepcopy
from typing import Any

from pydantic import BaseModel

from schemas import Action, CandidateFuture, Decision, Event, ObjectiveWorldState, StateProvenance


class WorldTransition:
    def apply(
        self,
        state: ObjectiveWorldState,
        future: CandidateFuture,
        actions: list[Action] | None = None,
        decisions: list[Decision] | None = None,
    ) -> ObjectiveWorldState:
        next_state = state.model_copy(deep=True)
        next_state.step = state.step + 1
        next_state.state_id = f"state_{next_state.step:03d}"
        next_state.timestamp = f"day_1_step_{next_state.step:02d}"

        actions = actions or []
        decisions = decisions or []
        action_ids = (
            [action.action_id for action in actions]
            if actions
            else [f"{action.agent_id}:{action.action}" for action in future.agent_actions]
        )
        source_observation_ids = sorted(
            {item for decision in decisions for item in decision.source_observation_ids}
        )
        for index, change in enumerate(future.expected_state_changes, start=1):
            self._set_path(next_state, change.path, change.new_value)
            next_state.history.append(
                StateProvenance(
                    provenance_id=f"prov_{next_state.step:03d}_{index:03d}",
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
                    action_ids=action_ids,
                    supporting_hypothesis_ids=future.supporting_hypotheses,
                    source_observation_ids=source_observation_ids,
                )
            )

        next_state.events.append(
            Event(
                event_id=f"event_{next_state.step:03d}_{future.future_id}",
                event_type="agent_action_outcome",
                timestamp=next_state.timestamp,
                description=future.summary,
                participant_ids=sorted(
                    {action.agent_id for action in actions}
                    or {action.agent_id for action in future.agent_actions}
                ),
                cause_ids=[decision.decision_id for decision in decisions],
                effect_paths=[change.path for change in future.expected_state_changes],
                decision_ids=[decision.decision_id for decision in decisions],
                action_ids=action_ids,
                source_belief_ids=sorted(
                    {item for decision in decisions for item in decision.supporting_belief_ids}
                ),
                source_observation_ids=source_observation_ids,
            )
        )
        return next_state

    def _set_path(self, state: ObjectiveWorldState, path: str, value: Any) -> None:
        target = state.__dict__
        parts = path.split(".")
        for part in parts[:-1]:
            target = target[part] if isinstance(target, dict) else getattr(target, part)

        if isinstance(target, dict):
            target[parts[-1]] = deepcopy(value)
        elif isinstance(target, BaseModel):
            setattr(target, parts[-1], deepcopy(value))
        else:
            raise TypeError(f"Cannot set path on unsupported target: {type(target)!r}")
