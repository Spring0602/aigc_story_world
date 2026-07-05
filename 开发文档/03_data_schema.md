# 03 数据结构设计

## 1. 为什么数据结构最重要

这个项目的第一版不是训练模型，而是搭建系统。系统能不能稳定运行，很大程度取决于中间数据结构是否清晰。

推荐所有关键中间层都使用 JSON 表示：

- `StorySetting`
- `CharacterCard`
- `WorldState`
- `EventCard`
- `SceneCard`
- `ImagePrompt`

---

## 2. StorySetting：故事设定

`StorySetting` 是对用户输入的结构化解析结果。

```json
{
  "genre": "校园悬疑",
  "theme": "未知系统与命运预警",
  "tone": ["神秘", "压抑", "紧张"],
  "protagonist_brief": "计算机专业女生",
  "initial_location": "大学宿舍",
  "initial_time": "深夜",
  "core_incident": "收到一封来自未来的邮件",
  "target_audience": "喜欢悬疑和科幻校园题材的玩家",
  "visual_style": "像素风 RPG CG"
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `genre` | string | 题材类型 |
| `theme` | string | 核心主题 |
| `tone` | list[string] | 情绪基调 |
| `protagonist_brief` | string | 主角简述 |
| `initial_location` | string | 初始地点 |
| `initial_time` | string | 初始时间 |
| `core_incident` | string | 核心事件 |
| `target_audience` | string | 目标受众 |
| `visual_style` | string | 视觉风格 |

---

## 3. CharacterCard：人物卡

用于保持角色设定一致。

```json
{
  "character_id": "char_001",
  "name": "林夏",
  "age": 20,
  "gender": "女",
  "identity": "计算机专业大学生",
  "personality": ["理性", "敏感", "有强烈好奇心"],
  "goal": "查明神秘邮件的来源",
  "fear": "自己的人生被未知系统操控",
  "secret": "曾经参与过一个异常 AI 实验",
  "current_emotion": "疑惑",
  "relationships": {
    "室友": "信任但有所隐瞒",
    "导师": "尊敬但不完全信任"
  },
  "visual_features": {
    "hair": "黑色中长发",
    "clothes": "宽松白色睡衣",
    "expression": "疲惫而警觉",
    "special_item": "旧款笔记本电脑"
  }
}
```

关键字段：

| 字段 | 作用 |
|---|---|
| `goal` | 决定角色为什么行动 |
| `fear` | 决定角色面对冲突时的反应 |
| `secret` | 可用于后续反转 |
| `current_emotion` | 用于状态更新 |
| `relationships` | 用于人物关系推进 |
| `visual_features` | 用于图像生成一致性 |

---

## 4. WorldState：世界状态卡

`WorldState` 是项目最核心的数据结构，记录当前故事世界已经演化到了什么状态。

```json
{
  "state_id": "state_001",
  "step": 0,
  "current_time": "第1天 23:50",
  "current_location": "女生宿舍",
  "atmosphere": "压抑、安静、诡异",
  "world_rules": [
    "午夜后校园网络会出现异常",
    "神秘邮件只能在特定时间被打开"
  ],
  "characters": {
    "林夏": {
      "current_emotion": "疑惑",
      "current_goal": "确认邮件是否真实",
      "location": "女生宿舍",
      "status": "清醒"
    }
  },
  "known_facts": [
    "林夏收到了一封陌生邮件"
  ],
  "unknowns": [
    "邮件是谁发来的？",
    "为什么邮件知道林夏的真实姓名？"
  ],
  "unresolved_conflicts": [
    "邮件内容暗示午夜将发生异常事件"
  ],
  "events_happened": [],
  "available_locations": [
    "女生宿舍",
    "计算机学院机房",
    "校园主干道",
    "旧实验楼"
  ]
}
```

---

## 5. EventCard：事件卡

`EventCard` 表示某一步剧情事件。

```json
{
  "event_id": "event_001",
  "step": 1,
  "summary": "林夏发现邮件发送时间显示为明天凌晨三点",
  "stage": "第一幕：异常引入",
  "cause": "她查看邮件详情时发现时间戳异常",
  "effect": "她开始怀疑这不是普通恶作剧",
  "involved_characters": ["林夏"],
  "location": "女生宿舍",
  "tension_change": "升高",
  "new_clues": [
    "邮件发送时间来自未来"
  ],
  "new_conflicts": [
    "未来的发送者为什么要联系现在的林夏？"
  ],
  "state_changes": {
    "林夏.current_emotion": "恐惧",
    "林夏.current_goal": "验证邮件真伪"
  }
}
```

---

## 6. SceneCard：场景卡

`SceneCard` 是剧情和图像之间的中间层。

```json
{
  "scene_id": "scene_001",
  "event_id": "event_001",
  "location": "女生宿舍",
  "time": "深夜",
  "main_action": "林夏盯着电脑屏幕上的邮件发送时间",
  "characters": [
    {
      "name": "林夏",
      "pose": "坐在书桌前，身体微微前倾",
      "expression": "脸色苍白，眼神惊恐"
    }
  ],
  "camera": {
    "shot_type": "正面中近景",
    "angle": "略微俯视",
    "focus": "电脑屏幕和林夏的表情"
  },
  "lighting": "电脑屏幕发出幽蓝色光，房间其他部分昏暗",
  "atmosphere": "紧张、诡异、压抑",
  "key_objects": [
    "笔记本电脑",
    "书桌",
    "床铺",
    "邮件界面",
    "电子钟"
  ],
  "visual_style": "像素风 RPG 游戏 CG，16:9",
  "negative_prompt_notes": [
    "不要出现多人",
    "不要出现明亮白天",
    "不要出现夸张科幻设备"
  ]
}
```

好的场景卡应该：

1. 能被画出来。
2. 服务剧情。
3. 风格统一。
4. 能转成 Prompt。

---

## 7. ImagePrompt：图像提示词

```json
{
  "prompt_cn": "像素风 RPG 游戏 CG，16:9，深夜大学宿舍，电脑屏幕发出幽蓝色光，一名中国计算机专业女生坐在书桌前，身体微微前倾，脸色苍白，盯着邮件界面上的未来发送时间，房间昏暗，氛围紧张诡异，电影感光影。",
  "prompt_en": "pixel art RPG game CG, 16:9, dark college dormitory at midnight, a young Chinese female computer science student sitting at a desk, leaning toward a laptop screen glowing cold blue, pale face, frightened eyes, mysterious email interface showing a future timestamp, dim room, tense and eerie atmosphere, cinematic lighting",
  "negative_prompt_cn": "不要多人，不要白天，不要现代科幻实验室，不要夸张机械装置，不要卡通夸张表情。",
  "negative_prompt_en": "multiple people, daytime, futuristic laboratory, exaggerated sci-fi machines, cartoonish expression, low quality, blurry"
}
```

---

## 8. 数据保存建议

每次运行可以保存为：

```text
outputs/run_001/
  ├── story_setting.json
  ├── character_cards.json
  ├── world_states.json
  ├── event_cards.json
  ├── scene_cards.json
  ├── image_prompts.json
  └── storyboard.md
```
