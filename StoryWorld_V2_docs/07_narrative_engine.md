# 07 Narrative Engine 叙事引擎

## 核心原则

```text
World Evolution
≠ Narrative Expression
```

世界先变化，叙事引擎后选择“什么值得被观众看到”。

完整链路固定为：

```text
World Simulation
→ Fabula
→ Narrative Planner + Narrative Importance
→ Syuzhet + Focalization
→ Story Output
```

Simulation 循环结束前不得创建 Narrative Plan 或 Story Output。Fabula 保存实际发生事件的时间与因果顺序；Narrative Planner 只负责选择表达素材；Syuzhet 与 Fabula 使用独立 Schema；Focalization 只能基于焦点角色可见 Observation 暴露信息。

V2.1 研究路线中，Narrative Engine 是下游展示层。主体认知、行动决策和世界转移实验完成前，不优先优化文风、图片或戏剧性。

## 输入

```text
Old Objective State
New Objective State
Selected Candidate Future
Subjective World Models
Narrative Context
```

## Narrative Importance

评分维度：

```text
Conflict Change
Information Gain
Character Decision
Relationship Change
Irreversibility
Theme Relevance
Visual Potential
```

当前 Day32 实现使用强类型 `NarrativeImportanceAssessment`，权重为：

```text
Conflict Change       0.16
Information Gain      0.18
Character Decision    0.18
Relationship Change   0.12
Irreversibility       0.14
Theme Relevance       0.12
Visual Potential      0.10
```

评分发生在 World Transition 之后，输入 Old/New Objective State、实际 World Event、Selected Candidate Future、Future Evaluation 与 Subjective Models。每个维度保存独立分数和 rationale，总分映射为 low / medium / high。Assessment 闭合 source/target state、Event、Future、Action、Decision、StateChange 与 provenance 引用。

评分不得依据摘要措辞、future ID 中是否出现 `secret` 或预设戏剧性标签。信息发现、社会协作、制度质询和过程惯性必须因结构化机制及实际 StateChange 不同而激活不同维度。Narrative Importance 只决定表达优先级，不反向改变 World Probability、Future Evaluation 或 Objective World。

## Focalization

同一事实可以从不同视角展示。

例如“学校部署监控系统”：

- 林夏：发现异常流量。
- 老师：收到网络安全通知。
- 普通学生：觉得校园网变慢。

## Information Control

需要区分：

```text
Audience Knows
Character Knows
Audience Knows But Character Does Not
Character Knows But Audience Does Not
```

它们产生：

```text
Suspense
Mystery
Dramatic Irony
```

## Fabula 与 Syuzhet

Fabula：

```text
A → B → C → D
```

Syuzhet：

```text
C → A → D → B
```

第一版按时间顺序表达，后续再支持非线性。

当前实现中，`FabulaBuilder` 由 Objective State 快照、World Event 与 StateProvenance 构建 Fabula。`NarrativePlanner` 按 Importance threshold 选择事件并标注 revelation、decision、confrontation、relationship shift、turning point、thematic reinforcement 或 visual emphasis 功能。`Syuzhet` 第一版保持 chronology；`Focalization` 固定 third-person limited，并显式保存 character known、audience known 与 withheld information IDs。`StoryOutput` 闭合 Fabula、Plan、Syuzhet、Focalization、NarrativeEvent 和 NarrativeBeat IDs。

## Day 33 Narrative Expression

`NarrativeEngine.render_beat()` 将一个已经选中的 NarrativeEvent 渲染为强类型 `NarrativeBeat`。每个节拍由以下可审计部分组成：

```text
World-grounded action
→ Visible perception
→ Subjective emotional response
→ Information-gap cue
→ Narrative-function transition
```

`InformationEffect` 将信息划分为 shared、audience-only、character-only 与 withheld 四个互斥集合，并确定 dominant effect：

```text
no gap          → alignment
withheld        → suspense
character-only  → mystery
audience-only   → dramatic irony
```

当前 third-person limited 策略通常令 audience known 与 character known 对齐，因此未观察信息形成 suspense。Schema 校验集合互斥、effect 标签和 tension score 一致。正文只能使用 audience information 对应内容；withheld 信息只生成“仍有信息处在视野之外”一类抽象提示，不能写出隐藏事实。最终 `StoryOutput.rendered_text` 按 Syuzhet 顺序组合所有节拍。

## NarrativeEvent

```json
{
  "narrative_event_id": "nar_001",
  "source_future_id": "future_001",
  "focal_agent": "lin_xia",
  "summary": "林夏决定秘密抓取网络数据，而不是直接质问老师",
  "narrative_importance": 0.84,
  "revealed_information": ["网络流量存在重定向"],
  "hidden_information": ["监控系统真正目的"],
  "emotional_focus": ["curiosity", "fear"],
  "visual_core": "电脑终端中不断刷新的异常网络记录"
}
```

## 第一版 Narrator

固定：

```text
Third-person limited
```

即第三人称限知，跟随一个 focal agent。

## 第一版不做

- 文学风格微调
- 自动模仿名家
- 长篇小说生成
- 多线非线性结构
- 复杂象征系统自动发现

40 天内只验证：

> 世界推演结果能否在不创造事实、不泄漏隐藏信息、不切断 provenance 的前提下，转为可理解的动态叙事。

## 延期项

- 图像生成质量优化。
- 复杂镜头语言与视觉风格搜索。
- 长篇结构和非线性叙事。
- 文学性自动评估。

SceneCard 和 ImagePrompt 可以保留为 Demo 输出，但不作为 Social Cognitive World Model 的主要实验指标。
