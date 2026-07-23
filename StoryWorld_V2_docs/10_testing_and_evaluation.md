# 10 测试与评估

V2 测试维度：

```text
State Integrity
Observation Correctness
Belief Consistency
Agent Perspective Difference
Theory of Mind Consistency
Action Explainability
Causal Explicitness
Lens Contribution
Future Plausibility
Provenance Completeness
Narrative Fidelity
```

测试优先回答研究问题，而不只检查代码能否运行。所有对比实验应固定 Objective World 和随机条件，只改变被研究变量。

## Objective / Subjective Separation Test

主体是否获得不应知道的信息？

隐藏事实未被观察时，角色若直接说出真相：

```text
FAIL
```

## False Belief Test

构造：

```text
Objective: A 没有背叛 B
B Belief: A 背叛了我
```

检查：

- B 是否基于错误信念行动？
- Narrative Engine 是否避免把错误信念写成客观事实？

## Perspective Difference Test

同一 Observation：

```text
网络流量异常
```

角色 A：

```text
trust_data = 0.9
trust_authority = 0.2
```

角色 B：

```text
trust_data = 0.3
trust_authority = 0.8
```

期望两者 Interpretation 明显不同。

除文本差异外，还要记录差异来自哪些显式参数，并进行参数交换实验：交换两人的 Epistemology 后，解释倾向应出现可预测变化。

当前校园案例中，林夏还拥有私人 DNS Observation，因此现有输出是有价值的 Demo，但不能单独证明认知参数导致差异。H1 主实验必须给所有对照角色完全相同的 Observation；信息可见性差异应作为另一组独立实验。

## Theory of Mind Test

检查：

- A 是否能基于可见行为建立 `A believes B believes X`。
- A 是否错误读取 B 的私有 Subjective Model。
- 二阶信念改变后，A 的互动行动是否变化。
- 错误但有证据的他人模型是否被保留，而非自动纠正为客观真相。

需同时运行 Without-ToM 对照，判断加入 Theory of Mind 是否真的改善互动行动一致性。

## Lens Quality Test

假设必须包含：

```text
claim
drivers
mediators
constraints
time_scale
confidence
```

## Time Scale Test

避免：

```text
一次宿舍争吵
→ 学校制度立即全面改革
```

## Candidate Future Diversity

错误：

```text
A：调查
B：秘密调查
C：私下调查
```

正确：

```text
A：秘密调查
B：向室友求助
C：直接质问老师
D：暂时忽略
```

## Agent Consistency

评分：

```text
Knowledge Compatibility
Value Compatibility
Goal Compatibility
Emotional Compatibility
Epistemic Compatibility
```

行动输出必须附带分项依据。消融 Belief、Value、Emotion 或 Constraint 后，行动排序应产生可解释变化。

## Lens Ablation Test

在同一世界状态下分别运行：

```text
All Lenses
Without PsychologyLens
Without EconomicLens
Without SocialStructureLens
```

比较 Hypothesis Pool、Agent Action 排序、Candidate Future 类型和最终状态变化。只比较文案差异不算有效消融。

## Provenance Test

每个重要 StateChange 必须能反向追踪到：

```text
source/target state
agent action
belief / goal / value / emotion / constraint
supporting and conflicting hypotheses
lens
observation or source fact
```

缺少任一关键链接时标记为 provenance incomplete。

## Narrative Fidelity Test

Narrative Engine 可以：

```text
隐藏
重排
聚焦
压缩
描述
```

但不能凭空改变世界事实。

Narrative Value 是次级展示指标；首要检查 NarrativeEvent 是否忠实于 WorldEvent、是否维持知识边界、是否保留原因链。

## 三个核心实验

Theory of Mind 的基础回归必须包含隐私边界测试：任意修改目标角色私有 Belief 或添加隐藏 Event，在公开证据不变时，观察者生成的 `BeliefAboutOther` 必须保持不变。

### Experiment 1：Same World Different Minds

同一个 Objective World，配置数据主义者、制度主义者、怀疑主义者三个认知模型，比较 Observation、Belief、Interpretation、Action 与 Future。

当前实现：

- 运行器：`experiments/same_world_different_minds.py`
- 自动测试：`tests/test_experiment_01.py`
- 结构化结果：`experiments/results/experiment_01.json`
- 实验报告：`experiments/results/experiment_01.md`

Day 10 主对照已通过：三种认知配置共享同一世界指纹和规范化 Observation，Belief、Interpretation 与 Action 差异率均为 `1.000`。Epistemology 参数交换和独立 Partial Observability 对照同时通过。

### Experiment 2：Lens Ablation

逐个移除 Lens，测量机制和未来分支变化。

### Experiment 3：Baseline Comparison

比较 `Prompt → Story` 与完整 StoryWorld 链路。至少报告角色一致性、因果显式性、未来多样性和可解释性。

## 人工评估

| 维度 | 1 分 | 3 分 | 5 分 |
|---|---|---|---|
| 角色认知差异 | 几乎相同 | 有差异 | 稳定且合理 |
| 因果显式性 | 无机制 | 简单原因 | 驱动/中介/约束清楚 |
| 未来多样性 | 同质 | 有分支 | 机制明显不同 |
| 状态一致性 | 经常矛盾 | 基本一致 | 可追踪 |
| 行动可解释性 | 只有动作 | 有部分理由 | 可追溯到认知与约束 |
| provenance | 无记录 | 有直接原因 | 可回溯完整因果链 |
| 叙事忠实度 | 创造或泄漏事实 | 基本一致 | 忠实且保留信息边界 |
| 可解释性 | 黑箱 | 部分可查 | 可定位 Lens/Hypothesis |

40 天核心实验固定使用“校园监控”。以下案例作为外部有效性扩展，不要求在主模型未稳定前全部完成：

```text
校园监控
贫困学生资源竞争
实验室权力冲突
群体谣言传播
灾难中的物资分配
```
