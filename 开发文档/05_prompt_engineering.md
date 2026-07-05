# 05 Prompt 工程设计

## 1. Prompt 在本项目中的作用

第一版系统不从零训练模型，因此 Prompt 是核心控制手段。

系统中的每个生成模块都需要单独 Prompt：

```text
parse_input.txt
init_world.txt
generate_event.txt
update_state.txt
generate_scene.txt
generate_image_prompt.txt
```

每个 Prompt 的目标不是“让模型自由发挥”，而是让模型按指定结构输出。

---

## 2. Prompt 通用原则

### 2.1 明确角色

告诉模型它在当前模块中扮演什么角色。

```text
你是一个互动叙事系统中的“剧情推进器”。
你的任务不是写完整小说，而是根据当前世界状态生成下一个剧情事件。
```

### 2.2 明确输入

```text
以下是当前世界状态：
{world_state}

以下是当前剧情步数：
{step}
```

### 2.3 明确约束

```text
要求：
1. 不得推翻已发生事件。
2. 不得突然改变人物身份。
3. 不得引入与题材无关的超大设定。
4. 必须让事件能被转化为具体场景。
```

### 2.4 明确输出格式

```text
请严格输出 JSON，不要输出 Markdown，不要输出解释。
```

---

## 3. 输入解析 Prompt

文件：`prompts/parse_input.txt`

```text
你是一个 AIGC 互动叙事系统的输入解析器。

你的任务是把用户输入的自然语言故事设定解析为结构化 JSON。

用户输入：
{user_input}

请提取以下字段：
- genre：题材
- theme：主题
- tone：情绪基调，数组
- protagonist_brief：主角简述
- initial_location：初始地点
- initial_time：初始时间
- core_incident：核心事件
- target_audience：目标受众
- visual_style：视觉风格

要求：
1. 如果用户没有明确说明某字段，请根据整体设定合理补全。
2. 不要写完整剧情。
3. 不要加入过多无关设定。
4. 严格输出 JSON，不要输出 Markdown。

输出格式：
{
  "genre": "",
  "theme": "",
  "tone": [],
  "protagonist_brief": "",
  "initial_location": "",
  "initial_time": "",
  "core_incident": "",
  "target_audience": "",
  "visual_style": ""
}
```

---

## 4. 初始化世界状态 Prompt

文件：`prompts/init_world.txt`

```text
你是一个叙事世界状态初始化器。

你的任务是根据故事设定，创建初始 WorldState 和主角 CharacterCard。

故事设定：
{story_setting}

请生成：
1. character_cards
2. world_state

要求：
1. 世界状态必须适合后续剧情推进。
2. 主角必须有目标、恐惧、秘密和视觉特征。
3. 世界规则控制在 2～4 条。
4. 初始未知问题控制在 2～4 个。
5. 不要直接写完整结局。
6. 严格输出 JSON，不要输出 Markdown。
```

---

## 5. 剧情事件生成 Prompt

文件：`prompts/generate_event.txt`

```text
你是一个互动叙事系统中的剧情推进器 PlotEngine。

你的任务是根据当前世界状态生成下一个剧情事件 EventCard。

当前世界状态：
{world_state}

当前剧情步数：
{step}

当前剧情阶段：
{story_stage}

要求：
1. 事件必须符合当前世界状态。
2. 不得推翻 events_happened 中已经发生的事件。
3. 不得突然改变角色身份、年龄、核心秘密。
4. 必须推动剧情发展，而不是只描写气氛。
5. 必须至少产生一个 new_clue 或 new_conflict。
6. 事件必须可以被转化成具体视觉场景。
7. 不要直接给出最终真相，除非处于最后阶段。
8. 严格输出 JSON，不要输出 Markdown。
```

---

## 6. 状态更新 Prompt

文件：`prompts/update_state.txt`

```text
你是一个叙事世界状态更新器 StateUpdater。

你的任务是根据旧世界状态和新事件，生成更新后的世界状态。

旧世界状态：
{old_world_state}

新事件：
{event_card}

要求：
1. 必须保留旧世界状态中的重要事实。
2. 必须把新事件加入 events_happened。
3. 必须根据事件更新角色情绪、目标、地点或关系。
4. 如果出现新线索，请加入 known_facts。
5. 如果出现新问题，请加入 unknowns 或 unresolved_conflicts。
6. 不要无原因删除未解决冲突。
7. step 必须加 1。
8. 严格输出完整的新 WorldState JSON，不要输出 Markdown。
```

---

## 7. 场景卡生成 Prompt

文件：`prompts/generate_scene.txt`

```text
你是一个游戏剧情系统中的场景设计器 SceneGenerator。

你的任务是根据剧情事件和当前世界状态生成一个可视化 SceneCard。

当前世界状态：
{world_state}

剧情事件：
{event_card}

要求：
1. 场景必须体现事件的核心信息。
2. 场景必须能被画成一张图。
3. 必须包含人物、动作、地点、时间、光照、镜头和关键物品。
4. 视觉风格应适合 RPG 游戏 CG。
5. 不要写成小说段落，要输出结构化 JSON。
6. 严格输出 JSON，不要输出 Markdown。
```

---

## 8. 图像 Prompt 生成 Prompt

文件：`prompts/generate_image_prompt.txt`

```text
你是一个图像生成 Prompt 工程师。

你的任务是根据 SceneCard 生成适合图像生成模型的中文和英文 Prompt。

SceneCard：
{scene_card}

要求：
1. 保留场景地点、时间、人物动作和情绪。
2. 保留关键物品。
3. 保留镜头语言和光照。
4. 保留视觉风格。
5. 英文 Prompt 要自然，适合 text-to-image 模型。
6. Negative Prompt 要避免与场景冲突的元素。
7. 严格输出 JSON，不要输出 Markdown。
```

---

## 9. Prompt 调试方法

1. 一次只调一个模块。
2. 固定测试输入。
3. 检查 JSON 合法性。
4. 保存 Prompt 版本。
5. 记录每次失败案例。

固定测试输入：

```text
校园悬疑，主角是计算机专业女生，深夜在宿舍收到一封来自未来的邮件。
```

JSON 解析工具建议：

```python
def safe_parse_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])
        raise
```

---

## 10. 常见问题

### 问题 1：模型输出太像小说

解决：强调“输出 EventCard，不要写小说段落”。

### 问题 2：剧情跳太快

解决：加入“当前是第 {step} 步，不要直接揭示最终真相”。

### 问题 3：前后矛盾

解决：在 Prompt 中加入 `events_happened`，并要求不得推翻旧事实。

### 问题 4：场景不可视化

解决：要求事件必须能被画成一个具体画面。

### 问题 5：图像 Prompt 太泛

解决：场景卡里必须明确人物、动作、光照、镜头和关键物品。
