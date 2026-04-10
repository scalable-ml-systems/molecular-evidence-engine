from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import AssayCategory, MeasurementType, SourceType


class RetrievedDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    retrieval_id: str
    run_id: str
    source_id: str
    chunk_id: str
    source_type: SourceType
    title: str | None = None
    text: str
    score: float = Field(ge=0.0, le=1.0)
    metadata: dict = Field(default_factory=dict)


class EvidenceProvenance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    source_id: str
    chunk_id: str | None = None
    source_type: SourceType
    tool_name: str
    agent_name: str
    extraction_method: str
    confidence: float = Field(ge=0.0, le=1.0)
    lineage: list[str] = Field(default_factory=list)


class EvidenceFact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    run_id: str
    entity: str
    target: str | None = None
    fact_type: str = "potency"
    measurement_type: MeasurementType = MeasurementType.UNKNOWN
    value: float | None = None
    unit: str | None = None
    assay_category: AssayCategory = AssayCategory.UNKNOWN
    assay_context: str | None = None
    source_id: str
    chunk_id: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    notes: str | None = None


class SARObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sar_id: str
    run_id: str
    entity: str
    analog_name: str | None = None
    scaffold_key: str | None = None
    observation: str
    source_id: str
    chunk_id: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)


class ADMETSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    admet_id: str
    run_id: str
    entity: str
    solubility_bucket: str | None = None
    permeability_bucket: str | None = None
    cyp450_liability: str | None = None
    herg_risk: str | None = None
    method: str
    source_type: SourceType = SourceType.COMPUTED
    confidence: float = Field(ge=0.0, le=1.0)
    notes: list[str] = Field(default_factory=list)