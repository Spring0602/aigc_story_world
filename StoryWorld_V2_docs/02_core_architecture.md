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
World Lens Router
     ↓
Causal Hypotheses H_1 ... H_n
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
→ Belief
→ Interpretation
→ Causal Hypothesis
→ Candidate Future
→ Transition
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

## 第一版必须实现的模块

```text
WorldInitializer
ObservationEngine
CognitionEngine
WorldLens
LensRouter
FutureGenerator
FutureEvaluator
WorldTransition
NarrativeEngine
SceneGenerator
OutputExporter
```

## 三种状态

### Objective State

世界客观事实。

### Observed State

角色能看到的信息。

### Interpreted State

角色基于自身认知对观察的解释。

## 架构原则

- 每个模块输入输出结构化。
- LLM 是模块实现方式，不是架构本身。
- Lens 必须可插拔。
- Objective State 不允许角色直接修改。
- Candidate Future 必须保留不确定性。
- Narrative Engine 不得反向篡改世界事实。
