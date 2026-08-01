from schemas import (
    AgentAction,
    CandidateFuture,
    CausalHypothesis,
    ObjectiveWorldState,
    PossibleWorldContext,
    StateChange,
    SubjectiveWorldModel,
)


class FutureGenerator:
    def generate(
        self,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
        hypotheses: list[CausalHypothesis],
        possible_world_context: PossibleWorldContext | None = None,
    ) -> list[CandidateFuture]:
        step = objective_state.step + 1
        support_ids = [hyp.hypothesis_id for hyp in hypotheses]
        futures = [
            CandidateFuture(
                future_id=f"future_{step:03d}_secret",
                summary="林夏不会立即公开对抗学校，而会先秘密验证监控机制。",
                estimated_plausibility=0.46,
                time_horizon="hours",
                trigger_conditions=["林夏确认网络流量异常"],
                supporting_hypotheses=support_ids,
                agent_actions=[AgentAction(agent_id="lin_xia", action="secretly_collect_network_evidence")],
                expected_state_changes=[
                    StateChange(
                        path="agents.lin_xia.location_id",
                        old_value=objective_state.agents["lin_xia"].location_id,
                        new_value="computer_lab",
                        reason="林夏需要更完整的网络环境来验证重定向。",
                        future_id=f"future_{step:03d}_secret",
                    )
                ],
                uncertainties=["检测系统是否真的记录个人行为"],
                risks=["被网络中心日志发现"],
            ),
            CandidateFuture(
                future_id=f"future_{step:03d}_roommate",
                summary="林夏向王晨求助，但王晨倾向相信学校解释。",
                estimated_plausibility=0.31,
                time_horizon="hours",
                trigger_conditions=["林夏需要旁证"],
                supporting_hypotheses=support_ids[:2],
                agent_actions=[AgentAction(agent_id="lin_xia", action="ask_roommate_for_help")],
                uncertainties=["王晨是否愿意参与"],
            ),
            CandidateFuture(
                future_id=f"future_{step:03d}_confront",
                summary="林夏直接质问老师或网络中心，导致制度压力提前出现。",
                estimated_plausibility=0.14,
                time_horizon="hours",
                trigger_conditions=["林夏愤怒超过谨慎"],
                supporting_hypotheses=support_ids[-1:],
                agent_actions=[AgentAction(agent_id="lin_xia", action="confront_authority")],
                risks=["公开对抗成本高"],
            ),
            CandidateFuture(
                future_id=f"future_{step:03d}_ignore",
                summary="林夏暂时忽略异常，监控 rollout 继续积累影响。",
                estimated_plausibility=0.09,
                time_horizon="days",
                trigger_conditions=["林夏认为证据不足"],
                supporting_hypotheses=[],
                agent_actions=[AgentAction(agent_id="lin_xia", action="delay_action")],
                risks=["失去早期验证窗口"],
            ),
        ]
        if possible_world_context is None:
            return futures
        return [
            self._attach_possible_world_support(future, possible_world_context)
            for future in futures
        ]

    def _attach_possible_world_support(
        self,
        future: CandidateFuture,
        context: PossibleWorldContext,
    ) -> CandidateFuture:
        if not future.agent_actions:
            return future
        action = future.agent_actions[0]
        if "secretly" in action.action or "confront" in action.action:
            world_kind = "institutional_monitoring"
        elif "help" in action.action:
            world_kind = "technical_anomaly"
        else:
            world_kind = "protective_security"

        world = next(
            (
                item
                for item in context.possible_worlds
                if item.agent_id == action.agent_id and item.kind == world_kind
            ),
            None,
        )
        distribution = next(
            (
                item
                for item in context.posterior_distributions
                if item.agent_id == action.agent_id
            ),
            None,
        )
        if world is None or distribution is None:
            return future
        return future.model_copy(
            update={
                "source_possible_world_ids": [world.possible_world_id],
                "source_belief_distribution_ids": [distribution.distribution_id],
                "belief_plausibility": distribution.probabilities[
                    world.possible_world_id
                ],
            },
            deep=True,
        )
