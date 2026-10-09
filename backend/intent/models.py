from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

CONTRACT_VERSION = "CARBON_SEARCH_V1"


class EpistemicState(str, Enum):
    EXPLICIT = "EXPLICIT"
    MEASURED = "MEASURED"
    HYPOTHESIZED = "HYPOTHESIZED"
    UNKNOWN = "UNKNOWN"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class SearchScope(str, Enum):
    PUBLIC = "PUBLIC"
    CARBON_INTERNAL = "CARBON_INTERNAL"
    CARBON_MARKETPLACE = "CARBON_MARKETPLACE"
    CLIENT_SPACE = "CLIENT_SPACE"
    MATRIX_INTERNAL = "MATRIX_INTERNAL"
    EXTERNAL_WEB = "EXTERNAL_WEB"
    CONNECTED_DATA = "CONNECTED_DATA"


class EntityType(str, Enum):
    PRODUCT = "PRODUCT"
    SERVICE = "SERVICE"
    CAPABILITY = "CAPABILITY"
    UTILITY = "UTILITY"
    MARKETPLACE_OFFER = "MARKETPLACE_OFFER"
    EVIDENCE_RECORD = "EVIDENCE_RECORD"
    CLIENT_ASSET = "CLIENT_ASSET"
    INTERNAL_WORKER = "INTERNAL_WORKER"
    UNKNOWN = "UNKNOWN"


class SearchStatus(str, Enum):
    RESOLVED = "RESOLVED"
    HOLD = "HOLD"
    DEGRADED = "DEGRADED"


class ContextSignal(BaseModel):
    signal_type: str = Field(min_length=1, max_length=80)
    value: Any
    source: str = Field(default="caller", max_length=120)
    timestamp: str | None = None
    freshness: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    visibility: SearchScope = SearchScope.PUBLIC
    precision: str | None = None
    provenance: str | None = None


class IntentCriterion(BaseModel):
    key: str = Field(min_length=1, max_length=120)
    operator: Literal["eq", "gte", "lte", "contains", "prefer_high", "prefer_low"] = "eq"
    value: Any = None
    weight: float = Field(default=1.0, gt=0.0, le=10.0)
    epistemic_state: EpistemicState = EpistemicState.EXPLICIT
    signal_basis: list[str] = Field(default_factory=list)


class IntentHypothesis(BaseModel):
    hypothesis_id: str = Field(min_length=1, max_length=120)
    label: str = Field(min_length=1, max_length=240)
    probability: float = Field(default=0.5, ge=0.0, le=1.0)
    epistemic_state: EpistemicState = EpistemicState.HYPOTHESIZED
    signal_basis: list[str] = Field(default_factory=list)
    criterion: IntentCriterion | None = None
    decision_impact: float = Field(default=0.5, ge=0.0, le=1.0)
    information_value: float = Field(default=0.5, ge=0.0, le=1.0)
    cost_of_error: float = Field(default=0.5, ge=0.0, le=1.0)

    @property
    def investigation_priority(self) -> float:
        return self.probability * self.decision_impact * self.information_value * self.cost_of_error


class HiddenVariable(BaseModel):
    key: str
    observed_values: list[Any] = Field(default_factory=list)
    decision_sensitivity: float = Field(ge=0.0, le=1.0)
    information_value: float = Field(ge=0.0, le=1.0)
    state: EpistemicState = EpistemicState.HYPOTHESIZED
    basis: list[str] = Field(default_factory=list)


class CanonicalEntity(BaseModel):
    entity_id: str = Field(min_length=1, max_length=160)
    canonical_name: str = Field(min_length=1, max_length=240)
    entity_type: EntityType = EntityType.UNKNOWN
    parent: str | None = None
    aliases: list[str] = Field(default_factory=list)
    description: str = ""
    capabilities: list[str] = Field(default_factory=list)
    offered_actions: list[str] = Field(default_factory=list)
    visibility: SearchScope = SearchScope.PUBLIC
    lifecycle_state: str = "ACTIVE"
    authoritative_source: str = ""
    version: str = "1"
    supersedes: list[str] = Field(default_factory=list)
    evidence_pointer: str | None = None


class EvidenceClaim(BaseModel):
    claim_id: str
    entity_id: str
    attribute: str
    value: Any
    units: str | None = None
    source: str
    source_type: str = "SUPPLIED"
    source_timestamp: str | None = None
    retrieved_at: str
    freshness_class: str = "UNKNOWN"
    authority_class: str = "UNRATED"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    contradiction_group: str | None = None
    visibility: SearchScope = SearchScope.PUBLIC
    evidence_pointer: str | None = None
    validity: Literal["VALID", "INVALID", "SUPERSEDED"] = "VALID"


