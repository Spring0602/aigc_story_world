from abc import ABC, abstractmethod

from schemas import CausalHypothesis, ObjectiveWorldState, SubjectiveWorldModel


class WorldLens(ABC):
    name: str

    @abstractmethod
    def analyze(
        self,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
    ) -> list[CausalHypothesis]:
        raise NotImplementedError
