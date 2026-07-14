# 13 后续研究方向

## 真正 World Model

当前 V2：

```text
LLM + Structured State + Explicit Causal Modules
```

后续研究：

```text
Learned Latent State
Learned Transition Dynamics
Action-conditioned Prediction
Long-horizon Rollout
```

## Active Inference

可能高度相关：

```text
Internal Generative Model
Belief
Preference
Perception
Action
```

研究问题：

> 不同主体拥有不同内部 world model 时，是否会自然产生稳定差异化行为？

## Theory of Mind

扩展：

```text
A believes X
A believes B believes X
A believes B believes A believes X
```

服务于：

- 欺骗
- 隐瞒
- 谈判
- 误会
- 戏剧反讽

## Agent-Based Modeling

```text
Agent
→ Observe
→ Update Belief
→ Decide
→ Act
```

多个 Agent 共同改变世界。

## Causal Graph

```text
Node = State Variable
Edge = Causal Relation
```

支持：

```text
Intervention
Counterfactual
Path Analysis
```

## Lens Learning

当前 Lens 由 Prompt 驱动。

未来：

```text
Domain Data
→ Lens Fine-tuning
→ Specialized Causal Hypothesis Generator
```

## Lens Debate

Lens 可能冲突：

```text
EconomicLens:
公开对抗成本高，因此不会行动。

PsychologyLens:
羞辱触发强烈愤怒，冲动行动概率上升。
```

未来设计：

```text
Hypothesis Conflict Resolver
```

## Philosophy as Meta-Reasoning

真正值得研究：

> 哲学方法论如何改变因果搜索和未来评估？

例如：

```text
Dialectical Method
→ Search Internal Contradictions
→ Identify Accumulating Tensions
→ Predict Qualitative Change

Consequentialist Method
→ Generate Stakeholders
→ Estimate Outcomes
→ Compare Consequences

Deontological Method
→ Detect Rules and Duties
→ Reject Certain Actions
```

哲学应改变算法过程，而不是 Prompt 口吻。

## 最终愿景

> 构建一个能够显式表示世界事实、主体认知差异与领域因果机制，并在不确定条件下生成多种可解释未来路径的动态叙事世界推演系统。
