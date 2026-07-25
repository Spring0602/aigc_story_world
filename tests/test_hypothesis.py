import unittest

from pydantic import ValidationError

from core.lens_router import LensRouter
from core.world_initializer import WorldInitializer
from schemas import CausalHypothesis


class HypothesisTest(unittest.TestCase):
    def test_lenses_return_explicit_hypotheses(self):
        state, agents, models = WorldInitializer().initialize("校园监控")
        hypotheses = LensRouter().analyze(state, models)

        self.assertEqual({hyp.lens for hyp in hypotheses}, {"psychology", "economic", "social_structure"})
        self.assertTrue(all(hyp.claim and hyp.drivers and hyp.mediators and hyp.constraints for hyp in hypotheses))
        for hypothesis in hypotheses:
            self.assertEqual(len(hypothesis.drivers), len(set(hypothesis.drivers)))
            self.assertEqual(len(hypothesis.mediators), len(set(hypothesis.mediators)))
            self.assertEqual(len(hypothesis.constraints), len(set(hypothesis.constraints)))

    def test_day12_schema_requires_complete_causal_mechanism(self):
        hypothesis = CausalHypothesis(
            hypothesis_id="  hyp_day12_001  ",
            lens="  psychology  ",
            claim="  不透明威胁通过控制需求提高秘密验证的可能性。  ",
            drivers=["unclear_monitoring_scope"],
            mediators=["need_for_control"],
            constraints=["limited_evidence"],
            affected_agents=["lin_xia"],
            time_scale="hours",
            confidence=0.72,
        )

        self.assertEqual(hypothesis.hypothesis_id, "hyp_day12_001")
        self.assertEqual(hypothesis.lens, "psychology")
        self.assertEqual(
            hypothesis.claim,
            "不透明威胁通过控制需求提高秘密验证的可能性。",
        )

    def test_day12_json_schema_marks_plan_fields_as_required(self):
        required = set(CausalHypothesis.model_json_schema()["required"])
        self.assertTrue(
            {
                "claim",
                "drivers",
                "mediators",
                "constraints",
                "time_scale",
                "confidence",
            }.issubset(required)
        )

    def test_day12_schema_rejects_missing_empty_or_duplicate_roles(self):
        base = {
            "hypothesis_id": "hyp_day12_invalid",
            "lens": "psychology",
            "claim": "不透明威胁会提高验证动机。",
            "drivers": ["unclear_monitoring_scope"],
            "mediators": ["need_for_control"],
            "constraints": ["limited_evidence"],
            "time_scale": "hours",
            "confidence": 0.72,
        }

        invalid_updates = [
            {"drivers": []},
            {"mediators": [" "]},
            {"constraints": ["limited_evidence", "limited_evidence"]},
            {"claim": " "},
            {"time_scale": "immediately"},
        ]
        for update in invalid_updates:
            with self.subTest(update=update), self.assertRaises(ValidationError):
                CausalHypothesis.model_validate({**base, **update})

        missing_drivers = dict(base)
        del missing_drivers["drivers"]
        with self.assertRaises(ValidationError):
            CausalHypothesis.model_validate(missing_drivers)

    def test_day12_schema_rejects_overlapping_causal_roles(self):
        with self.assertRaises(ValidationError):
            CausalHypothesis(
                hypothesis_id="hyp_day12_overlap",
                lens="economic",
                claim="信息不对称会提高非正式调查的吸引力。",
                drivers=["information_asymmetry"],
                mediators=["opportunity_cost"],
                constraints=["information_asymmetry"],
                time_scale="hours",
                confidence=0.64,
            )


if __name__ == "__main__":
    unittest.main()
