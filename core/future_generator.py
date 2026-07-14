from schemas import AgentAction, CandidateFuture, CausalHypothesis, ObjectiveWorldState, StateChange, SubjectiveWorldModel


class FutureGenerator:
    def generate(
        self,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
        hypotheses: list[CausalHypothesis],
    ) -> list[CandidateFuture]:
        step = objective_state.step + 1
        support_ids = [hyp.hypothesis_id for hyp in hypotheses]
        return [
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
                        path="agents.lin_xia.location",
                        old_value=objective_state.agents["lin_xia"]["location"],
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
