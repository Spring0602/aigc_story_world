# Day 11 因果推理基础笔记

本笔记服务于 StoryWorld V2 的因果机制建模。目标不是证明真实社会中的严格因果关系，而是让 Lens 生成的假设具备清晰、可检查、可反驳的结构，并能支持 Candidate Future、World Transition 和 State Provenance。

## 1. 核心问题

Future Engine 不应只回答：

> 接下来写什么？

它应回答：

> 当前状态中有哪些力量正在推动变化，这些力量通过什么机制产生结果，又受到哪些条件限制？

最小因果结构：

```text
Driver / Cause
      ↓
   Mediator
      ↓
    Effect

Constraint 限制路径能否成立或影响强度
```

Correlation 只说明变量共同变化，不能单独证明上述路径存在。

## 2. Cause：原因

Cause 是一个因素对结果产生改变的因果作用。

基本判断问题：

> 如果通过干预改变 X，Y 是否会随之改变？

校园监控案例：

```text
Cause:
学校部署不透明的网络检测系统

Effect:
林夏开始秘密收集网络证据
```

要支持这条因果主张，还需要说明中间机制：

```text
不透明监控
→ 林夏相信学校可能记录个人行为
→ 她感到自主权受到威胁
→ 秘密调查的吸引力上升
```

### 2.1 反事实

因果判断依赖反事实：

```text
实际世界：
学校部署不透明监控，林夏选择秘密调查。

反事实世界：
如果学校没有部署监控，或完整公开了系统边界，
林夏是否仍会在同一时间采取同样行动？
```

若移除 X 后 Y 的概率或强度明显下降，X 才具有因果支持。

StoryWorld 第一版只要求单步反事实：

```text
保持其他状态不变
→ 改变一个原因或约束
→ 重新生成或评分 Candidate Futures
→ 比较选中行动与 StateChange
```

### 2.2 充分原因与必要原因

- 必要原因：没有 X，Y 就不会发生。
- 充分原因：只要 X 出现，就足以导致 Y。
- 促成原因：X 提高 Y 的可能性，但既非必要也非充分。

社会系统中多数因素只是促成原因。StoryWorld 的 `CausalHypothesis` 默认表达概率性促成关系，不应轻易声称“必然导致”。

## 3. Correlation：相关性

Correlation 表示两个变量共同变化：

```text
监控强度上升
↔
学生隐蔽行为增加
```

它可能对应：

1. 监控增强导致隐蔽行为增加。
2. 隐蔽行为增加导致学校加强监控。
3. 第三个因素同时导致两者变化。
4. 只是有限样本中的偶然共同变化。

### 3.1 混杂因素

例如“校园安全事件增加”可能同时导致监控和隐蔽行为增加：

```text
       安全事件增加
        /         \
       ↓           ↓
监控强度上升   学生警惕上升
```

这里的安全事件是 Confounder。若忽略它，就可能错误地把相关性解释为直接因果。

### 3.2 StoryWorld 中的判断规则

以下内容只能作为相关性线索：

- 两个状态在同一步同时出现。
- 两个事件在历史中经常相邻。
- 角色相信二者相关。
- Lens 生成了语义上合理的解释。

将相关性升级为因果假设，至少需要：

- 原因发生在结果之前。
- 存在明确机制或中介变量。
- 能指出支持该机制的 Observation、State Fact 或 Event。
- 已考虑重要替代解释。
- 反事实干预会产生可预期差异。

角色的因果信念可以错误，但必须保存在 Subjective World；不能因为角色相信 X 导致 Y，就把它自动写成 Objective World 的事实。

## 4. Driver：驱动因素

Driver 是持续推动系统向某个方向发展的上游力量。它通常比单一 Cause 更长期、更结构化。

校园监控案例中的 Drivers：

```text
institutional_risk_pressure
low_cost_surveillance_technology
authority_asymmetry
information_asymmetry
high_public_confrontation_cost
```

Cause 与 Driver 的区别：

| 项目 | Cause | Driver |
|---|---|---|
| 关注点 | 某个结果为什么发生 | 系统为何持续朝某方向变化 |
| 形式 | 事件、状态或干预 | 趋势、激励、压力或结构 |
| 时间尺度 | 可短可长 | 通常跨多个 step |
| 示例 | 学校发布部署命令 | 长期安全责任压力 |

