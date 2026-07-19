import unittest

from core.agent_consistency import AgentConsistency
from core.evidence_evaluator import EvidenceEvaluator
from core.observation_engine import ObservationEngine
from core.world_initializer import WorldInitializer
from core.world_transition import WorldTransition
from schemas import (
    AgentAction,
    CandidateFuture,
    Epistemology,
    Event,
    HumanNatureModel,
    KnowledgeItem,
    Norm,
    Observation,
    Resource,
    StateChange,
    StateProvenance,
    SubjectiveWorldModel,
    TheoryOfChange,
    Uncertainty,
    Value,
)


class PhaseOneDaysOneToSixTest(unittest.TestCase):
    def setUp(self) -> None:
        self.state, self.profiles, self.models = WorldInitializer().initialize("校园网络监控")  # pyright: ignore[reportUnannotatedClassAttribute, reportUninitializedInstanceVariable]

    def test_day2_objective_world_entities_and_provenance_are_typed(self):
        self.assertTrue(all(isinstance(item, Resource) for item in self.state.resources.values()))
        self.assertTrue(all(isinstance(item, Norm) for item in self.state.norms.values()))
        self.assertTrue(all(isinstance(item, Event) for item in self.state.events))
        self.assertTrue(all(isinstance(item, StateProvenance) for item in self.state.history))

    def test_day3_subjective_world_tracks_known_unknown_and_false_beliefs(self):
        self.assertTrue(all(isinstance(item, KnowledgeItem) for model in self.models for item in model.knowledge))
        self.assertTrue(all(isinstance(item, Uncertainty) for model in self.models for item in model.uncertainties))
        self.assertTrue(any(model.false_beliefs for model in self.models))

    def test_day4_same_evidence_produces_different_epistemic_scores(self):
        observation = Observation(
            observation_id="obs_shared_data",
            information_id="info_shared_data",
            agent_id="observer",
            step=0,
            source="terminal",
            evidence_type="data",
            content="DNS requests were redirected.",
            reliability=0.8,
        )
        high_trust = SubjectiveWorldModel(
            agent_id="high",
            epistemology=Epistemology(trust_data=0.9),
        )
        low_trust = SubjectiveWorldModel(
            agent_id="low",
            epistemology=Epistemology(trust_data=0.2),
        )
        evaluator = EvidenceEvaluator()

        self.assertGreater(evaluator.score(observation, high_trust), evaluator.score(observation, low_trust))
        self.assertEqual(evaluator.trust_basis(observation), "trust_data")

    def test_day5_profiles_include_values_and_worldview_models(self):
        self.assertTrue(all(profile.values for profile in self.profiles))
        self.assertTrue(all(isinstance(profile.human_nature_model, HumanNatureModel) for profile in self.profiles))
        self.assertTrue(all(isinstance(profile.theory_of_change, TheoryOfChange) for profile in self.profiles))

        future = CandidateFuture(
            future_id="future_value_test",
            summary="Collect evidence privately",
            estimated_plausibility=0.5,
            time_horizon="hours",
            agent_actions=[AgentAction(agent_id="actor", action="secretly_collect_network_evidence")],
        )
        truth_first = SubjectiveWorldModel(
            agent_id="actor",
            values={"truth": Value(base_weight=0.9)},
            epistemology=Epistemology(trust_data=0.9),
        )
        conformity_first = SubjectiveWorldModel(
            agent_id="actor",
            values={"truth": Value(base_weight=0.2)},
            epistemology=Epistemology(trust_data=0.2),
        )
        scorer = AgentConsistency()
        self.assertGreater(scorer.score(future, [truth_first]), scorer.score(future, [conformity_first]))

    def test_day6_observation_engine_enforces_partial_observability(self):
        observations = ObservationEngine().observe(self.state, self.models)
        observed_ids = {item.information_id for item in observations}
        hidden_ids = {item.info_id for item in self.state.hidden_facts if item.visibility == "hidden"}

        self.assertTrue(hidden_ids)
        self.assertTrue(hidden_ids.isdisjoint(observed_ids))

    def test_state_transition_records_cause_and_source_state(self):
        future = CandidateFuture(
            future_id="future_move",
            summary="Move to the computer lab",
            estimated_plausibility=0.7,
            time_horizon="hours",
            supporting_hypotheses=["hyp_access"],
            agent_actions=[AgentAction(agent_id="lin_xia", action="move_to_computer_lab")],
            expected_state_changes=[
                StateChange(
                    path="agents.lin_xia.location_id",
                    old_value="dorm",
                    new_value="computer_lab",
                    reason="Collect direct network evidence",
                    future_id="future_move",
                )
            ],
        )
        next_state = WorldTransition().apply(self.state, future)
        provenance = next_state.history[-1]

        self.assertEqual(provenance.source_state_id, self.state.state_id)
        self.assertEqual(provenance.target_state_id, next_state.state_id)
        self.assertEqual(provenance.cause, "Collect direct network evidence")
        self.assertEqual(provenance.supporting_hypothesis_ids, ["hyp_access"])


if __name__ == "__main__":
    unittest.main()
