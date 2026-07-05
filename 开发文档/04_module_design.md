# 04 模块设计文档

## 1. 模块总览

第一版系统建议拆成以下模块：

```text
core/
  ├── llm_client.py
  ├── input_parser.py
  ├── world_initializer.py
  ├── world_state.py
  ├── plot_engine.py
  ├── state_updater.py
  ├── scene_generator.py
  ├── image_prompt_generator.py
  └── output_exporter.py
```

---

## 2. LLMClient

### 职责

统一封装大模型调用。

所有模块都通过 `LLMClient` 请求生成内容，避免每个模块直接写 API 调用代码。

### 接口建议

```python
class LLMClient:
    def generate_text(self, prompt: str) -> str:
        pass

    def generate_json(self, prompt: str) -> dict:
        pass
```

### 注意事项

- 第一版可以先用假数据或手写模拟返回值。
- 等框架跑通后再接真实 LLM API。
- `generate_json` 必须处理 JSON 解析失败问题。

---

## 3. InputParser

### 职责

把用户输入解析成 `StorySetting`。

### 输入

```python
user_input: str
```

### 输出

```python
story_setting: dict
```

### 函数示例

```python
class InputParser:
    def __init__(self, llm_client):
        self.llm = llm_client

    def parse(self, user_input: str) -> dict:
        prompt = self.build_prompt(user_input)
        return self.llm.generate_json(prompt)

    def build_prompt(self, user_input: str) -> str:
        pass
```

---

## 4. WorldInitializer

### 职责

根据 `StorySetting` 初始化 `WorldState` 和 `CharacterCard`。

### 输入

```python
story_setting: dict
```

### 输出

```python
world_state: dict
character_cards: list[dict]
```

### 核心要求

初始化时要生成：

- 主角
- 初始地点
- 初始时间
- 初始冲突
- 世界规则
- 未知问题
- 可用地点

---

## 5. WorldStateManager

### 职责

管理世界状态，包括读取、更新、保存和检查。

### 接口建议

```python
class WorldStateManager:
    def __init__(self, initial_state: dict):
        self.current_state = initial_state
        self.history = [initial_state]

    def get_current_state(self) -> dict:
        return self.current_state

    def update_state(self, new_state: dict):
        self.current_state = new_state
        self.history.append(new_state)

    def get_history(self) -> list[dict]:
        return self.history
```

---

## 6. PlotEngine

### 职责

根据当前世界状态生成下一个剧情事件。

### 输入

```python
world_state: dict
step: int
story_stage: str
```

### 输出

```python
event_card: dict
```

### 生成要求

每个事件必须：

1. 符合已有世界状态。
2. 不推翻已发生事件。
3. 至少产生一个变化。
4. 最好增加线索或冲突。
5. 能被视觉化成场景。

---

## 7. StateUpdater

### 职责

根据事件更新世界状态。

### 输入

```python
old_world_state: dict
event_card: dict
```

### 输出

```python
new_world_state: dict
```

### 更新内容

可能需要更新：

- `step`
- `current_time`
- `current_location`
- `characters`
- `known_facts`
- `unknowns`
- `unresolved_conflicts`
- `events_happened`
- `atmosphere`

### 关键规则

状态更新时必须保留旧事实，除非事件明确改变它。

错误示例：

```text
前文说主角在宿舍，下一步无原因突然出现在实验楼。
```

正确示例：

```text
事件中说明主角决定前往实验楼，状态再更新地点。
```

---

## 8. SceneGenerator

### 职责

把剧情事件转成可视化场景卡。

### 输入

```python
world_state: dict
event_card: dict
```

### 输出

```python
scene_card: dict
```

### 场景卡必须包含

- 地点
- 时间
- 主要人物
- 主要动作
- 镜头类型
- 光照
- 情绪氛围
- 关键物品
- 视觉风格

---

## 9. ImagePromptGenerator

### 职责

把 `SceneCard` 转成图像模型 Prompt。

### 输入

```python
scene_card: dict
```

### 输出

```python
image_prompt: dict
```

输出结构：

```json
{
  "prompt_cn": "...",
  "prompt_en": "...",
  "negative_prompt_cn": "...",
  "negative_prompt_en": "..."
}
```

---

## 10. OutputExporter

### 职责

保存每次运行结果。

输出文件：

```text
outputs/run_001/
  ├── story_setting.json
  ├── world_states.json
  ├── event_cards.json
  ├── scene_cards.json
  ├── image_prompts.json
  └── storyboard.md
```

---

## 11. app.py 主流程建议

```python
def main():
    user_input = input("请输入故事设定：")

    llm = LLMClient()
    parser = InputParser(llm)
    initializer = WorldInitializer(llm)
    plot_engine = PlotEngine(llm)
    updater = StateUpdater(llm)
    scene_generator = SceneGenerator(llm)
    prompt_generator = ImagePromptGenerator(llm)
    exporter = OutputExporter()

    story_setting = parser.parse(user_input)
    world_state, characters = initializer.init(story_setting)

    events = []
    scenes = []
    prompts = []
    world_states = [world_state]

    for step in range(1, 4):
        event = plot_engine.generate_event(world_state, step)
        world_state = updater.update(world_state, event)
        scene = scene_generator.generate_scene(world_state, event)
        image_prompt = prompt_generator.generate(scene)

        events.append(event)
        scenes.append(scene)
        prompts.append(image_prompt)
        world_states.append(world_state)

    exporter.export_all(
        story_setting=story_setting,
        characters=characters,
        world_states=world_states,
        events=events,
        scenes=scenes,
        prompts=prompts
    )
```

---

## 12. 开发建议

第一次写项目时，建议按以下顺序实现：

1. 先写数据结构示例。
2. 再写假 LLMClient，返回固定 JSON。
3. 跑通全流程。
4. 再接真实大模型。
5. 再优化 Prompt。
6. 最后加前端和图像生成。
