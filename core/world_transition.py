from copy import deepcopy
from typing import Any

from schemas import CandidateFuture, ObjectiveWorldState


class WorldTransition:
    def apply(self, state: ObjectiveWorldState, future: CandidateFuture) -> ObjectiveWorldState:
        next_state = state.model_copy(deep=True)
        next_state.step = state.step + 1
        next_state.state_id = f"state_{next_state.step:03d}"
        next_state.timestamp = f"day_1_step_{next_state.step:02d}"

        for change in future.expected_state_changes:
            self._set_path(next_state, change.path, change.new_value)
            next_state.history.append(
                {
                    "step": next_state.step,
                    "path": change.path,
                    "old_value": change.old_value,
                    "new_value": change.new_value,
                    "reason": change.reason,
                    "future_id": future.future_id,
                }
            )
        return next_state

    def _set_path(self, state: ObjectiveWorldState, path: str, value: Any) -> None:
        target = state.__dict__
        parts = path.split(".")
        for part in parts[:-1]:
            target = target[part]
        target[parts[-1]] = deepcopy(value)
