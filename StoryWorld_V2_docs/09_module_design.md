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
├── lens_router.py
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

## LensRouter

第一版固定调用三个 Lens，并合并假设。

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

## NarrativeEngine

输入旧状态、新状态、Future 和 Subjective Models，输出 NarrativeEvent。

## LLM 使用位置

允许用于：

```text
World Initialization
Belief Interpretation
Lens Analysis
Future Generation
Future Evaluation
Narrative Expression
Scene Generation
```

禁止一个 Prompt 一次性完成所有模块。

## 调试输出

```text
observations.json
subjective_models.json
hypotheses.json
candidate_futures.json
selected_future.json
objective_states.json
narrative_events.json
scene_cards.json
```
