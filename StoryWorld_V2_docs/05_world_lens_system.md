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

当前实现链路：

```text
World Event
→ Perception
→ Belief
→ Emotional Appraisal
→ Stress
→ Motivation
→ Value Evaluation
→ Decision
→ Action
```

`PsychologyEngine` 负责生成逐主体的 Perception、EmotionalAppraisal、StressState 和 MotivationState。`PsychologyLens` 消费这些结构化状态，为每个主体输出动态 `CausalHypothesis`，并保存 supporting event、perception、belief、emotion、stress 与 motivation IDs。

心理状态必须实际参与行为：Motivation alignment 和 Stress adjustment 进入 `ValueAssessment.score`。若移除或改变 Motivation 后行动评分完全不变，则 Psychology Lens 尚未有效接入。

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

当前实现链路：

```text
World
→ Information Boundary
→ Belief
→ Motivation + Value
→ Decision
→ Action
```

`EconomicEngine` 先按 Observation visibility 建立逐角色 `InformationBoundary`，禁止角色直接使用边界外隐藏事实。数量不足与访问规则分别形成 physical scarcity 和 access scarcity；Information Asymmetry 由可见信息覆盖率、Institution transparency 与 Belief uncertainty 共同决定。每个 Candidate Action 都会结合 Motivation 和 Value 生成收益、成本、净激励、放弃的最佳替代和 Economic Utility。

`EconomicLens` 按主体的 Value、资源约束和信息位置生成动态 `CausalHypothesis`，并保存 supporting scarcity assessment 与 information asymmetry IDs。Economic Utility 必须进入 `ValueAssessment.score`，只生成经济学描述不算完成。

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

当前实现链路：

```text
World → Observation → Belief
                    ├→ Psychology: Motivation / Emotion / Bias
                    └→ Society: Role / Norm / Institution
                                      ↓
                              Decision → Action
```

`SocialStructureEngine` 将角色期待、规范清晰度、制裁、制度权限、资源控制和权力不对称转换为逐主体社会状态。每项 Candidate Action 均产生 role alignment、norm compliance、institutional risk、social support 和 compatibility。

`SocialStructureLens` 按主体生成动态 `CausalHypothesis`，引用 RoleAssessment、NormPressureAssessment 和 InstitutionPowerAssessment。Social compatibility 必须进入 `ValueAssessment.score`；若改变制度权力后行动评分不变，则社会 Lens 尚未有效接入。

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

## Hypothesis Conflict Resolver

多个 Lens 不保证结论一致。例如：

```text
PsychologyLens: 愤怒提高立即对抗倾向
EconomicLens: 高行动成本降低立即对抗倾向
SocialStructureLens: 权力不对称进一步抑制公开对抗
```

Resolver 不负责选出“唯一正确理论”，而是输出结构化关系：

```text
supports
contradicts
conditions
shared_drivers
unresolved_tensions
```

Future Evaluator 必须能看到这些冲突，避免把三个假设简单计数后当作一致支持。

## Lens Ablation

每个 Lens 必须可独立关闭。实验比较：

```text
All Lenses
- PsychologyLens
- EconomicLens
- SocialStructureLens
```

若移除 Lens 后候选未来、行动排序或解释链完全不变，说明 Lens 尚未真正参与世界模型。
