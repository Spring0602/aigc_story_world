import argparse
import json

from config import DEFAULT_NUM_STEPS
from core.agent_action_model import AgentActionModel
from core.cognition_engine import CognitionEngine
from core.decision_engine import ActionExecutor, DecisionEngine
from core.economic_engine import EconomicEngine
from core.future_evaluator import FutureEvaluator
from core.future_generator import FutureGenerator
from core.fabula_builder import FabulaBuilder
from core.image_prompt_generator import ImagePromptGenerator
from core.lens_router import LensRouter
from core.model_utils import to_dict
from core.narrative_engine import NarrativeEngine
from core.narrative_planner import NarrativePlanner
from core.observation_engine import ObservationEngine
from core.output_exporter import OutputExporter
from core.possible_world_engine import PossibleWorldEngine
from core.psychology_engine import PsychologyEngine
from core.scene_generator import SceneGenerator
from core.social_structure_engine import SocialStructureEngine
from core.theory_of_mind import TheoryOfMindEngine
from core.world_initializer import WorldInitializer
from core.world_transition import WorldTransition
from schemas import SubjectiveWorldModel


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="StoryWorld V2 command line prototype")
    parser.add_argument("--input", "-i", default="校园监控：学校部署不透明的网络异常流量检测系统。")
    parser.add_argument("--steps", "-n", type=int, default=DEFAULT_NUM_STEPS)
    parser.add_argument("--no-export", action="store_true")
    parser.add_argument(
        "--no-subjective-models",
        action="store_true",
        help="replace configured subjective models with neutral agent carriers",
    )
    return parser


