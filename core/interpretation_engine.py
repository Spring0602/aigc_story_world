from schemas import Belief, EmotionState, Interpretation, Observation, SubjectiveWorldModel


class InterpretationEngine:
    def interpret(
        self,
        observation: Observation,
        model: SubjectiveWorldModel,
        belief: Belief,
        confidence: float,
        interpretation_id: str,
    ) -> Interpretation:
        threatens_autonomy = "监控" in belief.proposition and self._value_weight(model, "freedom") >= 0.7
        trusts_authority = model.epistemology.trust_authority >= 0.7

        if threatens_autonomy:
            causal_frame = "institutional opacity enables surveillance"
            meaning = "institution threatens autonomy"
            action_implication = (
                "collect evidence secretly"
                if model.epistemology.trust_data >= 0.7
                else "seek independent evidence"
            )
        elif trusts_authority:
            causal_frame = "institutional authority frames the change as protection"
            meaning = "institution protects collective security"
            action_implication = "follow institutional guidance"
        else:
            causal_frame = "incomplete evidence leaves institutional intent uncertain"
            meaning = "the situation requires further verification"
            action_implication = "seek additional evidence"

        return Interpretation(
            interpretation_id=interpretation_id,
            agent_id=observation.agent_id,
            observation_ids=[observation.observation_id],
            belief_basis=[belief.proposition],
            causal_frame=causal_frame,
            meaning=meaning,
            emotional_response=self._emotional_response(
                model,
                confidence,
                threatens_autonomy=threatens_autonomy,
                trusts_authority=trusts_authority,
            ),
            action_implication=action_implication,
            confidence=confidence,
        )

    def _emotional_response(
        self,
        model: SubjectiveWorldModel,
        confidence: float,
        *,
        threatens_autonomy: bool,
        trusts_authority: bool,
    ) -> EmotionState:
        emotion = model.emotion.model_copy(deep=True)
        if threatens_autonomy:
            freedom = self._value_weight(model, "freedom")
            emotion.fear = self._clamp(emotion.fear + confidence * 0.15)
            emotion.anger = self._clamp(
                emotion.anger
                + freedom * (1.0 - model.epistemology.trust_authority) * confidence * 0.8
            )
            emotion.curiosity = self._clamp(emotion.curiosity + confidence * 0.08)
        elif trusts_authority:
            safety = self._value_weight(model, "safety")
            emotion.fear = self._clamp(emotion.fear - confidence * 0.1)
            emotion.hope = self._clamp(emotion.hope + safety * confidence * 0.15)
        else:
            uncertainty = 1.0 - model.epistemology.tolerance_for_uncertainty
            emotion.fear = self._clamp(emotion.fear + confidence * uncertainty * 0.08)
            emotion.curiosity = self._clamp(
                emotion.curiosity
                + confidence * model.epistemology.tolerance_for_uncertainty * 0.15
            )
        return emotion

    def _value_weight(self, model: SubjectiveWorldModel, name: str) -> float:
        value = model.values.get(name)
        return value.base_weight if value else 0.5

    def _clamp(self, value: float) -> float:
        return min(1.0, max(0.0, value))
