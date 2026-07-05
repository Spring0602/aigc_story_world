import json
from pathlib import Path

from config import OUTPUT_DIR


class OutputExporter:
    def __init__(self, output_dir: Path = OUTPUT_DIR):
        self.output_dir = Path(output_dir)

    def export_all(
        self,
        story_setting: dict,
        characters: list[dict],
        world_states: list[dict],
        events: list[dict],
        scenes: list[dict],
        prompts: list[dict],
    ) -> Path:
        run_dir = self._next_run_dir()
        run_dir.mkdir(parents=True, exist_ok=False)

        self._write_json(run_dir / "story_setting.json", story_setting)
        self._write_json(run_dir / "character_cards.json", characters)
        self._write_json(run_dir / "world_states.json", world_states)
        self._write_json(run_dir / "event_cards.json", events)
        self._write_json(run_dir / "scene_cards.json", scenes)
        self._write_json(run_dir / "image_prompts.json", prompts)
        (run_dir / "storyboard.md").write_text(
            self._build_storyboard(story_setting, world_states, events, scenes, prompts),
            encoding="utf-8",
        )
        return run_dir

    def _next_run_dir(self) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        existing = [
            int(path.name.removeprefix("run_"))
            for path in self.output_dir.glob("run_*")
            if path.is_dir() and path.name.removeprefix("run_").isdigit()
        ]
        next_index = max(existing, default=0) + 1
        return self.output_dir / f"run_{next_index:03d}"

    def _write_json(self, path: Path, data) -> None:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _build_storyboard(
        self,
        story_setting: dict,
        world_states: list[dict],
        events: list[dict],
        scenes: list[dict],
        prompts: list[dict],
    ) -> str:
        lines = [
            "# StoryWorld Storyboard",
            "",
            f"- 题材：{story_setting.get('genre', '')}",
            f"- 核心事件：{story_setting.get('core_incident', '')}",
            f"- 初始地点：{story_setting.get('initial_location', '')}",
            "",
            "## 世界状态",
            "",
        ]
        for state in world_states:
            lines.extend(
                [
                    f"### {state.get('state_id', '')}",
                    "",
                    f"- 步骤：{state.get('step', '')}",
                    f"- 时间：{state.get('current_time', '')}",
                    f"- 地点：{state.get('current_location', '')}",
                    f"- 氛围：{state.get('atmosphere', '')}",
                    "",
                ]
            )

        lines.extend(["## 分镜", ""])
        for event, scene, image_prompt in zip(events, scenes, prompts):
            lines.extend(
                [
                    f"### {event.get('event_id', '')} / {scene.get('scene_id', '')}",
                    "",
                    f"- 剧情：{event.get('summary', '')}",
                    f"- 地点：{scene.get('location', '')}",
                    f"- 画面：{scene.get('main_action', '')}",
                    f"- 图像 Prompt：{image_prompt.get('prompt_cn', '')}",
                    "",
                ]
            )
        return "\n".join(lines)

