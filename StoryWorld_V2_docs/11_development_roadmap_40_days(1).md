# 11 StoryWorld V2 40 天学习与开发计划（V2.2 详细执行版）

> 本版本基于当前第 6 天成果调整。
>
> 目标：
>
> 在 40 天内完成一个 **Social Cognitive World Model MVP**。
>
> 每一天包含：
>
> -   学习内容
> -   开发任务
> -   当日交付物

> 文档角色：本文件是 **V2.2 详细执行与验收版**。V2.1 研究路线图解释研究动机，本文件决定每日具体工作。
>
> 验收规则：当前仓库中提前存在的 Schema、Engine、Lens、Narrative 或 Demo 只作为可运行基线。只有满足当天新增测试、结构化输出和实验要求，才标记该日完成。

------------------------------------------------------------------------

# Phase 1：主体认知模型完善（Day 1-10）

## Day 1：项目架构理解与工程规范

> 状态：已完成（2026-07-19）。基础目录、配置、依赖和项目说明已建立。

### 学习

-   软件模块化设计
-   Python 项目结构
-   Pydantic 数据建模
-   JSON Schema

### 开发

整理当前代码：

    schemas/
    core/
    lenses/
    data/
    tests/

补充：

-   config.py
-   requirements.txt
-   README.md

### 交付

    项目基础框架 v0.1

------------------------------------------------------------------------

## Day 2：Objective World State 完善

> 状态：已完成（2026-07-19）。实体、事件、资源和状态溯源均已强类型化，并提供独立示例世界。

### 学习

-   Entity
-   Relation
-   State Representation
-   State Provenance

### 开发

完善：

``` text
ObjectiveWorldState
Agent
Location
Institution
Resource
Relationship
Event
```

增加：

``` json
provenance
history
timestamp
```

### 交付

    schemas/objective_world.py
    example_world.json

------------------------------------------------------------------------

## Day 3：Subjective World Model 完善

> 状态：已完成（2026-07-19）。已知事实、不确定性、普通信念和错误信念可分别表示。

### 学习

-   Knowledge
-   Belief
-   False Belief
-   Uncertainty

### 开发

完善：

``` text
SubjectiveWorldModel
Belief
Knowledge
Uncertainty
```

实现：

角色拥有：

-   已知事实
-   未知事实
-   错误信念

### 交付

    schemas/subjective_world.py

------------------------------------------------------------------------

## Day 4：认识论模型 Epistemology

> 状态：已完成（2026-07-19）。证据类型映射到对应信任维度，同一证据可产生不同置信评分。

### 学习

-   认识论基础
-   Evidence
-   Authority
-   Experience
-   Consensus

### 开发

实现：

``` json
Epistemology:
{
trust_data,
trust_authority,
trust_personal_experience,
trust_social_consensus,
tolerance_for_uncertainty
}
```

测试：

同一 Observation 不同角色不同信任。

### 交付

    evidence_evaluator.py

------------------------------------------------------------------------

## Day 5：Value 与 Human Nature Model

> 状态：已完成（2026-07-19）。角色档案包含价值、人性模型和变革理论，价值差异会影响行动一致性评分。

### 学习

-   Axiology
-   人性假设
-   价值排序

### 开发

增加：

``` text
Values
HumanNatureModel
TheoryOfChange
```

测试：

不同价值导致不同判断。

### 交付

    agent_profiles.json

------------------------------------------------------------------------

## Day 6：Observation Engine

> 状态：已完成（2026-07-19）。观察按公开性、授权角色、授权主体和地点过滤，隐藏事实不可见。

### 学习

-   Partial Observability
-   信息边界

### 开发

实现：

    Objective World

    ↓

    Observation Engine

    ↓

    Agent Observation

规则：

角色不能看到隐藏事实。

### 交付

    core/observation_engine.py

------------------------------------------------------------------------

## Day 7：Interpretation Engine

> 状态：已完成（2026-07-19）。Cognitive Interpretation Layer 已将信念基础、因果框架、主观意义、情绪反应和行动倾向结构化，并验证同一世界中的角色差异。

### 学习

-   Cognitive Bias
-   Mental Model
-   Theory of Mind 基础

### 开发

实现：

    Observation

    ↓

    Belief

    ↓

    Interpretation

测试：

同一事件：

角色A/B/C产生不同解释。

### 交付

    core/cognition_engine.py
    core/interpretation_engine.py
    schemas/interpretation.py

------------------------------------------------------------------------

## Day 8：Belief Update

### 学习

-   Bayesian intuition
-   信念修正

### 开发

实现：

    Old Belief
    +
    New Evidence

    ↓

    Updated Belief

要求：

允许错误但合理的认知。

### 交付

    belief_updater.py

------------------------------------------------------------------------

## Day 9：Theory of Mind

### 学习

-   一阶信念
-   二阶信念
-   他人模型

### 开发

增加：

``` text
BeliefAboutOther
beliefs_about_others
```

案例：

A认为：

    B认为学校是安全的

### 交付

    theory_of_mind.py
    schemas/theory_of_mind.py
    tests/test_theory_of_mind.py

------------------------------------------------------------------------

## Day 10：主体认知实验

### 实验

