from lenses.base import WorldLens
from schemas import (
    CausalHypothesis,
    EconomicContext,
    ObjectiveWorldState,
    PsychologyContext,
    SocialContext,
    SubjectiveWorldModel,
)


class SocialStructureLens(WorldLens):
    name = "social_structure"

    def analyze(
        self,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
        psychology: PsychologyContext | None = None,
        economics: EconomicContext | None = None,
        social: SocialContext | None = None,
    ) -> list[CausalHypothesis]:
        step = objective_state.step + 1
        if social is None:
            return [self._fallback_hypothesis(step)]

        roles = {item.agent_id: item for item in social.role_assessments}
        norms_by_agent = {}
        for item in social.norm_pressures:
            norms_by_agent.setdefault(item.agent_id, []).append(item)
        powers_by_agent = {}
        for item in social.institution_powers:
            powers_by_agent.setdefault(item.agent_id, []).append(item)

        hypotheses = []
        for model in subjective_models:
            agent_id = model.agent_id
            role = roles.get(agent_id)
            norms = norms_by_agent.get(agent_id, [])
            powers = powers_by_agent.get(agent_id, [])
            if role is None or not norms or not powers:
                continue
            pressure = sum(
                item.compliance_pressure for item in norms
            ) / len(norms)
            asymmetry = sum(
                item.power_asymmetry for item in powers
            ) / len(powers)
            prefers_compliance = model.epistemology.trust_authority >= 0.6
            hypotheses.append(
                CausalHypothesis(
                    hypothesis_id=f"hyp_soc_{step:03d}_{agent_id}",
                    lens=self.name,
                    claim=(
                        "角色规范与制度权力共同提高公开对抗成本，"
                        "但同伴角色仍为低可见度调查提供社会支持。"
                        if not prefers_compliance
                        else
                        "角色规范、制裁预期与制度权威共同强化遵从，"
                        "使延迟行动比公开对抗更符合社会位置。"
                    ),
                    drivers=[
                        f"institutional_power:{self._band(asymmetry)}",
                        f"norm_pressure:{self._band(pressure)}",
                    ],
                    mediators=[
                        f"role_constraint:{self._band(role.role_constraint)}",
                        (
                            "peer_support"
                            if not prefers_compliance
                            else "authority_deference"
                        ),
                    ],
                    constraints=[
                        f"role:{'+'.join(role.roles) or 'unspecified'}"
                    ],
                    promotes_actions=(
                        [
                            "secretly_collect_network_evidence",
                            "ask_roommate_for_help",
                        ]
                        if not prefers_compliance
                        else ["delay_action"]
                    ),
                    inhibits_actions=["confront_authority"],
                    affected_agents=[agent_id],
                    supporting_role_assessment_ids=[
                        role.role_assessment_id
                    ],
                    supporting_norm_pressure_ids=[
                        item.norm_pressure_id for item in norms
                    ],
                    supporting_institution_power_ids=[
                        item.institution_power_id for item in powers
                    ],
                    time_scale="days",
                    confidence=min(
                        0.95,
                        0.4 + (pressure * 0.25) + (asymmetry * 0.3),
                    ),
                )
            )
        return hypotheses

    def _fallback_hypothesis(self, step: int) -> CausalHypothesis:
        return CausalHypothesis(
            hypothesis_id=f"hyp_soc_{step:03d}",
            lens=self.name,
            claim="角色约束、规范压力与制度权力不对称会抑制直接对抗。",
            drivers=["authority_asymmetry", "institutional_opacity"],
            mediators=["role_constraint", "fear_of_sanction"],
            constraints=["unclear_policy_boundary"],
            promotes_actions=["delay_action"],
            inhibits_actions=["confront_authority"],
            affected_agents=["lin_xia", "wang_chen"],
            time_scale="days",
            confidence=0.69,
        )

    def _band(self, value: float) -> str:
        if value < 0.35:
            return "low"
        if value < 0.7:
            return "moderate"
        return "high"