在代码中，`drivers` 应写成可识别的机制变量，而不是重复 Claim。

较好：

```text
authority_asymmetry
institutional_opacity
risk_of_liability
```

较差：

```text
things_get_worse
plot_needs_conflict
students_are_unhappy
```

Driver 应能映射到 ObjectiveWorldState、ActiveProcess、Institution、Relationship，或主体的 Belief、Goal、Value、Emotion。

## 5. Mediator：中介机制

Mediator 位于 Cause 和 Effect 之间，解释因果影响如何传递。

```text
X → M → Y
```

校园案例：

```text
X: 不透明监控上线
M1: 学生相信个人行为可能被记录
M2: 自主权威胁感上升
M3: 愤怒与验证动机上升
Y: 秘密收集证据
```

可能的认知中介链：

```text
Observation
→ Evidence
→ Belief
→ Mental Model
→ Interpretation
→ Emotion
→ Decision
```

### 5.1 中介判断

一个变量适合作为 Mediator，需要满足：

1. 原因能够改变该变量。
2. 该变量能够影响结果。
3. 它在时间上位于原因和结果之间。
4. 如果阻断它，原因对结果的影响应减弱。

不要把所有中间出现的对象都列为 Mediator。文件 ID、显示文本和无行为影响的元数据通常不是机制。

### 5.2 Mediator 与混杂因素

```text
Mediator:
X → M → Y

Confounder:
C → X
C → Y
```

Mediator 传递 X 的影响；Confounder 在 X 之前，同时影响 X 和 Y。混淆二者会导致错误的反事实结果。

## 6. Constraint：约束

Constraint 限制因果过程、行动可行性或结果强度。它不一定推动变化，但决定某条路径是否能够实现。

校园案例：

```text
limited_access_to_network_logs
student_status
risk_of_punishment
unclear_policy_boundary
limited_evidence
```

例如：

```text
Goal:
验证学校是否记录个人行为

Desired Action:
检查网络中心服务器

Constraint:
没有管理员权限

Feasible Action:
收集本地 DNS 和流量证据
```

### 6.1 硬约束与软约束

- 硬约束：使行动不可能，例如没有物理入口、资源为零。
- 软约束：降低行动吸引力或成功率，例如处分风险、时间成本。

Candidate Future 应区分：

```text
hard constraint violated
→ future infeasible

soft constraint present
→ plausibility or utility reduced
```

### 6.2 Constraint 与 Mediator

```text
Mediator:
解释影响如何传递。

Constraint:
解释路径为何受阻、减弱或只能换一种形式实现。
```

“恐惧处分”可能根据模型位置承担不同角色：

- 若它传递“权力不对称 → 避免公开对抗”的影响，则是 Mediator。
- 若它只限制公开行动的可行性，则是 Constraint。

因此分类必须结合完整因果图，而不能只看变量名称。

## 7. 统一案例拆解

目标结果：

```text
林夏前往计算机实验室秘密收集网络证据。
```

可解释为：

```text
Drivers:
- institutional_opacity
- authority_asymmetry
- high_public_confrontation_cost

Cause:
- network_monitoring_rollout
- private_dns_redirect_observation

Mediators:
- belief_that_school_may_monitor_students
- perceived_autonomy_threat
- curiosity
- fear_of_sanction
- preference_for_low_cost_verification

Constraints:
- limited_access_to_network_logs
- student_status
- risk_of_punishment

Effect:
- secretly_collect_network_evidence
```

因果图：

```text
network_monitoring_rollout
        ↓
private_dns_redirect_observation
        ↓
belief_that_school_may_monitor_students
        ↓
perceived_autonomy_threat
        ↓
verification_motivation
        ↓
secretly_collect_network_evidence
        ↑
high_public_confrontation_cost

limited_access_to_network_logs 限制可收集的证据范围
risk_of_punishment 降低公开质问的相对吸引力
```

## 8. 反馈回路

社会世界经常不是单向链路，而是反馈循环：

```text
监控加强
→ 学生信任下降
→ 隐蔽行为增加
→ 学校感知风险上升
→ 监控进一步加强
```

实现时不能在一个 step 内无限循环。应将反馈展开到多个世界状态：

```text
state_001: monitoring increases
state_002: trust decreases
state_003: covert behavior increases
state_004: institution updates risk assessment
```

