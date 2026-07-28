from abc import ABC, abstractmethod

from schemas import (
    CausalHypothesis,
    EconomicContext,
    ObjectiveWorldState,
    PsychologyContext,
    SubjectiveWorldModel,
)


class WorldLens(ABC):
    name: str

    @abstractmethod
    def analyze(
        self,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
        psychology: PsychologyContext | None = None,
        economics: EconomicContext | None = None,
    ) -> list[CausalHypothesis]:
        raise NotImplementedError
