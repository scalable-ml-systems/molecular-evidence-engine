from __future__ import annotations

from app.data.loader import load_jsonl
from app.retrieval.simple_search import top_k_search
from app.tools.contracts import ToolRequest, ToolResponse, ToolResultItem


class LiteratureSearchTool:
    name = "literature_search"

    def __init__(self, papers_path: str) -> None:
        self._rows = load_jsonl(papers_path)

    def execute(self, request: ToolRequest) -> ToolResponse:
        query = request.query or ""
        top_k = request.top_k

        rows = top_k_search(
            query=query,
            rows=self._rows,
            text_field="text",
            title_field="title",
            top_k=top_k,
        )

        results = [
            ToolResultItem(
                id=row["id"],
                source_id=row["source_id"],
                chunk_id=row.get("chunk_id"),
                title=row.get("title"),
                text=row.get("text"),
                score=row["_score"],
                metadata={
                    "year": row.get("year"),
                    "authors": row.get("authors", []),
                    "source_type": "literature",
                },
            )
            for row in rows
        ]

        return ToolResponse(
            tool_name=self.name,
            status="ok",
            results=results,
            metadata={"query": query, "top_k": top_k},
        )