每次 World Transition 只应用当前被选 Future 的直接变化，并通过 Provenance 指向前一状态和支持假设。

## 9. 时间尺度

同一因果机制必须匹配合理时间尺度：

| 时间尺度 | 适合变化 |
|---|---|
| seconds / minutes | 即时感知、短暂情绪、技术响应 |
| hours | 调查、对话、局部行动 |
| days / weeks | 信任变化、关系调整、组织回应 |
| months / years | 制度改革、资源结构变化 |
| generations | 文化与长期社会结构 |

错误示例：

```text
一次宿舍争论
→ 几分钟内完成全校制度改革
```

正确表达：

```text
一次宿舍争论
→ 几小时内形成调查行动
→ 数天内积累证据
→ 数周内触发制度回应
```

## 10. Confidence 的含义

`confidence` 是当前模型对假设的相对可信度，不是真实世界中的精确概率。

它应综合：

- 支持证据的可靠性。
- Observation 与 State Fact 的 provenance。
- 机制是否完整。
- 是否存在冲突证据。
- 是否有多个 Lens 独立支持。
- 时间尺度是否合理。
- 约束是否被满足。

禁止仅因为叙述“听起来合理”就赋予高置信度。

## 11. Day 12 Schema 建模约定

下一步 `CausalHypothesis` 的最小字段：

```text
Claim
Drivers
Mediators
Constraints
TimeScale
Confidence
```

字段语义：

| 字段 | 要回答的问题 |
|---|---|
| `claim` | 什么因素将使什么结果更可能发生？ |
| `drivers` | 哪些上游力量持续推动该变化？ |
| `mediators` | 影响通过哪些机制传递？ |
| `constraints` | 哪些条件限制路径或结果？ |
| `time_scale` | 该机制通常需要多久显现？ |
| `confidence` | 在当前证据下，对假设有多大信心？ |

推荐 Claim 句式：

```text
在 [条件] 下，
[Cause / Driver]
通过 [Mediator]
使 [Effect] 更可能发生，
但受 [Constraint] 限制。
```

例子：

```text
在监控范围不透明且公开对抗成本较高时，
权力不对称通过处分恐惧和低成本验证偏好，
使学生更可能选择秘密调查，
但调查范围受日志访问权限限制。
```

## 12. 假设审查清单

生成或审核一个 `CausalHypothesis` 时逐项检查：

- [ ] Claim 是否包含明确的变化方向或预期结果？
- [ ] 原因是否发生在结果之前？
- [ ] Driver 是否来自可引用的世界状态、过程或主体状态？
- [ ] Mediator 是否真正传递影响，而非只是相关对象？
- [ ] Constraint 是否改变可行性、强度或行动排序？
- [ ] 是否存在可能的反向因果？
- [ ] 是否考虑了关键 Confounder 或替代解释？
- [ ] 时间尺度是否与机制匹配？
- [ ] Confidence 是否有证据依据，而非语言流畅度评分？
- [ ] 角色信念与客观因果事实是否保持分离？
- [ ] 是否能通过单步反事实说明移除某因素后的预期变化？
- [ ] 是否能沿 Provenance 回溯到 Observation、Event 或 State Fact？

## 13. 当前代码映射

现有三个 Lens 已输出基础结构：

```text
PsychologyLens
→ unclear_monitoring_scope
→ curiosity / fear / need_for_control
→ verification action

EconomicLens
→ information_asymmetry / confrontation_cost
→ opportunity_cost / resource_dependence
→ low-cost covert action

SocialStructureLens
→ authority_asymmetry / institutional_opacity
→ role_constraint / fear_of_sanction
→ avoidance of direct confrontation
```

Day 12 之后需要继续强化：

- Driver、Mediator 和 Constraint 与真实 State ID 的引用。
- 支持证据与冲突证据。
- 原因、结果和方向的结构化表达。
- 跨 Lens 的重复、支持与冲突关系。
- Counterfactual 与 State Provenance 的闭合引用。

## 14. 最简记忆

```text
Cause:
改变它，结果会不会改变？

Correlation:
它们是否只是一起变化？

Driver:
什么力量持续推动系统？

Mediator:
影响通过什么过程传递？

Constraint:
什么限制路径和结果？
```

StoryWorld 中一个合格的因果假设，不只是“合理的故事解释”，而是一条可以引用、比较、反驳和进行反事实测试的世界演化机制。
