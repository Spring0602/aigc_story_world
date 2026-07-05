import argparse
import json

from config import DEFAULT_NUM_EVENTS
from core.image_prompt_generator import ImagePromptGenerator
from core.input_parser import InputParser
from core.llm_client import LLMClient
from core.output_exporter import OutputExporter
from core.plot_engine import PlotEngine
from core.scene_generator import SceneGenerator
from core.state_updater import StateUpdater
from core.world_initializer import WorldInitializer
from core.world_state import WorldStateManager


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="StoryWorld 命令行原型")
    parser.add_argument("--input", "-i", help="一句话故事设定")
    parser.add_argument(
        "--num-events",
        "-n",
        type=int,
        default=DEFAULT_NUM_EVENTS,
        help="生成事件数量，默认 1",
    )
    return parser


def run_pipeline(user_input: str, num_events: int) -> dict:
    llm = LLMClient()
    input_parser = InputParser(llm)
    initializer = WorldInitializer(llm)
    plot_engine = PlotEngine(llm)
    updater = StateUpdater(llm)
    scene_generator = SceneGenerator(llm)
    prompt_generator = ImagePromptGenerator(llm)
    exporter = OutputExporter()

    story_setting = input_parser.parse(user_input)
    initial_world_state, characters = initializer.init(story_setting)
    state_manager = WorldStateManager(initial_world_state)

    events = []
    scenes = []
    image_prompts = []

    for step in range(1, num_events + 1):
        current_state = state_manager.get_current_state()
        event = plot_engine.generate_event(current_state, step)
        updated_state = updater.update(current_state, event)
        state_manager.update_state(updated_state)
        scene = scene_generator.generate_scene(updated_state, event)
        image_prompt = prompt_generator.generate(scene)

        events.append(event)
        scenes.append(scene)
        image_prompts.append(image_prompt)

    run_dir = exporter.export_all(
        story_setting=story_setting,
        characters=characters,
        world_states=state_manager.get_history(),
        events=events,
        scenes=scenes,
        prompts=image_prompts,
    )

    return {
        "run_dir": str(run_dir),
        "story_setting": story_setting,
        "world_states": state_manager.get_history(),
        "events": events,
        "scenes": scenes,
        "image_prompts": image_prompts,
    }


def main() -> None:
    args = build_parser().parse_args()
    user_input = args.input or input("请输入故事设定：").strip()
    result = run_pipeline(user_input, max(1, args.num_events))

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n结果已保存到：{result['run_dir']}")


if __name__ == "__main__":
    main()

