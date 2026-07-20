# 11 StoryWorld V2 40 天学习与开发计划（V2.1 修订版）

> 本版本基于第 6 天实际开发结果调整。

> 文档角色：本文件是 **V2.1 研究路线图**，用于说明研究目标、阶段与优先级；每日任务、交付物和验收以 `11_development_roadmap_40_days(1).md` 的 **V2.2 详细执行版**为准。

> 状态说明：当前仓库已具备若干可运行原型，但新版计划会按更严格的研究标准重新验收。文件存在或流程可运行，不代表 Theory of Mind、行动归因、Lens 冲突或完整 provenance 已完成。

原计划目标偏向"完成一个动态剧情生成系统"，现在调整为：

**验证一个社会认知世界模型（Social Cognitive World Model）的可行性。**

核心路线：

``` text
主体认知建模
↓
因果世界推演
↓
动态叙事表达
```

------------------------------------------------------------------------

# 一、为什么需要调整

目前项目已经完成：

-   Objective World
-   两个角色
-   Subjective World Model
-   Belief
-   Epistemology
-   不同角色对同一事件产生差异化解释

因此项目最有价值的部分不是：

> AI 能否写故事

而是：

> AI 能否模拟不同主体如何理解世界，并基于这种理解产生不同未来。

后续重点增加：

-   Theory of Mind
-   Belief Update
-   Causal Reasoning
-   Agent Action Model
-   社会机制演化
-   可解释性实验

降低：

-   过早优化图片生成
-   过早扩展剧情表达
-   过早增加大量哲学模块

------------------------------------------------------------------------

# 二、新路线

``` text
Phase 1
主体认知模型强化

↓

Phase 2
因果机制建模

↓

Phase 3
未来推演与世界演化

↓

Phase 4
叙事表达

↓

Phase 5
实验验证
```

------------------------------------------------------------------------

# Phase 1：主体认知模型强化（Day 1-10）

## Day 1-4：客观/主观状态基础

已完成基础结构：

-   ObjectiveWorldState
-   AgentProfile
-   SubjectiveWorldModel

新版待强化：

``` text
State Provenance
Knowledge / Uncertainty 结构化
Human Nature Model
Theory of Change
```

重点理解：

角色不是人格标签，而是拥有：

``` text
Knowledge
Belief
False Belief
Uncertainty
Value
Goal
Emotion
Epistemology
Theory of Change
Human Nature Model
```

------------------------------------------------------------------------

## Day 5-7：价值、观察与解释

建立可控的认知差异：

-   Value 与 Human Nature Model
-   Partial Observability
-   Observation → Belief → Mental Model → Bias Filter → Interpretation
-   同一 Observation 的参数对照测试

------------------------------------------------------------------------

## Day 8-10：Belief Update 与 Theory of Mind

新增学习：

-   一阶信念
-   二阶信念
-   他人认知预测

例如：

``` text
A believes X

A believes B believes X
```

同时完成：

``` text
Old Belief + New Evidence + Epistemology → Updated Belief
```

测试：

角色是否能预测别人如何理解自己。

------------------------------------------------------------------------

目标是允许角色保持合理但错误的认知，并基于有限证据形成可能错误的他人模型。

------------------------------------------------------------------------

# Phase 2：因果世界建模（Day 11-20）

## Day 11-12

学习：

-   Cause vs Correlation
-   Driver
-   Mediator
-   Constraint
-   Feedback Loop
-   Path Dependence
-   Counterfactual

------------------------------------------------------------------------

## Day 13-16

实现：

World Lens：

``` text
PsychologyLens
EconomicLens
SocialStructureLens
```

输出：

``` text
CausalHypothesis
```

而不是观点描述。

------------------------------------------------------------------------

## Day 17-20

新增：

Hypothesis Conflict Resolver

处理：

不同 Lens 对同一事件的冲突解释。

例如：

心理学：

``` text
压力导致冲动
```

经济学：

``` text
行动成本导致谨慎
```

------------------------------------------------------------------------

# Phase 3：未来推演与世界演化（Day 21-30）

## Day 21-23

Candidate Future：

生成多个可能未来：

``` text
Future A
Future B
Future C
```

重点：

不是剧情分支，而是世界状态分支。

------------------------------------------------------------------------

## Day 24-26

Agent Action Model：

行动由：

``` text
Belief
+
Goal
+
Value
+
Emotion
+
Constraint
```

共同决定。

------------------------------------------------------------------------

## Day 27-30

完成：

World Transition：

``` text
State(t)

↓

Action

↓

Environment Change

↓

State(t+1)
```

所有变化保存：

``` text
provenance
```

------------------------------------------------------------------------

# Phase 4：Narrative Engine（Day 31-35）

世界演化完成后，再进行：

``` text
World Event

↓

Narrative Importance

↓

Focalization

↓

Scene Card
```

重点：

-   谁知道？
-   谁不知道？
-   观众知道什么？
-   信息差在哪里？

------------------------------------------------------------------------

# Phase 5：实验验证（Day 36-40）

## Experiment 1：Same World Different Minds

验证：

同一客观世界，不同认知模型是否产生不同未来。

------------------------------------------------------------------------

## Experiment 2：Lens Ablation

去掉不同 Lens，比较未来变化。

------------------------------------------------------------------------

## Experiment 3：Baseline Comparison

Baseline：

``` text
Prompt
→ LLM
→ Story
```

StoryWorld：

``` text
World
→ Cognition
→ Lens
→ Future
→ Narrative
```

比较：

-   角色一致性
-   因果解释
-   未来多样性
-   可解释性

------------------------------------------------------------------------

# 最终目标

40 天结束不是：

"生成一个故事"。

而是完成：

## Social Cognitive World Model MVP

结构：

``` text
Objective World

↓

Multiple Subjective World Models

↓

Causal Lenses

↓

Candidate Futures

↓

World Transition

↓

Dynamic Narrative
```

------------------------------------------------------------------------

# 暂时延期

-   复杂哲学 Lens
-   图像生成优化
-   大规模 Agent
-   强化学习
-   神经 World Model
-   完整社会模拟

原因：

当前最大创新点：

> 模拟不同主体如何理解世界，并影响世界未来。
