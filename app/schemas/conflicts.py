from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import AssayCategory, MeasurementType


class ConflictGroup(BaseModel):
    model_config = ConfigDict(extra="forbid")

    group_key: str
    entity: str
    target: str | None = None
    measurement_type: MeasurementType = MeasurementType.UNKNOWN
    normalized_unit: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)


class ConflictRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conflict_id: str
    run_id: str
    group_key: str
    issue_type: str
    normalized_values: list[float] = Field(default_factory=list)
    unit: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    assay_categories: list[AssayCategory] = Field(default_factory=list)
    reason_hint: str | None = None
    requires_review: bool = True
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)