from lenses.base import WorldLens
from schemas import CausalHypothesis, ObjectiveWorldState, SubjectiveWorldModel


class EconomicLens(WorldLens):
    name = "economic"

    def analyze(
        self,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
    ) -> list[CausalHypothesis]:
        step = objective_state.step + 1
        return [
            CausalHypothesis(
                hypothesis_id=f"hyp_eco_{step:03d}",
                lens=self.name,
                claim="公开质疑权威的成本较高，会提高低成本秘密取证的相对吸引力。",
                drivers=["information_asymmetry", "high_public_confrontation_cost"],
                mediators=["opportunity_cost", "resource_dependence"],
                constraints=["limited_access_to_network_logs"],
                affected_agents=["lin_xia", "wang_chen"],
                time_scale="hours",
                confidence=0.64,
            )
        ]
