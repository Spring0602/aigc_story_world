# 10 测试与评估

V2 测试维度：

```text
State Integrity
Observation Correctness
Belief Consistency
Agent Perspective Difference
Causal Explicitness
Future Plausibility
Narrative Value
```

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

## Narrative Separation Test

Narrative Engine 可以：

```text
隐藏
重排
聚焦
压缩
描述
```

但不能凭空改变世界事实。

## 人工评估

| 维度 | 1 分 | 3 分 | 5 分 |
|---|---|---|---|
| 角色认知差异 | 几乎相同 | 有差异 | 稳定且合理 |
| 因果显式性 | 无机制 | 简单原因 | 驱动/中介/约束清楚 |
| 未来多样性 | 同质 | 有分支 | 机制明显不同 |
| 状态一致性 | 经常矛盾 | 基本一致 | 可追踪 |
| 叙事价值 | 平淡 | 可读 | 有信息控制与张力 |
| 可解释性 | 黑箱 | 部分可查 | 可定位 Lens/Hypothesis |

第一版五个案例：

```text
校园监控
贫困学生资源竞争
实验室权力冲突
群体谣言传播
灾难中的物资分配
```
