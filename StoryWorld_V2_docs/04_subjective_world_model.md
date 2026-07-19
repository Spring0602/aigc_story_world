# 04 Subjective World Model 主体世界模型

每个角色维护自己的主观世界模型，而不是客观世界的副本。

## 核心字段

```text
Knowledge
Beliefs
False Beliefs
Uncertainty
Values
Goals
Fears
Identity
Roles
Epistemology
Human Nature Model
Theory of Change
Methodology
Memory
Emotion
Beliefs About Others
```

推荐结构：

```json
{
  "agent_id": "lin_xia",
  "knowledge": [],
  "beliefs": [],
  "false_beliefs": [],
  "uncertainties": [],
  "values": {},
  "goals": [],
  "fears": [],
  "identity": {},
  "roles": [],
  "epistemology": {},
  "human_nature_model": {},
  "theory_of_change": {},
  "methodology": [],
  "memory": [],
  "emotion": {},
  "beliefs_about_others": {}
}
```

## Epistemology

```json
{
  "trust_data": 0.90,
  "trust_authority": 0.20,
  "trust_personal_experience": 0.70,
  "trust_social_consensus": 0.30,
  "trust_intuition": 0.35,
  "tolerance_for_uncertainty": 0.65
}
```

## Values

价值不是固定常量。

```json
{
  "freedom": {
    "base_weight": 0.85,
    "context_modifiers": {
      "war": -0.20,
      "personal_surveillance": 0.15
    }
  }
}
```

## Human Nature Model

它表示角色“认为人是什么样”，不是角色真实人性。

```json
{
  "self_interest": 0.75,
  "altruism": 0.40,
  "rationality": 0.50,
  "malleability": 0.70,
  "trust_default": 0.35
}
```

## Theory of Change

```json
{
  "material_conditions": 0.80,
  "institutions": 0.65,
  "technology": 0.70,
  "ideas": 0.45,
  "individual_leaders": 0.30,
  "social_networks": 0.75,
  "contingency": 0.55
}
```

## Belief

```json
{
  "belief_id": "belief_001",
  "proposition": "学校正在监控学生网络",
  "confidence": 0.72,
  "evidence": ["dns_anomaly", "traffic_redirect"],
  "source": "personal_analysis",
  "last_updated_step": 2
}
```

## False Belief

必须允许角色错误地相信某事。

客观事实：

```text
教授没有泄密
```

角色信念：

```text
教授向学校举报了我
```

角色基于错误信念采取行动，仍然可以是“主观合理”的。

## Theory of Mind 与 Beliefs About Others

`beliefs_about_others` 不是人物印象标签，而是主体对他人认知状态的显式估计：

```json
{
  "target_agent_id": "wang_chen",
  "beliefs": [
    {
      "proposition": "学校的升级是正常安全措施",
      "confidence": 0.78
    }
  ],
  "predicted_goals": ["避免处分", "维持稳定"],
  "predicted_action": "劝阻林夏公开质疑",
  "evidence": ["wang_chen_trust_authority_high"],
  "last_updated_step": 1
}
```

40 天 MVP 只实现两层：

```text
一阶：A believes X
二阶：A believes B believes X
```

该模型允许错误。系统评估的是“是否能解释互动行动”，而不是要求主体准确读心。

## Emotion

不使用单标签。

```json
{
  "fear": 0.72,
  "anger": 0.21,
  "shame": 0.08,
  "curiosity": 0.83,
  "hope": 0.31
}
```

40 天 MVP 中，角色差异至少来自：

```text
Knowledge
Belief
Values
Epistemology
Goals
Emotions
Beliefs About Others
```

## 从认知到行动

Subjective World Model 不直接修改 Objective World。它先进入 Agent Action Model：

```text
Belief + Goal + Value + Emotion + Beliefs About Others + Constraint
→ Candidate Agent Action
```

测试必须能指出某个行动由哪些显式字段支持，而不是只判断生成文本“像这个角色”。
