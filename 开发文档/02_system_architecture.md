# 02 系统总体架构

## 1. 总体架构图

第一版系统可以理解为一个流水线：

```text
UserInput
   ↓
InputParser
   ↓
StorySetting
   ↓
WorldInitializer
   ↓
WorldState
   ↓
PlotEngine
   ↓
EventCard
   ↓
StateUpdater
   ↓
Updated WorldState
   ↓
SceneGenerator
   ↓
SceneCard
   ↓
ImagePromptGenerator
   ↓
ImagePrompt
   ↓
OutputExporter
```

如果后续接图像模型，则继续：

```text
ImagePrompt
   ↓
ImageGenerationModel
   ↓
GeneratedImage
   ↓
StoryboardExporter
```

---

## 2. 核心思想

系统的核心不是“让大模型随便生成”，而是让每一次生成都经过三个约束：

1. **当前世界状态约束**
   - 已发生的事不能被推翻。
   - 人物已有情绪、目标和秘密要延续。
   - 世界规则不能随意改变。

2. **剧情阶段约束**
   - 第一幕：建立背景、引入冲突。
   - 第二幕：冲突升级、线索展开。
   - 第三幕：真相揭示、冲突解决或反转。

3. **可视化约束**
   - 事件要能被转化成场景。
   - 场景要能被转化成图像 Prompt。
   - 场景元素要有画面感。

---

## 3. 模块依赖关系

```text
app.py
 ├── InputParser
 ├── WorldInitializer
 ├── PlotEngine
 ├── StateUpdater
 ├── SceneGenerator
 ├── ImagePromptGenerator
 └── OutputExporter
```

每个模块尽量保持单一职责。

---

## 4. 核心数据流

一个完整迭代周期：

```text
当前世界状态 S_t
  ↓
生成事件 E_t
  ↓
根据事件更新世界状态 S_{t+1}
  ↓
根据 E_t 和 S_{t+1} 生成场景 C_t
  ↓
根据 C_t 生成图像 Prompt P_t
```

伪代码：

```python
world_state = init_world_state(story_setting)

for step in range(num_events):
    event = plot_engine.generate_event(world_state, step)
    world_state = state_updater.update(world_state, event)
    scene = scene_generator.generate_scene(world_state, event)
    image_prompt = image_prompt_generator.generate(scene)
    exporter.save(step, world_state, event, scene, image_prompt)
```

---

## 5. 第一版 LLM 调用方式

第一版可以把 LLM 封装成一个统一客户端：

```python
class LLMClient:
    def generate_json(self, prompt: str) -> dict:
        pass

    def generate_text(self, prompt: str) -> str:
        pass
```

各模块不要直接调用具体 API，而是通过 `LLMClient` 调用。

这样后续可以方便替换：

- OpenAI API
- 本地大模型
- Ollama
- Hugging Face 模型
- 其他云端模型

---

## 6. 推荐执行流程

### 6.1 命令行版本

第一阶段先做命令行：

```bash
python app.py --input "校园悬疑，主角收到未来邮件"
```

输出保存到：

```text
outputs/run_001/
  ├── story_setting.json
  ├── world_states.json
  ├── events.json
  ├── scenes.json
  ├── image_prompts.txt
  └── storyboard.md
```

### 6.2 Notebook 调试版本

可以保留一个 notebook 用来调 Prompt：

```text
notebooks/
  └── prompt_debug.ipynb
```

但是正式逻辑不要只写在 notebook 里。

### 6.3 前端版本

后期再加：

```text
Gradio / Streamlit
```

---

## 7. 架构升级路线

### V0：规则 + Prompt 版本

- JSON 管状态。
- Prompt 调用 LLM。
- 不训练模型。

### V1：前端 Demo 版本

- 加 Gradio / Streamlit。
- 用户可输入设定。
- 前端展示剧情、状态、场景卡。

### V2：图像生成版本

- 接 Diffusion 或外部图像模型。
- 自动生成分镜图。
- 支持固定风格，如像素风 RPG CG。

### V3：微调版本

- 收集样例数据。
- 使用 LoRA / PEFT 微调某个小模型。
- 让它更符合自己的剧情风格。

### V4：研究版本

- 引入世界模型思想。
- 加入状态预测、反事实推演、剧情分支评估。
