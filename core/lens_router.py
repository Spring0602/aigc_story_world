from lenses.economics import EconomicLens
from lenses.psychology import PsychologyLens
from lenses.social_structure import SocialStructureLens
from schemas import (
    CausalHypothesis,
    ObjectiveWorldState,
    PsychologyContext,
    SubjectiveWorldModel,
)


class LensRouter:
    def __init__(self) -> None:
        self.lenses = [PsychologyLens(), EconomicLens(), SocialStructureLens()]

    def analyze(
        self,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
        psychology: PsychologyContext | None = None,
    ) -> list[CausalHypothesis]:
        hypotheses: list[CausalHypothesis] = []
        for lens in self.lenses:
            hypotheses.extend(
                lens.analyze(objective_state, subjective_models, psychology)
            )
        return hypotheses
