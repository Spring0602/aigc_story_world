from lenses.economics import EconomicLens
from lenses.psychology import PsychologyLens
from lenses.social_structure import SocialStructureLens
from schemas import (
    CausalHypothesis,
    EconomicContext,
    ObjectiveWorldState,
    PsychologyContext,
    SocialContext,
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
        economics: EconomicContext | None = None,
        social: SocialContext | None = None,
    ) -> list[CausalHypothesis]:
        hypotheses: list[CausalHypothesis] = []
        for lens in self.lenses:
            hypotheses.extend(
                lens.analyze(
                    objective_state,
                    subjective_models,
                    psychology,
                    economics,
                    social,
                )
            )
        return hypotheses
