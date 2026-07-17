import unittest

from pydantic import ValidationError

from schemas import (
    ActiveProcess,
    Agent,
    Belief,
    CausalHypothesis,
    EmotionState,
    Epistemology,
    Institution,
    ObjectiveWorldState,
    Relationship,
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
                "truth": 0.88,
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


if __name__ == "__main__":
    unittest.main()