def run_pipeline(
    user_input: str,
    steps: int = DEFAULT_NUM_STEPS,
    export: bool = True,
    enabled_lenses: set[str] | None = None,
    use_subjective_models: bool = True,
) -> dict:
    initializer = WorldInitializer()
    observation_engine = ObservationEngine()
    cognition_engine = CognitionEngine()
    agent_action_model = AgentActionModel()
    psychology_engine = PsychologyEngine()
    theory_of_mind_engine = TheoryOfMindEngine()
    lens_router = LensRouter(enabled_lenses=enabled_lenses)
    active_lens_names = {lens.name for lens in lens_router.lenses}
    future_generator = FutureGenerator()
    future_evaluator = FutureEvaluator()
    decision_engine = DecisionEngine()
    economic_engine = EconomicEngine()
    possible_world_engine = PossibleWorldEngine()
    social_structure_engine = SocialStructureEngine()
    action_executor = ActionExecutor()
    transition = WorldTransition()
    narrative_engine = NarrativeEngine()
    fabula_builder = FabulaBuilder()
    narrative_planner = NarrativePlanner()
    scene_generator = SceneGenerator()
    image_prompt_generator = ImagePromptGenerator()

    objective_state, agents, subjective_models = initializer.initialize(user_input)
    if not use_subjective_models:
        subjective_models = [
            SubjectiveWorldModel(
                agent_id=agent.agent_id,
                roles=list(agent.roles),
            )
            for agent in objective_state.agents.values()
        ]

    objective_states = [objective_state]
    all_state_provenance = list(objective_state.history)
    all_observations = []
    all_evidence = []
    all_belief_updates = []
    all_belief_states = []
    all_mental_models = []
    all_bias_filter_results = []
    all_interpretations = []
    all_perceptions = []
    all_emotional_appraisals = []
    all_stress_states = []
    all_motivation_states = []
    all_information_boundaries = []
    all_possible_worlds = []
    all_world_evidence_assessments = []
    all_prior_belief_distributions = []
    all_world_revisions = []
    all_posterior_belief_distributions = []
    all_possible_world_beliefs = []
    all_scarcity_assessments = []
    all_information_asymmetries = []
    all_incentive_assessments = []
    all_opportunity_costs = []
    all_economic_action_evaluations = []
    all_role_assessments = []
    all_norm_pressures = []
    all_institution_powers = []
    all_social_action_evaluations = []
    all_other_models = []
    all_hypotheses = []
    all_hypothesis_relations = []
    all_unresolved_hypothesis_conflicts = []
    all_future_scores = []
    all_future_evaluations = []
    all_agent_action_decisions = []
    all_candidate_futures = []
    selected_futures = []
    all_value_assessments = []
    all_decisions = []
    all_actions = []
    all_world_events = []
    narrative_events = []
    narrative_importance_assessments = []
    subjective_model_snapshots = []
    fabulas = []
    narrative_plans = []
    syuzhets = []
    focalizations = []
    story_outputs = []
    scene_cards = []
    image_prompts = []

    for _ in range(max(1, steps)):
        observations = observation_engine.observe(objective_state, subjective_models)
        perceptions = psychology_engine.perceive(
            objective_state,
            observations,
            subjective_models,
        )
        cognition = cognition_engine.interpret(
            observations,
            subjective_models,
            perceptions=perceptions,
        )
        subjective_models = cognition.subjective_models
        psychology = psychology_engine.appraise(
            perceptions,
            subjective_models,
            cognition.belief_states,
            cognition.interpretations,
        )
        active_psychology = (
            psychology
            if "psychology" in active_lens_names
            else type(psychology)()
        )
        subjective_models, other_models = theory_of_mind_engine.infer(
            objective_state,
            observations,
            subjective_models,
        )
        economics = economic_engine.assess_context(
            objective_state,
            subjective_models,
            observations,
            cognition.belief_states,
        )
        possible_worlds = possible_world_engine.build_context(
            observations=observations,
            evidence=cognition.evidence,
            information_boundaries=economics.information_boundaries,
            subjective_models=subjective_models,
            step=objective_state.step,
        )
        social = social_structure_engine.assess_context(
            objective_state,
            observations,
            subjective_models,
            cognition.belief_states,
        )
        lens_analysis = lens_router.route(
            objective_state,
            subjective_models,
            psychology=psychology,
            economics=economics,
            social=social,
        )
        hypotheses = lens_analysis.hypotheses
        agent_action_decisions = agent_action_model.evaluate(
            subjective_models=subjective_models,
            belief_states=cognition.belief_states,
            possible_worlds=possible_worlds,
            psychology=active_psychology,
            information_boundaries=economics.information_boundaries,
            other_models=other_models,
            hypotheses=hypotheses,
            step=objective_state.step + 1,
            economics=(
                economics if "economic" in active_lens_names else None
            ),
            social=(
                social if "social_structure" in active_lens_names else None
            ),
        )
        futures = future_generator.generate(
            objective_state,
            subjective_models,
            hypotheses,
            possible_world_context=possible_worlds,
            action_decisions=agent_action_decisions,
        )
        economics = economic_engine.evaluate_actions(
            economics,
            futures,
            subjective_models,
            step=objective_state.step + 1,
            motivation_states=active_psychology.motivation_states,
        )
        social = social_structure_engine.evaluate_actions(
            social,
            objective_state,
            futures,
            active_psychology,
            cognition.bias_results,
            cognition.mental_models,
            step=objective_state.step + 1,
        )
        future_evaluations = [
            future_evaluator.evaluate(
                future,
                objective_state,
                subjective_models,
                hypotheses,
                lens_analysis.relations,
                agent_action_decisions,
            )
            for future in futures
        ]
        future_scores = {
            evaluation.future_id: evaluation.score_breakdown.final_score
            for evaluation in future_evaluations
        }
        all_future_scores.extend(
            {
                "step": objective_state.step + 1,
                "future_id": future_id,
                "score": score,
            }
            for future_id, score in future_scores.items()
        )
        selected_future, value_assessments, decisions = decision_engine.decide(
            candidate_futures=futures,
            future_scores=future_scores,
            subjective_models=subjective_models,
            belief_states=cognition.belief_states,
            interpretations=cognition.interpretations,
            other_models=other_models,
            step=objective_state.step + 1,
            psychology=(
                psychology
                if "psychology" in active_lens_names
                else None
            ),
            economics=(
                economics if "economic" in active_lens_names else None
            ),
            social=(
                social if "social_structure" in active_lens_names else None
            ),
            action_decisions=agent_action_decisions,
        )
        actions = action_executor.execute(decisions)
        selected_evaluation = next(
            item
            for item in future_evaluations
            if item.future_id == selected_future.future_id
        )
        previous_history_length = len(objective_state.history)
        new_state = transition.apply(
            objective_state,
            selected_future,
            actions=actions,
            decisions=decisions,
            action_decisions=agent_action_decisions,
            value_assessments=value_assessments,
            future_evaluation=selected_evaluation,
        )
        all_state_provenance.extend(
            new_state.history[previous_history_length:]
        )
        world_events = new_state.events[len(objective_state.events) :]

        all_observations.extend(observations)
        all_evidence.extend(cognition.evidence)
        all_belief_updates.extend(cognition.belief_updates)
        all_belief_states.extend(cognition.belief_states)
        all_mental_models.extend(cognition.mental_models)
        all_bias_filter_results.extend(cognition.bias_results)
        all_interpretations.extend(cognition.interpretations)
        all_perceptions.extend(psychology.perceptions)
        all_emotional_appraisals.extend(psychology.emotional_appraisals)
        all_stress_states.extend(psychology.stress_states)
        all_motivation_states.extend(psychology.motivation_states)
        all_information_boundaries.extend(economics.information_boundaries)
        all_possible_worlds.extend(possible_worlds.possible_worlds)
        all_world_evidence_assessments.extend(
            possible_worlds.evidence_assessments
        )
        all_prior_belief_distributions.extend(
            possible_worlds.prior_distributions
        )
        all_world_revisions.extend(possible_worlds.revisions)
        all_posterior_belief_distributions.extend(
            possible_worlds.posterior_distributions
        )
        all_possible_world_beliefs.extend(possible_worlds.new_beliefs)
        all_scarcity_assessments.extend(economics.scarcity_assessments)
        all_information_asymmetries.extend(economics.information_asymmetries)
        all_incentive_assessments.extend(economics.incentive_assessments)
        all_opportunity_costs.extend(economics.opportunity_costs)
        all_economic_action_evaluations.extend(economics.action_evaluations)
        all_role_assessments.extend(social.role_assessments)
        all_norm_pressures.extend(social.norm_pressures)
        all_institution_powers.extend(social.institution_powers)
        all_social_action_evaluations.extend(social.action_evaluations)
        all_other_models.extend(other_models)
        all_hypotheses.extend(hypotheses)
        all_hypothesis_relations.extend(lens_analysis.relations)
        all_unresolved_hypothesis_conflicts.extend(
            lens_analysis.unresolved_conflict_ids
        )
        all_candidate_futures.extend(futures)
        all_agent_action_decisions.extend(agent_action_decisions)
        all_future_evaluations.extend(future_evaluations)
        selected_futures.append(selected_future)
        all_value_assessments.extend(value_assessments)
        all_decisions.extend(decisions)
        all_actions.extend(actions)
        all_world_events.extend(world_events)
        objective_states.append(new_state)
        subjective_model_snapshots.append(
            [item.model_copy(deep=True) for item in subjective_models]
        )
        objective_state = new_state

    fabula = fabula_builder.build(objective_states, all_state_provenance)
    fabulas.append(fabula)
    world_events_by_id = {
        item.event_id: item for item in all_world_events
    }
    evaluations_by_future = {
        item.future_id: item for item in all_future_evaluations
    }
    for fabula_event in fabula.events:
        future = next(
            item
            for item in selected_futures
            if item.source_state_id == fabula_event.source_state_id
        )
        assessment = narrative_engine.importance.assess(
            objective_states[fabula_event.step - 1],
            objective_states[fabula_event.step],
            world_events_by_id[fabula_event.world_event_id],
            future,
            subjective_model_snapshots[fabula_event.step - 1],
            evaluations_by_future[future.future_id],
            fabula_event=fabula_event,
        )
        narrative_importance_assessments.append(assessment)

    narrative_plan = narrative_planner.plan(
        fabula,
        narrative_importance_assessments,
    )
    narrative_plans.append(narrative_plan)
    syuzhet = narrative_planner.arrange(fabula, narrative_plan)
    syuzhets.append(syuzhet)
    focalizations = narrative_planner.focalize(
        fabula,
        syuzhet,
        objective_states[-1],
        all_observations,
    )
    fabula_events_by_id = {
        item.fabula_event_id: item for item in fabula.events
    }
    assessments_by_fabula_event = {
        item.source_fabula_event_id: item
        for item in narrative_importance_assessments
    }
    for focalization in focalizations:
        fabula_event = fabula_events_by_id[focalization.fabula_event_id]
        narrative_event = narrative_engine.express_planned(
            objective_states[fabula_event.step],
            fabula_event,
            narrative_plan,
            syuzhet,
            focalization,
            assessments_by_fabula_event[fabula_event.fabula_event_id],
            subjective_model_snapshots[fabula_event.step - 1],
        )
        narrative_events.append(narrative_event)
        scene_card = scene_generator.generate(
            objective_states[fabula_event.step],
            narrative_event,
        )
        scene_cards.append(scene_card)
        image_prompts.append(image_prompt_generator.generate(scene_card))
    story_outputs.append(
        narrative_planner.story_output(
            fabula,
            narrative_plan,
            syuzhet,
            focalizations,
            narrative_events,
        )
    )

    run_dir = None
    if export:
        run_dir = OutputExporter().export_all(
            objective_states=objective_states,
            state_provenance=all_state_provenance,
            agents=agents,
            observations=all_observations,
            evidence=all_evidence,
            belief_updates=all_belief_updates,
            belief_states=all_belief_states,
            subjective_models=subjective_models,
            mental_models=all_mental_models,
            bias_filter_results=all_bias_filter_results,
            interpretations=all_interpretations,
            perceptions=all_perceptions,
            emotional_appraisals=all_emotional_appraisals,
            stress_states=all_stress_states,
            motivation_states=all_motivation_states,
            information_boundaries=all_information_boundaries,
            possible_worlds=all_possible_worlds,
            world_evidence_assessments=all_world_evidence_assessments,
            prior_belief_distributions=all_prior_belief_distributions,
            world_revisions=all_world_revisions,
            posterior_belief_distributions=(
                all_posterior_belief_distributions
            ),
            possible_world_beliefs=all_possible_world_beliefs,
            scarcity_assessments=all_scarcity_assessments,
            information_asymmetries=all_information_asymmetries,
            incentive_assessments=all_incentive_assessments,
            opportunity_costs=all_opportunity_costs,
            economic_action_evaluations=all_economic_action_evaluations,
            role_assessments=all_role_assessments,
            norm_pressures=all_norm_pressures,
            institution_powers=all_institution_powers,
            social_action_evaluations=all_social_action_evaluations,
            beliefs_about_others=all_other_models,
            hypotheses=all_hypotheses,
            hypothesis_relations=all_hypothesis_relations,
            candidate_futures=all_candidate_futures,
            agent_action_decisions=all_agent_action_decisions,
            future_evaluations=all_future_evaluations,
            selected_futures=selected_futures,
            value_assessments=all_value_assessments,
            decisions=all_decisions,
            actions=all_actions,
            world_events=all_world_events,
            fabulas=fabulas,
            narrative_importance_assessments=(
                narrative_importance_assessments
            ),
            narrative_plans=narrative_plans,
            syuzhets=syuzhets,
            focalizations=focalizations,
            story_outputs=story_outputs,
            narrative_events=narrative_events,
            scene_cards=scene_cards,
            image_prompts=image_prompts,
        )

    return {
        "run_dir": str(run_dir) if run_dir else None,
        "enabled_lenses": sorted(active_lens_names),
        "subjective_models_enabled": use_subjective_models,
        "objective_states": to_dict(objective_states),
        "state_provenance": to_dict(all_state_provenance),
        "agent_profiles": to_dict(agents),
        "observations": to_dict(all_observations),
        "evidence": to_dict(all_evidence),
        "belief_updates": to_dict(all_belief_updates),
        "belief_states": to_dict(all_belief_states),
        "subjective_models": to_dict(subjective_models),
        "mental_models": to_dict(all_mental_models),
        "bias_filter_results": to_dict(all_bias_filter_results),
        "interpretations": to_dict(all_interpretations),
        "perceptions": to_dict(all_perceptions),
        "emotional_appraisals": to_dict(all_emotional_appraisals),
        "stress_states": to_dict(all_stress_states),
        "motivation_states": to_dict(all_motivation_states),
        "information_boundaries": to_dict(all_information_boundaries),
        "possible_worlds": to_dict(all_possible_worlds),
        "world_evidence_assessments": to_dict(
            all_world_evidence_assessments
        ),
        "prior_belief_distributions": to_dict(
            all_prior_belief_distributions
        ),
        "world_revisions": to_dict(all_world_revisions),
        "posterior_belief_distributions": to_dict(
            all_posterior_belief_distributions
        ),
        "possible_world_beliefs": to_dict(all_possible_world_beliefs),
        "scarcity_assessments": to_dict(all_scarcity_assessments),
        "information_asymmetries": to_dict(all_information_asymmetries),
        "incentive_assessments": to_dict(all_incentive_assessments),
        "opportunity_costs": to_dict(all_opportunity_costs),
        "economic_action_evaluations": to_dict(
            all_economic_action_evaluations
        ),
        "role_assessments": to_dict(all_role_assessments),
        "norm_pressures": to_dict(all_norm_pressures),
        "institution_powers": to_dict(all_institution_powers),
        "social_action_evaluations": to_dict(
            all_social_action_evaluations
        ),
        "beliefs_about_others": to_dict(all_other_models),
        "hypotheses": to_dict(all_hypotheses),
        "hypothesis_relations": to_dict(all_hypothesis_relations),
        "unresolved_hypothesis_conflicts": list(
            all_unresolved_hypothesis_conflicts
        ),
        "future_scores": all_future_scores,
        "future_evaluations": to_dict(all_future_evaluations),
        "candidate_futures": to_dict(all_candidate_futures),
        "agent_action_decisions": to_dict(all_agent_action_decisions),
        "selected_futures": to_dict(selected_futures),
        "value_assessments": to_dict(all_value_assessments),
        "decisions": to_dict(all_decisions),
        "actions": to_dict(all_actions),
        "world_events": to_dict(all_world_events),
        "fabulas": to_dict(fabulas),
        "narrative_importance_assessments": to_dict(
            narrative_importance_assessments
        ),
        "narrative_events": to_dict(narrative_events),
        "narrative_plans": to_dict(narrative_plans),
        "syuzhets": to_dict(syuzhets),
        "focalizations": to_dict(focalizations),
        "story_outputs": to_dict(story_outputs),
        "scene_cards": to_dict(scene_cards),
        "image_prompts": to_dict(image_prompts),
    }


def main() -> None:
    args = build_parser().parse_args()
    result = run_pipeline(
        args.input,
        args.steps,
        export=not args.no_export,
        use_subjective_models=not args.no_subjective_models,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["run_dir"]:
        print(f"\n结果已保存到：{result['run_dir']}")


if __name__ == "__main__":
    main()
