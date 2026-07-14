from lenses.base import WorldLens
from schemas import CausalHypothesis, ObjectiveWorldState, SubjectiveWorldModel


class PsychologyLens(WorldLens):
    name = "psychology"

    def analyze(
        self,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
    ) -> list[CausalHypothesis]:
        step = objective_state.step + 1
        return [
            CausalHypothesis(
                hypothesis_id=f"hyp_psy_{step:03d}",
                lens=self.name,
                claim="不透明威胁会提高高好奇心主体的警觉与验证动机。",
                drivers=["unclear_monitoring_scope", "private_dns_redirect"],
                mediators=["curiosity", "fear", "need_for_control"],
                constraints=["risk_of_punishment", "limited_evidence"],
                affected_agents=["lin_xia"],
                time_scale="hours",
                confidence=0.72,
            )
        ]
