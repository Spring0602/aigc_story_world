# StoryWorld V2

以动态叙事为应用出口的社会认知世界模型（Social Cognitive World Model）研究原型。

当前 40 天目标是验证：不同主体能否基于各自的观察、信念、价值与认识论形成不同解释和行动，并在结构化社会机制作用下产生可追踪的未来世界。故事和 Scene 是实验结果的表达层，不是模型的决策中心。

V2 不再使用旧版 `WorldState -> PlotEngine -> EventCard` 链路，而是显式拆分：

```text
ObjectiveWorldState
→ Observation
→ SubjectiveWorldModel
→ CausalHypothesis
→ AgentAction
→ CandidateFuture
→ WorldTransition / Provenance
→ NarrativeEvent
→ SceneCard / ImagePrompt
```

## Quick Start

```bash
python app.py --input "校园监控：学校部署不透明的网络异常流量检测系统。" --steps 3
```

不写入 `outputs/`：

```bash
python app.py --no-export
```

## Current MVP

- 1 个客观世界。
- 2 个角色：林夏、王晨。
- 2 个主观世界模型。
- 3 个 Lens：Psychology、Economic、SocialStructure。
- 每步 4 个 CandidateFuture。
- Narrative Engine 只表达世界变化，不反向修改客观事实。

当前可运行链路是研究基线。V2.1/V2.2 计划将继续补充 Theory of Mind、Agent Action Model、Hypothesis Conflict Resolver、完整 State Provenance，以及 Same World Different Minds、Lens Ablation 和 Baseline Comparison 实验。

## Roadmaps

- `StoryWorld_V2_docs/11_development_roadmap_40_days.md`：V2.1 研究路线图。
- `StoryWorld_V2_docs/11_development_roadmap_40_days(1).md`：V2.2 每日详细执行版。

## Output

每次运行写入 `outputs/run_XXX/`：

```text
objective_states.json
agent_profiles.json
observations.json
subjective_models.json
mental_models.json
bias_filter_results.json
interpretations.json
hypotheses.json
candidate_futures.json
selected_futures.json
narrative_events.json
scene_cards.json
image_prompts.json
report.md
```
