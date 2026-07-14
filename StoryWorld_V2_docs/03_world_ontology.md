# 03 世界本体与客观世界状态

## 为什么需要 Ontology

系统必须先知道“世界中有什么”，才能稳定推演。

第一版 Ontology 不追求完成人类知识本体，只定义叙事世界常见实体。

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

## History Provenance

重要状态应能回答：

> 为什么现在是这样？

```json
{
  "fact": "lin_xia_trust_prof_chen_low",
  "value": 0.32,
  "provenance": ["event_003", "event_014"]
}
```

40 天 MVP 先实现：

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
