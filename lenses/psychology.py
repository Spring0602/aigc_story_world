from lenses.base import WorldLens
from schemas import (
    CausalHypothesis,
    ObjectiveWorldState,
    PsychologyContext,
    SubjectiveWorldModel,
)


class PsychologyLens(WorldLens):
    name = "psychology"

    def analyze(
        self,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
        psychology: PsychologyContext | None = None,
    ) -> list[CausalHypothesis]:
        step = objective_state.step + 1
        if psychology is None or not psychology.motivation_states:
            return [self._fallback_hypothesis(step)]

        perceptions = {
            item.perception_id: item for item in psychology.perceptions
        }
        emotional_appraisals = {
            item.emotional_appraisal_id: item
            for item in psychology.emotional_appraisals
        }
        stress_states = {
            item.stress_state_id: item for item in psychology.stress_states
        }
        hypotheses = []
        for motivation in psychology.motivation_states:
            stress = stress_states[motivation.stress_state_id]
            emotion = emotional_appraisals[motivation.emotional_appraisal_id]
            perception = perceptions[stress.perception_id]
            threat_band = self._band(perception.threat)
            coping_band = self._band(stress.coping_capacity)
            hypotheses.append(
                CausalHypothesis(
                    hypothesis_id=f"hyp_psy_{step:03d}_{motivation.agent_id}",
                    lens=self.name,
                    claim=self._claim_for(motivation.motive),
                    drivers=[
                        f"world_event:{perception.source_event_id}",
                        f"perceived_threat:{threat_band}",
                    ],
                    mediators=[
                        f"emotion:{emotion.dominant_emotion}",
                        f"motivation:{motivation.motive}",
                    ],
                    constraints=[
                        f"stress_load:{stress.band}",
                        f"coping_capacity:{coping_band}",
                    ],
                    affected_agents=[motivation.agent_id],
                    supporting_event_ids=[perception.source_event_id],
                    supporting_perception_ids=[perception.perception_id],
                    supporting_belief_ids=emotion.belief_ids,
                    supporting_emotional_appraisal_ids=[
                        emotion.emotional_appraisal_id
                    ],
                    supporting_stress_state_ids=[stress.stress_state_id],
                    supporting_motivation_state_ids=[
                        motivation.motivation_state_id
                    ],
                    time_scale="hours",
                    confidence=min(
                        0.95,
                        0.45
                        + (motivation.intensity * 0.3)
                        + (perception.salience * 0.2),
                    ),
                )
            )
        return hypotheses

    def _fallback_hypothesis(self, step: int) -> CausalHypothesis:
        return CausalHypothesis(
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

    def _claim_for(self, motive: str) -> str:
        if motive == "verify_threat":
            return "自主权威胁通过警觉和验证动机，提高主体秘密收集证据的可能性。"
        if motive == "preserve_stability":
            return "安全价值通过稳定动机，降低主体立即对抗制度的可能性。"
        return "高不确定性通过证据寻求动机，促使主体延迟定论并寻找旁证。"

    def _band(self, value: float) -> str:
        if value < 0.35:
            return "low"
        if value < 0.7:
            return "moderate"
        return "high"
