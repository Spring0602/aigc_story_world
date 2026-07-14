# 05 World Lens 开放式认知模块架构

## 定义

World Lens 是：

> 用特定领域机制解释当前世界变化的分析模块。

它不是“扮演经济学家聊天”。

它必须输出结构化 `CausalHypothesis`。

## 统一接口

```python
from abc import ABC, abstractmethod

class WorldLens(ABC):
    name: str

    @abstractmethod
    def analyze(
        self,
        objective_state,
        subjective_models,
        context,
    ):
        pass
```

输出：

```text
list[CausalHypothesis]
```

## CausalHypothesis

```json
{
  "hypothesis_id": "hyp_eco_001",
  "lens": "economic",
  "claim": "资源获取渠道受限会提高非正式合作网络形成概率",
  "drivers": ["resource_scarcity", "formal_access_barrier"],
  "mediators": ["opportunity_cost", "network_dependency"],
  "constraints": ["high_monitoring"],
  "affected_agents": ["lin_xia", "roommate"],
  "time_scale": "days",
  "confidence": 0.64
}
```

## 第一批三个 Lens

### PsychologyLens

关注：

```text
Emotion
Motivation
Cognitive Bias
Stress
Scarcity Mindset
Defense Mechanism
Social Perception
```

### EconomicLens

关注：

```text
Scarcity
Incentive
Opportunity Cost
Information Asymmetry
Resource Dependence
Strategic Exchange
```

### SocialStructureLens

第一版合并社会学与基础政治机制。

关注：

```text
Role
Norm
Status
Authority
Institution
Power Asymmetry
Collective Pressure
```

## 后续 Lens

```text
LegalLens
PoliticalLens
AnthropologyLens
HistoricalLens
GeographyLens
CulturalLens
GameTheoryLens
BiologicalConstraintLens
```

## 哲学为什么不做 PhilosophyLens

哲学更适合定义：

```text
Ontology
Epistemology
Axiology
Methodology
Human Nature
Theory of Change
```

后续若研究哲学方法论，应让其改变：

```text
Causal Search Strategy
Value Evaluation
State Representation
Action Selection
```

而不是只改变说话口吻。

## Lens 输出最低要求

每条假设必须有：

```text
Claim
Drivers
Mediators
Constraints
Affected Agents
Time Scale
Confidence
```

禁止仅输出：

```text
“从心理学角度看，主角可能感到焦虑。”
```
