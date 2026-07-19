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
→ Belief Update
→ Interpretation
```

`CognitionEngine` 负责流程编排，`InterpretationEngine` 负责 Cognitive Interpretation Layer：将 Observation、更新后的 Belief、角色价值观、认识论与当前情绪组合为 `belief_basis`、`causal_frame`、`meaning`、`emotional_response` 和 `action_implication`。生成的情绪反应写回 `SubjectiveWorldModel`，供后续认知步骤使用。

## LensRouter

第一版固定调用三个 Lens，并合并假设。

## TheoryOfMindEngine

输入主体自己的 `SubjectiveWorldModel`、可见 Observation 与他人公开行为，输出结构化 `BeliefAboutOther`。禁止读取目标角色私有主观状态作为推理捷径。

## HypothesisConflictResolver

标记跨 Lens 的支持、冲突和条件关系。Resolver 不直接修改世界，也不删除尚未解决的少数假设。

## AgentActionModel

输入：

```text
Subjective Model
Beliefs About Others
Causal Hypotheses
Objective Constraints
```

输出多个带解释分解的 `AgentActionDecision`，供 Future Generator 组合为世界状态分支。

## FutureGenerator

输入：

```text
Objective State
Subjective Models
Hypotheses
```

输出：

```text
3～5 CandidateFuture
```

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

## WorldTransition

必须：

- 校验 StateChange。
- 记录 provenance。
- 保存旧状态。
- 创建新 state_id。
- 将 StateChange 关联到 action、future、hypothesis、observation 与 source state。

## NarrativeEngine

输入旧状态、新状态、Future 和 Subjective Models，输出 NarrativeEvent。

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
narrative_events.json
scene_cards.json
```

当前 OutputExporter 尚未生成全部新增文件；该清单是 V2.2 目标契约。
