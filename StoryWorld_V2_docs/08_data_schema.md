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
BeliefAboutOther
Interpretation
Perception
EmotionalAppraisal
StressState
MotivationState
InformationBoundary
PossibleWorld
WorldEvidenceAssessment
BeliefDistribution
BayesianWorldRevision
PossibleWorldBelief
ScarcityAssessment
InformationAsymmetryAssessment
IncentiveAssessment
OpportunityCostAssessment
EconomicActionEvaluation
HypothesisRelation
LensAblationConditionResult
LensAblationComparison
LensAblationExperimentResult
RoleAssessment
NormPressureAssessment
InstitutionPowerAssessment
SocialActionEvaluation
CausalHypothesis
AgentAction
ValueAssessment
Decision
Action
CandidateFuture
FutureMechanism
StateChange
Event (WorldEvent)
NarrativeEvent
SceneCard
ImagePrompt
```

“字段存在”不等于“研究模型完成”：后续 Schema 仍必须通过可验证行为、信息边界和完整引用链验收。

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

## Possible Worlds 与 Belief Distribution

```text
World Truth
→ Observation
→ InformationBoundary
→ PossibleWorld[]
→ Prior BeliefDistribution
→ WorldEvidenceAssessment[]
→ Remove impossible worlds
→ BayesianWorldRevision
→ Posterior BeliefDistribution
→ PossibleWorldBelief
→ Value + Motivation
→ Decision
→ Action
```

- `PossibleWorld` 是主体对当前世界的互斥解释，不是客观事实，也不是后续剧情分支。
- `WorldEvidenceAssessment` 为每个 Evidence / Possible World 对保存似然、兼容方向、理由与 `rules_out_world`。
- `BeliefDistribution` 同时保存 prior / posterior 概率、主导世界、归一化熵和已排除世界；全部概率之和必须为 1，已排除世界必须为 0。
- `BayesianWorldRevision` 保存先验分布、后验分布、证据评估、归一化常数和公式。
- `PossibleWorldBelief` 是后验分布产生的新信念，保留 Observation、Evidence、Revision 和 Information Boundary 的完整来源链。
- `CandidateFuture` 仍表示行动之后的候选世界状态分支，通过来源世界 ID、分布 ID 与 `belief_plausibility` 接入认识论层。

## FutureMechanism 与 CandidateFuture

`FutureMechanism` 显式区分 `information_discovery`、`social_coordination`、`institutional_contestation` 和 `process_inertia`，并保存 drivers、mediators、constraints、Lens、CausalHypothesis 与 ActiveProcess 来源。

生成后的 `CandidateFuture` 必须包含 `source_state_id`、结构化 mechanism、支持与抑制假设、AgentAction、风险、不确定性、generation rationale 和至少一个 `StateChange`。Mechanism 的 source hypothesis IDs 必须与 Candidate Future 的 supporting hypothesis IDs 一致，StateChange 也必须反向引用所属 future ID。

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

认知解释子链固定为 `Observation → Belief → MentalModel → BiasFilterResult → Interpretation`。`MentalModel` 保存尚未经过偏差过滤的因果假设，`BiasFilterResult` 记录偏差如何选择显著信息并调整因果框架，`Interpretation` 通过两类 ID 保留完整引用链。

## Psychology Chain

```text
World Event
→ Perception
→ Belief
→ EmotionalAppraisal
→ StressState
→ MotivationState
→ ValueAssessment
→ Decision
→ Action
```

- `Perception` 引用可见 `source_event_id` 与相关 `observation_ids`，记录 goal relevance、threat、controllability、ambiguity 和 salience。
- `EmotionalAppraisal` 引用 Perception、BeliefState、Belief 与 Interpretation，保存多维 Emotion 和 dominant emotion。
- `StressState` 引用 EmotionalAppraisal，保存 stressors、level、band 与 coping capacity。
- `MotivationState` 引用 Stress、Emotion 和 BeliefState，保存 motive、target、orientation、intensity 与 preferred action。
- `ValueAssessment` 保存 Motivation alignment 与 Stress adjustment；`Decision` 引用整条心理状态链。

## Economic Chain

```text
World
→ InformationBoundary
→ BeliefState
→ MotivationState + ValueAssessment
→ Decision
→ Action
```

- `InformationBoundary` 保存 Observation 来源、visible / inaccessible information IDs、可见资源、访问规则与 coverage。
- `ScarcityAssessment` 分离 physical scarcity 与 access scarcity，并引用 InformationBoundary、BeliefState、Resource 和 access-rule constraints。
- `InformationAsymmetryAssessment` 由角色边界内可见覆盖率、transparency 与 belief uncertainty 计算，同时保留边界外信息 ID 供系统审计，但不得把其内容写入主体 Belief。
- `IncentiveAssessment` 引用 InformationBoundary、BeliefState 与 MotivationState，对 Candidate Action 分解 benefits、costs、expected benefit、expected cost 与 net incentive。
- `OpportunityCostAssessment` 记录选择当前行动所放弃的最佳替代。
- `EconomicActionEvaluation` 闭合上述四类引用并给出相对 utility；`ValueAssessment` 保存该 utility 和 opportunity cost。

## Social Agent Chain

```text
World → Observation → BeliefState
                         ├→ Motivation / Emotion / Bias
                         └→ Role / Norm / Institution
                                      ↓
                    SocialActionEvaluation
                                      ↓
                       ValueAssessment → Decision → Action
