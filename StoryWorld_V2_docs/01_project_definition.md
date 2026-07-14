# 01 项目定义与研究问题

## 项目定义

**StoryWorld：面向动态叙事生成的多主体、多视角因果世界推演框架。**

它不只是：

```text
输入一句话 → LLM 写故事
```

也不只是：

```text
角色卡 + Prompt → 多 Agent 对话
```

项目真正关注：

> 不同主体为什么会对同一世界产生不同解释，而这些解释、知识、价值与社会机制如何共同影响未来发展。

## 核心研究问题

### RQ1：客观世界与主体认知如何分离？

```text
Objective State
≠ Observed State
≠ Interpreted State
```

### RQ2：角色的世界观如何影响行动？

角色不只包含人格标签，而需要：

```text
Belief
Knowledge
False Belief
Values
Epistemology
Human Nature Model
Theory of Change
Role
Identity
Memory
Emotion
```

### RQ3：领域知识如何参与状态转移？

经济学、心理学、社会学等应输出：

```text
Causal Hypothesis
```

而不是知识问答或“从某某角度看”的评论。

### RQ4：如何避免唯一正确未来？

系统生成多个：

```text
Candidate Future
```

并记录 `estimated_plausibility`，而不是宣称真实世界概率。

### RQ5：世界演化与剧情表达如何分离？

```text
World Probability
≠ Narrative Importance
```

## V2 原则

1. 客观世界优先。
2. 主体可以犯错。
3. 因果解释显式化。
4. 理论模块可扩展。
5. Narrative Engine 最后工作。
6. Narrative Engine 不得修改 Objective World。
7. 所有重要状态变化必须可追踪 provenance。

## 40 天版本的研究表达

> 本项目设计了一种面向动态叙事生成的模块化世界推演框架。系统显式区分客观世界状态与主体认知状态，并通过多个领域因果 Lens 对当前世界产生多组因果假设，进一步生成概率化候选未来。叙事引擎从潜在世界演化中选择具有叙事价值的事件进行表达。

注意：这是工程原型与研究框架，不宣称已经解决真实社会未来预测问题。
