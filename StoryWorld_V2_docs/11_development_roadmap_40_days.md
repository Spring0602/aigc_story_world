# 11 StoryWorld V2 40 天学习与开发计划

> 目标：40 天完成 StoryWorld V2 MVP，而不是完成“人类世界模拟器”。

每天建议约 4 小时：

```text
30% 学习
50% 开发
20% 记录与测试
```

---

# Phase 1：重建认知框架与工程基础

## Day 1｜理解 V2 架构

- [已完成] 阅读 `01_project_definition.md`
- [已完成] 阅读 `02_core_architecture.md`
- [已完成] 手画 V2 数据流
- [已完成] 写 500 字：为什么 World Engine 和 Narrative Engine 要分开

交付：`docs/my_understanding_v2.md`

## Day 2｜Python 数据工程复习

学习：

- json
- pathlib
- Pydantic BaseModel
- 类型注解

任务：

- [已完成] 创建 V2 项目
- [已完成] 配置虚拟环境
- [已完成] 初始化 Git
- [已完成] 安装 pydantic
- [已完成] 创建 schemas 目录

## Day 3｜ObjectiveWorldState

学习：

- 状态建模
- Entity / Relation
- State provenance

任务：

- [已完成] 定义 ObjectiveWorldState
- [已完成] 定义 Agent
- [已完成] 定义 Relationship
- [已完成] 定义 Institution
- [已完成] 定义 ActiveProcess

交付：`schemas/objective_world.py`

## Day 4｜SubjectiveWorldModel

学习：

- Belief
- Knowledge
- False Belief
- Uncertainty

任务：

- [已完成] 定义 SubjectiveWorldModel
- [已完成] 定义 Belief
- [已完成] 定义 Epistemology
- [已完成] 定义 Value
- [已完成] 定义 EmotionState

交付：`schemas/subjective_world.py`

## Day 5｜其余 Schema

- [已完成] Observation
- [已完成] Interpretation
- [已完成] CausalHypothesis
- [已完成] CandidateFuture
- [已完成] StateChange
- [已完成] NarrativeEvent
- [已完成] SceneCard

完成标准：所有 Pydantic Schema 可成功实例化。

---

# Phase 2：客观世界与主体认知

## Day 6｜假数据世界

创建固定案例：

```text
校园网络监控系统
```

- [ ] 1 个大学 Institution
- [ ] 2 个角色
- [ ] 1 个 ActiveProcess
- [ ] 2 个隐藏事实
- [ ] 1 个公开事实

交付：`data/examples/campus_monitoring.json`

## Day 7｜ObservationEngine

学习：

- 信息可见性
- 局部观察

任务：

- [ ] 根据 location 过滤事实
- [ ] 根据 visibility 过滤事实
- [ ] 根据 role 提供额外观察

交付：`core/observation_engine.py`

## Day 8｜认识论与证据评价

学习：

- Empiricism
- Testimony
- Authority
- Evidence Reliability
- Bayesian intuition

任务：

- [ ] 写简化 Evidence Score
- [ ] 不同角色对同一 Observation 给出不同信任度

交付：`core/evidence_evaluator.py`

## Day 9｜Belief Update

实现：

```text
Old Belief
+ Observation
+ Epistemology
→ New Belief
```

- [ ] confidence 更新
- [ ] evidence 记录
- [ ] uncertainty 保存

交付：`core/belief_updater.py`

## Day 10｜Interpretation Engine

设置：

- 林夏：低权威信任，高数据信任
- 王晨：高权威信任，中等数据信任

任务：

- [ ] 同一事实产生不同解释
- [ ] 保存 reasoning_basis
- [ ] 完成 perspective difference 测试

交付：`core/cognition_engine.py`

---

# Phase 3：World Lens 与因果假设

## Day 11｜因果推理基础

学习：

- Cause vs Correlation
- Mediator
- Confounder
- Trigger
- Constraint
- Feedback Loop

任务：

- [ ] 给 10 个日常事件画简单因果链
- [ ] 标出 driver / mediator / constraint

交付：`docs/causal_exercises.md`

## Day 12｜WorldLens 接口

