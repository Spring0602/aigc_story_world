# 07 Narrative Engine 叙事引擎

## 核心原则

```text
World Evolution
≠ Narrative Expression
```

世界先变化，叙事引擎后选择“什么值得被观众看到”。

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

只验证：

> 世界推演结果能否转为更合理的动态剧情。
