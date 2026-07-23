# Experiment 01: Same World, Different Minds

**实验状态：PASS**

## 研究问题

在相同客观世界和相同观察下，仅改变主体认知配置，会产生可归因的不同信念、解释与行动。

## 实验控制

- 客观状态：`state_000`
- 世界指纹：`b604dc02745fed68ac8b1991e93e9efe022b723ae3c51d66ca368ca450bda411`
- 自变量：`cognitive_configuration`
- 固定变量：objective_world, observation_content, observation_source, evidence_type, observation_reliability, initial_belief_prior, deterministic_runtime
- 共享观察：Network monitoring increased.

三个条件接收内容、来源、证据类型、可靠度和 provenance 完全相同的观察；仅 `agent_id` 与记录 ID 为维持引用完整性而不同。

## 主实验结果

| 认知配置 | 证据权重 | 后验信念 | Bias | Interpretation | Action |
| --- | ---: | --- | --- | --- | --- |
| 数据主义者 | 0.917 | 学校可能正在监控学生网络。 (0.950) | autonomy_threat_sensitivity | institution threatens autonomy | `secretly_collect_network_evidence` |
| 制度主义者 | 0.725 | 网络异常更可能是安全升级带来的正常现象。 (0.855) | authority_deference | institution protects collective security | `follow_institutional_guidance` |
| 怀疑主义者 | 0.708 | 校园网升级存在尚未解释的异常。 (0.847) | evidential_skepticism | the situation requires further verification | `seek_additional_evidence` |

## 定量验收

| 指标 | 值 | 结果 | 说明 |
| --- | ---: | :---: | --- |
| observation_equivalence | 1.000 | PASS | Normalized observation signatures are identical. |
| belief_diversity | 1.000 | PASS | 3/3 unique belief propositions. |
| interpretation_diversity | 1.000 | PASS | 3/3 unique meanings. |
| action_diversity | 1.000 | PASS | 3/3 unique selected actions. |

## 参数交换实验

只交换 Dataist 与 Institutionalist 的 Epistemology，其他 Value 配置保持不变。

| 配置 | 借用参数 | 原解释 / 行动 | 交换后解释 / 行动 | 结果 |
| --- | --- | --- | --- | :---: |
| dataist | institutionalist | institution threatens autonomy / `secretly_collect_network_evidence` | institution protects collective security / `follow_institutional_guidance` | PASS |
| institutionalist | dataist | institution protects collective security / `follow_institutional_guidance` | the situation requires further verification / `seek_additional_evidence` | PASS |

## Partial Observability 对照

该对照独立于主实验，用于确认信息差来自可见性规则，而不是认知参数。

| Agent | Public | Private |
| --- | --- | --- |
| lin_xia | info_public_network_upgrade | info_private_dns_redirect |
| wang_chen | info_public_network_upgrade | - |

- 被观察到的 hidden information：无
- 信息边界：PASS

## 结论

H1 在当前确定性校园监控基线上得到支持：共享观察保持一致时，三种认知配置产生了不同的信念命题、解释框架和行动建议；参数交换进一步表明变化可归因于显式 Epistemology，而非输入信息差。

本实验验证的是当前规则模型内部的因果敏感性，不代表对真实人类认知的外部有效性。后续仍需扩大场景、重复样本并加入人工评分。