- [ ] 定义抽象 WorldLens
- [ ] 定义 Lens 输出验证
- [ ] Lens 不得直接修改世界状态

交付：`lenses/base.py`

## Day 13｜PsychologyLens

学习：

- Emotion
- Stress
- Cognitive Bias
- Motivation
- Social Perception

任务：

- [ ] 实现 PsychologyLens Prompt
- [ ] 输出 CausalHypothesis
- [ ] 固定 drivers / mediators / constraints

交付：`lenses/psychology.py`

## Day 14｜EconomicLens

学习：

- Scarcity
- Incentive
- Opportunity Cost
- Information Asymmetry
- Resource Dependence

任务：

- [ ] 实现 EconomicLens
- [ ] 测试资源竞争案例

交付：`lenses/economics.py`

## Day 15｜SocialStructureLens

学习：

- Role
- Norm
- Institution
- Authority
- Power Asymmetry

任务：

- [ ] 实现 SocialStructureLens
- [ ] 测试学生—学校权力关系

交付：`lenses/social_structure.py`

## Day 16｜Lens Router

- [ ] 调用三个 Lens
- [ ] 合并 CausalHypothesis
- [ ] 去除完全重复假设
- [ ] 保存 Lens 来源

交付：`core/lens_router.py`

## Day 17｜Hypothesis Debugger

检查每条假设：

- [ ] claim
- [ ] drivers
- [ ] mediators
- [ ] constraints
- [ ] time_scale
- [ ] confidence

交付：`tests/test_hypothesis.py`

---

# Phase 4：Candidate Future 与世界演化

## Day 18｜概率与不确定性基础

学习：

- Conditional Probability
- Uncertainty
- Calibration intuition
- Relative plausibility

任务：

- [ ] 明确项目不宣称真实概率
- [ ] 统一使用 `estimated_plausibility`

交付：`docs/probability_notes.md`

## Day 19｜FutureGenerator

- [ ] 生成 3 个机制明显不同的 Future
- [ ] 每个 Future 绑定 hypothesis_ids
- [ ] 保存 uncertainties 和 risks

交付：`core/future_generator.py`

## Day 20｜角色行动合理性

学习：

- Bounded Rationality
- Goal
- Value
- Emotion
- Habit

评分：

```text
Knowledge Compatibility
Value Compatibility
Goal Compatibility
Emotion Compatibility
Epistemic Compatibility
```

交付：`core/agent_consistency.py`

## Day 21｜FutureEvaluator

实现：

```text
causal_support
agent_consistency
state_compatibility
constraint_satisfaction
cross_lens_support
contradiction_penalty
```

交付：`core/future_evaluator.py`

## Day 22｜WorldTransition

- [ ] 应用 StateChange
- [ ] 生成新 state_id
- [ ] 保存 provenance
- [ ] 保存 old/new state

交付：`core/world_transition.py`

## Day 23｜单步完整世界循环

跑通：

```text
Objective World
→ Observation
→ Belief
→ Interpretation
→ Lens
→ Hypothesis
→ Candidate Futures
→ Future Selection
→ World Transition
```

交付：StoryWorld V2 v0.3

## Day 24｜三步世界演化

- [ ] 连续运行 3 step
- [ ] 每步重新观察
- [ ] 每步更新 belief
- [ ] 每步重新调用 Lens
- [ ] 每步生成新 Future

交付：`outputs/examples/campus_monitoring/world_run/`

---

# Phase 5：Narrative Engine

## Day 25｜叙事学基础

学习：

- Fabula
- Syuzhet
- Focalization
- Narrator
- Dramatic Irony
- Suspense
- Mystery

任务：

- [ ] 写 5 个“同一事实不同视角”的例子

交付：`docs/narratology_notes.md`

## Day 26｜Narrative Importance

评分：

```text
Conflict Change
Information Gain
Character Decision
Relationship Change
Irreversibility
Theme Relevance
Visual Potential
```

交付：`core/narrative_importance.py`

## Day 27｜NarrativeEngine

- [ ] 选择 focal_agent
- [ ] 决定 revealed_information
- [ ] 决定 hidden_information
- [ ] 生成 NarrativeEvent

