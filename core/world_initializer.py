from schemas import (
    ActiveProcess,
    AgentProfile,
    InformationItem,
    Location,
    ObjectiveWorldState,
    Relationship,
    SubjectiveWorldModel,
)


class WorldInitializer:
    def initialize(self, setting: str) -> tuple[ObjectiveWorldState, list[AgentProfile], list[SubjectiveWorldModel]]:
        objective_state = ObjectiveWorldState(
            state_id="state_000",
            step=0,
            timestamp="day_1_23_50",
            locations={
                "dorm": Location(location_id="dorm", name="女生宿舍", description="深夜里只有电脑屏幕亮着"),
                "campus_network": Location(location_id="campus_network", name="校园网络", description="近期正在升级检测系统"),
                "computer_lab": Location(location_id="computer_lab", name="计算机学院机房"),
            },
            agents={
                "lin_xia": {"location": "dorm", "status": "awake"},
                "wang_chen": {"location": "dorm", "status": "awake"},
            },
            institutions={
                "university_it_office": {
                    "name": "学校网络中心",
                    "authority_scope": ["campus_network"],
                    "transparency": 0.35,
                }
            },
            norms={
                "student_network_policy": {
                    "content": "学生应遵守校园网安全规则，但升级细节不会完全公开。",
                    "clarity": 0.48,
                }
            },
            relationships={
                "lin_xia__wang_chen": Relationship(
                    source="lin_xia",
                    target="wang_chen",
                    trust=0.72,
                    dependency=0.35,
                    emotional_attachment=0.62,
                    conflict=0.18,
                )
            },
            public_information=[
                InformationItem(
                    info_id="info_public_network_upgrade",
                    content="学校近期部署网络异常流量检测系统。",
                    visibility="public",
                    source="university_notice",
                )
            ],
            hidden_facts=[
                InformationItem(
                    info_id="info_hidden_scope_unclear",
                    content="检测系统的功能边界并不透明。",
                    visibility="hidden",
                    source="system_fact",
                ),
                InformationItem(
                    info_id="info_private_dns_redirect",
                    content="林夏的终端记录到部分 DNS 请求被重定向。",
                    visibility="private",
                    location_id="dorm",
                    source="terminal",
                ),
            ],
            active_processes=[
                ActiveProcess(
                    process_id="campus_network_monitoring_rollout",
                    type="institutional_change",
                    start_time="day_1",
                    time_scale="days",
                    drivers=["security_policy", "network_risk_control"],
                    current_stage="pilot",
                )
            ],
            history=[{"step": 0, "fact": "scenario_seed", "value": setting}],
        )

        agents = [
            AgentProfile(
                agent_id="lin_xia",
                name="林夏",
                identity={"age": 20, "occupation": "计算机专业学生"},
                roles=["student", "roommate"],
                goals=["确认网络异常是否意味着监控", "保护个人自由"],
                values={"freedom": 0.9, "truth": 0.88, "safety": 0.45, "order": 0.35},
                epistemology={"trust_data": 0.92, "trust_authority": 0.18, "tolerance_for_uncertainty": 0.62},
                human_nature_model={"trust_default": 0.35, "self_interest": 0.66},
                theory_of_change={"technology": 0.75, "institutions": 0.62, "individual_leaders": 0.25},
                methodology=["inspect_logs", "compare_network_traces"],
                visual_features={"hair": "black medium-length hair", "clothes": "loose white hoodie"},
            ),
            AgentProfile(
                agent_id="wang_chen",
                name="王晨",
                identity={"age": 20, "occupation": "学生"},
                roles=["student", "roommate"],
                goals=["维持宿舍稳定", "避免惹上学校处分"],
                values={"freedom": 0.42, "truth": 0.55, "safety": 0.86, "order": 0.82},
                epistemology={"trust_data": 0.45, "trust_authority": 0.82, "tolerance_for_uncertainty": 0.38},
                human_nature_model={"trust_default": 0.58, "self_interest": 0.52},
                theory_of_change={"institutions": 0.78, "social_networks": 0.42, "technology": 0.52},
                methodology=["ask_authority", "follow_policy"],
            ),
        ]

        subjective_models = [
            SubjectiveWorldModel(
                agent_id=agent.agent_id,
                knowledge=["学校发布了网络安全升级通知"],
                values=agent.values,
                goals=agent.goals,
                identity=agent.identity,
                roles=agent.roles,
                epistemology=agent.epistemology,
                human_nature_model=agent.human_nature_model,
                theory_of_change=agent.theory_of_change,
                methodology=agent.methodology,
                emotion={"fear": 0.36, "curiosity": 0.58, "anger": 0.12, "hope": 0.31},
            )
            for agent in agents
        ]
        return objective_state, agents, subjective_models
