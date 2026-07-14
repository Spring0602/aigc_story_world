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
│   ├── lens_router.py
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
│   ├── agent.py
│   ├── observation.py
│   ├── interpretation.py
│   ├── causal_hypothesis.py
│   ├── candidate_future.py
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
│   └── test_cases/
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
│   ├── test_hypothesis.py
│   ├── test_future.py
│   └── test_narrative_separation.py
│
└── docs/
```

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
├── interpretations.json
├── hypotheses.json
├── candidate_futures.json
├── selected_futures.json
├── narrative_events.json
├── scene_cards.json
├── image_prompts.json
└── report.md
```

## Git 里程碑

```text
v0.1 schemas
v0.2 objective/subjective separation
v0.3 world loop
v0.4 three lenses
v0.5 candidate future
v0.6 narrative engine
v0.7 testing
v0.8 demo
v1.0 MVP
```
