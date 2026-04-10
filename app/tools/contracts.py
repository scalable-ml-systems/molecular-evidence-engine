from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str | None = None
    top_k: int = 5
    filters: dict[str, Any] = Field(default_factory=dict)
    payload: dict[str, Any] = Field(default_factory=dict)


class ToolResultItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    source_id: str
    chunk_id: str | None = None
    title: str | None = None
    text: str | None = None
    score: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: str
    status: str
    results: list[ToolResultItem] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)