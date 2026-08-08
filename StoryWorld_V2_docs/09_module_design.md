# 09 Python 模块设计

## core/

```text
core/
├── llm_client.py
├── world_initializer.py
├── observation_engine.py
├── evidence_evaluator.py
├── belief_updater.py
├── cognition_engine.py
├── theory_of_mind.py
├── lens_router.py
├── hypothesis_conflict_resolver.py
├── agent_action_model.py
├── future_generator.py
├── agent_consistency.py
├── future_evaluator.py
├── world_transition.py
├── narrative_importance.py
├── narrative_engine.py
├── scene_generator.py
├── image_prompt_generator.py
└── output_exporter.py
```

其中 `theory_of_mind.py`、`hypothesis_conflict_resolver.py` 与 `agent_action_model.py` 是 V2.2 新增目标；当前仓库尚未完成这些模块。

## lenses/

```text
lenses/
├── base.py
├── psychology.py
├── economics.py
└── social_structure.py
```

## WorldLens

```python
class WorldLens(ABC):
    @abstractmethod
    def analyze(
        self,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
    ) -> list[CausalHypothesis]:
        raise NotImplementedError
```

## ObservationEngine

职责：

- 根据 location 过滤事实。
- 根据 visibility 过滤事实。
- 根据 role 提供额外观察。
- 不负责解释。

## CognitionEngine

```text
Observation
→ Evidence Evaluation
→ Bayesian Belief Update
→ Belief State
→ Mental Model
→ Bias Filter
→ Interpretation
```

`CognitionEngine` 负责流程编排。`MentalModelEngine` 将 Observation 与更新后的 Belief 组织为因果假设、制度预期和相关价值权重；`BiasFilter` 根据认识论、价值与不确定性容忍度记录偏差类型、强度和显著性焦点；`InterpretationEngine` 只消费这两层的结构化输出，生成 `meaning`、`emotional_response` 和 `action_implication`。生成的情绪反应写回 `SubjectiveWorldModel`，供后续认知步骤使用。

## PsychologyEngine

```text
World Event
→ Perception
→ Belief
→ Emotional Appraisal
→ Stress State
→ Motivation State
→ Value Assessment
→ Decision
→ Action
```

`perceive()` 按 Event visibility 和行动者身份执行信息边界过滤，并结合主体 Value、Epistemology 与 Observation 计算 threat、controllability、ambiguity 和 salience。`appraise()` 将更新后的 Belief 与 Interpretation 转换为 Emotion、Stress 和 Motivation。DecisionEngine 使用 Motivation alignment 与 Stress adjustment 调整 ValueAssessment，并在 Decision 中保留整条心理状态引用。

## EconomicEngine

```text
World
→ Information Boundary
→ Belief
→ Motivation + Value
→ Decision
→ Action
```

`assess_context()` 先根据 Observation visibility 生成逐主体 InformationBoundary，再结合 Belief uncertainty、Resource quantity、owner、access rules 和 Institution transparency 形成角色可知的经济约束。`evaluate_actions()` 结合 Motivation 与 Value，对 Candidate Actions 计算 expected benefit、expected cost、net incentive、forgone alternative 和 opportunity cost。DecisionEngine 将 Economic Utility 作为 `ValueAssessment` 的独立评分分量，并保留 Boundary、Belief、Motivation、Decision 与 Action 的闭合引用。

## SocialStructureEngine

```text
World → Observation → Belief
                    ├→ Psychology: Motivation / Emotion / Bias
                    └→ Society: Role / Norm / Institution
                                      ↓
                              Decision → Action
```

`assess_context()` 从 Agent roles、Norm clarity / sanctions、Institution authority / resource control 生成逐主体 RoleAssessment、NormPressureAssessment 和 InstitutionPowerAssessment。`evaluate_actions()` 将这些社会状态与 PsychologyContext、BiasFilterResult 汇合，对 Candidate Action 计算社会适配度。DecisionEngine 将 Social compatibility 作为 `ValueAssessment` 的独立评分分量，并在 Decision 中保留 `social_evaluation_id`。

## LensRouter / HypothesisConflictResolver

```text
Objective State
→ Enabled Lenses
→ Hypothesis Pool
→ Support / Conflict / Condition Relations
→ FutureEvaluator
```

