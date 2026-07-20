import argparse
import json

from config import DEFAULT_NUM_STEPS
from core.cognition_engine import CognitionEngine
from core.future_evaluator import FutureEvaluator
from core.future_generator import FutureGenerator
from core.image_prompt_generator import ImagePromptGenerator
from core.lens_router import LensRouter
from core.model_utils import to_dict
from core.narrative_engine import NarrativeEngine
from core.observation_engine import ObservationEngine
from core.output_exporter import OutputExporter
from core.scene_generator import SceneGenerator
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
    lens_router = LensRouter()
    future_generator = FutureGenerator()
    future_evaluator = FutureEvaluator()
    transition = WorldTransition()
    narrative_engine = NarrativeEngine()
    scene_generator = SceneGenerator()
    image_prompt_generator = ImagePromptGenerator()

    objective_state, agents, subjective_models = initializer.initialize(user_input)

    objective_states = [objective_state]
    all_observations = []
    all_mental_models = []
    all_bias_filter_results = []
    all_interpretations = []
    all_hypotheses = []
    all_candidate_futures = []
    selected_futures = []
    narrative_events = []
    scene_cards = []
    image_prompts = []

    for _ in range(max(1, steps)):
        observations = observation_engine.observe(objective_state, subjective_models)
        subjective_models, mental_models, bias_filter_results, interpretations = cognition_engine.interpret(
            observations,
            subjective_models,
        )
        hypotheses = lens_router.analyze(objective_state, subjective_models)
        futures = future_generator.generate(objective_state, subjective_models, hypotheses)
        selected_future = future_evaluator.select(futures, objective_state, subjective_models, hypotheses)
        new_state = transition.apply(objective_state, selected_future)
        narrative_event = narrative_engine.express(objective_state, new_state, selected_future, subjective_models)
        scene_card = scene_generator.generate(new_state, narrative_event)
        image_prompt = image_prompt_generator.generate(scene_card)

        all_observations.extend(observations)
        all_mental_models.extend(mental_models)
        all_bias_filter_results.extend(bias_filter_results)
        all_interpretations.extend(interpretations)
        all_hypotheses.extend(hypotheses)
        all_candidate_futures.extend(futures)
        selected_futures.append(selected_future)
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
            subjective_models=subjective_models,
            mental_models=all_mental_models,
            bias_filter_results=all_bias_filter_results,
            interpretations=all_interpretations,
            hypotheses=all_hypotheses,
            candidate_futures=all_candidate_futures,
            selected_futures=selected_futures,
            narrative_events=narrative_events,
            scene_cards=scene_cards,
            image_prompts=image_prompts,
        )

    return {
        "run_dir": str(run_dir) if run_dir else None,
        "objective_states": to_dict(objective_states),
        "agent_profiles": to_dict(agents),
        "observations": to_dict(all_observations),
        "subjective_models": to_dict(subjective_models),
        "mental_models": to_dict(all_mental_models),
        "bias_filter_results": to_dict(all_bias_filter_results),
        "interpretations": to_dict(all_interpretations),
        "hypotheses": to_dict(all_hypotheses),
        "candidate_futures": to_dict(all_candidate_futures),
        "selected_futures": to_dict(selected_futures),
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
