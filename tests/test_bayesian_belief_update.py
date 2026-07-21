import unittest

from core.belief_updater import BeliefUpdater
from schemas import Belief, Evidence, EvidencePolarity, SubjectiveWorldModel


class BayesianBeliefUpdateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.proposition = "学校可能正在监控学生网络。"
        self.model = SubjectiveWorldModel(
            agent_id="lin_xia",
            beliefs=[
                Belief(
                    belief_id="belief_monitoring",
                    proposition=self.proposition,
                    confidence=0.6,
                )
            ],
        )

    def test_supporting_evidence_raises_the_posterior_and_updates_existing_belief(self) -> None:
        evidence = self._evidence("evidence_001_001", "supports")

        updated, belief, update, state = BeliefUpdater().update(
            self.model,
            evidence,
            update_id="update_001_001",
            belief_state_id="belief_state_001_001",
            proposition=self.proposition,
        )

        self.assertEqual(update.prior, 0.6)
        expected = (
            update.likelihood_e_given_true * update.prior
            / (
                (update.likelihood_e_given_true * update.prior)
                + (update.likelihood_e_given_false * (1.0 - update.prior))
            )
        )
        self.assertAlmostEqual(update.posterior, expected)
        self.assertGreater(update.posterior, update.prior)
        self.assertEqual(belief.confidence, update.posterior)
        self.assertEqual(len(updated.beliefs), 1)
        self.assertEqual(belief.update_ids, ["update_001_001"])
        self.assertEqual(state.dominant_belief_id, belief.belief_id)

    def test_contradictory_evidence_lowers_the_posterior(self) -> None:
        evidence = self._evidence("evidence_002_001", "contradicts")

        _, belief, update, state = BeliefUpdater().update(
            self.model,
            evidence,
            update_id="update_002_001",
            belief_state_id="belief_state_002_001",
            proposition=self.proposition,
        )

        self.assertLess(update.posterior, update.prior)
        self.assertEqual(belief.confidence, update.posterior)
        self.assertAlmostEqual(state.uncertainty, 1.0 - update.posterior)

    def test_repeated_evidence_uses_the_previous_posterior_as_the_new_prior(self) -> None:
        updater = BeliefUpdater()
        first_model, _, first_update, _ = updater.update(
            self.model,
            self._evidence("evidence_001_001", "supports"),
            update_id="update_001_001",
            belief_state_id="belief_state_001_001",
            proposition=self.proposition,
        )
        second_model, _, second_update, _ = updater.update(
            first_model,
            self._evidence("evidence_002_001", "supports"),
            update_id="update_002_001",
            belief_state_id="belief_state_002_001",
            proposition=self.proposition,
        )

        self.assertAlmostEqual(second_update.prior, first_update.posterior)
        self.assertGreater(second_update.posterior, first_update.posterior)
        self.assertEqual(len(second_model.beliefs), 1)

    def _evidence(self, evidence_id: str, polarity: EvidencePolarity) -> Evidence:
        return Evidence(
            evidence_id=evidence_id,
            observation_id=f"obs_{evidence_id}",
            agent_id="lin_xia",
            step=1,
            source="terminal",
            evidence_type="data",
            content="DNS requests were redirected.",
            reliability=0.9,
            trust_basis="trust_data",
            trust_weight=0.9,
            strength=0.9,
            polarity=polarity,
        )


if __name__ == "__main__":
    unittest.main()