`LensRouter.route()` 支持启用或关闭指定 Lens，并返回 `LensAnalysisResult`。Resolver 基于 `promotes_actions` 和 `inhibits_actions` 判断跨 Lens 关系，不解析自然语言 claim。`FutureEvaluator.causal_support_score()` 使用 confidence 加权假设证据，并根据 supports、contradicts、conditions 调整分数；未解决冲突不会从结果中删除。

## BeliefUpdater

输入旧 Belief 与结构化 Evidence，使用显式先验、`P(E|H)` 和 `P(E|~H)` 计算后验。支持性证据提高后验，反驳性证据降低后验；每次更新输出 `BayesianBeliefUpdate` 与 `BeliefState`，不以新对象覆盖历史原因链。

## DecisionEngine

`ValueAssessment` 对行动与角色价值、Motivation、Stress 和 Economic Utility 的匹配程度评分；`Decision` 引用 Perception、Belief State、Interpretation、Emotional Appraisal、Stress State、Motivation State 和 Value Assessment；`ActionExecutor` 生成已执行 Action；`WorldTransition` 根据 Action 与环境变化生成客观 World Event。

## LensRouter

第一版固定调用三个 Lens，并合并假设。

## TheoryOfMindEngine

输入主体自己的 `SubjectiveWorldModel`、可见 Observation 与他人公开行为，输出结构化 `BeliefAboutOther`。禁止读取目标角色私有主观状态作为推理捷径。

输出进入 `DecisionEngine`：每个 Decision 同时引用自己的 `belief_state_id` 和一个或多个 `other_model_ids`。Other Model 可以调整合作、对抗、秘密行动等候选项，但不能直接修改 World State。执行后的 Event 和 State Provenance 继续保存这些引用。

## HypothesisConflictResolver

标记跨 Lens 的支持、冲突和条件关系。Resolver 不直接修改世界，也不删除尚未解决的少数假设。

## AgentActionModel

输入：

```text
Subjective Model
Belief State / Possible World Context
Emotion / Motivation
Value System
Beliefs About Others
Causal Hypotheses
Objective Constraints
```

输出多个带解释分解的 `AgentActionDecision`，供 Future Generator 组合为世界状态分支。

当前实现对 belief、possible world、goal、value、emotion、motivation、other model 与 constraint 八项评分。阈值随 belief uncertainty、stress 和 information coverage 调整；动作达到阈值表示“足够可接受”，排序第一的动作标记为 preferred。所有动作仍作为 Candidate Future 的可比较分支保留，最终执行权属于 Decision Engine。

## FutureGenerator

输入：

```text
Objective State
Subjective Models
Hypotheses
Possible World Context
Active Processes
Agent Action Decisions
```

输出：

```text
3～5 CandidateFuture
```

每个输出必须形成独立机制而非同义行动文案，并闭合以下引用：

```text
Source State
→ Possible World / Belief Distribution
→ Supporting + Opposing Hypotheses
→ Future Mechanism
→ Agent Action
→ Expected StateChange
```

当前实现生成信息发现、社会协作、制度争议和过程惯性四类分支；相对可信度由 base rate、机制支持、抑制约束和 belief plausibility 共同计算。

## FutureEvaluator

评分：

```text
causal_support
agent_consistency
state_compatibility
constraint_satisfaction
cross_lens_support
contradiction_penalty
```

当前实现输出 `FutureEvaluation`，并以如下权重计算最终分数：

```text
0.15 * estimated_plausibility
+ 0.20 * causal_support
+ 0.20 * agent_consistency
+ 0.15 * constraint_satisfaction
+ 0.20 * compatibility
+ 0.10 * cross_lens_support
- 0.15 * contradiction_penalty
```

其中 `compatibility` 由 `state_compatibility`（0.50）、`epistemic_compatibility`（0.20）和 `action_compatibility`（0.30）组成。StateChange 必须匹配当前 `source_state_id`、可解析路径和 `old_value`；约束与行动兼容性继承对应的 `AgentActionDecision`。输出同时记录正反假设、跨 Lens 关系、约束、动作决策及状态路径，供实验复核。

## WorldTransition

必须：

- 在修改前校验 Candidate Future 的 `source_state_id`。
- 校验 StateChange 路径存在、`old_value` 与当前事实一致、`new_value` 不是 no-op，且不得重复修改同一路径或覆盖 state_id、step、timestamp、events、history。
- 校验 Action 已执行并与 Decision、Candidate Future 及目标 step 一致。
- 在深拷贝状态上原子应用全部变化，校验失败时旧状态和新状态都不得出现部分写入。
- 创建新 `state_id`、World Event 和强类型 StateProvenance。
- 将 StateChange 关联到 source/target state、event、action、decision、AgentActionDecision、ValueAssessment、future、FutureEvaluation、正反 hypothesis、relation、lens、observation、belief、goal、emotion、motivation、constraint、Other Model 与 Possible World。
- World Event 通过 `provenance_ids` 反向引用产生的状态变化。

