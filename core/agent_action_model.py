from schemas import (
    ActionScoreBreakdown,
    AgentActionDecision,
    BeliefAboutOther,
    BeliefState,
    CausalHypothesis,
    EconomicContext,
    InformationBoundary,
    PossibleWorldContext,
    PsychologyContext,
    SocialContext,
    SubjectiveWorldModel,
)


class AgentActionModel:
    ACTIONS = (
        "secretly_collect_network_evidence",
        "ask_roommate_for_help",
        "confront_authority",
        "delay_action",
    )
    WORLD_KIND_BY_ACTION = {
        "secretly_collect_network_evidence": "institutional_monitoring",
        "ask_roommate_for_help": "technical_anomaly",
        "confront_authority": "institutional_monitoring",
        "delay_action": "protective_security",
    }
    VALUES_BY_ACTION = {
        "secretly_collect_network_evidence": ("truth", "freedom"),
        "ask_roommate_for_help": ("truth", "safety"),
        "confront_authority": ("truth", "freedom", "safety"),
        "delay_action": ("safety", "order"),
    }

    def evaluate(
        self,
        subjective_models: list[SubjectiveWorldModel],
        belief_states: list[BeliefState],
        possible_worlds: PossibleWorldContext,
        psychology: PsychologyContext,
        information_boundaries: list[InformationBoundary],
        other_models: list[BeliefAboutOther],
        hypotheses: list[CausalHypothesis],
        step: int,
        economics: EconomicContext | None = None,
        social: SocialContext | None = None,
    ) -> list[AgentActionDecision]:
        actor = self._select_actor(subjective_models)
        belief_state = max(
            (
                item
                for item in belief_states
                if item.agent_id == actor.agent_id
            ),
            key=lambda item: (item.step, len(item.belief_ids), item.belief_state_id),
        )
        boundary = next(
            item
            for item in information_boundaries
            if item.agent_id == actor.agent_id
        )
        world_belief = next(
            item
            for item in possible_worlds.new_beliefs
            if item.agent_id == actor.agent_id
        )
        distribution = next(
            item
            for item in possible_worlds.posterior_distributions
            if item.agent_id == actor.agent_id
        )
        worlds_by_kind = {
            item.kind: item
            for item in possible_worlds.possible_worlds
            if item.agent_id == actor.agent_id
        }
        appraisal = next(
            (
                item
                for item in psychology.emotional_appraisals
                if item.agent_id == actor.agent_id
            ),
            None,
        )
        motivation = next(
            (
                item
                for item in psychology.motivation_states
                if item.agent_id == actor.agent_id
            ),
            None,
        )
        stress = next(
            (
                item
                for item in psychology.stress_states
                if item.agent_id == actor.agent_id
            ),
            None,
        )
        actor_other_models = [
            item
            for item in other_models
            if item.observer_agent_id == actor.agent_id
        ]
        threshold = self._satisficing_threshold(
            belief_state.uncertainty,
            stress.level if stress else 0.0,
            boundary.coverage,
        )

        provisional = []
        for action in self.ACTIONS:
            supporting = self._matching_hypotheses(
                hypotheses, actor.agent_id, action, promoted=True
            )
            opposing = self._matching_hypotheses(
                hypotheses, actor.agent_id, action, promoted=False
            )
            world = worlds_by_kind[self.WORLD_KIND_BY_ACTION[action]]
            possible_world_score = distribution.probabilities[
                world.possible_world_id
            ]
            belief_score = self._belief_score(actor, belief_state)
            goal_score, supporting_goals = self._goal_score(
                actor,
                action,
                motivation,
            )
            value_score, supporting_values = self._value_score(actor, action)
            emotion_score = self._emotion_score(actor, action, appraisal)
            motivation_score = self._motivation_score(action, motivation)
            other_score = self._other_model_score(action, actor_other_models)
            constraint_score, constraint_ids = self._constraint_score(
                actor.agent_id,
                action,
                opposing,
                economics,
                social,
            )
            weighted_score = self._clamp(
                (belief_score * 0.20)
                + (possible_world_score * 0.10)
                + (goal_score * 0.12)
                + (value_score * 0.15)
                + (emotion_score * 0.12)
                + (motivation_score * 0.14)
                + (other_score * 0.07)
                + (constraint_score * 0.10)
            )
            breakdown = ActionScoreBreakdown(
                belief_compatibility=belief_score,
                possible_world_compatibility=possible_world_score,
                goal_compatibility=goal_score,
                value_compatibility=value_score,
                emotional_compatibility=emotion_score,
                motivation_compatibility=motivation_score,
                other_model_compatibility=other_score,
                constraint_satisfaction=constraint_score,
                weighted_score=weighted_score,
            )
            provisional.append(
                AgentActionDecision(
                    action_decision_id=(
                        f"action_decision_{step:03d}_{actor.agent_id}_"
                        f"{self._action_suffix(action)}"
                    ),
                    agent_id=actor.agent_id,
                    step=step,
                    action=action,
                    information_boundary_id=boundary.information_boundary_id,
                    information_coverage=boundary.coverage,
                    belief_state_id=belief_state.belief_state_id,
                    dominant_possible_world_belief_id=world_belief.belief_id,
                    evaluated_possible_world_id=world.possible_world_id,
                    belief_distribution_id=distribution.distribution_id,
                    emotional_appraisal_id=(
                        appraisal.emotional_appraisal_id if appraisal else None
                    ),
                    motivation_state_id=(
                        motivation.motivation_state_id if motivation else None
                    ),
                    supporting_observation_ids=boundary.observation_ids,
                    supporting_belief_ids=belief_state.belief_ids,
                    supporting_goals=supporting_goals,
                    supporting_values=supporting_values,
                    other_model_ids=[
                        item.other_model_id for item in actor_other_models
                    ],
                    constraint_ids=constraint_ids,
                    supporting_hypothesis_ids=[
                        item.hypothesis_id for item in supporting
                    ],
                    opposing_hypothesis_ids=[
                        item.hypothesis_id for item in opposing
                    ],
                    score_breakdown=breakdown,
                    satisficing_threshold=threshold,
                    consideration_rank=1,
                    is_satisficing=weighted_score >= threshold,
                    rationale=self._rationale(action, breakdown, threshold),
                )
            )

        ranked = sorted(
            provisional,
            key=lambda item: item.score_breakdown.weighted_score,
            reverse=True,
        )
        return [
            item.model_copy(
                update={
                    "consideration_rank": rank,
                    "is_preferred": rank == 1,
                },
                deep=True,
            )
            for rank, item in enumerate(ranked, start=1)
        ]

    def _select_actor(
        self,
        models: list[SubjectiveWorldModel],
    ) -> SubjectiveWorldModel:
        if not models:
            raise ValueError("agent action model requires a subjective model")
        return max(
            models,
            key=lambda item: (
                self._value_weight(item, "truth")
                + self._value_weight(item, "freedom")
                + item.epistemology.trust_data
                - item.epistemology.trust_authority
            ),
        )

    def _belief_score(
        self,
        model: SubjectiveWorldModel,
        belief_state: BeliefState,
    ) -> float:
        beliefs = {
            item.belief_id: item for item in [*model.beliefs, *model.false_beliefs]
        }
        confidences = [
            beliefs[item].confidence
            for item in belief_state.belief_ids
            if item in beliefs
        ]
        return sum(confidences) / len(confidences) if confidences else 0.5

    def _goal_score(self, model, action, motivation):
        supporting_goals = (
            [item for item in motivation.supporting_goals if item in model.goals]
            if motivation
            else []
        )
        base = {
            "secretly_collect_network_evidence": 0.85,
            "ask_roommate_for_help": 0.72,
            "confront_authority": 0.52,
            "delay_action": 0.42,
        }[action]
        if motivation and action == motivation.preferred_action:
            base += 0.12
        return self._clamp(base), supporting_goals or list(model.goals)

    def _value_score(self, model, action):
        value_ids = [
            item for item in self.VALUES_BY_ACTION[action] if item in model.values
        ]
        score = (
            sum(model.values[item].base_weight for item in value_ids)
            / len(value_ids)
            if value_ids
            else 0.5
        )
        return score, value_ids

    def _emotion_score(self, model, action, appraisal):
        if appraisal is None:
            return 0.5
        emotion = appraisal.emotion
        if action == "secretly_collect_network_evidence":
            score = (
                emotion.curiosity * 0.50
                + emotion.anger * 0.20
                + (1.0 - emotion.fear) * 0.30
            )
        elif action == "ask_roommate_for_help":
            score = (
                emotion.hope * 0.30
                + emotion.curiosity * 0.35
                + (1.0 - emotion.fear) * 0.35
            )
        elif action == "confront_authority":
            score = (
                emotion.anger * 0.55
                + emotion.curiosity * 0.15
                + (1.0 - emotion.fear) * 0.30
            )
        else:
            score = (
                emotion.fear * 0.35
                + (1.0 - emotion.anger) * 0.35
                + (1.0 - emotion.curiosity) * 0.30
            )
        return self._clamp(score)

    def _motivation_score(self, action, motivation):
        if motivation is None:
            return 0.5
        if action == motivation.preferred_action:
            return 1.0
        compatibility = {
            "verify_threat": {
                "secretly_collect_network_evidence": 1.0,
                "ask_roommate_for_help": 0.7,
                "confront_authority": 0.6,
                "delay_action": 0.2,
            },
            "preserve_stability": {
                "delay_action": 1.0,
                "ask_roommate_for_help": 0.7,
                "secretly_collect_network_evidence": 0.35,
                "confront_authority": 0.1,
            },
            "reduce_uncertainty": {
                "ask_roommate_for_help": 1.0,
                "secretly_collect_network_evidence": 0.75,
                "delay_action": 0.55,
                "confront_authority": 0.15,
            },
        }[motivation.motive][action]
        return self._clamp(
            (compatibility * 0.7) + (motivation.intensity * 0.3)
        )

    def _other_model_score(self, action, other_models):
        score = 0.5
        for other in other_models:
            prediction = other.predicted_action
            if prediction == "discourage public confrontation":
                if action == "confront_authority":
                    score -= 0.2 * other.confidence
                elif action == "secretly_collect_network_evidence":
                    score += 0.08 * other.confidence
            elif prediction == "support further investigation" and action in {
                "secretly_collect_network_evidence",
                "ask_roommate_for_help",
            }:
                score += 0.12 * other.confidence
            elif prediction == "withhold judgment" and action == "confront_authority":
                score -= 0.08 * other.confidence
        return self._clamp(score)

    def _constraint_score(self, agent_id, action, opposing, economics, social):
        scarcity = 0.0
        asymmetry = 0.0
        power = 0.0
        norm = 0.0
        constraint_ids = []
        if economics:
            scarcity_items = [
                item for item in economics.scarcity_assessments
                if item.agent_id == agent_id
            ]
            asymmetry_items = [
                item for item in economics.information_asymmetries
                if item.agent_id == agent_id
            ]
            scarcity = max(
                (item.scarcity_level for item in scarcity_items), default=0.0
            )
            asymmetry = max(
                (item.asymmetry_level for item in asymmetry_items), default=0.0
            )
            constraint_ids.extend(
                item.scarcity_assessment_id for item in scarcity_items
            )
            constraint_ids.extend(
                item.information_asymmetry_id for item in asymmetry_items
            )
        if social:
            power_items = [
                item for item in social.institution_powers
                if item.agent_id == agent_id
            ]
            norm_items = [
                item for item in social.norm_pressures
                if item.agent_id == agent_id
            ]
            power = max(
                (item.power_asymmetry for item in power_items), default=0.0
            )
            norm = max(
                (item.compliance_pressure for item in norm_items), default=0.0
            )
            constraint_ids.extend(item.institution_power_id for item in power_items)
            constraint_ids.extend(item.norm_pressure_id for item in norm_items)
        opposition = self._average_confidence(opposing)
        risk = {
            "secretly_collect_network_evidence": (
                scarcity * 0.22 + asymmetry * 0.12 + power * 0.08
                + opposition * 0.18
            ),
            "ask_roommate_for_help": (
                scarcity * 0.10 + norm * 0.08 + opposition * 0.15
            ),
            "confront_authority": (
                scarcity * 0.15 + asymmetry * 0.18 + power * 0.24
                + norm * 0.18 + opposition * 0.22
            ),
            "delay_action": (
                asymmetry * 0.08 + opposition * 0.15
            ),
        }[action]
        constraint_ids.extend(
            constraint for item in opposing for constraint in item.constraints
        )
        return self._clamp(1.0 - risk), list(dict.fromkeys(constraint_ids))

    def _matching_hypotheses(self, hypotheses, agent_id, action, promoted):
        return [
            item for item in hypotheses
            if (not item.affected_agents or agent_id in item.affected_agents)
            and action in (
                item.promotes_actions if promoted else item.inhibits_actions
            )
        ]

    def _satisficing_threshold(self, uncertainty, stress, coverage):
        return round(
            self._clamp(
                0.52 + uncertainty * 0.08 + stress * 0.05
                + (1.0 - coverage) * 0.05
            ),
            3,
        )

    def _rationale(self, action, breakdown, threshold):
        return (
            f"bounded evaluation for {action}: belief="
            f"{breakdown.belief_compatibility:.3f}; possible-world="
            f"{breakdown.possible_world_compatibility:.3f}; goal="
            f"{breakdown.goal_compatibility:.3f}; value="
            f"{breakdown.value_compatibility:.3f}; emotion="
            f"{breakdown.emotional_compatibility:.3f}; motivation="
            f"{breakdown.motivation_compatibility:.3f}; other-model="
            f"{breakdown.other_model_compatibility:.3f}; constraint="
            f"{breakdown.constraint_satisfaction:.3f}; threshold={threshold:.3f}."
        )

    def _action_suffix(self, action):
        return {
            "secretly_collect_network_evidence": "secret",
            "ask_roommate_for_help": "roommate",
            "confront_authority": "confront",
            "delay_action": "delay",
        }[action]

    def _average_confidence(self, hypotheses):
        return (
            sum(item.confidence for item in hypotheses) / len(hypotheses)
            if hypotheses else 0.0
        )

    def _value_weight(self, model, name):
        value = model.values.get(name)
        return value.base_weight if value else 0.5

    def _clamp(self, value):
        return min(1.0, max(0.0, value))
