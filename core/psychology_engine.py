from schemas import (
    BeliefState,
    EmotionalAppraisal,
    Interpretation,
    MotivationState,
    ObjectiveWorldState,
    Observation,
    Perception,
    PsychologyContext,
    StressState,
    SubjectiveWorldModel,
)


class PsychologyEngine:
    def perceive(
        self,
        objective_state: ObjectiveWorldState,
        observations: list[Observation],
        subjective_models: list[SubjectiveWorldModel],
    ) -> list[Perception]:
        observations_by_agent: dict[str, list[Observation]] = {}
        for observation in observations:
            observations_by_agent.setdefault(observation.agent_id, []).append(observation)

        perceptions = []
        for model in subjective_models:
            visible_events = [
                event
                for event in objective_state.events
                if self._event_is_visible(event, model.agent_id)
            ]
            if not visible_events:
                continue
            event = visible_events[-1]
            agent_observations = observations_by_agent.get(model.agent_id, [])
            observed_content = " ".join(item.content for item in agent_observations)
            perceived_content = f"{event.description} {observed_content}".strip()
            freedom = self._value_weight(model, "freedom")
            safety = self._value_weight(model, "safety")
            authority_distrust = 1.0 - model.epistemology.trust_authority
            monitoring_signal = 1.0 if any(
                token in perceived_content for token in ("监控", "检测", "重定向")
            ) else 0.3
            threat = self._clamp(
                (freedom * authority_distrust * monitoring_signal * 0.75)
                + (model.emotion.fear * 0.25)
            )
            controllability = self._clamp(
                (model.epistemology.trust_data * 0.45)
                + (model.epistemology.tolerance_for_uncertainty * 0.35)
                + (0.2 if agent_observations else 0.0)
            )
            reliability = (
                sum(item.reliability for item in agent_observations) / len(agent_observations)
                if agent_observations
                else 0.5
            )
            ambiguity = self._clamp(
                ((1.0 - reliability) * 0.55) + (authority_distrust * 0.45)
            )
            goal_relevance = self._clamp(
                0.45
                + (0.25 if model.goals else 0.0)
                + (0.2 * max(freedom, safety))
            )
            salience = self._clamp(
                (goal_relevance * 0.35)
                + (threat * 0.35)
                + (ambiguity * 0.15)
                + ((1.0 - controllability) * 0.15)
            )
            perceptions.append(
                Perception(
                    perception_id=f"perception_{objective_state.step:03d}_{model.agent_id}",
                    agent_id=model.agent_id,
                    step=objective_state.step,
                    source_event_id=event.event_id,
                    observation_ids=[
                        item.observation_id for item in agent_observations
                    ],
                    perceived_content=perceived_content,
                    goal_relevance=goal_relevance,
                    threat=threat,
                    controllability=controllability,
                    ambiguity=ambiguity,
                    salience=salience,
                )
            )
        return perceptions

    def appraise(
        self,
        perceptions: list[Perception],
        subjective_models: list[SubjectiveWorldModel],
        belief_states: list[BeliefState],
        interpretations: list[Interpretation],
    ) -> PsychologyContext:
        models = {model.agent_id: model for model in subjective_models}
        latest_beliefs = {item.agent_id: item for item in belief_states}
        latest_interpretations = {item.agent_id: item for item in interpretations}
        emotional_appraisals = []
        stress_states = []
        motivation_states = []

        for perception in perceptions:
            agent_id = perception.agent_id
            model = models.get(agent_id)
            belief_state = latest_beliefs.get(agent_id)
            interpretation = latest_interpretations.get(agent_id)
            if model is None or belief_state is None or interpretation is None:
                continue

            emotion = interpretation.emotional_response.model_copy(deep=True)
            emotion_values = emotion.model_dump()
            dominant_emotion = max(emotion_values, key=emotion_values.get)
            emotion_intensity = emotion_values[dominant_emotion]
            emotional_appraisal = EmotionalAppraisal(
                emotional_appraisal_id=f"emotion_{perception.step:03d}_{agent_id}",
                agent_id=agent_id,
                step=perception.step,
                perception_id=perception.perception_id,
                belief_state_id=belief_state.belief_state_id,
                belief_ids=belief_state.belief_ids,
                interpretation_id=interpretation.interpretation_id,
                emotion=emotion,
                dominant_emotion=dominant_emotion,
                intensity=emotion_intensity,
            )
            emotional_appraisals.append(emotional_appraisal)

            stressors = []
            if perception.threat >= 0.5:
                stressors.append("perceived_threat")
            if perception.ambiguity >= 0.5:
                stressors.append("ambiguity")
            if perception.controllability < 0.5:
                stressors.append("low_control")
            if emotion.fear >= 0.5:
                stressors.append("fear_arousal")
            if not stressors:
                stressors.append("low_activation")
            coping_capacity = self._clamp(
                (perception.controllability * 0.6)
                + (model.epistemology.tolerance_for_uncertainty * 0.4)
            )
            stress_level = self._clamp(
                (emotion.fear * 0.35)
                + (emotion.anger * 0.2)
                + (perception.threat * 0.25)
                + (perception.ambiguity * 0.15)
                + ((1.0 - coping_capacity) * 0.05)
            )
            stress_state = StressState(
                stress_state_id=f"stress_{perception.step:03d}_{agent_id}",
                agent_id=agent_id,
                step=perception.step,
                emotional_appraisal_id=emotional_appraisal.emotional_appraisal_id,
                perception_id=perception.perception_id,
                stressors=stressors,
                level=stress_level,
                band=self._stress_band(stress_level),
                coping_capacity=coping_capacity,
            )
            stress_states.append(stress_state)

            motive, target, preferred_action = self._motivation_for(interpretation)
            relevant_value = {
                "verify_threat": max(
                    self._value_weight(model, "truth"),
                    self._value_weight(model, "freedom"),
                ),
                "preserve_stability": max(
                    self._value_weight(model, "safety"),
                    self._value_weight(model, "order"),
                ),
                "reduce_uncertainty": self._value_weight(model, "truth"),
            }[motive]
            motivation_intensity = self._clamp(
                (emotion_intensity * 0.3)
                + (stress_level * 0.3)
                + (relevant_value * 0.4)
            )
            motivation_states.append(
                MotivationState(
                    motivation_state_id=f"motivation_{perception.step:03d}_{agent_id}",
                    agent_id=agent_id,
                    step=perception.step,
                    stress_state_id=stress_state.stress_state_id,
                    emotional_appraisal_id=emotional_appraisal.emotional_appraisal_id,
                    belief_state_id=belief_state.belief_state_id,
                    motive=motive,
                    target=target,
                    orientation=self._orientation_for(motive, emotion.fear, emotion.curiosity),
                    intensity=motivation_intensity,
                    supporting_goals=model.goals,
                    preferred_action=preferred_action,
                )
            )

        return PsychologyContext(
            perceptions=perceptions,
            emotional_appraisals=emotional_appraisals,
            stress_states=stress_states,
            motivation_states=motivation_states,
        )

    def _event_is_visible(self, event, agent_id: str) -> bool:
        if event.visibility == "public":
            return True
        if event.visibility == "hidden":
            return agent_id in event.actor_ids
        if event.visibility == "private":
            return (
                agent_id in event.allowed_agent_ids
                or agent_id in event.participant_ids
                or agent_id in event.actor_ids
            )
        return agent_id in event.participant_ids or agent_id in event.actor_ids

    def _motivation_for(
        self,
        interpretation: Interpretation,
    ) -> tuple[str, str, str]:
        if interpretation.meaning == "institution threatens autonomy":
            return (
                "verify_threat",
                "verify whether monitoring reaches individual behavior",
                "secretly_collect_network_evidence",
            )
        if interpretation.meaning == "institution protects collective security":
            return (
                "preserve_stability",
                "maintain safety and institutional order",
                "delay_action",
            )
        return (
            "reduce_uncertainty",
            "obtain evidence before committing to a causal explanation",
            "ask_roommate_for_help",
        )

    def _orientation_for(
        self,
        motive: str,
        fear: float,
        curiosity: float,
    ) -> str:
        if motive == "preserve_stability":
            return "avoidance"
        if motive == "reduce_uncertainty":
            return "mixed"
        return "approach" if curiosity >= fear else "mixed"

    def _stress_band(self, level: float) -> str:
        if level < 0.35:
            return "low"
        if level < 0.7:
            return "moderate"
        return "high"

    def _value_weight(self, model: SubjectiveWorldModel, name: str) -> float:
        value = model.values.get(name)
        return value.base_weight if value else 0.5

    def _clamp(self, value: float) -> float:
        return min(1.0, max(0.0, value))
