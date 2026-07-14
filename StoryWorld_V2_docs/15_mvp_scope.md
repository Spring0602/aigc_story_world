# 15 40 天 MVP 范围

## MVP 要证明什么

### H1

显式区分 Objective World 与 Subjective World 后，不同角色可以对同一事实形成稳定差异化解释。

### H2

结构化 World Lens 可以生成比“直接问 LLM 下一步发生什么”更显式的因果机制。

### H3

先生成 Candidate Future，再由 Narrative Engine 选择表达，可以减少纯剧情 Prompt 对世界演化的戏剧性污染。

## MVP 必须有

```text
1 个 Objective World
2～3 个 Agent
2 个以上明显不同的 Subjective World Model
3 个 Lens
3～5 个 Candidate Future / step
3 个连续 world transition step
1 个 Narrative Engine
1 个 Scene Generator
1 个 Gradio Demo
```

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
→ Lens
→ Hypothesis
→ Candidate Future
→ Narrative
```

比较：

```text
角色差异
因果显式性
未来多样性
状态一致性
可解释性
```

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

Estimated Plausibility:
0.46
```

能做到这一点，V2 MVP 就成功。
