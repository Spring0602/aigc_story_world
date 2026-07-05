import json
from copy import deepcopy

from config import DEFAULT_VISUAL_STYLE


class LLMClient:
    """Mock LLM client for the first runnable prototype."""

    def generate_text(self, prompt: str) -> str:
        data = self.generate_json(prompt)
        return json.dumps(data, ensure_ascii=False, indent=2)

    def generate_json(self, prompt: str) -> dict:
        if "TASK: parse_input" in prompt:
            return self._mock_story_setting(prompt)
        if "TASK: init_world" in prompt:
            return self._mock_initial_world(prompt)
        if "TASK: generate_event" in prompt:
            return self._mock_event(prompt)
        if "TASK: update_state" in prompt:
            return self._mock_updated_state(prompt)
        if "TASK: generate_scene" in prompt:
            return self._mock_scene(prompt)
        if "TASK: generate_image_prompt" in prompt:
            return self._mock_image_prompt(prompt)
        return {}

    def _mock_story_setting(self, prompt: str) -> dict:
        user_input = prompt.split("USER_INPUT:", 1)[-1].strip()
        genre = "校园悬疑" if "校园" in user_input or "邮件" in user_input else "奇幻冒险"
        core_incident = user_input or "主角遇到一件改变命运的异常事件"
        return {
            "genre": genre,
            "theme": "未知系统与命运预警",
            "tone": ["神秘", "紧张", "压抑"],
            "protagonist_brief": "理性但敏感的年轻主角",
            "initial_location": "大学宿舍" if genre == "校园悬疑" else "边境小镇旅店",
            "initial_time": "深夜",
            "core_incident": core_incident,
            "target_audience": "喜欢悬疑、科幻和视觉小说的玩家",
            "visual_style": DEFAULT_VISUAL_STYLE,
        }

    def _mock_initial_world(self, prompt: str) -> dict:
        setting = self._extract_json(prompt, "STORY_SETTING:")
        location = setting.get("initial_location", "未知地点")
        time = setting.get("initial_time", "未知时间")
        visual_style = setting.get("visual_style", DEFAULT_VISUAL_STYLE)
        return {
            "world_state": {
                "state_id": "state_000",
                "step": 0,
                "current_time": f"第1天 {time}",
                "current_location": location,
                "atmosphere": "安静中带着不祥预感",
                "world_rules": [
                    "异常事件会留下可追踪的线索",
                    "已经确认的事实不能被无理由推翻",
                ],
                "characters": {
                    "林夏": {
                        "current_emotion": "疑惑",
                        "current_goal": "确认异常事件是否真实",
                        "location": location,
                        "status": "清醒",
                    }
                },
                "known_facts": [f"林夏遭遇了核心事件：{setting.get('core_incident', '未知事件')}"],
                "unknowns": ["异常事件的来源是什么？", "它为什么选择林夏？"],
                "unresolved_conflicts": ["林夏必须判断这是否是危险预警"],
                "events_happened": [],
                "available_locations": [location, "校园主干道", "计算机学院机房", "旧实验楼"],
                "visual_style": visual_style,
            },
            "character_cards": [
                {
                    "character_id": "char_001",
                    "name": "林夏",
                    "age": 20,
                    "gender": "女",
                    "identity": "计算机专业大学生",
                    "personality": ["理性", "敏感", "好奇心强"],
                    "goal": "查明异常事件的来源",
                    "fear": "自己的人生被未知力量操控",
                    "secret": "曾经接触过一个未公开的异常 AI 实验",
                    "current_emotion": "疑惑",
                    "relationships": {"室友": "信任但有所隐瞒", "导师": "尊敬但不完全信任"},
                    "visual_features": {
                        "hair": "黑色中长发",
                        "clothes": "宽松白色睡衣",
                        "expression": "疲惫而警觉",
                        "special_item": "旧款笔记本电脑",
                    },
                }
            ],
        }

    def _mock_event(self, prompt: str) -> dict:
        world_state = self._extract_json(prompt, "WORLD_STATE:")
        step = int(self._extract_value(prompt, "STEP:", "1"))
        location = world_state.get("current_location", "未知地点")
        clue = "屏幕上出现了未来时间戳" if step == 1 else f"第 {step} 条线索指向旧实验楼"
        return {
            "event_id": f"event_{step:03d}",
            "step": step,
            "summary": f"林夏发现{clue}",
            "stage": self._stage_for_step(step),
            "cause": "她试图验证异常事件时查看了隐藏信息",
            "effect": "她意识到事件并非普通恶作剧，危险正在靠近",
            "involved_characters": ["林夏"],
            "location": location,
            "tension_change": "升高",
            "new_clues": [clue],
            "new_conflicts": ["未来的信息为什么会提前出现？"],
            "state_changes": {
                "林夏.current_emotion": "紧张",
                "林夏.current_goal": "追查线索来源",
            },
        }

    def _mock_updated_state(self, prompt: str) -> dict:
        old_state = self._extract_json(prompt, "OLD_WORLD_STATE:")
        event = self._extract_json(prompt, "EVENT_CARD:")
        new_state = deepcopy(old_state)
        step = event.get("step", old_state.get("step", 0) + 1)
        new_state["state_id"] = f"state_{step:03d}"
        new_state["step"] = step
        new_state["atmosphere"] = "紧张、压抑，异常感更强"
        new_state.setdefault("known_facts", []).extend(event.get("new_clues", []))
        new_state.setdefault("unknowns", []).append("未来信息是否可以被改变？")
        new_state.setdefault("unresolved_conflicts", []).extend(event.get("new_conflicts", []))
        new_state.setdefault("events_happened", []).append(event.get("summary", "未知事件"))
        if "林夏" in new_state.get("characters", {}):
            new_state["characters"]["林夏"]["current_emotion"] = "紧张"
            new_state["characters"]["林夏"]["current_goal"] = "追查线索来源"
        return new_state

    def _mock_scene(self, prompt: str) -> dict:
        world_state = self._extract_json(prompt, "WORLD_STATE:")
        event = self._extract_json(prompt, "EVENT_CARD:")
        step = event.get("step", 1)
        return {
            "scene_id": f"scene_{step:03d}",
            "event_id": event.get("event_id", f"event_{step:03d}"),
            "location": event.get("location", world_state.get("current_location", "未知地点")),
            "time": world_state.get("current_time", "深夜"),
            "main_action": event.get("summary", "林夏注视着异常线索"),
            "characters": [
                {
                    "name": "林夏",
                    "pose": "坐在书桌前，身体微微前倾",
                    "expression": "脸色苍白，眼神紧张",
                }
            ],
            "camera": {
                "shot_type": "中近景",
                "angle": "略微俯视",
                "focus": "林夏的表情和发光的屏幕",
            },
            "lighting": "电脑屏幕发出幽蓝色光，房间其余部分昏暗",
            "atmosphere": world_state.get("atmosphere", "紧张、诡异"),
            "key_objects": ["笔记本电脑", "邮件界面", "电子钟", "凌乱书桌"],
            "visual_style": world_state.get("visual_style", DEFAULT_VISUAL_STYLE),
            "negative_prompt_notes": ["不要出现多人", "不要出现明亮白天", "不要出现夸张科幻设备"],
        }

    def _mock_image_prompt(self, prompt: str) -> dict:
        scene = self._extract_json(prompt, "SCENE_CARD:")
        prompt_cn = (
            f"{scene.get('visual_style', DEFAULT_VISUAL_STYLE)}，{scene.get('time', '深夜')}，"
            f"{scene.get('location', '未知地点')}，{scene.get('main_action', '主角发现异常线索')}，"
            f"{scene.get('lighting', '低调光照')}，氛围{scene.get('atmosphere', '紧张诡异')}。"
        )
        return {
            "prompt_cn": prompt_cn,
            "prompt_en": (
                "pixel art RPG game CG, 16:9, midnight, college dormitory, "
                "a young Chinese female student finds an abnormal clue on a glowing laptop screen, "
                "dim room, cold blue light, tense and eerie atmosphere, cinematic lighting"
            ),
            "negative_prompt_cn": "多人，白天，夸张科幻设备，低质量，模糊。",
            "negative_prompt_en": "multiple people, daytime, exaggerated sci-fi machines, low quality, blurry",
        }

    def _extract_json(self, prompt: str, marker: str) -> dict:
        if marker not in prompt:
            return {}
        text = prompt.split(marker, 1)[-1].strip()
        json_start_candidates = [index for index in (text.find("{"), text.find("[")) if index >= 0]
        if not json_start_candidates:
            return {}
        text = text[min(json_start_candidates) :]
        try:
            return json.JSONDecoder().raw_decode(text)[0]
        except json.JSONDecodeError:
            return {}

    def _extract_value(self, prompt: str, marker: str, default: str) -> str:
        if marker not in prompt:
            return default
        return prompt.split(marker, 1)[-1].strip().splitlines()[0]

    def _stage_for_step(self, step: int) -> str:
        if step <= 1:
            return "第一幕：异常引入"
        if step <= 3:
            return "第二幕：冲突升级"
        return "第三幕：真相逼近"
