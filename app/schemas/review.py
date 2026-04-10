from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import ReviewDecision


class ReviewItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    review_id: str
    run_id: str
    artifact_id: str
    requires_review: bool = True
    reasons: list[str] = Field(default_factory=list)
    decision: ReviewDecision = ReviewDecision.PENDING
    reviewer_notes: str | None = None
    created_at: datetime
    decided_at: datetime | None = None