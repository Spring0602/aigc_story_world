# 01 项目定义与研究问题

## 项目定义

**StoryWorld：以动态叙事为应用出口的社会认知世界模型研究原型。**

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

动态叙事用于观察和展示实验结果，不是 40 天研究的优化中心。

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

### RQ3：主体如何形成对他人心智的模型？

系统至少表示：

```text
A believes X
A believes B believes X
```

并检验这种一阶、二阶信念是否改善互动行动的一致性。

### RQ4：主体认知如何转化为行动？

行动不是由人格标签或单一 Prompt 决定，而由以下因素共同约束：

```text
Belief + Goal + Value + Emotion + Constraint → Agent Action
```

### RQ5：领域知识如何参与状态转移？

经济学、心理学、社会学等应输出：

```text
Causal Hypothesis
```

而不是知识问答或“从某某角度看”的评论。

### RQ6：如何处理多个领域机制的冲突？

不同 Lens 可以给出相反机制。系统必须保留冲突、支持与约束，不能简单拼接或平均结论。

### RQ7：如何避免唯一正确未来？

系统生成多个：

```text
Candidate Future
```

并记录 `estimated_plausibility`，而不是宣称真实世界概率。

### RQ8：世界演化与剧情表达如何分离？

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
8. 行动必须能追溯到主体认知和现实约束。
9. 已存在的模块原型不等于通过新版实验验收。

## 40 天版本的研究表达

> 本项目设计并验证一个社会认知世界模型原型。系统显式区分客观世界、主体观察、主体信念和对他人信念的估计；通过结构化领域 Lens、行动模型和状态转移生成多个可解释未来；最后由叙事引擎表达已经发生的世界变化。

注意：这是工程原型与可行性实验，不宣称精确预测真实社会，也不把相对可信度解释为真实概率。
