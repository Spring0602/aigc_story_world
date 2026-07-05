# 08 前端 Demo 设计

## 1. 前端目标

前端不是第一阶段重点。等命令行版本跑通后，再做一个简单 Demo 方便展示。

前端目标：

- 用户可以输入故事设定。
- 点击按钮后生成剧情。
- 展示世界状态、剧情事件、场景卡和图像 Prompt。
- 后续可展示生成图片。

---

## 2. 推荐技术选择

### 2.1 Gradio

适合 AI Demo：

- 写法简单。
- 很适合输入文本、输出文本/图片。
- 容易做成作品展示。

推荐优先使用。

### 2.2 Streamlit

适合数据面板：

- 展示 JSON 和表格方便。
- 页面布局灵活。
- 适合做调试工具。

如果你想展示世界状态变化，Streamlit 也不错。

---

## 3. 页面布局设计

建议三栏布局：

```text
┌──────────────────────────────┐
│ 项目标题：StoryWorld          │
├──────────┬──────────┬────────┤
│ 输入区   │ 剧情区   │ 场景区 │
│          │          │        │
│ 故事设定 │ 事件列表 │ 场景卡 │
│ 生成按钮 │ 世界状态 │ Prompt │
└──────────┴──────────┴────────┘
```

---

## 4. 页面功能

### 4.1 输入区

包含：

- 故事设定输入框
- 生成事件数量
- 视觉风格选择
- 生成按钮

示例：

```text
故事设定：
校园悬疑，主角是计算机专业女生，深夜收到一封来自未来的邮件。

事件数量：
3

视觉风格：
像素风 RPG CG
```

### 4.2 剧情区

展示：

- StorySetting
- EventCards
- WorldState 简要变化

展示方式：

```markdown
## 事件 1

林夏发现邮件发送时间显示为明天凌晨三点。

- 新线索：邮件来自未来
- 新冲突：未来的发送者为什么联系她？
- 情绪变化：疑惑 → 恐惧
```

### 4.3 场景区

展示：

- SceneCard
- 中文 Prompt
- 英文 Prompt
- Negative Prompt
- 后续生成图片

---

## 5. Gradio 示例代码

```python
import gradio as gr

def generate_story(user_input, num_events, visual_style):
    result = run_pipeline(
        user_input=user_input,
        num_events=int(num_events),
        visual_style=visual_style
    )

    story_md = result["storyboard_md"]
    scene_md = result["scene_md"]
    prompt_text = result["image_prompts_text"]

    return story_md, scene_md, prompt_text

with gr.Blocks() as demo:
    gr.Markdown("# StoryWorld：情景与剧情生成系统")

    with gr.Row():
        with gr.Column():
            user_input = gr.Textbox(
                label="故事设定",
                lines=8,
                value="校园悬疑，主角是计算机专业女生，深夜收到一封来自未来的邮件。"
            )
            num_events = gr.Number(label="生成事件数量", value=3)
            visual_style = gr.Textbox(label="视觉风格", value="像素风 RPG CG")
            button = gr.Button("生成")

        with gr.Column():
            story_output = gr.Markdown(label="剧情与世界状态")

        with gr.Column():
            scene_output = gr.Markdown(label="场景卡")
            prompt_output = gr.Textbox(label="图像 Prompt", lines=12)

    button.click(
        fn=generate_story,
        inputs=[user_input, num_events, visual_style],
        outputs=[story_output, scene_output, prompt_output]
    )

demo.launch()
```

---

## 6. Demo 展示重点

前端 Demo 不需要特别复杂。展示时重点强调：

1. 系统不是一次性写故事，而是逐步维护世界状态。
2. 每个剧情事件都会更新世界状态。
3. 每个事件都能生成对应场景卡。
4. 场景卡可以进一步转图像 Prompt。
5. 该框架可扩展到游戏剧情生成和 RPG CG 生成。
