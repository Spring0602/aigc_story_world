# 10 项目目录结构与代码规范

## 1. 推荐项目目录

```text
aigc_story_world/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
│
├── core/
│   ├── __init__.py
│   ├── llm_client.py
│   ├── input_parser.py
│   ├── world_initializer.py
│   ├── world_state.py
│   ├── plot_engine.py
│   ├── state_updater.py
│   ├── scene_generator.py
│   ├── image_prompt_generator.py
│   └── output_exporter.py
│
├── schemas/
│   ├── __init__.py
│   ├── story_setting.py
│   ├── character_card.py
│   ├── world_state.py
│   ├── event_card.py
│   └── scene_card.py
│
├── prompts/
│   ├── parse_input.txt
│   ├── init_world.txt
│   ├── generate_event.txt
│   ├── update_state.txt
│   ├── generate_scene.txt
│   └── generate_image_prompt.txt
│
├── data/
│   ├── examples/
│   └── test_cases/
│
├── outputs/
│   └── .gitkeep
│
├── notebooks/
│   └── prompt_debug.ipynb
│
├── frontend/
│   ├── gradio_app.py
│   └── streamlit_app.py
│
├── tests/
│   ├── test_schema.py
│   ├── test_pipeline.py
│   └── test_consistency.py
│
└── docs/
    ├── architecture.md
    ├── data_schema.md
    └── development_log.md
```

---

## 2. 文件职责

### 2.1 app.py

项目入口。

负责：

- 读取用户输入。
- 初始化各模块。
- 调用完整 pipeline。
- 保存输出。

不要把所有逻辑都写在 `app.py` 里。

---

### 2.2 config.py

保存配置。

示例：

```python
DEFAULT_NUM_EVENTS = 3
DEFAULT_VISUAL_STYLE = "像素风 RPG CG"
OUTPUT_DIR = "outputs"
PROMPT_DIR = "prompts"
```

如果接 API，可以保存：

```python
MODEL_NAME = "xxx"
TEMPERATURE = 0.7
MAX_TOKENS = 2048
```

不要把密钥直接写进代码。密钥应放在 `.env` 文件中，并加入 `.gitignore`。

---

### 2.3 core/

核心业务逻辑。

每个文件对应一个模块。

不要在 core 里写前端代码。不要在 core 里直接写大量测试代码。

---

### 2.4 schemas/

保存数据结构定义。

第一版可以用 dataclass。后续可以换成 pydantic。

示例：

```python
from dataclasses import dataclass
from typing import List

@dataclass
class StorySetting:
    genre: str
    theme: str
    tone: List[str]
    protagonist_brief: str
    initial_location: str
    initial_time: str
    core_incident: str
    visual_style: str
```

---

### 2.5 prompts/

保存 Prompt 模板。

每个模块一个 Prompt 文件。

命名要清楚：

```text
generate_event.txt
update_state.txt
generate_scene.txt
```

不要把长 Prompt 直接写死在 Python 代码里。

---

### 2.6 outputs/

保存生成结果。

每次运行创建一个新目录：

```text
outputs/run_001/
outputs/run_002/
outputs/run_003/
```

每个目录保存：

```text
story_setting.json
world_states.json
event_cards.json
scene_cards.json
image_prompts.json
storyboard.md
```

---

## 3. 命名规范

### Python 文件

使用小写加下划线：

```text
plot_engine.py
state_updater.py
image_prompt_generator.py
```

### 类名

使用大驼峰：

```python
class PlotEngine:
    pass

class StateUpdater:
    pass
```

### 函数名

使用小写加下划线：

```python
def generate_event():
    pass

def update_world_state():
    pass
```

### JSON 字段名

统一使用小写加下划线：

```json
{
  "current_time": "",
  "current_location": "",
  "known_facts": []
}
```

---

## 4. Git 版本管理建议

### 初始化

```bash
git init
```

### .gitignore

建议创建 `.gitignore`：

```text
__pycache__/
.env
outputs/
*.pyc
.ipynb_checkpoints/
```

如果想保留示例输出，可以把 `outputs/examples/` 单独加入仓库。

### 提交粒度

好的提交：

```bash
git commit -m "feat: add world state manager"
git commit -m "feat: add scene card generator"
git commit -m "fix: improve event json parsing"
```

不好的提交：

```bash
git commit -m "update"
git commit -m "修了一堆东西"
```

---

## 5. 开发顺序建议

1. 搭空项目。
2. 写假数据。
3. 跑通流程。
4. 替换为 LLM 调用。
5. 加保存功能。
6. 加前端。
7. 接图像生成。

---

## 6. requirements.txt 建议

第一版最小依赖：

```text
python-dotenv
pydantic
gradio
streamlit
```

如果暂时不做前端，可以只用：

```text
python-dotenv
pydantic
```

如果要接图像生成，后续再加：

```text
torch
diffusers
transformers
accelerate
safetensors
```

---

## 7. 新手开发注意事项

1. 不要一开始追求完美架构，第一目标是跑通。
2. 不要所有代码写在一个文件里，至少拆出 core 模块。
3. 不要依赖一次生成成功，LLM 输出会不稳定，要准备解析失败处理。
4. 不要只看最终故事，要检查中间 JSON。
5. 不要急着训练模型，先把系统框架做出来。

---

## 8. 里程碑版本命名

| 版本 | 内容 |
|---|---|
| v0.1 | 命令行纯文本单轮 |
| v0.2 | 多轮剧情推进 |
| v0.3 | 场景卡与 Prompt |
| v0.4 | 结果导出 |
| v0.5 | Gradio Demo |
| v0.6 | 图像生成接入 |
| v1.0 | 完整作品集展示版 |
