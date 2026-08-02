from typing import Any

from schemas import (
    AgentAction,
    CandidateFuture,
    CausalHypothesis,
    FutureMechanism,
    ObjectiveWorldState,
    PossibleWorldContext,
    StateChange,
    SubjectiveWorldModel,
)


class FutureGenerator:
    BRANCHES = (
        {
            "suffix": "secret",
            "action": "secretly_collect_network_evidence",
            "mechanism_type": "information_discovery",
            "world_kind": "institutional_monitoring",
            "base_rate": 0.28,
            "description": "低可见度取证提高信息量，并可能改变后续制度判断。",
            "fallback_drivers": ["unresolved_network_anomaly"],
            "fallback_mediators": ["private_evidence_collection"],
            "fallback_constraints": ["detection_risk"],
            "trigger": "主体认为异常值得进一步验证",
            "uncertainty": "新增证据能否区分安全措施与行为监控",
            "risk": "秘密访问可能被网络日志发现",
        },
        {
            "suffix": "roommate",
            "action": "ask_roommate_for_help",
            "mechanism_type": "social_coordination",
            "world_kind": "technical_anomaly",
            "base_rate": 0.24,
            "description": "同伴协作扩展信息来源，并通过关系信任分担调查风险。",
            "fallback_drivers": ["need_for_independent_corroboration"],
            "fallback_mediators": ["peer_coordination"],
            "fallback_constraints": ["coordination_uncertainty"],
            "trigger": "主体需要独立旁证",
            "uncertainty": "同伴是否认同问题定义并愿意参与",
            "risk": "扩大知情范围会增加社会暴露",
        },
        {
            "suffix": "confront",
            "action": "confront_authority",
            "mechanism_type": "institutional_contestation",
            "world_kind": "institutional_monitoring",
            "base_rate": 0.20,
            "description": "公开质询把私人疑虑转化为制度问责压力。",
            "fallback_drivers": ["demand_for_accountability"],
            "fallback_mediators": ["public_institutional_pressure"],
            "fallback_constraints": ["authority_asymmetry"],
            "trigger": "主体认为公开问责收益高于制裁风险",
            "uncertainty": "制度会提高透明度还是强化防御",
            "risk": "公开对抗可能触发规范制裁",
        },
        {
            "suffix": "ignore",
            "action": "delay_action",
            "mechanism_type": "process_inertia",
            "world_kind": "protective_security",
            "base_rate": 0.19,
            "description": "缺少干预使既有制度过程沿当前方向继续演化。",
            "fallback_drivers": ["ongoing_institutional_rollout"],
            "fallback_mediators": ["absence_of_countervailing_action"],
            "fallback_constraints": ["insufficient_decisive_evidence"],
            "trigger": "主体暂时保留判断并等待更多证据",
            "uncertainty": "等待期间制度过程会积累多大影响",
            "risk": "主体可能失去早期验证窗口",
        },
    )

    def generate(
        self,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
        hypotheses: list[CausalHypothesis],
        possible_world_context: PossibleWorldContext | None = None,
    ) -> list[CandidateFuture]:
        step = objective_state.step + 1
        actor = self._select_actor(objective_state, subjective_models)
        companion_id = self._select_companion(objective_state, actor.agent_id)
        active_process_ids = [
            item.process_id for item in objective_state.active_processes
        ]
        active_process_drivers = [
            driver
            for process in objective_state.active_processes
            for driver in process.drivers
        ]

        futures = []
        for branch in self.BRANCHES:
            action = str(branch["action"])
            supporting = self._matching_hypotheses(
                hypotheses,
                actor.agent_id,
                action,
                promoted=True,
            )
            opposing = self._matching_hypotheses(
                hypotheses,
                actor.agent_id,
                action,
                promoted=False,
            )
            world_ids, distribution_ids, belief_plausibility = (
                self._possible_world_support(
                    actor.agent_id,
                    str(branch["world_kind"]),
                    possible_world_context,
                )
            )
            future_id = f"future_{step:03d}_{branch['suffix']}"
            mechanism = self._build_mechanism(
                future_id,
                branch,
                supporting,
                opposing,
                active_process_ids,
                active_process_drivers,
            )
            estimated_plausibility = self._estimate_plausibility(
                float(branch["base_rate"]),
                supporting,
                opposing,
                belief_plausibility,
                process_inertia=(branch["mechanism_type"] == "process_inertia"),
            )
            futures.append(
                CandidateFuture(
                    future_id=future_id,
                    source_state_id=objective_state.state_id,
                    summary=self._summary(
                        str(branch["mechanism_type"]),
                        objective_state,
                        actor.agent_id,
                        companion_id,
                    ),
                    estimated_plausibility=estimated_plausibility,
                    time_horizon=self._time_horizon(supporting, branch),
                    trigger_conditions=[str(branch["trigger"])],
                    supporting_hypotheses=[
                        item.hypothesis_id for item in supporting
                    ],
                    opposing_hypotheses=[
                        item.hypothesis_id for item in opposing
                    ],
                    agent_actions=[
                        AgentAction(agent_id=actor.agent_id, action=action)
                    ],
                    expected_state_changes=[
                        self._state_change(
                            str(branch["mechanism_type"]),
                            objective_state,
                            actor.agent_id,
                            companion_id,
                            future_id,
                            step,
                        )
                    ],
                    uncertainties=[str(branch["uncertainty"])],
                    risks=[str(branch["risk"])],
                    source_possible_world_ids=world_ids,
                    source_belief_distribution_ids=distribution_ids,
                    belief_plausibility=belief_plausibility,
                    mechanism=mechanism,
                    generation_rationale=(
                        f"base={branch['base_rate']:.2f}; "
                        f"support={self._average_confidence(supporting):.3f}; "
                        f"opposition={self._average_confidence(opposing):.3f}; "
                        f"belief={belief_plausibility:.3f}."
                    ),
                )
            )
        return futures

    def _build_mechanism(
        self,
        future_id: str,
        branch: dict[str, Any],
        supporting: list[CausalHypothesis],
        opposing: list[CausalHypothesis],
        active_process_ids: list[str],
        active_process_drivers: list[str],
    ) -> FutureMechanism:
        drivers = [
            *[item for hypothesis in supporting for item in hypothesis.drivers],
            *active_process_drivers,
            *branch["fallback_drivers"],
        ]
        mediators = [
            *[item for hypothesis in supporting for item in hypothesis.mediators],
            *branch["fallback_mediators"],
        ]
        constraints = [
            *[item for hypothesis in supporting for item in hypothesis.constraints],
            *[item for hypothesis in opposing for item in hypothesis.constraints],
            *branch["fallback_constraints"],
        ]
        return FutureMechanism(
            mechanism_id=f"mechanism_{future_id}",
            mechanism_type=branch["mechanism_type"],
            description=str(branch["description"]),
            drivers=self._unique(drivers),
            mediators=self._unique(mediators),
            constraints=self._unique(constraints),
            lens_names=self._unique([item.lens for item in supporting]),
            source_hypothesis_ids=[
                item.hypothesis_id for item in supporting
            ],
            source_active_process_ids=active_process_ids,
        )

    def _matching_hypotheses(
        self,
        hypotheses: list[CausalHypothesis],
        agent_id: str,
        action: str,
        promoted: bool,
    ) -> list[CausalHypothesis]:
        return [
            item
            for item in hypotheses
            if (not item.affected_agents or agent_id in item.affected_agents)
            and action
            in (item.promotes_actions if promoted else item.inhibits_actions)
        ]

    def _possible_world_support(
        self,
        agent_id: str,
        world_kind: str,
        context: PossibleWorldContext | None,
    ) -> tuple[list[str], list[str], float]:
        if context is None:
            return [], [], 0.5
        world = next(
            (
                item
                for item in context.possible_worlds
                if item.agent_id == agent_id and item.kind == world_kind
            ),
            None,
        )
        distribution = next(
            (
                item
                for item in context.posterior_distributions
                if item.agent_id == agent_id
            ),
            None,
        )
        if world is None or distribution is None:
            return [], [], 0.5
        return (
            [world.possible_world_id],
            [distribution.distribution_id],
            distribution.probabilities[world.possible_world_id],
        )

    def _estimate_plausibility(
        self,
        base_rate: float,
        supporting: list[CausalHypothesis],
        opposing: list[CausalHypothesis],
        belief_plausibility: float,
        process_inertia: bool,
    ) -> float:
        score = (
            base_rate
            + (self._average_confidence(supporting) * 0.22)
            + (belief_plausibility * 0.18)
            - (self._average_confidence(opposing) * 0.14)
            + (0.05 if process_inertia else 0.0)
        )
        return round(min(1.0, max(0.0, score)), 3)

    def _state_change(
        self,
        mechanism_type: str,
        state: ObjectiveWorldState,
        actor_id: str,
        companion_id: str | None,
        future_id: str,
        step: int,
    ) -> StateChange:
        actor = state.agents[actor_id]
        if mechanism_type == "information_discovery":
            destination = (
                "computer_lab"
                if "computer_lab" in state.locations
                else actor.location_id
            )
            if destination != actor.location_id:
                return StateChange(
                    path=f"agents.{actor_id}.location_id",
                    old_value=actor.location_id,
                    new_value=destination,
                    reason="调查行动需要进入可获取更完整技术证据的位置。",
                    future_id=future_id,
                )
            return StateChange(
                path=f"agents.{actor_id}.status",
                old_value=actor.status,
                new_value=f"collecting_network_evidence_{step:03d}",
                reason="主体已在调查位置，继续执行低可见度证据收集。",
                future_id=future_id,
            )
        if mechanism_type == "social_coordination":
            relation_key = self._relationship_key(state, actor_id, companion_id)
            if relation_key is not None:
                relation = state.relationships[relation_key]
                return StateChange(
                    path=f"relationships.{relation_key}.trust",
                    old_value=relation.trust,
                    new_value=round(min(1.0, relation.trust + 0.05), 3),
                    reason="请求协作使双方交换信息并小幅提高关系依赖。",
                    future_id=future_id,
                )
            return StateChange(
                path=f"agents.{actor_id}.status",
                old_value=actor.status,
                new_value=f"seeking_peer_support_{step:03d}",
                reason="主体开始寻找能够提供独立旁证的协作者。",
                future_id=future_id,
            )
        if mechanism_type == "institutional_contestation" and state.institutions:
            institution_id = sorted(state.institutions)[0]
            institution = state.institutions[institution_id]
            return StateChange(
                path=f"institutions.{institution_id}.transparency",
                old_value=institution.transparency,
                new_value=round(min(1.0, institution.transparency + 0.05), 3),
                reason="公开质询形成有限问责压力，促使制度释放少量信息。",
                future_id=future_id,
            )
        return StateChange(
            path=f"agents.{actor_id}.status",
            old_value=actor.status,
            new_value=f"waiting_for_more_evidence_{step:03d}",
            reason="主体延迟干预，既有过程继续而个人进入等待状态。",
            future_id=future_id,
        )

    def _summary(
        self,
        mechanism_type: str,
        state: ObjectiveWorldState,
        actor_id: str,
        companion_id: str | None,
    ) -> str:
        actor_name = state.agents[actor_id].name
        companion_name = (
            state.agents[companion_id].name if companion_id else "同伴"
        )
        return {
            "information_discovery": (
                f"{actor_name}先秘密验证网络异常，世界进入证据积累分支。"
            ),
            "social_coordination": (
                f"{actor_name}向{companion_name}寻求旁证，世界进入同伴协作分支。"
            ),
            "institutional_contestation": (
                f"{actor_name}公开质询网络中心，世界进入制度问责分支。"
            ),
            "process_inertia": (
                f"{actor_name}暂缓行动，既有监测过程沿当前方向继续。"
            ),
        }[mechanism_type]

    def _select_actor(
        self,
        state: ObjectiveWorldState,
        models: list[SubjectiveWorldModel],
    ) -> SubjectiveWorldModel:
        candidates = [item for item in models if item.agent_id in state.agents]
        if not candidates:
            raise ValueError("future generation requires an agent in the world")
        return max(
            candidates,
            key=lambda item: (
                self._value_weight(item, "truth")
                + self._value_weight(item, "freedom")
                + item.epistemology.trust_data
                - item.epistemology.trust_authority
            ),
        )

    def _select_companion(
        self,
        state: ObjectiveWorldState,
        actor_id: str,
    ) -> str | None:
        related = []
        for relationship in state.relationships.values():
            if relationship.source == actor_id:
                related.append((relationship.trust, relationship.target))
            elif relationship.target == actor_id:
                related.append((relationship.trust, relationship.source))
        if related:
            return max(related)[1]
        return next(
            (agent_id for agent_id in state.agents if agent_id != actor_id),
            None,
        )

    def _relationship_key(
        self,
        state: ObjectiveWorldState,
        actor_id: str,
        companion_id: str | None,
    ) -> str | None:
        if companion_id is None:
            return None
        return next(
            (
                key
                for key, relationship in state.relationships.items()
                if {relationship.source, relationship.target}
                == {actor_id, companion_id}
            ),
            None,
        )

    def _time_horizon(
        self,
        supporting: list[CausalHypothesis],
        branch: dict[str, Any],
    ) -> str:
        if branch["mechanism_type"] == "process_inertia":
            return "days"
        return supporting[0].time_scale if supporting else "hours"

    def _average_confidence(
        self,
        hypotheses: list[CausalHypothesis],
    ) -> float:
        if not hypotheses:
            return 0.0
        return sum(item.confidence for item in hypotheses) / len(hypotheses)

    def _value_weight(self, model: SubjectiveWorldModel, name: str) -> float:
        value = model.values.get(name)
        return value.base_weight if value else 0.5

    def _unique(self, values: list[str]) -> list[str]:
        return list(dict.fromkeys(values))