交付：`core/narrative_engine.py`

## Day 28｜SceneGenerator

NarrativeEvent → SceneCard

字段：

- [ ] location
- [ ] time
- [ ] focal_agent
- [ ] visible_action
- [ ] visual_clue
- [ ] camera
- [ ] lighting
- [ ] atmosphere

交付：`core/scene_generator.py`

## Day 29｜Image Prompt

- [ ] 中文 Prompt
- [ ] 英文 Prompt
- [ ] Negative Prompt
- [ ] 固定像素风 RPG CG 风格

交付：`core/image_prompt_generator.py`

## Day 30｜Narrative Separation Test

- [ ] Narrative Engine 不创造新事实
- [ ] Subjective Belief 不被写成 Objective Fact
- [ ] 隐藏事实不会提前泄露

交付：`tests/test_narrative_separation.py`

---

# Phase 6：测试、前端与作品集

## Day 31｜五类测试案例

建立：

- [ ] 校园监控
- [ ] 贫困学生资源竞争
- [ ] 实验室权力冲突
- [ ] 群体谣言传播
- [ ] 灾难物资分配

交付：`data/test_cases/`

## Day 32｜Perspective Evaluation

每个案例检查：

- [ ] 角色是否形成差异化解释
- [ ] 差异是否来自显式认知参数
- [ ] 是否出现角色全知

交付：`docs/perspective_evaluation.md`

## Day 33｜Causal Evaluation

人工评估：

- [ ] 因果显式性
- [ ] 时间尺度
- [ ] Lens 机制合理性
- [ ] Candidate Future 多样性

交付：`docs/causal_evaluation.md`

## Day 34｜Gradio 基础

学习：

- Blocks
- Row
- Column
- JSON
- Markdown
- Button

任务：

- [ ] 创建页面
- [ ] 接入 `run_pipeline`

交付：`frontend/gradio_app.py`

## Day 35｜V2 Demo 页面

展示：

```text
输入设定
Objective World
角色主观世界
Lens 假设
Candidate Futures
Selected Future
Narrative Event
Scene Card
```

交付：可运行 Demo

## Day 36｜可解释性展示

用户点击某 Future，展示：

```text
Why?
→ Supporting Lenses
→ Supporting Hypotheses
→ Agent Beliefs
→ Constraints
```

交付：Explain Future 面板

## Day 37｜最佳 Showcase

推荐：

```text
校园监控：不同学生对同一网络异常的认知差异
```

展示：

- [ ] Objective Fact
- [ ] Agent A Observation / Interpretation
- [ ] Agent B Observation / Interpretation
- [ ] 三个 Lens
- [ ] 三个 Future
- [ ] 被选择 Future
- [ ] Narrative Event
- [ ] Scene Prompt

交付：`outputs/showcase/campus_monitoring.md`

## Day 38｜README 与研究表达

README 包含：

- [ ] 项目动机
- [ ] 核心问题
- [ ] 架构图
- [ ] 六个核心对象
- [ ] Demo
- [ ] 案例
- [ ] 局限
- [ ] Future Work

交付：高质量 README

## Day 39｜代码清理与复现

- [ ] 新环境安装
- [ ] 按 README 运行
- [ ] 删除无用代码
- [ ] 检查 `.env`
- [ ] 检查异常处理
- [ ] 检查输出目录

交付：StoryWorld V2 v0.9

## Day 40｜最终打包

最终成果：

- [ ] 可运行代码
- [ ] V2 Gradio Demo
- [ ] 五类测试案例
- [ ] 最佳 Showcase
- [ ] 技术文档
- [ ] README
- [ ] 演示视频
- [ ] 项目总结

最终版本：

- [ ] **StoryWorld V2 v1.0 MVP**

---

# 40 天后暂不要求掌握

- 从零训练 LLM
- 从零训练 World Model
- 强化学习
- Dreamer 完整复现
- Genie 复现
- Active Inference 数学推导
- 大规模 Agent 仿真
- 完整哲学体系形式化

40 天后再进入研究强化阶段。
