import unittest

from pydantic import ValidationError

from schemas import (
    ActiveProcess,
    Agent,
    AgentAction,
    Belief,
    CameraSetup,
    CandidateFuture,
    CausalHypothesis,
    EmotionState,
    Epistemology,
    Institution,
    Interpretation,
    NarrativeEvent,
    ObjectiveWorldState,
    Observation,
    Relationship,
    SceneCard,
    SceneCharacter,
    StateChange,
    SubjectiveWorldModel,
    Value,
)


class SchemaTest(unittest.TestCase):
    def test_causal_hypothesis_confidence_range(self):
        hypothesis = CausalHypothesis(
            hypothesis_id="hyp_001",
            lens="psychology",
            claim="不透明威胁会提高验证动机。",
            time_scale="hours",
            confidence=0.7,
        )

        self.assertEqual(hypothesis.confidence, 0.7)

    def test_causal_hypothesis_rejects_invalid_confidence(self):
        with self.assertRaises(ValidationError):
            CausalHypothesis(
                hypothesis_id="hyp_bad",
                lens="psychology",
                claim="invalid",
                time_scale="hours",
                confidence=1.7,
            )

    def test_objective_world_day3_models_are_defined(self):
        state = ObjectiveWorldState(
            state_id="state_000",
            step=0,
            timestamp="day_1",
            agents={
                "lin_xia": Agent(agent_id="lin_xia", name="林夏", location_id="dorm"),
            },
            institutions={
                "school": Institution(institution_id="school", name="大学", transparency=0.4),
            },
            relationships={
                "lin_xia__school": Relationship(source="lin_xia", target="school", authority_asymmetry=0.9),
            },
            active_processes=[
                ActiveProcess(
                    process_id="network_rollout",
                    type="institutional_change",
                    start_time="day_1",
                    time_scale="days",
                )
            ],
        )

        self.assertEqual(state.agents["lin_xia"].location_id, "dorm")
        self.assertEqual(state.institutions["school"].transparency, 0.4)
        self.assertEqual(state.relationships["lin_xia__school"].authority_asymmetry, 0.9)
        self.assertEqual(state.active_processes[0].time_scale, "days")

    def test_subjective_world_day4_models_are_defined(self):
        model = SubjectiveWorldModel(
            agent_id="lin_xia",
            beliefs=[
                Belief(
                    belief_id="belief_001",
                    proposition="学校正在监控学生网络",
                    confidence=0.72,
                    evidence=["dns_anomaly"],
                    source="personal_analysis",
                    last_updated_step=2,
                )
            ],
            values={
                "freedom": Value(
                    base_weight=0.85,
                    context_modifiers={"personal_surveillance": 0.15},
                ),
                "truth": Value.model_validate(0.88),
            },
            epistemology=Epistemology(trust_data=0.9, trust_authority=0.2),
            emotion=EmotionState(fear=0.72, curiosity=0.83, hope=0.31),
        )

        self.assertEqual(model.beliefs[0].confidence, 0.72)
        self.assertEqual(model.values["truth"].base_weight, 0.88)
        self.assertEqual(model.values["freedom"].weight_for("personal_surveillance"), 1.0)
        self.assertEqual(model.epistemology.trust_data, 0.9)
        self.assertEqual(model.emotion.curiosity, 0.83)

    def test_subjective_world_rejects_scores_outside_valid_range(self):
        with self.assertRaises(ValidationError):
            Epistemology(trust_data=1.1)

        with self.assertRaises(ValidationError):
            EmotionState(fear=-0.1)

        with self.assertRaises(ValidationError):
            Value(base_weight=0.5, context_modifiers={"crisis": 1.1})

    def test_day5_schemas_are_instantiable(self):
        observation = Observation(
            observation_id="obs_001",
            information_id="info_dns_redirect",
            agent_id="lin_xia",
            step=1,
            source="terminal",
            evidence_type="data",
            content="部分 DNS 请求被重定向",
            reliability=0.92,
            visibility="private",
        )
        interpretation = Interpretation(
            interpretation_id="int_001",
            agent_id="lin_xia",
            observation_ids=[observation.observation_id],
            belief_basis=["学校可能在监控学生网络"],
            mental_model_id="mm_001",
            bias_filter_id="bias_001",
            causal_frame="institutional opacity enables surveillance",
            meaning="institution threatens autonomy",
            emotional_response=EmotionState(fear=0.4, anger=0.7),
            action_implication="collect evidence secretly",
            confidence=0.72,
        )
        hypothesis = CausalHypothesis(
            hypothesis_id="hyp_eco_001",
            lens="economic",
            claim="资源获取渠道受限会提高非正式合作网络形成概率",
            drivers=["resource_scarcity"],
            mediators=["opportunity_cost"],
            constraints=["high_monitoring"],
            affected_agents=["lin_xia"],
            time_scale="days",
            confidence=0.64,
        )
        state_change = StateChange(
            path="agents.lin_xia.location_id",
            old_value="dorm",
            new_value="computer_lab",
            reason="林夏秘密调查网络流量",
            future_id="future_001",
        )
        future = CandidateFuture(
            future_id="future_001",
            summary="林夏先秘密验证监控机制",
            estimated_plausibility=0.46,
            time_horizon="hours",
            trigger_conditions=["林夏确认网络流量异常"],
            supporting_hypotheses=[hypothesis.hypothesis_id],
            agent_actions=[AgentAction(agent_id="lin_xia", action="secretly_collect_network_evidence")],
            expected_state_changes=[state_change],
        )
        event = NarrativeEvent(
            narrative_event_id="nar_001",
            source_future_id=future.future_id,
            focal_agent="lin_xia",
            summary="林夏决定秘密抓取网络数据",
            narrative_importance=0.84,
            revealed_information=["网络流量存在重定向"],
            hidden_information=["监控系统真正目的"],
            emotional_focus=["curiosity", "fear"],
            visual_core="电脑终端中不断刷新的异常网络记录",
        )
        scene = SceneCard.model_validate(
            {
                "scene_id": "scene_001",
                "narrative_event_id": event.narrative_event_id,
                "location": "计算机学院机房",
                "time": "day_1_23_50",
                "focal_agent": "lin_xia",
                "main_action": "林夏保存异常流量记录",
                "characters": [{"agent_id": "lin_xia", "pose": "leaning forward"}],
                "camera": {"shot_type": "medium close-up", "focus": "terminal logs"},
            }
        )

        self.assertEqual(interpretation.observation_ids, ["obs_001"])
        self.assertEqual(interpretation.emotional_response.anger, 0.7)
        self.assertEqual(future.expected_state_changes[0].new_value, "computer_lab")
        self.assertIsInstance(scene.characters[0], SceneCharacter)
        self.assertIsInstance(scene.camera, CameraSetup)

    def test_day5_schemas_reject_invalid_ranges_and_enums(self):
        with self.assertRaises(ValidationError):
            Observation.model_validate(
                {
                    "observation_id": "obs_bad",
                    "information_id": "info_bad",
                    "agent_id": "lin_xia",
                    "step": -1,
                    "source": "terminal",
                    "evidence_type": "data",
                    "content": "invalid",
                    "reliability": 1.2,
                    "visibility": "hidden",
                }
            )

        with self.assertRaises(ValidationError):
            CandidateFuture.model_validate(
                {
                    "future_id": "future_bad",
                    "summary": "invalid",
                    "estimated_plausibility": 0.5,
                    "time_horizon": "sometime",
                }
            )

        with self.assertRaises(ValidationError):
            NarrativeEvent(
                narrative_event_id="nar_bad",
                source_future_id="future_bad",
                focal_agent="lin_xia",
                summary="invalid",
                narrative_importance=1.2,
            )


if __name__ == "__main__":
    unittest.main()
