from core.hypothesis_conflict_resolver import HypothesisConflictResolver
from lenses.economics import EconomicLens
from lenses.psychology import PsychologyLens
from lenses.social_structure import SocialStructureLens
from schemas import (
    CausalHypothesis,
    EconomicContext,
    LensAnalysisResult,
    ObjectiveWorldState,
    PsychologyContext,
    SocialContext,
    SubjectiveWorldModel,
)


class LensRouter:
    def __init__(
        self,
        enabled_lenses: set[str] | None = None,
    ) -> None:
        available = [
            PsychologyLens(),
            EconomicLens(),
            SocialStructureLens(),
        ]
        available_names = {lens.name for lens in available}
        requested = (
            available_names
            if enabled_lenses is None
            else enabled_lenses
        )
        unknown = requested - available_names
        if unknown:
            raise ValueError(
                f"unknown lenses: {', '.join(sorted(unknown))}"
            )
        self.lenses = [
            lens for lens in available if lens.name in requested
        ]
        self.resolver = HypothesisConflictResolver()

    def analyze(
        self,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
        psychology: PsychologyContext | None = None,
        economics: EconomicContext | None = None,
        social: SocialContext | None = None,
    ) -> list[CausalHypothesis]:
        return self.route(
            objective_state,
            subjective_models,
            psychology,
            economics,
            social,
        ).hypotheses

    def route(
        self,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
        psychology: PsychologyContext | None = None,
        economics: EconomicContext | None = None,
        social: SocialContext | None = None,
    ) -> LensAnalysisResult:
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
        relations = self.resolver.resolve(hypotheses)
        return LensAnalysisResult(
            enabled_lenses=[lens.name for lens in self.lenses],
            hypotheses=hypotheses,
            relations=relations,
            unresolved_conflict_ids=[
                item.relation_id
                for item in relations
                if item.resolution_status == "unresolved"
            ],
        )
