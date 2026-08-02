import unittest

from pydantic import ValidationError

from app import run_pipeline
from core.future_generator import FutureGenerator
from core.lens_router import LensRouter
from core.world_initializer import WorldInitializer
from core.world_transition import WorldTransition
from schemas import CandidateFuture, FutureMechanism, StateChange


class FutureGeneratorTest(unittest.TestCase):
    def test_generates_three_to_five_mechanically_distinct_world_branches(self):
        result = run_pipeline("校园监控", steps=1, export=False)
        futures = result["candidate_futures"]

        self.assertGreaterEqual(len(futures), 3)
        self.assertLessEqual(len(futures), 5)
        self.assertEqual(
            {item["mechanism"]["mechanism_type"] for item in futures},
            {
                "information_discovery",
                "social_coordination",
                "institutional_contestation",
                "process_inertia",
            },
        )
        for future in futures:
            self.assertEqual(future["source_state_id"], "state_000")
            self.assertTrue(future["agent_actions"])
            self.assertTrue(future["expected_state_changes"])
            self.assertTrue(future["uncertainties"])
            self.assertTrue(future["risks"])
            self.assertTrue(future["mechanism"]["drivers"])
            self.assertTrue(future["mechanism"]["mediators"])
            self.assertTrue(future["mechanism"]["constraints"])
            self.assertTrue(future["generation_rationale"])

    def test_hypothesis_binding_uses_action_effects_and_agent_scope(self):
        result = run_pipeline("校园监控", steps=1, export=False)
        hypotheses = {
            item["hypothesis_id"]: item for item in result["hypotheses"]
        }
        for future in result["candidate_futures"]:
            action = future["agent_actions"][0]
            self.assertEqual(
                future["mechanism"]["source_hypothesis_ids"],
                future["supporting_hypotheses"],
            )
            for hypothesis_id in future["supporting_hypotheses"]:
                hypothesis = hypotheses[hypothesis_id]
                self.assertIn(action["action"], hypothesis["promotes_actions"])
                self.assertIn(action["agent_id"], hypothesis["affected_agents"])
            for hypothesis_id in future["opposing_hypotheses"]:
                hypothesis = hypotheses[hypothesis_id]
                self.assertIn(action["action"], hypothesis["inhibits_actions"])
                self.assertIn(action["agent_id"], hypothesis["affected_agents"])

    def test_every_branch_applies_a_real_bounded_state_change(self):
        state, _, models = WorldInitializer().initialize("校园监控")
        hypotheses = LensRouter().analyze(state, models)
        futures = FutureGenerator().generate(state, models, hypotheses)

        for future in futures:
            next_state = WorldTransition().apply(state, future)
            change = future.expected_state_changes[0]
            self.assertEqual(self._read_path(next_state, change.path), change.new_value)
            self.assertEqual(self._read_path(state, change.path), change.old_value)
            self.assertNotEqual(change.old_value, change.new_value)
            self.assertEqual(next_state.step, state.step + 1)

    def test_supporting_mechanisms_raise_generated_plausibility(self):
        state, _, models = WorldInitializer().initialize("校园监控")
        hypotheses = LensRouter().analyze(state, models)
        generator = FutureGenerator()
        baseline = generator.generate(state, models, hypotheses)
        without_secret_support = generator.generate(
            state,
            models,
            [
                item
                for item in hypotheses
                if "secretly_collect_network_evidence"
                not in item.promotes_actions
            ],
        )
        baseline_secret = next(
            item for item in baseline if item.future_id.endswith("secret")
        )
        ablated_secret = next(
            item
            for item in without_secret_support
            if item.future_id.endswith("secret")
        )

        self.assertTrue(baseline_secret.supporting_hypotheses)
        self.assertFalse(ablated_secret.supporting_hypotheses)
        self.assertGreater(
            baseline_secret.estimated_plausibility,
            ablated_secret.estimated_plausibility,
        )

    def test_actor_is_selected_from_subjective_models_instead_of_hardcoded(self):
        state, _, models = WorldInitializer().initialize("校园监控")
        by_agent = {item.agent_id: item for item in models}
        by_agent["lin_xia"].values["truth"].base_weight = 0.0
        by_agent["lin_xia"].values["freedom"].base_weight = 0.0
        by_agent["lin_xia"].epistemology.trust_data = 0.0
        by_agent["lin_xia"].epistemology.trust_authority = 1.0
        by_agent["wang_chen"].values["truth"].base_weight = 1.0
        by_agent["wang_chen"].values["freedom"].base_weight = 1.0
        by_agent["wang_chen"].epistemology.trust_data = 1.0
        by_agent["wang_chen"].epistemology.trust_authority = 0.0

        futures = FutureGenerator().generate(state, models, [])

        self.assertEqual(
            {action.agent_id for future in futures for action in future.agent_actions},
            {"wang_chen"},
        )

    def test_multi_step_generation_preserves_diversity_without_noop_changes(self):
        result = run_pipeline("校园监控", steps=3, export=False)
        futures = result["candidate_futures"]
        for start in range(0, len(futures), 4):
            step_futures = futures[start : start + 4]
            self.assertEqual(
                len({item["mechanism"]["mechanism_type"] for item in step_futures}),
                4,
            )
        for selected in result["selected_futures"]:
            change = selected["expected_state_changes"][0]
            self.assertNotEqual(change["old_value"], change["new_value"])

    def test_candidate_future_rejects_broken_mechanism_references(self):
        mechanism = FutureMechanism(
            mechanism_id="mechanism_invalid",
            mechanism_type="information_discovery",
            description="invalid reference test",
            drivers=["driver"],
            mediators=["mediator"],
            constraints=["constraint"],
            source_hypothesis_ids=["hyp_other"],
        )
        with self.assertRaises(ValidationError):
            CandidateFuture(
                future_id="future_invalid",
                source_state_id="state_000",
                summary="invalid",
                estimated_plausibility=0.5,
                time_horizon="hours",
                supporting_hypotheses=["hyp_expected"],
                mechanism=mechanism,
                expected_state_changes=[
                    StateChange(
                        path="agents.lin_xia.status",
                        old_value="awake",
                        new_value="investigating",
                        reason="test",
                        future_id="future_invalid",
                    )
                ],
            )

    def _read_path(self, state, path):
        current = state
        for part in path.split("."):
            current = current[part] if isinstance(current, dict) else getattr(current, part)
        return current


if __name__ == "__main__":
    unittest.main()
