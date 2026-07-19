# 03 世界本体与客观世界状态

## 为什么需要 Ontology

系统必须先知道“世界中有什么”，才能稳定推演。

第一版 Ontology 不追求完成人类知识本体，只定义社会认知实验和世界状态转移所需实体。

## 基础实体

```text
Agent
Location
Information
Relationship
Institution
Norm
Resource
Event
ActiveProcess
```

预留：

```text
Body
Object
Environment
Group
PowerRelation
HistoryRecord
```

## ObjectiveWorldState

```json
{
  "state_id": "state_000",
  "step": 0,
  "timestamp": "day_1_23_50",
  "locations": {},
  "agents": {},
  "resources": {},
  "institutions": {},
  "norms": {},
  "relationships": {},
  "public_information": [],
  "hidden_facts": [],
  "active_processes": [],
  "history": []
}
```

## 关系必须结构化

不要：

```text
林夏和老师关系紧张
```

建议：

```json
{
  "source": "lin_xia",
  "target": "prof_chen",
  "trust": 0.32,
  "dependency": 0.76,
  "authority_asymmetry": 0.91,
  "emotional_attachment": 0.20,
  "conflict": 0.68
}
```

## Active Process

现实变化往往是持续过程，而非单一事件。

```json
{
  "process_id": "network_monitoring_rollout",
  "type": "institutional_change",
  "start_time": "day_1",
  "time_scale": "days",
  "drivers": ["security_policy"],
  "current_stage": "pilot"
}
```

## State Provenance

重要状态应能回答：

> 为什么现在是这样？

```json
{
  "provenance_id": "prov_001",
  "source_state_id": "state_000",
  "target_state_id": "state_001",
  "step": 1,
  "path": "agents.lin_xia.location_id",
  "old_value": "dorm",
  "new_value": "computer_lab",
  "cause": "林夏决定秘密验证网络重定向",
  "agent_action_ids": ["action_lin_xia_001"],
  "supporting_hypothesis_ids": ["hyp_psy_001", "hyp_social_001"],
  "source_observation_ids": ["obs_dns_redirect"]
}
```

`history` 不是任意字典日志，而应由强类型 provenance 记录组成。初始事实也要记录 `source`，例如案例文件、用户输入或系统规则。当前代码只有 `reason` 与 `future_id` 的最小记录，完整模型按 V2.2 的 World Transition 阶段实现。

## Event 与 Action 的边界

```text
AgentAction = 主体基于主观模型作出的选择
WorldEvent = 行动与环境机制共同产生的客观结果
NarrativeEvent = 对已发生 WorldEvent 的表达
```

三者不得混用。角色不能直接把主观意图写成客观事实。

40 天 MVP 优先实现：

```text
Agent
Location
Information
Relationship
Institution
Norm
Resource
Event
ActiveProcess
StateProvenance
```
