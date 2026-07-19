# 14 推荐项目目录结构

```text
storyworld_v2/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
│
├── core/
│   ├── llm_client.py
│   ├── world_initializer.py
│   ├── observation_engine.py
│   ├── evidence_evaluator.py
│   ├── belief_updater.py
│   ├── cognition_engine.py
│   ├── theory_of_mind.py
│   ├── lens_router.py
│   ├── hypothesis_conflict_resolver.py
│   ├── agent_action_model.py
│   ├── future_generator.py
│   ├── agent_consistency.py
│   ├── future_evaluator.py
│   ├── world_transition.py
│   ├── narrative_importance.py
│   ├── narrative_engine.py
│   ├── scene_generator.py
│   ├── image_prompt_generator.py
│   └── output_exporter.py
│
├── lenses/
│   ├── base.py
│   ├── psychology.py
│   ├── economics.py
│   └── social_structure.py
│
├── schemas/
│   ├── objective_world.py
│   ├── subjective_world.py
│   ├── theory_of_mind.py
│   ├── agent.py
│   ├── observation.py
│   ├── interpretation.py
│   ├── causal_hypothesis.py
│   ├── candidate_future.py
│   ├── state_provenance.py
│   ├── narrative_event.py
│   └── scene_card.py
│
├── prompts/
│   ├── world_init/
│   ├── cognition/
│   ├── lenses/
│   ├── future/
│   ├── narrative/
│   └── scene/
│
├── data/
│   ├── examples/
│   ├── test_cases/
│   └── experiments/
│
├── outputs/
│
├── frontend/
│   └── gradio_app.py
│
├── tests/
│   ├── test_schema.py
│   ├── test_observation.py
│   ├── test_belief.py
│   ├── test_theory_of_mind.py
│   ├── test_agent_action.py
│   ├── test_provenance.py
│   ├── test_hypothesis.py
│   ├── test_future.py
│   └── test_narrative_separation.py
│
├── experiments/
│   ├── same_world_different_minds.py
│   ├── lens_ablation.py
│   └── baseline_comparison.py
│
└── docs/
```

新增路径表示 V2.2 目标结构；在对应日任务验收前可以尚不存在。

模块依赖建议：

```text
schemas
   ↑
lenses
   ↑
core
   ↑
frontend
```

避免 `schemas import core`。

## 输出目录

```text
outputs/run_001/
├── objective_states.json
├── observations.json
├── subjective_models.json
├── beliefs_about_others.json
├── interpretations.json
├── hypotheses.json
├── hypothesis_relations.json
├── agent_actions.json
├── candidate_futures.json
├── selected_futures.json
├── state_provenance.json
├── narrative_events.json
├── scene_cards.json
├── image_prompts.json
└── report.md
```

## Git 里程碑

```text
v0.1 schemas
v0.2 objective/subjective separation + provenance contract
v0.3 belief update + Theory of Mind
v0.4 three lenses + conflict resolution
v0.5 agent action + candidate future
v0.6 world transition + multi-step simulation
v0.7 experiments + narrative expression
v0.8 demo
v1.0 MVP
```
