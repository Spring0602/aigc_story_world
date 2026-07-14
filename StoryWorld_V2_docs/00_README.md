# StoryWorld V2 开发文档总览

> 项目定位：**面向动态叙事生成的多主体、多视角因果世界推演框架**

StoryWorld V2 的核心链路：

```text
Objective World
    ↓
Observation
    ↓
Subjective World Models
    ↓
World Lenses
    ↓
Causal Hypotheses
    ↓
Candidate Futures
    ↓
Future Evaluation
    ↓
World Transition
    ↓
Narrative Selection
    ↓
Scene / Story Expression
```

核心目标：

> 显式区分客观世界、角色观察、角色解释与叙事表达，使不同主体可以基于不同认知、价值、知识和方法论，对同一世界形成不同判断，并在多种因果机制作用下推演潜在未来。

## 文档目录

| 文件 | 说明 |
|---|---|
| `01_project_definition.md` | 项目定义、研究问题与边界 |
| `02_core_architecture.md` | V2 核心架构 |
| `03_world_ontology.md` | 世界本体与客观状态设计 |
| `04_subjective_world_model.md` | 主体认知、信念、价值与三观建模 |
| `05_world_lens_system.md` | World Lens 开放式认知模块架构 |
| `06_causal_future_engine.md` | 因果假设、概率未来、反事实与时间尺度 |
| `07_narrative_engine.md` | 世界演化与剧情表达分离 |
| `08_data_schema.md` | 核心数据结构 |
| `09_module_design.md` | Python 模块与接口建议 |
| `10_testing_and_evaluation.md` | 测试与评估 |
| `11_development_roadmap_40_days.md` | 新版 40 天计划 |
| `12_learning_map.md` | 学习地图 |
| `13_future_research.md` | 后续研究方向 |
| `14_project_structure.md` | 推荐目录结构 |
| `15_mvp_scope.md` | 40 天 MVP 范围 |

## V2 六个核心对象

```text
ObjectiveWorldState
SubjectiveWorldModel
WorldLens
CausalHypothesis
CandidateFuture
NarrativeEvent
```

40 天目标不是完成“人类世界模拟器”，而是验证：

1. 客观世界与主体认知可以显式分离。
2. 不同角色能稳定形成不同解释。
3. 多个 Lens 能产生不同因果机制。
4. 系统能生成多个概率化候选未来。
5. Narrative Engine 只负责选择和表达，不反向篡改世界事实。
