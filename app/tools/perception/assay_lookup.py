from __future__ import annotations

from app.data.loader import load_json
from app.tools.contracts import ToolRequest, ToolResponse, ToolResultItem


class AssayLookupTool:
    name = "assay_lookup"

    def __init__(self, assays_path: str) -> None:
        self._rows: list[dict] = load_json(assays_path)

    def execute(self, request: ToolRequest) -> ToolResponse:
        compound = request.payload.get("compound")
        target = request.payload.get("target")

        results: list[ToolResultItem] = []
        for row in self._rows:
            if compound and row.get("compound") != compound:
                continue
            if target and row.get("target") != target:
                continue

            results.append(
                ToolResultItem(
                    id=row["id"],
                    source_id=row["source_id"],
                    chunk_id=row.get("chunk_id"),
                    title=row.get("title"),
                    text=row.get("text"),
                    score=1.0,
                    metadata={
                        "compound": row.get("compound"),
                        "target": row.get("target"),
                        "measurement_type": row.get("measurement_type"),
                        "value": row.get("value"),
                        "unit": row.get("unit"),
                        "assay_category": row.get("assay_category"),
                        "assay_context": row.get("assay_context"),
                    },
                )
            )

        return ToolResponse(
            tool_name=self.name,
            status="ok",
            results=results,
            metadata={"compound": compound, "target": target},
        )