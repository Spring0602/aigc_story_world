from schemas import BiasFilterResult, BiasSignal, BiasType, MentalModel, SubjectiveWorldModel


class BiasFilter:
    def apply(
        self,
        mental_model: MentalModel,
        model: SubjectiveWorldModel,
        bias_filter_id: str,
    ) -> BiasFilterResult:
        freedom = self._value_weight(model, "freedom")
        monitoring_assumption = any("surveillance" in item for item in mental_model.causal_assumptions)

        if monitoring_assumption and freedom >= 0.7:
            strength = freedom * (1.0 - model.epistemology.trust_authority)
            signal = BiasSignal(
                bias_type="autonomy_threat_sensitivity",
                strength=strength,
                rationale="High autonomy value increases the salience of surveillance risk.",
            )
            return BiasFilterResult(
                bias_filter_id=bias_filter_id,
                mental_model_id=mental_model.mental_model_id,
                applied_biases=[signal],
                filtered_causal_frame="institutional opacity enables surveillance",
                salience_focus="autonomy",
                confidence_modifier=0.05 * strength,
            )

        if model.epistemology.trust_authority >= 0.7:
            strength = model.epistemology.trust_authority
            signal = BiasSignal(
                bias_type="authority_deference",
                strength=strength,
                rationale="High authority trust favors the institution's protective explanation.",
            )
            return BiasFilterResult(
                bias_filter_id=bias_filter_id,
                mental_model_id=mental_model.mental_model_id,
                applied_biases=[signal],
                filtered_causal_frame="institutional authority frames the change as protection",
                salience_focus="collective_security",
                confidence_modifier=0.03 * strength,
            )

        if mental_model.uncertainty_tolerance >= 0.7:
            strength = mental_model.uncertainty_tolerance
            bias_type: BiasType = "evidential_skepticism"
            rationale = "High uncertainty tolerance delays commitment to a single explanation."
        else:
            strength = 1.0 - mental_model.uncertainty_tolerance
            bias_type = "ambiguity_aversion"
            rationale = "Low uncertainty tolerance increases attention to unresolved risk."

        return BiasFilterResult(
            bias_filter_id=bias_filter_id,
            mental_model_id=mental_model.mental_model_id,
            applied_biases=[
                BiasSignal(bias_type=bias_type, strength=strength, rationale=rationale)
            ],
            filtered_causal_frame="incomplete evidence leaves institutional intent uncertain",
            salience_focus="epistemic_uncertainty",
            confidence_modifier=-0.1 * strength,
        )

    def _value_weight(self, model: SubjectiveWorldModel, name: str) -> float:
        value = model.values.get(name)
        return value.base_weight if value else 0.5
