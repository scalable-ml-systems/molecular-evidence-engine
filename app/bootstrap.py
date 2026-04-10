from __future__ import annotations

from app.tools import ToolRegistry
from app.tools.computation import ADMETTool, MeasurementNormalizerTool
from app.tools.perception import AssayLookupTool, LiteratureSearchTool, PatentSearchTool


def build_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()

    registry.register(LiteratureSearchTool("data/seed/papers.jsonl"))
    registry.register(PatentSearchTool("data/seed/patents.jsonl"))
    registry.register(AssayLookupTool("data/seed/assays.json"))
    registry.register(MeasurementNormalizerTool())
    registry.register(ADMETTool())

    return registry