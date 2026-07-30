import unittest

from pydantic import ValidationError

from app import run_pipeline
from core.future_evaluator import FutureEvaluator
from core.hypothesis_conflict_resolver import HypothesisConflictResolver
from core.lens_router import LensRouter
from core.world_initializer import WorldInitializer
from schemas import (
    CandidateFuture,
    CausalHypothesis,
    HypothesisRelation,
)


class HypothesisConflictResolverTest(unittest.TestCase):
    def _hypothesis(
        self,
        hypothesis_id: str,
        lens: str,
        promotes: list[str] | None = None,
        inhibits: list[str] | None = None,
        drivers: list[str] | None = None,
    ) -> CausalHypothesis:
        return CausalHypothesis(
            hypothesis_id=hypothesis_id,
            lens=lens,
            claim=f"{lens} mechanism",
            drivers=drivers or [f"{lens}_driver"],
            mediators=[f"{lens}_mediator"],
            constraints=[f"{lens}_constraint"],
            promotes_actions=promotes or [],
            inhibits_actions=inhibits or [],
            affected_agents=["lin_xia"],
            time_scale="hours",
            confidence=0.8,
        )

    def test_router_returns_structured_cross_lens_relations(self):
        result = run_pipeline("校园监控", steps=1, export=False)
        hypothesis_ids = {
            item["hypothesis_id"] for item in result["hypotheses"]
        }

        self.assertEqual(len(result["hypotheses"]), 6)
        self.assertEqual(len(result["hypothesis_relations"]), 6)
        for relation in result["hypothesis_relations"]:
            self.assertIn(relation["source_hypothesis_id"], hypothesis_ids)
            self.assertIn(relation["target_hypothesis_id"], hypothesis_ids)
            self.assertNotEqual(
                relation["source_lens"],
                relation["target_lens"],
            )
            self.assertIn(
                relation["relation_type"],
                {"supports", "contradicts", "conditions"},
            )
            self.assertTrue(relation["basis"])

    def test_matching_action_effects_create_support_relation(self):
        source = self._hypothesis(
            "hyp_support_psy",
            "psychology",
            promotes=["secretly_collect_network_evidence"],
        )
        target = self._hypothesis(
            "hyp_support_eco",
            "economic",
            promotes=["secretly_collect_network_evidence"],
        )

        relation = HypothesisConflictResolver().resolve(
            [source, target]
        )[0]

        self.assertEqual(relation.relation_type, "supports")
        self.assertEqual(relation.resolution_status, "reinforcing")
        self.assertIn(
            "shared_action_effect:secretly_collect_network_evidence",
            relation.basis,
        )

    def test_opposed_action_effects_remain_unresolved(self):
        source = self._hypothesis(
            "hyp_conflict_psy",
            "psychology",
            promotes=["confront_authority"],
        )
        target = self._hypothesis(
            "hyp_conflict_eco",
            "economic",
            inhibits=["confront_authority"],
        )

        relation = HypothesisConflictResolver().resolve(
            [source, target]
        )[0]

        self.assertEqual(relation.relation_type, "contradicts")
        self.assertEqual(relation.resolution_status, "unresolved")
        self.assertIn(
            "opposed_action:confront_authority",
            relation.basis,
        )

    def test_indirect_relation_preserves_conditions_and_shared_drivers(self):
        source = self._hypothesis(
            "hyp_condition_psy",
            "psychology",
            drivers=["institutional_opacity:high"],
        )
        target = self._hypothesis(
            "hyp_condition_social",
            "social_structure",
            drivers=["institutional_opacity:moderate"],
        )

        relation = HypothesisConflictResolver().resolve(
            [source, target]
        )[0]

        self.assertEqual(relation.relation_type, "conditions")
        self.assertEqual(
            relation.resolution_status,
            "context_dependent",
        )
        self.assertEqual(
            relation.shared_drivers,
            ["institutional_opacity"],
        )

    def test_future_support_uses_relation_quality_not_hypothesis_count(self):
        supporting_a = self._hypothesis(
            "hyp_a",
            "psychology",
            promotes=["secretly_collect_network_evidence"],
        )
        supporting_b = self._hypothesis(
            "hyp_b",
            "economic",
            promotes=["secretly_collect_network_evidence"],
        )
        conflicting = self._hypothesis(
            "hyp_c",
            "social_structure",
            inhibits=["secretly_collect_network_evidence"],
        )
        hypotheses = [supporting_a, supporting_b, conflicting]
        relations = HypothesisConflictResolver().resolve(hypotheses)
        supported_future = CandidateFuture(
            future_id="future_supported",
            summary="supported",
            estimated_plausibility=0.5,
            time_horizon="hours",
            supporting_hypotheses=["hyp_a", "hyp_b"],
        )
        conflicted_future = CandidateFuture(
            future_id="future_conflicted",
            summary="conflicted",
            estimated_plausibility=0.5,
            time_horizon="hours",
            supporting_hypotheses=["hyp_a", "hyp_c"],
        )
        evaluator = FutureEvaluator()

        supported_score = evaluator.causal_support_score(
            supported_future,
            hypotheses,
            relations,
        )
        conflicted_score = evaluator.causal_support_score(
            conflicted_future,
            hypotheses,
            relations,
        )

        self.assertEqual(
            len(supported_future.supporting_hypotheses),
            len(conflicted_future.supporting_hypotheses),
        )
        self.assertGreater(supported_score, conflicted_score)

    def test_router_can_disable_lenses_and_rejects_unknown_names(self):
        state, _, models = WorldInitializer().initialize("校园监控")
        result = LensRouter(
            enabled_lenses={"psychology", "economic"}
        ).route(state, models)

        self.assertEqual(
            set(result.enabled_lenses),
            {"psychology", "economic"},
        )
        self.assertEqual(
            {item.lens for item in result.hypotheses},
            {"psychology", "economic"},
        )
        self.assertTrue(
            all(
                "social_structure"
                not in {item.source_lens, item.target_lens}
                for item in result.relations
            )
        )
        with self.assertRaises(ValueError):
            LensRouter(enabled_lenses={"unknown"})

    def test_relation_schema_rejects_self_reference(self):
        with self.assertRaises(ValidationError):
            HypothesisRelation(
                relation_id="relation_invalid",
                source_hypothesis_id="hyp_same",
                target_hypothesis_id="hyp_same",
                source_lens="psychology",
                target_lens="economic",
                relation_type="supports",
                basis=["same action"],
                strength=0.8,
                resolution_status="reinforcing",
            )


if __name__ == "__main__":
    unittest.main()
