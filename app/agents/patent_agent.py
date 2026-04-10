from __future__ import annotations

from app.agents.base import BaseAgent
from app.common.clock import now_utc
from app.common.ids import new_id
from app.schemas import (
    AgentName,
    AgentResult,
    RetrievedDocument,
    SARObservation,
    SourceType,
    StepStatus,
)
from app.tools.contracts import ToolRequest


class PatentAgent(BaseAgent):
    agent_name = AgentName.PATENT

    def run(self, run, workspace) -> AgentResult:
        tool = self.get_tool("patent_search")

        request = ToolRequest(
            query=f"{run.query} analog scaffold selectivity",
            top_k=3,
        )
        response = tool.execute(request)

        if response.status != "ok":
            return AgentResult(
                result_id=new_id("result"),
                run_id=run.run_id,
                agent_name=self.agent_name,
                status=StepStatus.FAILED,
                payload={},
                warnings=[],
                errors=response.errors,
                produced_at=now_utc(),
            )

        retrieved_documents = []
        sar_observations = []

        for item in response.results:
            retrieved_documents.append(
                RetrievedDocument(
                    retrieval_id=new_id("ret"),
                    run_id=run.run_id,
                    source_id=item.source_id,
                    chunk_id=item.chunk_id or new_id("chunk"),
                    source_type=SourceType.PATENT,
                    title=item.title,
                    text=item.text or "",
                    score=item.score,
                    metadata=item.metadata,
                )
            )

            sar_observations.append(
                SARObservation(
                    sar_id=new_id("sar"),
                    run_id=run.run_id,
                    entity=run.query,
                    analog_name="analog_x",
                    scaffold_key="btk_core_scaffold_A",
                    observation=(
                        item.text[:160] if item.text else
                        "Patent-derived SAR clue"
                    ),
                    source_id=item.source_id,
                    chunk_id=item.chunk_id,
                    confidence=min(max(item.score, 0.5), 0.95),
                )
            )

        return AgentResult(
            result_id=new_id("result"),
            run_id=run.run_id,
            agent_name=self.agent_name,
            status=StepStatus.SUCCEEDED,
            payload={
                "retrieved_documents": retrieved_documents,
                "sar_observations": sar_observations,
            },
            warnings=[],
            errors=[],
            produced_at=now_utc(),
        )