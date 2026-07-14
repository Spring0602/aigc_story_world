from lenses.base import WorldLens
from schemas import CausalHypothesis, ObjectiveWorldState, SubjectiveWorldModel


class SocialStructureLens(WorldLens):
    name = "social_structure"

    def analyze(
        self,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
    ) -> list[CausalHypothesis]:
        step = objective_state.step + 1
        return [
            CausalHypothesis(
                hypothesis_id=f"hyp_soc_{step:03d}",
                lens=self.name,
                claim="学生与学校网络中心之间的权力不对称会抑制直接对抗，并推动非正式调查。",
                drivers=["authority_asymmetry", "institutional_opacity"],
                mediators=["role_constraint", "fear_of_sanction"],
                constraints=["student_status", "unclear_policy_boundary"],
                affected_agents=["lin_xia"],
                time_scale="days",
                confidence=0.69,
            )
        ]
