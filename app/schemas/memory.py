from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.conflicts import ConflictGroup, ConflictRecord
from app.schemas.evidence import ADMETSummary, EvidenceFact, RetrievedDocument, SARObservation


class RunWorkspace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    retrieved_documents: list[RetrievedDocument] = Field(default_factory=list)
    evidence_facts: list[EvidenceFact] = Field(default_factory=list)
    sar_observations: list[SARObservation] = Field(default_factory=list)
    admet_summary: ADMETSummary | None = None
    conflict_groups: list[ConflictGroup] = Field(default_factory=list)
    conflicts: list[ConflictRecord] = Field(default_factory=list)
    interim_notes: list[str] = Field(default_factory=list)
    updated_at: datetime


class QueryStrategyMemory(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memory_id: str
    entity_class: str
    goal: str
    preferred_terms: list[str] = Field(default_factory=list)
    preferred_sources: list[str] = Field(default_factory=list)
    expansion_terms: list[str] = Field(default_factory=list)
    observed_quality_score: float
    last_used_at: datetime


class ScaffoldPropertyMemory(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memory_id: str
    scaffold_key: str
    property_signals: dict = Field(default_factory=dict)
    supporting_entities: list[str] = Field(default_factory=list)
    source_artifact_ids: list[str] = Field(default_factory=list)
    confidence: float
    last_updated_at: datetime


class ConflictMemory(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memory_id: str
    group_pattern: str
    typical_reason_hint: str
    supporting_conflict_ids: list[str] = Field(default_factory=list)
    confidence: float
    last_updated_at: datetime