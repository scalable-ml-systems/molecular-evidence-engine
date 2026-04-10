from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.schemas import AgentResult, Run, RunWorkspace
from app.tools.registry import ToolRegistry


@dataclass(slots=True)
class RunRequest:
    query: str
    entity_type: str = "compound"


class Agent(Protocol):
    def run(self, run: Run, workspace: RunWorkspace) -> AgentResult:
        ...


class BaseAgent:
    agent_name: str = "base_agent"

    def __init__(self, tool_registry: ToolRegistry) -> None:
        self.tool_registry = tool_registry

    def get_tool(self, name: str):
        return self.tool_registry.get(name)