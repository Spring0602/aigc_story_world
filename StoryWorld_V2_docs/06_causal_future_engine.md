# 06 因果未来推演引擎

Future Engine 不回答“接下来写什么剧情”。

它回答：

> 当前世界在这些机制作用下，哪些未来状态更可能出现？

## 输入

```text
ObjectiveWorldState
SubjectiveWorldModels
CausalHypotheses
ActiveProcesses
```

## CandidateFuture

```json
{
  "future_id": "future_001",
  "summary": "林夏不会立即公开对抗学校，而会先秘密验证监控机制",
  "estimated_plausibility": 0.46,
  "time_horizon": "hours",
  "trigger_conditions": ["林夏确认网络流量异常"],
  "supporting_hypotheses": ["hyp_psy_001", "hyp_social_003"],
  "agent_actions": [
    {
      "agent_id": "lin_xia",
      "action": "secretly_collect_network_evidence"
    }
  ],
  "expected_state_changes": [],
  "uncertainties": [],
  "risks": []
}
```

## 候选未来

一次生成 3～5 个机制明显不同的未来。

例如：

```text
A：秘密调查
B：向室友求助
C：直接质问老师
D：暂时忽略
```

## 概率说明

第一版的 `estimated_plausibility` 是相对可信度评分。

不得宣称为真实世界精确概率。

## 评分组成

```text
Plausibility Score =
    Causal Support
  + Agent Consistency
  + State Compatibility
  + Constraint Satisfaction
  + Cross-Lens Agreement
  - Contradiction Penalty
```

## 时间尺度

使用：

```text
seconds
minutes
hours
days
weeks
months
years
generations
```

## Feedback Loop

例如：

```text
监控加强
→ 学生信任下降
→ 隐蔽行为增加
→ 学校认为风险提高
→ 进一步加强监控
```

## 反事实

```python
def simulate_counterfactual(
    objective_state,
    intervention,
):
    pass
```

第一版只做单步反事实。

## World Transition

只有 Future 被选择后才更新客观世界。

更新记录：

```text
State Change
Cause
Supporting Hypotheses
Future ID
Step
```

40 天内可以由 LLM 实现 Lens、Future、Evaluation，但所有输出必须结构化。
