import argparse
import json

from config import DEFAULT_NUM_STEPS
from core.cognition_engine import CognitionEngine
from core.decision_engine import ActionExecutor, DecisionEngine
from core.future_evaluator import FutureEvaluator
from core.future_generator import FutureGenerator
from core.image_prompt_generator import ImagePromptGenerator
from core.lens_router import LensRouter
from core.model_utils import to_dict
from core.narrative_engine import NarrativeEngine
from core.observation_engine import ObservationEngine
from core.output_exporter import OutputExporter
from core.scene_generator import SceneGenerator
from core.theory_of_mind import TheoryOfMindEngine
from core.world_initializer import WorldInitializer
from core.world_transition import WorldTransition


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="StoryWorld V2 command line prototype")
    parser.add_argument("--input", "-i", default="校园监控：学校部署不透明的网络异常流量检测系统。")
    parser.add_argument("--steps", "-n", type=int, default=DEFAULT_NUM_STEPS)
    parser.add_argument("--no-export", action="store_true")
    return parser


def run_pipeline(user_input: str, steps: int = DEFAULT_NUM_STEPS, export: bool = True) -> dict:
    initializer = WorldInitializer()
    observation_engine = ObservationEngine()
    cognition_engine = CognitionEngine()
    theory_of_mind_engine = TheoryOfMindEngine()
    lens_router = LensRouter()
    future_generator = FutureGenerator()
    future_evaluator = FutureEvaluator()
    decision_engine = DecisionEngine()
    action_executor = ActionExecutor()
    transition = WorldTransition()
    narrative_engine = NarrativeEngine()
    scene_generator = SceneGenerator()
    image_prompt_generator = ImagePromptGenerator()

    objective_state, agents, subjective_models = initializer.initialize(user_input)

    objective_states = [objective_state]
    all_observations = []
    all_evidence = []
    all_belief_updates = []
    all_belief_states = []
    all_mental_models = []
    all_bias_filter_results = []
    all_interpretations = []
    all_other_models = []
    all_hypotheses = []
    all_candidate_futures = []
    selected_futures = []
    all_value_assessments = []
    all_decisions = []
    all_actions = []
    all_world_events = []
    narrative_events = []
    scene_cards = []
    image_prompts = []

    for _ in range(max(1, steps)):
        observations = observation_engine.observe(objective_state, subjective_models)
        cognition = cognition_engine.interpret(
            observations,
            subjective_models,
        )
        subjective_models = cognition.subjective_models
        subjective_models, other_models = theory_of_mind_engine.infer(
            objective_state,
            observations,
            subjective_models,
        )
        hypotheses = lens_router.analyze(objective_state, subjective_models)
        futures = future_generator.generate(objective_state, subjective_models, hypotheses)
        future_scores = {
            future.future_id: future_evaluator.score(
                future,
                objective_state,
                subjective_models,
                hypotheses,
            )
            for future in futures
        }
        selected_future, value_assessments, decisions = decision_engine.decide(
            candidate_futures=futures,
            future_scores=future_scores,
            subjective_models=subjective_models,
            belief_states=cognition.belief_states,
            interpretations=cognition.interpretations,
            other_models=other_models,
            step=objective_state.step + 1,
        )
        actions = action_executor.execute(decisions)
        new_state = transition.apply(
            objective_state,
            selected_future,
            actions=actions,
            decisions=decisions,
        )
        world_events = new_state.events[len(objective_state.events) :]
        narrative_event = narrative_engine.express(objective_state, new_state, selected_future, subjective_models)
        scene_card = scene_generator.generate(new_state, narrative_event)
        image_prompt = image_prompt_generator.generate(scene_card)

        all_observations.extend(observations)
        all_evidence.extend(cognition.evidence)
        all_belief_updates.extend(cognition.belief_updates)
        all_belief_states.extend(cognition.belief_states)
        all_mental_models.extend(cognition.mental_models)
        all_bias_filter_results.extend(cognition.bias_results)
        all_interpretations.extend(cognition.interpretations)
        all_other_models.extend(other_models)
        all_hypotheses.extend(hypotheses)
        all_candidate_futures.extend(futures)
        selected_futures.append(selected_future)
        all_value_assessments.extend(value_assessments)
        all_decisions.extend(decisions)
        all_actions.extend(actions)
        all_world_events.extend(world_events)
        objective_states.append(new_state)
        narrative_events.append(narrative_event)
        scene_cards.append(scene_card)
        image_prompts.append(image_prompt)
        objective_state = new_state

    run_dir = None
    if export:
        run_dir = OutputExporter().export_all(
            objective_states=objective_states,
            agents=agents,
            observations=all_observations,
            evidence=all_evidence,
            belief_updates=all_belief_updates,
            belief_states=all_belief_states,
            subjective_models=subjective_models,
            mental_models=all_mental_models,
            bias_filter_results=all_bias_filter_results,
            interpretations=all_interpretations,
            beliefs_about_others=all_other_models,
            hypotheses=all_hypotheses,
            candidate_futures=all_candidate_futures,
            selected_futures=selected_futures,
            value_assessments=all_value_assessments,
            decisions=all_decisions,
            actions=all_actions,
            world_events=all_world_events,
            narrative_events=narrative_events,
            scene_cards=scene_cards,
            image_prompts=image_prompts,
        )

    return {
        "run_dir": str(run_dir) if run_dir else None,
        "objective_states": to_dict(objective_states),
        "agent_profiles": to_dict(agents),
        "observations": to_dict(all_observations),
        "evidence": to_dict(all_evidence),
        "belief_updates": to_dict(all_belief_updates),
        "belief_states": to_dict(all_belief_states),
        "subjective_models": to_dict(subjective_models),
        "mental_models": to_dict(all_mental_models),
        "bias_filter_results": to_dict(all_bias_filter_results),
        "interpretations": to_dict(all_interpretations),
        "beliefs_about_others": to_dict(all_other_models),
        "hypotheses": to_dict(all_hypotheses),
        "candidate_futures": to_dict(all_candidate_futures),
        "selected_futures": to_dict(selected_futures),
        "value_assessments": to_dict(all_value_assessments),
        "decisions": to_dict(all_decisions),
        "actions": to_dict(all_actions),
        "world_events": to_dict(all_world_events),
        "narrative_events": to_dict(narrative_events),
        "scene_cards": to_dict(scene_cards),
        "image_prompts": to_dict(image_prompts),
    }


def main() -> None:
    args = build_parser().parse_args()
    result = run_pipeline(args.input, args.steps, export=not args.no_export)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["run_dir"]:
        print(f"\n结果已保存到：{result['run_dir']}")


if __name__ == "__main__":
    main()
