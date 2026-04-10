from __future__ import annotations

from typing import Protocol

from app.tools.contracts import ToolRequest, ToolResponse


class Tool(Protocol):
    name: str

    def execute(self, request: ToolRequest) -> ToolResponse:
        ...