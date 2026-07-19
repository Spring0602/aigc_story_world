# 02 StoryWorld V2 核心架构

## 总体流程

```text
User Setting
     ↓
World Initializer
     ↓
Objective World State S_t
     ↓
Observation Engine
     ↓
Agent Observations O_i
     ↓
Subjective World Models B_i
     ↓
Interpretation Engine
     ↓
Agent Interpretations I_i
    ↓
Theory of Mind
    ↓
Beliefs About Others M_i,j
    ↓
World Lens Router
     ↓
Causal Hypotheses H_1 ... H_n
    ↓
Hypothesis Conflict Resolver
    ↓
Agent Action Model
    ↓
Candidate Agent Actions A_i
    ↓
Future Generator
     ↓
Candidate Futures F_1 ... F_k
     ↓
Future Evaluator
     ↓
Selected World Transition
     ↓
Objective World State S_t+1
     ↓
Narrative Engine
     ↓
Narrative Event / Scene Card
```

## 两条数据流

### 世界推演流

```text
State
→ Observation
→ Belief Update
→ Interpretation
→ Theory of Mind
→ Causal Hypothesis
→ Conflict Resolution
→ Agent Action
→ Candidate Future
→ Transition + Provenance
```

### 叙事表达流

```text
World Changes
→ Narrative Importance
→ Focalization
→ Information Control
→ Event Expression
→ Scene Card
```

## 为什么不再直接使用 PlotEngine

旧架构：

```text
WorldState → PlotEngine → Event
```

问题：

- 模型优先追求戏剧性。
- 事件可能缺乏真实驱动力。
- 不同角色认知差异被压平。
- 领域机制只能作为 Prompt 描述。
- 未来只有一条。

V2：

```text
World Engine 负责“可能发生什么”
Narrative Engine 负责“展示什么”
```

## 40 天目标模块

```text
WorldInitializer
ObservationEngine
CognitionEngine
TheoryOfMindEngine
WorldLens
LensRouter
HypothesisConflictResolver
AgentActionModel
FutureGenerator
FutureEvaluator
WorldTransition
NarrativeEngine
SceneGenerator
OutputExporter
```

当前仓库中部分后期模块已有可运行原型，但新版计划将按研究验收标准重新实现或验证。开发状态以 V2.2 详细执行版和测试结果为准，不以“文件已经存在”为准。

## 三种状态

### Objective State

世界客观事实。

### Observed State

角色能看到的信息。

### Interpreted State

角色基于自身认知对观察的解释。

### Socially Modeled State

角色对其他角色知识、信念和预期行动的估计。该状态可能错误，并且不能直接写入 Objective State。

## 架构原则

- 每个模块输入输出结构化。
- LLM 是模块实现方式，不是架构本身。
- Lens 必须可插拔。
- Objective State 不允许角色直接修改。
- Candidate Future 必须保留不确定性。
- Candidate Future 是世界状态分支，不是剧情分支。
- Agent Action 必须能追溯到 Belief、Goal、Value、Emotion 与 Constraint。
- 冲突的 Lens 假设必须显式保留并参与评估。
- World Transition 必须记录 source state、action、hypotheses、old/new value 与 step。
- Narrative Engine 不得反向篡改世界事实。
