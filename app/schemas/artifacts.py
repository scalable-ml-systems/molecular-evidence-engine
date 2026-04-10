from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.conflicts import ConflictRecord
from app.schemas.enums import ArtifactType, ReviewDecision
from app.schemas.evidence import ADMETSummary, EvidenceFact, SARObservation


class EvidenceBrief(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    run_id: str
    entity: str
    analogs: list[str] = Field(default_factory=list)
    evidence_facts: list[EvidenceFact] = Field(default_factory=list)
    sar_observations: list[SARObservation] = Field(default_factory=list)
    admet_summary: ADMETSummary | None = None
    conflicts: list[ConflictRecord] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    final_summary: str
    requires_review: bool = False
    review_decision: ReviewDecision = ReviewDecision.PENDING
    created_at: datetime


class ArtifactEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    artifact_type: ArtifactType
    schema_version: str = "1.0"
    payload: EvidenceBrief
    created_at: datetime