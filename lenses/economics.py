from lenses.base import WorldLens
from schemas import (
    CausalHypothesis,
    EconomicContext,
    ObjectiveWorldState,
    PsychologyContext,
    SocialContext,
    SubjectiveWorldModel,
)


class EconomicLens(WorldLens):
    name = "economic"

    def analyze(
        self,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
        psychology: PsychologyContext | None = None,
        economics: EconomicContext | None = None,
        social: SocialContext | None = None,
    ) -> list[CausalHypothesis]:
        step = objective_state.step + 1
        if economics is None or not economics.scarcity_assessments:
            return [self._fallback_hypothesis(step)]

        models = {model.agent_id: model for model in subjective_models}
        scarcity_by_agent = {}
        for item in economics.scarcity_assessments:
            current = scarcity_by_agent.get(item.agent_id)
            if current is None or item.scarcity_level > current.scarcity_level:
                scarcity_by_agent[item.agent_id] = item
        asymmetry_by_agent = {
            item.agent_id: item for item in economics.information_asymmetries
        }
        hypotheses = []
        for agent_id, scarcity in sorted(scarcity_by_agent.items()):
            model = models[agent_id]
            asymmetry = asymmetry_by_agent[agent_id]
            truth_freedom = (
                self._value_weight(model, "truth")
                + self._value_weight(model, "freedom")
            ) / 2.0
            safety_order = (
                self._value_weight(model, "safety")
                + self._value_weight(model, "order")
            ) / 2.0
            investigation_preferred = truth_freedom >= safety_order
            hypotheses.append(
                CausalHypothesis(
                    hypothesis_id=f"hyp_eco_{step:03d}_{agent_id}",
                    lens=self.name,
                    claim=(
                        "资源访问稀缺与信息不对称提高公开行动成本，"
                        "使低成本秘密取证更具相对吸引力。"
                        if investigation_preferred
                        else
                        "资源依赖与信息不对称提高行动成本，"
                        "使维持稳定和延迟行动更具相对吸引力。"
                    ),
                    drivers=[
                        f"resource_scarcity:{self._band(scarcity.scarcity_level)}",
                        (
                            "information_asymmetry:"
                            f"{self._band(asymmetry.asymmetry_level)}"
                        ),
                    ],
                    mediators=[
                        "relative_action_cost",
                        (
                            "incentive:low_cost_verification"
                            if investigation_preferred
                            else "incentive:stability_preservation"
                        ),
                    ],
                    constraints=[
                        f"access_level:{self._band(scarcity.access_level)}"
                    ],
                    affected_agents=[agent_id],
                    supporting_scarcity_assessment_ids=[
                        scarcity.scarcity_assessment_id
                    ],
                    supporting_information_asymmetry_ids=[
                        asymmetry.information_asymmetry_id
                    ],
                    time_scale="hours",
                    confidence=min(
                        0.95,
                        0.45
                        + (scarcity.scarcity_level * 0.2)
                        + (asymmetry.asymmetry_level * 0.25),
                    ),
                )
            )
        return hypotheses

    def _fallback_hypothesis(self, step: int) -> CausalHypothesis:
        return CausalHypothesis(
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

    def _value_weight(
        self,
        model: SubjectiveWorldModel,
        name: str,
    ) -> float:
        value = model.values.get(name)
        return value.base_weight if value else 0.5

    def _band(self, value: float) -> str:
        if value < 0.35:
            return "low"
        if value < 0.7:
            return "moderate"
        return "high"
