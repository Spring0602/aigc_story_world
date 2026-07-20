import unittest

from core.cognition_engine import CognitionEngine
from schemas import Epistemology, Observation, SubjectiveWorldModel, Value


class InterpretationEngineTest(unittest.TestCase):
    def test_same_event_produces_three_distinct_cognitive_interpretations(self) -> None:
        shared_observation = Observation(
            observation_id="obs_shared_dataist",
            information_id="info_network_monitoring_increase",
            agent_id="dataist",
            step=1,
            source="network_terminal",
            evidence_type="data",
            content="Network monitoring increased.",
            reliability=0.9,
            visibility="public",
        )
        observations = [
            shared_observation,
            shared_observation.model_copy(
                update={"observation_id": "obs_shared_institutionalist", "agent_id": "institutionalist"}
            ),
            shared_observation.model_copy(
                update={"observation_id": "obs_shared_skeptic", "agent_id": "skeptic"}
            ),
        ]
        models = [
            SubjectiveWorldModel(
                agent_id="dataist",
                values={"freedom": Value(base_weight=0.9)},
                epistemology=Epistemology(
                    trust_data=0.95,
                    trust_authority=0.15,
                    tolerance_for_uncertainty=0.55,
                ),
            ),
            SubjectiveWorldModel(
                agent_id="institutionalist",
                values={"safety": Value(base_weight=0.9)},
                epistemology=Epistemology(
                    trust_data=0.4,
                    trust_authority=0.9,
                    tolerance_for_uncertainty=0.35,
                ),
            ),
            SubjectiveWorldModel(
                agent_id="skeptic",
                values={"truth": Value(base_weight=0.9)},
                epistemology=Epistemology(
                    trust_data=0.35,
                    trust_authority=0.2,
                    tolerance_for_uncertainty=0.85,
                ),
            ),
        ]

        updated_models, mental_models, bias_results, interpretations = CognitionEngine().interpret(
            observations,
            models,
        )
        by_agent = {item.agent_id: item for item in interpretations}
        mental_models_by_id = {item.mental_model_id: item for item in mental_models}
        bias_results_by_id = {item.bias_filter_id: item for item in bias_results}

        self.assertEqual({item.information_id for item in observations}, {"info_network_monitoring_increase"})
        self.assertEqual({item.content for item in observations}, {"Network monitoring increased."})
        self.assertEqual(len({item.belief_basis[0] for item in interpretations}), 3)
        self.assertEqual(len({item.meaning for item in interpretations}), 3)
        self.assertEqual(len({item.action_implication for item in interpretations}), 3)
        self.assertEqual(by_agent["dataist"].meaning, "institution threatens autonomy")
        self.assertEqual(by_agent["dataist"].action_implication, "collect evidence secretly")
        self.assertEqual(by_agent["institutionalist"].meaning, "institution protects collective security")
        self.assertEqual(by_agent["institutionalist"].action_implication, "follow institutional guidance")
        self.assertEqual(by_agent["skeptic"].meaning, "the situation requires further verification")
        self.assertEqual(by_agent["skeptic"].action_implication, "seek additional evidence")
        self.assertEqual({model.agent_id for model in updated_models}, set(by_agent))
        observations_by_agent = {item.agent_id: item for item in observations}
        for model in updated_models:
            interpretation = by_agent[model.agent_id]
            observation = observations_by_agent[model.agent_id]
            belief = model.beliefs[-1]
            self.assertEqual(belief.evidence, [observation.observation_id])
            self.assertEqual(interpretation.observation_ids, [observation.observation_id])
            self.assertEqual(interpretation.belief_basis, [belief.proposition])
            self.assertIn(interpretation.mental_model_id, mental_models_by_id)
            self.assertIn(interpretation.bias_filter_id, bias_results_by_id)
            bias_result = bias_results_by_id[interpretation.bias_filter_id]
            self.assertEqual(bias_result.mental_model_id, interpretation.mental_model_id)

        applied_biases = {
            result.applied_biases[0].bias_type for result in bias_results
        }
        self.assertEqual(
            applied_biases,
            {"autonomy_threat_sensitivity", "authority_deference", "evidential_skepticism"},
        )


if __name__ == "__main__":
    unittest.main()
