import unittest

from pydantic import ValidationError

from schemas import ActiveProcess, Agent, CausalHypothesis, Institution, ObjectiveWorldState, Relationship


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


if __name__ == "__main__":
    unittest.main()
