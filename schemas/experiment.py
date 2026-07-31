from pydantic import BaseModel, Field

from schemas.cognitive import BiasFilterResult, MentalModel
from schemas.evidence import BayesianBeliefUpdate, BeliefState, Evidence
from schemas.interpretation import Interpretation
from schemas.observation import Observation
from schemas.subjective_world import Belief, Epistemology, Value


class CognitiveCondition(BaseModel):
    condition_id: str
    label: str
    values: dict[str, Value] = Field(default_factory=dict)
    epistemology: Epistemology


class ExperimentalAction(BaseModel):
    action: str
    source_interpretation_id: str
    rationale: str


class CognitiveExperimentTrial(BaseModel):
    condition: CognitiveCondition
    objective_state_id: str
    objective_world_fingerprint: str
    observation: Observation
    evidence: Evidence
    belief: Belief
    belief_update: BayesianBeliefUpdate
    belief_state: BeliefState
    mental_model: MentalModel
    bias_filter_result: BiasFilterResult
    interpretation: Interpretation
    action: ExperimentalAction


class ExperimentMetric(BaseModel):
    metric: str
    value: float
    passed: bool
    detail: str


class EpistemologySwapResult(BaseModel):
    condition_id: str
    borrowed_epistemology_from: str
    baseline_meaning: str
    swapped_meaning: str
    baseline_action: str
    swapped_action: str
    changed_as_predicted: bool


class PartialObservabilityControl(BaseModel):
    public_information_ids_by_agent: dict[str, list[str]] = Field(default_factory=dict)
    private_information_ids_by_agent: dict[str, list[str]] = Field(default_factory=dict)
    hidden_information_ids_observed: list[str] = Field(default_factory=list)
    boundary_preserved: bool


class SameWorldDifferentMindsResult(BaseModel):
    experiment_id: str
    hypothesis: str
    controlled_variables: list[str] = Field(default_factory=list)
    independent_variable: str
    objective_state_id: str
    objective_world_fingerprint: str
    shared_observation_signature: dict[str, object] = Field(default_factory=dict)
    trials: list[CognitiveExperimentTrial] = Field(default_factory=list)
    metrics: list[ExperimentMetric] = Field(default_factory=list)
    epistemology_swap: list[EpistemologySwapResult] = Field(default_factory=list)
    partial_observability_control: PartialObservabilityControl
    passed: bool


class LensAblationConditionResult(BaseModel):
    condition_id: str
    removed_lens: str | None = None
    enabled_lenses: list[str] = Field(default_factory=list)
    objective_world_fingerprint: str
    hypothesis_ids: list[str] = Field(default_factory=list)
    relation_ids: list[str] = Field(default_factory=list)
    relation_type_counts: dict[str, int] = Field(default_factory=dict)
    future_scores: dict[str, float] = Field(default_factory=dict)
    action_scores: dict[str, float] = Field(default_factory=dict)
    action_ranking: list[str] = Field(default_factory=list)
    selected_future_id: str
    selected_action: str
    final_state_fingerprint: str


class LensAblationComparison(BaseModel):
    condition_id: str
    removed_lens: str
    world_control_preserved: bool
    removed_lens_absent: bool
    hypothesis_pool_changed: bool
    relation_graph_changed: bool
    future_score_deltas: dict[str, float] = Field(default_factory=dict)
    action_score_deltas: dict[str, float] = Field(default_factory=dict)
    future_scores_changed: bool
    action_scores_changed: bool
    action_ranking_changed: bool
    selected_future_changed: bool
    selected_action_changed: bool
    final_state_changed: bool
    passed: bool


class LensAblationExperimentResult(BaseModel):
    experiment_id: str
    hypothesis: str
    controlled_variables: list[str] = Field(default_factory=list)
    baseline: LensAblationConditionResult
    ablations: list[LensAblationConditionResult] = Field(default_factory=list)
    comparisons: list[LensAblationComparison] = Field(default_factory=list)
    metrics: list[ExperimentMetric] = Field(default_factory=list)
    passed: bool
