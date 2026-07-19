# 15 40 天 MVP 范围

## MVP 要证明什么

### H1

显式区分 Objective World 与 Subjective World 后，不同角色可以对同一事实形成稳定差异化解释。

### H2

显式 Theory of Mind 能让角色基于对他人信念的估计产生更一致的互动行动，同时不读取他人私有状态。

### H3

结构化 World Lens 及其冲突关系可以生成比“直接问 LLM 下一步发生什么”更显式的因果机制。

### H4

将 Belief、Goal、Value、Emotion 与 Constraint 显式接入 Agent Action Model 后，不同主观模型会产生不同的世界状态分支。

### H5

完整 provenance 和后置 Narrative Engine 可以解释事件为何发生，并减少纯剧情 Prompt 对世界演化的戏剧性污染。

## MVP 必须有

```text
1 个 Objective World
2～3 个 Agent
2 个以上明显不同的 Subjective World Model
1 个结构化 Theory of Mind 模块
3 个 Lens
1 个 Hypothesis Conflict Resolver
1 个 Agent Action Model
3～5 个 Candidate Future / step
3 个连续 world transition step
完整 State Provenance
1 个 Narrative Engine
1 个 Gradio Demo
3 个核心对比实验
```

主案例保留林夏、王晨两名角色；Same World Different Minds 实验增加第三个对照认知配置，不要求扩展主剧情角色数量。

## 第一批 Lens

固定：

```text
PsychologyLens
EconomicLens
SocialStructureLens
```

理由：

- 覆盖个体心理。
- 覆盖资源与激励。
- 覆盖角色、制度与权力。
- 容易在校园、实验室、灾难场景中产生不同机制。

## MVP 不做

```text
完整 Philosophy Module
真实世界预测
神经网络 World Model 训练
强化学习
完整 Agent-Based Simulation
长期数百步 rollout
自动联网学习知识
医学/法律事实判断
现实政治预测
精确概率校准
图像生成质量优化
复杂文学风格优化
```

## 推荐主案例：校园监控

客观事实：

```text
学校部署网络异常流量检测系统。
系统功能边界并不透明。
```

角色 A：林夏

```text
高数据信任
低权威信任
高自由价值
高真相价值
```

角色 B：王晨

```text
中等数据信任
高权威信任
高安全价值
高秩序价值
```

同一异常：

```text
校园网络流量重定向
```

正式 H1 对照实验会向所有认知配置提供相同 Observation。主 Demo 中的私人信息边界用于测试 Partial Observability，两者分开报告。

期望：

```text
林夏 → 怀疑监控 → 秘密验证
王晨 → 认为安全升级 → 接受或劝阻林夏
```

## 对照基线

Baseline：

```text
当前故事 + 人物设定
→ LLM 直接生成下一事件
```

StoryWorld V2：

```text
Objective State
→ Observation
→ Subjective Model
→ Theory of Mind
→ Lens
→ Hypothesis
→ Agent Action
→ Candidate Future
→ World Transition / Provenance
→ Narrative
```

比较：

```text
角色差异
互动行动一致性
因果显式性
未来多样性
状态一致性
provenance 完整性
可解释性
```

## 核心实验

```text
Experiment 1: Same World Different Minds
Experiment 2: Lens Ablation
Experiment 3: Prompt-to-Story Baseline Comparison
```

实验必须保存输入配置、中间结构化输出和评价结果，不能只展示最佳故事样例。

## 40 天结束标准

现场回答：

> 为什么林夏选择秘密调查？

系统应展示：

```text
Observation:
网络流量异常

Belief:
学校可能监控学生

Epistemology:
高数据信任，低权威信任

Value:
自由、真相权重高

PsychologyLens:
不确定威胁提高警觉

SocialStructureLens:
高权力不对称降低公开质疑概率

Candidate Future:
秘密收集证据

Agent Action:
由监控信念、真相/自由价值、验证目标与权力约束共同支持

Provenance:
Observation → Belief / Theory of Mind + Hypothesis → Action → Future → StateChange

Estimated Plausibility:
0.46
```

同时能够展示王晨及第三个对照认知配置为何得出不同解释和行动，并通过三项核心实验复现差异，V2 MVP 才算成功。