```

- `RoleAssessment` 保存角色集合、行为期待、role constraint、role conflict，并引用 Observation 与 BeliefState。
- `NormPressureAssessment` 保存规范清晰度、制裁强度和 compliance pressure。
- `InstitutionPowerAssessment` 保存 authority scope、受控制资源、resource dependence、authority power 与 power asymmetry。
- `SocialActionEvaluation` 闭合心理与社会两条分支，计算 role alignment、norm compliance、institutional risk、social support 和 compatibility。
- `ValueAssessment` 与 `Decision` 保存 `social_evaluation_id`，使 Action 可追溯到完整社会原因链。

## HypothesisRelation

```text
source_hypothesis_id / target_hypothesis_id
source_lens / target_lens
relation_type: supports | contradicts | conditions
basis / shared_drivers / affected_agents
strength
resolution_status: reinforcing | context_dependent | unresolved
```

关系仅在具有共同 affected agent 的跨 Lens 假设之间生成。`contradicts` 必须保留为 `unresolved`，不得通过平均 confidence 隐式消除。`LensAnalysisResult` 同时保存 enabled lenses、Hypothesis Pool、relations 与 unresolved conflict IDs。

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

## BeliefAboutOther

```json
{
  "other_model_id": "other_000_lin_xia_wang_chen",
  "observer_agent_id": "lin_xia",
  "target_agent_id": "wang_chen",
  "order": 2,
  "attributed_beliefs": [{
    "proposition": "目标角色认为学校的升级是正常安全措施",
    "confidence": 0.655
  }],
  "predicted_goals": ["避免冲突", "维持稳定"],
  "predicted_action": "discourage public confrontation",
  "confidence": 0.655,
  "uncertainty": 0.345,
  "evidence_observation_ids": ["obs_000_lin_xia_info_public_network_upgrade"],
  "evidence_event_ids": ["event_wang_reassures_lin"],
  "inference_basis": ["observer-visible evidence only"],
  "last_updated_step": 0
}
```

该结构表达二阶信念“A believes B believes X”。它允许推断错误，但禁止使用 B 的私有认知状态作为证据。

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
  "other_model_ids": ["other_000_lin_xia_wang_chen"],
  "other_model_adjustment": 0.0524,
  "confidence": 0.9
}
```

完整主干为 `World Event → Perception → Observation / Evidence → Bayesian Belief Update → Belief State → Emotion → Stress → Motivation → Value System → Decision → Action → World Event`。解释子链 `Belief State → Mental Model → Bias Filter → Interpretation` 为 Emotion 与 Decision 提供可检查的主观理由。

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
from typing import Literal

from pydantic import BaseModel, Field

TimeScale = Literal[
    "seconds", "minutes", "hours", "days",
    "weeks", "months", "years", "generations",
]

class CausalHypothesis(BaseModel):
    hypothesis_id: str
    lens: str
    claim: str
    drivers: list[str] = Field(min_length=1)
    mediators: list[str] = Field(min_length=1)
    constraints: list[str] = Field(min_length=1)
    affected_agents: list[str] = Field(default_factory=list)
    time_scale: TimeScale
    confidence: float = Field(ge=0.0, le=1.0)
```

Day 12 数据契约：

- `claim`、`drivers`、`mediators`、`constraints`、`time_scale`、`confidence` 均为必填。
- Claim、Lens 和各列表元素必须是非空文本，输入时去除首尾空格。
- Driver、Mediator、Constraint 各自不得重复，三类角色之间不得使用同一机制变量。
- `time_scale` 只能使用系统规定的八种时间尺度。
- `confidence` 是当前证据下的相对可信度，限制在 0～1，不表示真实世界精确概率。

数据原则：

- 客观事实与角色信念分离。
- confidence 限定 0～1。
- 状态变化可追踪。
- 主体对他人的信念与客观事实分离。
- 行动可追溯到认知参数与环境约束。
- provenance 使用强类型记录，不使用不可验证的任意字典。
- Lens 不直接修改世界。
- NarrativeEvent 不修改 ObjectiveWorldState。
