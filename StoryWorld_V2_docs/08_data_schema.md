# 08 核心数据结构

当前已实现的核心 Schema：

```text
ObjectiveWorldState
AgentProfile
SubjectiveWorldModel
Observation
Evidence
BayesianBeliefUpdate
BeliefState
Interpretation
CausalHypothesis
AgentAction
ValueAssessment
Decision
Action
CandidateFuture
StateChange
Event (WorldEvent)
NarrativeEvent
SceneCard
ImagePrompt
```

V2.2 研究计划新增或强化：

```text
BeliefAboutOther
HypothesisRelation
```

“字段存在”不等于“研究模型完成”：当前 `beliefs_about_others` 仍是宽松字典，Day 9 必须升级为可验证、可追踪的结构化对象。

## AgentProfile

```json
{
  "agent_id": "lin_xia",
  "name": "林夏",
  "identity": {
    "age": 20,
    "occupation": "计算机专业学生"
  },
  "roles": ["student", "roommate", "research_assistant"],
  "goals": [],
  "values": {},
  "epistemology": {},
  "human_nature_model": {},
  "theory_of_change": {},
  "methodology": [],
  "physical_state": {},
  "visual_features": {}
}
```

## Observation

```json
{
  "observation_id": "obs_001",
  "agent_id": "lin_xia",
  "step": 1,
  "source": "terminal",
  "content": "部分 DNS 请求被重定向",
  "reliability": 0.92,
  "visibility": "private"
}
```

## Evidence

```json
{
  "evidence_id": "evidence_000_002",
  "observation_id": "obs_000_lin_xia_info_private_dns_redirect",
  "agent_id": "lin_xia",
  "step": 0,
  "evidence_type": "data",
  "trust_basis": "trust_data",
  "trust_weight": 0.92,
  "strength": 0.92,
  "polarity": "supports"
}
```

## BayesianBeliefUpdate

```json
{
  "update_id": "update_000_002",
  "belief_id": "belief_lin_xia_002",
  "evidence_id": "evidence_000_002",
  "prior": 0.5,
  "likelihood_e_given_true": 0.9508,
  "likelihood_e_given_false": 0.0492,
  "posterior": 0.9508,
  "polarity": "supports"
}
```

更新公式为：`P(H|E)=P(E|H)P(H)/(P(E|H)P(H)+P(E|~H)P(~H))`。后验会成为同一信念下一次更新的先验。

## BeliefState

`BeliefState` 保存某一步主体全部信念 ID、当前主导信念、来源更新和不确定性，是认知层进入价值决策层的稳定接口。

## MentalModel

```json
{
  "mental_model_id": "mm_001",
  "agent_id": "lin_xia",
  "source_belief_ids": ["belief_lin_xia_002"],
  "source_observation_ids": ["obs_001"],
  "causal_assumptions": ["technical anomalies may be caused by institutional surveillance"],
  "institutional_expectation": "institutions strongly shape individual options",
  "relevant_value_weights": {"freedom": 0.9, "truth": 0.88},
  "uncertainty_tolerance": 0.62
}
```

## BiasFilterResult

```json
{
  "bias_filter_id": "bias_001",
  "mental_model_id": "mm_001",
  "applied_biases": [{
    "bias_type": "autonomy_threat_sensitivity",
    "strength": 0.74,
    "rationale": "High autonomy value increases the salience of surveillance risk."
  }],
  "filtered_causal_frame": "institutional opacity enables surveillance",
  "salience_focus": "autonomy",
  "confidence_modifier": 0.037
}
```

## Interpretation

```json
{
  "interpretation_id": "int_001",
  "agent_id": "lin_xia",
  "observation_ids": ["obs_001"],
  "belief_basis": ["学校可能在监控学生网络"],
  "mental_model_id": "mm_001",
  "bias_filter_id": "bias_001",
  "causal_frame": "institutional opacity enables surveillance",
  "meaning": "institution threatens autonomy",
  "emotional_response": {
    "fear": 0.4,
    "anger": 0.7,
    "shame": 0.0,
    "curiosity": 0.6,
    "hope": 0.2
  },
  "action_implication": "collect evidence secretly",
  "confidence": 0.72
}
```

认知链路固定为 `Observation → Belief → MentalModel → BiasFilterResult → Interpretation`。`MentalModel` 保存尚未经过偏差过滤的因果假设，`BiasFilterResult` 记录偏差如何选择显著信息并调整因果框架，`Interpretation` 通过两类 ID 保留完整引用链。

## StateChange

```json
{
  "path": "agents.lin_xia.location",
  "old_value": "dorm",
  "new_value": "computer_lab",
  "reason": "lin_xia secretly investigates network traffic",
  "future_id": "future_001"
}
```

`StateChange` 描述“改了什么”，`StateProvenance` 描述“为什么改、由谁推动、依据什么机制”。两者不能互相替代。

## BeliefAboutOther（计划）

```json
{
  "observer_agent_id": "lin_xia",
  "target_agent_id": "wang_chen",
  "proposition": "王晨认为网络升级是正常安全措施",
  "confidence": 0.78,
  "evidence": ["int_wang_chen_001"],
  "last_updated_step": 1
}
```

## ValueAssessment / Decision / Action

```json
{
  "decision_id": "decision_001_001",
  "agent_id": "lin_xia",
  "belief_state_id": "belief_state_000_002",
  "interpretation_id": "int_000_002",
  "value_assessment_id": "value_001_001",
  "selected_action": "secretly_collect_network_evidence",
  "supporting_belief_ids": ["belief_monitoring_001"],
  "source_observation_ids": ["obs_000_lin_xia_info_private_dns_redirect"],
  "confidence": 0.9
}
```

完整主干为 `World State → Observation → Evidence → Bayesian Belief Update → Belief State → Value System → Decision → Action → World Event`。解释子链 `Belief State → Mental Model → Bias Filter → Interpretation` 为 Decision 提供可检查的主观理由。

## StateProvenance（计划）

至少记录：

```text
source_state_id / target_state_id / step
path / old_value / new_value
cause / future_id / action_ids
supporting_hypothesis_ids / source_observation_ids
```

## Pydantic 建议

```python
from pydantic import BaseModel, Field

class CausalHypothesis(BaseModel):
    hypothesis_id: str
    lens: str
    claim: str
    drivers: list[str] = Field(default_factory=list)
    mediators: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    affected_agents: list[str] = Field(default_factory=list)
    time_scale: str
    confidence: float = Field(ge=0.0, le=1.0)
```

数据原则：

- 客观事实与角色信念分离。
- confidence 限定 0～1。
- 状态变化可追踪。
- 主体对他人的信念与客观事实分离。
- 行动可追溯到认知参数与环境约束。
- provenance 使用强类型记录，不使用不可验证的任意字典。
- Lens 不直接修改世界。
- NarrativeEvent 不修改 ObjectiveWorldState。
