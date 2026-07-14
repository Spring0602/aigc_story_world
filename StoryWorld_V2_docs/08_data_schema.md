# 08 核心数据结构

第一版核心 Schema：

```text
ObjectiveWorldState
AgentProfile
SubjectiveWorldModel
Observation
Interpretation
CausalHypothesis
CandidateFuture
NarrativeEvent
SceneCard
```

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
- Lens 不直接修改世界。
- NarrativeEvent 不修改 ObjectiveWorldState。
