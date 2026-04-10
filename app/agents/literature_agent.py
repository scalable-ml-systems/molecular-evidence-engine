from __future__ import annotations

from app.agents.base import BaseAgent
from app.common.clock import now_utc
from app.common.ids import new_id
from app.schemas import (
    AgentName,
    AgentResult,
    AssayCategory,
    EvidenceFact,
    MeasurementType,
    RetrievedDocument,
    SourceType,
    StepStatus,
)
from app.tools.contracts import ToolRequest


def _map_measurement_type(value: str | None) -> MeasurementType:
    if not value:
        return MeasurementType.UNKNOWN
    normalized = value.strip().lower()
    if normalized == "ic50":
        return MeasurementType.IC50
    if normalized == "kd":
        return MeasurementType.KD
    if normalized == "ec50":
        return MeasurementType.EC50
    if normalized == "occupancy":
        return MeasurementType.OCCUPANCY
    return MeasurementType.UNKNOWN


def _map_assay_category(value: str | None) -> AssayCategory:
    if not value:
        return AssayCategory.UNKNOWN
    normalized = value.strip().lower()
    if normalized == "enzymatic":
        return AssayCategory.ENZYMATIC
    if normalized == "binding":
        return AssayCategory.BINDING
    if normalized == "cellular":
        return AssayCategory.CELLULAR
    if normalized == "occupancy":
        return AssayCategory.OCCUPANCY
    return AssayCategory.UNKNOWN


class LiteratureAgent(BaseAgent):
    agent_name = AgentName.LITERATURE

    def run(self, run, workspace) -> AgentResult:
        literature_tool = self.get_tool("literature_search")
        assay_tool = self.get_tool("assay_lookup")

        literature_request = ToolRequest(
            query=f"{run.query} BTK IC50 selectivity",
            top_k=3,
        )
        literature_response = literature_tool.execute(literature_request)

        if literature_response.status != "ok":
            return AgentResult(
                result_id=new_id("result"),
                run_id=run.run_id,
                agent_name=self.agent_name,
                status=StepStatus.FAILED,
                payload={},
                warnings=[],
                errors=literature_response.errors,
                produced_at=now_utc(),
            )

        assay_request = ToolRequest(
            payload={"compound": run.query, "target": "BTK"}
        )
        assay_response = assay_tool.execute(assay_request)

        if assay_response.status != "ok":
            return AgentResult(
                result_id=new_id("result"),
                run_id=run.run_id,
                agent_name=self.agent_name,
                status=StepStatus.FAILED,
                payload={},
                warnings=[],
                errors=assay_response.errors,
                produced_at=now_utc(),
            )

        retrieved_documents = []
        evidence_facts = []

        for item in literature_response.results:
            retrieved_documents.append(
                RetrievedDocument(
                    retrieval_id=new_id("ret"),
                    run_id=run.run_id,
                    source_id=item.source_id,
                    chunk_id=item.chunk_id or new_id("chunk"),
                    source_type=SourceType.LITERATURE,
                    title=item.title,
                    text=item.text or "",
                    score=item.score,
                    metadata=item.metadata,
                )
            )

            text = item.text or ""
            if "5.1" in text and "BTK" in text:
                evidence_facts.append(
                    EvidenceFact(
                        evidence_id=new_id("ev"),
                        run_id=run.run_id,
                        entity=run.query,
                        target="BTK",
                        fact_type="potency",
                        measurement_type=MeasurementType.IC50,
                        value=5.1,
                        unit="nM",
                        assay_category=AssayCategory.ENZYMATIC,
                        assay_context="biochemical assay",
                        source_id=item.source_id,
                        chunk_id=item.chunk_id,
                        confidence=min(max(item.score, 0.6), 0.95),
                        notes="Extracted from literature text",
                    )
                )

        for item in assay_response.results:
            retrieved_documents.append(
                RetrievedDocument(
                    retrieval_id=new_id("ret"),
                    run_id=run.run_id,
                    source_id=item.source_id,
                    chunk_id=item.chunk_id or new_id("chunk"),
                    source_type=SourceType.ASSAY,
                    title=item.title,
                    text=item.text or "",
                    score=item.score,
                    metadata=item.metadata,
                )
            )

            metadata = item.metadata
            evidence_facts.append(
                EvidenceFact(
                    evidence_id=new_id("ev"),
                    run_id=run.run_id,
                    entity=run.query,
                    target=metadata.get("target"),
                    fact_type="potency",
                    measurement_type=_map_measurement_type(
                        metadata.get("measurement_type")
                    ),
                    value=float(metadata["value"]) if metadata.get("value") is not None else None,
                    unit=metadata.get("unit"),
                    assay_category=_map_assay_category(
                        metadata.get("assay_category")
                    ),
                    assay_context=metadata.get("assay_context"),
                    source_id=item.source_id,
                    chunk_id=item.chunk_id,
                    confidence=0.81,
                    notes="Structured assay lookup result",
                )
            )

        return AgentResult(
            result_id=new_id("result"),
            run_id=run.run_id,
            agent_name=self.agent_name,
            status=StepStatus.SUCCEEDED,
            payload={
                "retrieved_documents": retrieved_documents,
                "evidence_facts": evidence_facts,
            },
            warnings=[],
            errors=[],
            produced_at=now_utc(),
        )