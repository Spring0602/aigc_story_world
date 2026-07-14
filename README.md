# StoryWorld V2

面向动态叙事生成的多主体、多视角因果世界推演框架。

V2 不再使用旧版 `WorldState -> PlotEngine -> EventCard` 链路，而是显式拆分：

```text
ObjectiveWorldState
→ Observation
→ SubjectiveWorldModel
→ CausalHypothesis
→ CandidateFuture
→ WorldTransition
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

## Output

每次运行写入 `outputs/run_XXX/`：

```text
objective_states.json
agent_profiles.json
observations.json
subjective_models.json
interpretations.json
hypotheses.json
candidate_futures.json
selected_futures.json
narrative_events.json
scene_cards.json
image_prompts.json
report.md
```
