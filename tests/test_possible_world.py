import unittest

from pydantic import ValidationError

from app import run_pipeline
from core.cognition_engine import CognitionEngine
from core.economic_engine import EconomicEngine
from core.observation_engine import ObservationEngine
from core.possible_world_engine import PossibleWorldEngine
from core.world_initializer import WorldInitializer
from schemas import BeliefDistribution


class PossibleWorldEngineTest(unittest.TestCase):
    def setUp(self):
        state, _, models = WorldInitializer().initialize("校园监控")
        observations = ObservationEngine().observe(state, models)
        cognition = CognitionEngine().interpret(observations, models)
        economics = EconomicEngine().assess_context(
            state,
            cognition.subjective_models,
            observations,
            cognition.belief_states,
        )
        self.evidence = cognition.evidence
        self.boundaries = {
            item.agent_id: item for item in economics.information_boundaries
        }
        self.context = PossibleWorldEngine().build_context(
            observations,
            cognition.evidence,
            economics.information_boundaries,
            cognition.subjective_models,
            step=state.step,
        )

    def test_each_agent_gets_normalized_prior_revision_and_new_belief(self):
        self.assertEqual(len(self.context.possible_worlds), 6)
        self.assertEqual(len(self.context.prior_distributions), 2)
        self.assertEqual(len(self.context.posterior_distributions), 2)
        self.assertEqual(len(self.context.revisions), 2)
        self.assertEqual(len(self.context.new_beliefs), 2)

        worlds = {item.possible_world_id for item in self.context.possible_worlds}
        for distribution in self.context.posterior_distributions:
            self.assertAlmostEqual(sum(distribution.probabilities.values()), 1.0)
            self.assertIn(distribution.dominant_possible_world_id, worlds)
        for belief in self.context.new_beliefs:
            self.assertIn(belief.possible_world_id, worlds)
            self.assertGreater(belief.confidence, 0.0)
        dominant_kinds = {
            belief.agent_id: next(
                world.kind
                for world in self.context.possible_worlds
                if world.possible_world_id == belief.possible_world_id
            )
            for belief in self.context.new_beliefs
        }
        self.assertEqual(
            dominant_kinds,
            {
                "lin_xia": "institutional_monitoring",
                "wang_chen": "protective_security",
            },
        )

    def test_information_boundary_prevents_hidden_evidence_leakage(self):
        boundaries = {
            agent_id: set(item.observation_ids)
            for agent_id, item in self.boundaries.items()
        }
        for world in self.context.possible_worlds:
            self.assertTrue(
                set(world.source_observation_ids).issubset(boundaries[world.agent_id])
            )
        for belief in self.context.new_beliefs:
            self.assertTrue(
                set(belief.source_observation_ids).issubset(boundaries[belief.agent_id])
            )
        evidence_by_id = {item.evidence_id: item for item in self.evidence}
        worlds_by_id = {
            item.possible_world_id: item for item in self.context.possible_worlds
        }
        for assessment in self.context.evidence_assessments:
            evidence = evidence_by_id[assessment.evidence_id]
            world = worlds_by_id[assessment.possible_world_id]
            self.assertEqual(evidence.agent_id, world.agent_id)
            self.assertIn(evidence.observation_id, boundaries[world.agent_id])

    def test_hard_evidence_removes_world_and_renormalizes_posterior(self):
        agent_id = "lin_xia"
        worlds = [
            item for item in self.context.possible_worlds if item.agent_id == agent_id
        ]
        prior = next(
            item
            for item in self.context.prior_distributions
            if item.agent_id == agent_id
        )
        assessments = [
            item
            for item in self.context.evidence_assessments
            if item.possible_world_id in {world.possible_world_id for world in worlds}
        ]
        removed_id = worlds[0].possible_world_id
        hard_constraint = assessments[0].model_copy(
            update={
                "assessment_id": "hard_constraint_001",
                "possible_world_id": removed_id,
                "rules_out_world": True,
                "likelihood": 0.0,
                "compatibility": "contradicts",
            }
        )

        posterior, revision = PossibleWorldEngine().revise(
            prior,
            worlds,
            [*assessments, hard_constraint],
        )

        self.assertEqual(posterior.probabilities[removed_id], 0.0)
        self.assertIn(removed_id, posterior.eliminated_world_ids)
        self.assertIn(removed_id, revision.eliminated_world_ids)
        self.assertAlmostEqual(sum(posterior.probabilities.values()), 1.0)

    def test_possible_world_belief_changes_candidate_future_plausibility(self):
        result = run_pipeline("校园监控", steps=1, export=False)
        futures = result["candidate_futures"]
        self.assertTrue(all(item["source_possible_world_ids"] for item in futures))
        self.assertTrue(
            all(item["source_belief_distribution_ids"] for item in futures)
        )
        plausibilities = {item["belief_plausibility"] for item in futures}
        self.assertGreater(len(plausibilities), 1)

    def test_distribution_rejects_probabilities_that_do_not_sum_to_one(self):
        with self.assertRaises(ValidationError):
            BeliefDistribution(
                distribution_id="invalid_distribution",
                agent_id="lin_xia",
                step=0,
                stage="posterior",
                information_boundary_id="boundary_001",
                probabilities={"world_a": 0.8, "world_b": 0.8},
                dominant_possible_world_id="world_a",
                uncertainty=0.5,
            )

if __name__ == "__main__":
    unittest.main()