Same World Different Minds

输入：

同一个 Objective World。

主对照使用完全相同的 Observation，只改变认知配置；另设 Partial Observability 对照测试信息边界。

三个角色：

-   数据主义者
-   制度主义者
-   怀疑主义者

比较：

    Observation
    Belief
    Interpretation
    Action

### 交付

    experiment_01.md

------------------------------------------------------------------------

# Phase 2：因果机制建模（Day 11-20）

## Day 11：因果推理基础

学习：

-   Cause
-   Correlation
-   Driver
-   Mediator
-   Constraint

开发：

整理：

    causal_notes.md

------------------------------------------------------------------------

## Day 12：CausalHypothesis Schema

开发：

定义：

``` text
Claim
Drivers
Mediators
Constraints
TimeScale
Confidence
```

交付：

    causal_hypothesis.py

------------------------------------------------------------------------

## Day 13-14：Psychology Lens

学习：

-   Motivation
-   Emotion
-   Cognitive Bias
-   Stress

开发：

实现：

    PsychologyLens

输出：

CausalHypothesis。

------------------------------------------------------------------------

## Day 15-16：Economic Lens

学习：

-   Scarcity
-   Incentive
-   Opportunity Cost
-   Information Asymmetry

开发：

    EconomicLens

------------------------------------------------------------------------

## Day 17-18：Social Structure Lens

学习：

-   Role
-   Norm
-   Institution
-   Authority
-   Power

开发：

    SocialStructureLens

------------------------------------------------------------------------

## Day 19：Lens Router 与 Hypothesis Conflict Resolver

开发：

    Objective State

    ↓

    Multiple Lens

    ↓

    Hypothesis Pool

    ↓

    Support / Conflict / Condition Relations

要求：

-   不简单按假设数量计算支持度
-   保留尚未解决的跨 Lens 冲突
-   输出结构化 HypothesisRelation

交付：

    core/lens_router.py
    core/hypothesis_conflict_resolver.py
    schemas/hypothesis_relation.py

------------------------------------------------------------------------

## Day 20：Lens 实验

测试：

加入/删除 Lens 是否改变未来。

交付：

    lens_ablation.md

------------------------------------------------------------------------

# Phase 3：未来推演与世界演化（Day 21-30）

## Day 21：Candidate Future Schema

学习：

-   Possible World
-   Uncertainty

开发：

定义：

    CandidateFuture

------------------------------------------------------------------------

## Day 22-23：Future Generator

开发：

生成：

3-5 个未来。

要求：

机制不同。

------------------------------------------------------------------------

## Day 24：Agent Action Model

学习：

-   Bounded Rationality

开发：

行动评分：

    Belief
    Goal
    Value
    Emotion
    Beliefs About Others
    Constraint

输出：

    AgentActionDecision

要求记录每个动作的支持信念、目标、价值、情绪和约束分项。

交付：

    core/agent_action_model.py
    schemas/agent_action.py
    tests/test_agent_action.py

------------------------------------------------------------------------

## Day 25-26：Future Evaluator

开发：

评分：

    causal_support
    agent_consistency
    constraint
    compatibility

------------------------------------------------------------------------

## Day 27-28：World Transition

开发：

实现：

    State(t)

    ↓

    Action

    ↓

    State(t+1)

保存：

    provenance

至少包含：

    source_state_id
    target_state_id
    action_ids
    future_id
    supporting_hypothesis_ids
    source_observation_ids
    old_value / new_value / cause / step

交付：

    core/world_transition.py
    schemas/state_provenance.py
    tests/test_provenance.py

------------------------------------------------------------------------

## Day 29：多步 Simulation

运行：

3-5 step 世界演化。

------------------------------------------------------------------------

## Day 30：世界模型实验

比较：

-   无 Subjective Model
-   有 Subjective Model

效果差异。

------------------------------------------------------------------------

# Phase 4：Narrative Engine（Day 31-35）

## Day 31

学习：

-   Fabula
-   Syuzhet
-   Focalization

------------------------------------------------------------------------

## Day 32

开发：

Narrative Importance。

------------------------------------------------------------------------

## Day 33

开发：

Narrative Engine。

------------------------------------------------------------------------

## Day 34

开发：

Scene Card。

------------------------------------------------------------------------

## Day 35

完成：

World → Story Demo。

------------------------------------------------------------------------

# Phase 5：实验与展示（Day 36-40）

## Day 36

完成：

Baseline。

    Prompt → Story

------------------------------------------------------------------------

## Day 37

完成：

StoryWorld 对比实验。

指标：

-   一致性
-   可解释性
-   多样性
-   provenance 完整性

------------------------------------------------------------------------

## Day 38

制作：

Gradio Demo。

展示：

    World
    Characters
    Beliefs
    Lens
    Future
    Narrative

------------------------------------------------------------------------

## Day 39

整理：

-   README
-   架构图
-   实验报告

------------------------------------------------------------------------

## Day 40

发布：

StoryWorld V2 MVP。

最终成果：

    Social Cognitive World Model

    Objective World

    ↓

    Subjective Minds

    ↓

    Causal Reasoning

    ↓

    Future Simulation

    ↓

    Narrative Generation
