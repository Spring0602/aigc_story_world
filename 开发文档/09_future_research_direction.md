# 09 后续研究方向

## 1. 当前版本与研究版的区别

当前版本是工程 MVP：

```text
JSON 世界状态 + LLM Prompt + 场景卡 + 图像 Prompt
```

它不是严格意义上的神经网络世界模型，但它已经具备世界模型思想：

- 有状态。
- 有事件。
- 有状态转移。
- 有未来推进。
- 有观测输出，即场景卡和图像 Prompt。

---

## 2. 从规则版世界状态到世界模型

### 2.1 当前 V0

```text
WorldState_t + Event_t → WorldState_{t+1}
```

这个过程由 Prompt 和规则完成。

### 2.2 V1：LLM 状态转移模型

让 LLM 学会更稳定地做状态转移：

```text
输入：旧状态 + 事件
输出：新状态
```

可以收集样例，形成小数据集。

### 2.3 V2：微调状态转移模型

当你有足够数据后，可以训练或微调一个小模型：

```text
(old_world_state, event_card) → new_world_state
```

训练目标不是写小说，而是学习“剧情世界如何更新”。

### 2.4 V3：可预测剧情分支的世界模型

系统可以对多个候选事件进行 rollout：

```text
当前状态
  ├── 候选事件 A → 未来状态 A
  ├── 候选事件 B → 未来状态 B
  └── 候选事件 C → 未来状态 C
```

然后根据评分选择最优剧情方向。

评分维度：

- 连贯性
- 悬念感
- 人物动机合理性
- 可视化程度
- 与主题一致性

---

## 3. 与具身学习的关系

具身学习强调：

```text
Agent 在环境中感知 → 决策 → 行动 → 环境变化
```

你的项目可以抽象成：

```text
角色在故事世界中观察 → 做出行动 → 剧情世界变化
```

对应关系：

| 具身学习 | 叙事生成项目 |
|---|---|
| Agent | 角色 / NPC |
| Environment | 故事世界 |
| Observation | 当前场景和已知事实 |
| Action | 角色行动 / 剧情事件 |
| State Transition | 世界状态更新 |
| Reward | 剧情质量评分 |

因此，你后续可以把角色做成轻量 Agent：

```text
角色目标 + 当前观察 + 性格 → 角色行动
角色行动 + 世界规则 → 世界状态变化
```

---

## 4. 可交互叙事方向

后续可以让用户参与剧情：

```text
系统给出 3 个行动选项
用户选择其中一个
系统根据选择更新世界状态
继续生成剧情
```

示例：

```text
当前事件：林夏发现邮件来自未来。

可选行动：
A. 立即回复邮件
B. 去机房查询邮件源地址
C. 告诉室友这件事
```

用户选择 B 后：

```text
WorldState + Action_B → NewWorldState
```

这就从单向生成变成了交互式叙事。

---

## 5. 人物 Agent 设计

后续可以为每个角色添加 Agent 模块。

### 角色决策输入

```json
{
  "character": "林夏",
  "personality": ["理性", "敏感"],
  "goal": "查明邮件来源",
  "fear": "被未知系统操控",
  "current_observation": "邮件发送时间来自未来",
  "available_actions": [
    "回复邮件",
    "查询源地址",
    "告诉室友",
    "忽略邮件"
  ]
}
```

### 角色决策输出

```json
{
  "chosen_action": "查询源地址",
  "reason": "林夏性格理性，会优先验证技术细节，而不是情绪化求助。",
  "risk": "可能触发校园网络异常"
}
```

---

## 6. 加入剧情评分器

未来可以增加 `StoryEvaluator`。

输入：

```text
当前世界状态 + 候选事件
```

输出评分：

```json
{
  "coherence": 4,
  "tension": 5,
  "character_consistency": 4,
  "visual_potential": 5,
  "theme_relevance": 4,
  "overall": 4.4
}
```

然后选择评分最高的事件。

---

## 7. 论文/科研表达方向

如果后续想包装成研究型项目，可以使用这些表述：

1. 面向交互式叙事生成的结构化世界状态建模方法
2. 基于事件驱动状态转移的情景—剧情联合生成框架
3. 面向 RPG 游戏内容生成的叙事世界模型原型系统
4. 结合 LLM 与场景卡中间表示的可视化剧情生成方法

---

## 8. 作品集亮点表达

可以在简历或作品集中写：

```text
设计并实现了一个基于结构化世界状态的 AIGC 情景—剧情生成系统。系统将用户输入解析为世界状态，通过事件卡驱动剧情推进和状态更新，并将剧情事件转化为场景卡与图像生成 Prompt，实现了从叙事逻辑到视觉场景的自动化生成流程。
```

技术关键词：

- LLM
- Prompt Engineering
- World State
- Event-driven Story Generation
- Scene Card
- Image Prompt Generation
- Interactive Narrative
- RPG Content Generation
- World Model-inspired System