class CandidateInput(BaseModel):
    candidate_id: str = Field(min_length=1, max_length=160)
    title: str = Field(min_length=1, max_length=240)
    summary: str = Field(default="", max_length=4000)
    entity_id: str | None = None
    entity_type: EntityType = EntityType.UNKNOWN
    attributes: dict[str, Any] = Field(default_factory=dict)
    source: str = "caller"
    source_type: str = "SUPPLIED"
    source_timestamp: str | None = None
    visibility: SearchScope = SearchScope.PUBLIC
    evidence_pointer: str | None = None
    action: dict[str, Any] | None = None


class CandidateOutcome(BaseModel):
    candidate_id: str
    title: str
    summary: str = ""
    entity_id: str | None = None
    entity_type: EntityType = EntityType.UNKNOWN
    attributes: dict[str, Any] = Field(default_factory=dict)
    measured_score: float = Field(ge=0.0, le=1.0)
    expected_intent_fulfilment: float = Field(ge=0.0, le=1.0)
    relevance_score: float = Field(ge=0.0, le=1.0)
    score_inputs: list[dict[str, Any]] = Field(default_factory=list)
    evidence_pointers: list[str] = Field(default_factory=list)
    decisive_factors: list[str] = Field(default_factory=list)
    action: dict[str, Any] | None = None


class IntentPivot(BaseModel):
    pivot_id: str
    label: str
    hypothesis_id: str | None = None
    reason: str
    projected_candidate_id: str | None = None


class SearchIntentRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1200)
    limit: int = Field(default=8, ge=1, le=50)
    surface: Literal["public", "matrix", "client", "internal"] = "public"
    requested_scopes: list[SearchScope] = Field(default_factory=lambda: [SearchScope.PUBLIC])
    context_signals: list[ContextSignal] = Field(default_factory=list, max_length=40)
    criteria: list[IntentCriterion] = Field(default_factory=list, max_length=40)
    hypotheses: list[IntentHypothesis] = Field(default_factory=list, max_length=20)
    candidates: list[CandidateInput] = Field(default_factory=list, max_length=100)
    provider_mode: Literal["AUTO", "LOCAL", "EXTERNAL"] = "AUTO"
    allow_pivots: bool = True
    max_pivots: int = Field(default=2, ge=0, le=2)
    action_target: str | None = Field(default=None, max_length=120)

    @model_validator(mode="after")
    def normalize_scopes(self):
        if not self.requested_scopes:
            self.requested_scopes = [SearchScope.PUBLIC]
        return self


class SearchSession(BaseModel):
    session_id: str
    contract_version: str = CONTRACT_VERSION
    status: SearchStatus
    raw_query: str
    surface: str
    allowed_scopes: list[SearchScope]
    observed_signals: list[ContextSignal] = Field(default_factory=list)
    explicit_constraints: list[IntentCriterion] = Field(default_factory=list)
    measured_intent: list[IntentCriterion] = Field(default_factory=list)
    hypotheses: list[IntentHypothesis] = Field(default_factory=list)
    hidden_variables: list[HiddenVariable] = Field(default_factory=list)
    negative_signals: list[str] = Field(default_factory=list)
    candidates: list[CandidateOutcome] = Field(default_factory=list)
    claims: list[EvidenceClaim] = Field(default_factory=list)
    contradictions: list[dict[str, Any]] = Field(default_factory=list)
    primary: CandidateOutcome | None = None
    pivots: list[IntentPivot] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    expected_regret: float = Field(default=1.0, ge=0.0, le=1.0)
    decision_stable: bool = False
    stop_reason: str = ""
    material_gaps: list[str] = Field(default_factory=list)
    provider_state: str = "LOCAL_RULES"
    selected_pivot: str | None = None
    correction_count: int = 0
    action_state: dict[str, Any] | None = None
    created_at: str
    updated_at: str
    audit_ref: str


class SearchResponse(BaseModel):
    session_id: str
    contract_version: str = CONTRACT_VERSION
    status: SearchStatus
    measured_intent: list[IntentCriterion]
    hypotheses: list[IntentHypothesis]
    hidden_variables: list[HiddenVariable]
    primary: CandidateOutcome | None
    pivots: list[IntentPivot]
    confidence: float
    expected_regret: float
    decision_stable: bool
    stop_reason: str
    material_gaps: list[str]
    provider_state: str
    audit_ref: str


class PivotRequest(BaseModel):
    pivot_id: str


class FeedbackRequest(BaseModel):
    kind: Literal["CONFIRM", "REJECT", "CORRECT"]
    message: str = Field(default="", max_length=1200)
    signal: ContextSignal | None = None


class ActionRequest(BaseModel):
    action: str = Field(min_length=1, max_length=80)
    candidate_id: str | None = None
