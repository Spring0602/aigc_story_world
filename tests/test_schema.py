import unittest

from pydantic import ValidationError

from schemas import CausalHypothesis


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


if __name__ == "__main__":
    unittest.main()
