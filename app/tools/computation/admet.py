from __future__ import annotations

from app.tools.contracts import ToolRequest, ToolResponse, ToolResultItem


class ADMETTool:
    name = "compute_admet"

    def execute(self, request: ToolRequest) -> ToolResponse:
        compound = request.payload.get("compound") or request.query or "unknown"

        # V1 heuristic placeholder.
        result = ToolResultItem(
            id=f"admet_{compound}",
            source_id="computed",
            chunk_id=None,
            title=f"ADMET summary for {compound}",
            text=None,
            score=1.0,
            metadata={
                "compound": compound,
                "solubility_bucket": "medium",
                "permeability_bucket": "high",
                "cyp450_liability": "low",
                "herg_risk": "low",
                "method": "heuristic_v1",
                "confidence": 0.72,
            },
        )

        return ToolResponse(
            tool_name=self.name,
            status="ok",
            results=[result],
        )