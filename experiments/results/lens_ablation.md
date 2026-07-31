# Experiment 02: Lens Ablation

**实验状态：PASS**

## 研究假设

在客观世界、主体配置和候选未来模板不变时，移除任一 Lens 应改变假设池、跨 Lens 关系以及 Future 和 Action 的评分。

## 条件结果

| 条件 | 启用 Lens | 假设 | 关系 | 选择 Future | 选择 Action |
|---|---|---:|---:|---|---|
| all_lenses | economic, psychology, social_structure | 6 | 6 | future_001_secret | secretly_collect_network_evidence |
| without_economic | psychology, social_structure | 4 | 2 | future_001_secret | secretly_collect_network_evidence |
| without_psychology | economic, social_structure | 4 | 2 | future_001_secret | secretly_collect_network_evidence |
| without_social_structure | economic, psychology | 4 | 2 | future_001_secret | secretly_collect_network_evidence |

## 消融差异

| 移除 Lens | 最大 Future 分数变化 | 最大 Action 分数变化 | 排序变化 | 最终选择变化 | 通过 |
|---|---:|---:|:---:|:---:|:---:|
| economic | 0.038 | 0.016 | 否 | 否 | PASS |
| psychology | 0.031 | 0.098 | 否 | 否 | PASS |
| social_structure | 0.046 | 0.110 | 否 | 否 | PASS |

## 结论

三个 Lens 的消融都会改变机制假设、关系图、Future 分数和 Action 分数。
当前校园场景中，秘密取证仍保持第一名，说明最终选择对单 Lens 移除具有稳健性，
但其形成过程、相对优势以及最终状态 provenance 对各 Lens 均敏感。
