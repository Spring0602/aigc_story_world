# 08 核心数据结构

当前已实现的核心 Schema：

```text
ObjectiveWorldState
AgentProfile
SubjectiveWorldModel
Observation
Interpretation
CausalHypothesis
AgentAction
CandidateFuture
StateChange
NarrativeEvent
SceneCard
ImagePrompt
```

V2.2 研究计划新增或强化：

```text
BeliefAboutOther
AgentActionDecision
HypothesisRelation
StateProvenance
WorldEvent
```

“字段存在”不等于“研究模型完成”：当前 `beliefs_about_others` 与 `history` 仍是宽松字典，后续必须升级为可验证、可追踪的结构化对象。

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

## Interpretation

```json
{
  "interpretation_id": "int_001",
  "agent_id": "lin_xia",
  "observation_ids": ["obs_001"],
  "claim": "学校可能在监控学生网络",
  "confidence": 0.72,
  "reasoning_basis": ["high_trust_data", "low_trust_authority"]
}
```

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

## AgentActionDecision（计划）

```json
{
  "action_id": "action_lin_xia_001",
  "agent_id": "lin_xia",
  "action": "secretly_collect_network_evidence",
  "supporting_belief_ids": ["belief_monitoring_001"],
  "supporting_goals": ["确认网络异常"],
  "supporting_values": ["truth", "freedom"],
  "constraints": ["risk_of_punishment"],
  "score": 0.81
}
```

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
