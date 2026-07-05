# StoryWorld

基于世界状态演化的情景—剧情联合生成系统。

当前版本是开发文档中的 v0.1/v0.2 风格命令行原型：先用规则化的假 `LLMClient` 跑通完整文本链路，后续可以替换为真实大模型 API。

## 快速开始

```bash
python app.py --input "校园悬疑，主角收到未来邮件"
```

可选参数：

```bash
python app.py --input "赛博都市，侦探寻找失踪仿生人" --num-events 3
```

运行结果会保存到 `outputs/run_XXX/`：

- `story_setting.json`
- `character_cards.json`
- `world_states.json`
- `event_cards.json`
- `scene_cards.json`
- `image_prompts.json`
- `storyboard.md`

## 项目结构

```text
core/       核心流水线模块
schemas/    结构化数据定义
prompts/    Prompt 模板占位
data/       示例和测试数据
outputs/    每次运行的导出结果
tests/      基础测试
frontend/   后续 Gradio / Streamlit Demo
docs/       后续整理后的项目文档
```

## 当前链路

```text
用户输入
  ↓
StorySetting
  ↓
WorldState + CharacterCard
  ↓
EventCard
  ↓
Updated WorldState
  ↓
SceneCard
  ↓
ImagePrompt
  ↓
outputs/run_XXX
```

