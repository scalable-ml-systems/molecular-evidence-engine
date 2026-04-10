from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import AgentName, RunStatus, StepStatus


class RunStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_id: str
    run_id: str
    agent_name: AgentName
    status: StepStatus = StepStatus.PENDING
    attempt_count: int = 0
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_code: str | None = None
    error_message: str | None = None
    output_ref: str | None = None


class Run(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    schema_version: str = "1.0"
    query: str
    entity_type: str = "compound"
    status: RunStatus = RunStatus.PENDING
    current_phase: str | None = None
    has_conflicts: bool = False
    requires_review: bool = False
    artifact_ready: bool = False
    created_at: datetime
    updated_at: datetime


class AgentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    result_id: str
    run_id: str
    agent_name: AgentName
    status: StepStatus
    payload: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    produced_at: datetime