## NarrativeImportance

`NarrativeImportance.assess()` 输入 Old/New Objective State、World Event、Selected Future、Subjective Models 与 Future Evaluation，输出七维 `NarrativeImportanceAssessment`。评分依据结构化机制、实际 StateChange、Action / Decision、因果支持和主体价值目标，不能依据摘要关键词。`score(future)` 仅作为旧调用方的兼容接口；主流水线使用完整 `assess()`。

`rank()` 按 weighted score 降序和 event ID 稳定排序。Narrative Importance 在 World Transition 之后执行，不得修改 Objective World，也不得反馈到 Future Evaluation。

## NarrativeEngine

World Simulation 循环完成后，`FabulaBuilder` 从 Objective State snapshots、World Events 与 StateProvenance 构建时间和因果均闭合的 Fabula。`NarrativePlanner.plan()` 按 Importance 选材，`arrange()` 生成独立 Syuzhet，`focalize()` 依据焦点角色真实 Observation 建立第三人称限知的信息边界，`story_output()` 汇总表达链引用。

`NarrativeEngine.express_planned()` 将计划结果转换为 NarrativeEvent；`analyze_information_effect()` 根据 Focalization 的 character/audience/withheld 信息集合确定 alignment、suspense、mystery 或 dramatic irony；`render_beat()` 再组合世界动作、可见线索、角色情绪、信息差提示和叙事功能，输出可追溯 NarrativeBeat。这些步骤均只读 Objective World，不参与世界演化，也不允许把 withheld 内容写入正文。

## LensAblationExperiment

`experiments/lens_ablation.py` 使用 `run_pipeline(enabled_lenses=...)` 运行全 Lens 基线和三组 leave-one-out 条件。禁用 Lens 时同时切断其 Hypothesis、关系和 ValueAssessment 分量，避免“名称删除但评分仍泄漏”。运行器输出世界指纹、假设与关系 IDs、Future / Action scores、排序、最终选择和状态指纹，并导出 JSON 与 Markdown。

## Multi-step Simulation

`experiments/multi_step_simulation.py` 调用确定性的 `run_pipeline` 执行 3-5 步 rollout，并输出 `MultiStepSimulationResult`。每个 `SimulationStepTrace` 保存 source/target state、Observation、BeliefState、Candidate Future、Decision、Action、Event、StateChange 与 provenance IDs。运行器验证状态连续性、快照不可变、old/new value、无 no-op 和引用闭合。

## Subjective Model Ablation

`run_pipeline(use_subjective_models=False)` 保留相同 Objective Agent、角色和可见性规则，但将配置的 Subjective World Model 替换为中性接口载体，不注入个体知识、信念先验、价值、目标或认识论偏好。该模式只用于受控实验，不改变默认运行行为。

`experiments/world_model_ablation.py` 在 3 步条件下比较完整与中性主体配置，固定 Objective World、Observation 边界、Lens、Future 模板及决策权重，比较 Belief、Interpretation、Future / Action Score、选择轨迹、最终事实状态和 provenance。Action 未翻转不自动判为失败，只要认知或决策形成机制出现可复现差异且两组 provenance 完整。

## LLM 使用位置

允许用于：

```text
World Initialization（结构化校验后）
Belief Interpretation
Theory of Mind 假设生成
Lens Analysis
Future Generation
Narrative Expression
```

行动评分、状态应用、provenance 记录和实验指标优先采用确定性代码。禁止一个 Prompt 一次性完成所有模块。

## 调试输出

```text
observations.json
subjective_models.json
beliefs_about_others.json
hypotheses.json
hypothesis_relations.json
agent_actions.json
candidate_futures.json
selected_future.json
objective_states.json
state_provenance.json
narrative_importance_assessments.json
narrative_plans.json
syuzhets.json
focalizations.json
story_outputs.json
narrative_events.json
narrative_beats.json
scene_cards.json
```

当前 OutputExporter 已生成上述核心链路文件；一次完整运行共输出 52 个 JSON 和一份 Markdown 汇总报告。
