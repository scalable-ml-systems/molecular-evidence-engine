from app.common.clock import now_utc
from app.common.ids import new_id
from app.schemas import (
    ADMETSummary,
    AgentName,
    AgentResult,
    AssayCategory,
    ConflictGroup,
    ConflictRecord,
    EvidenceFact,
    MeasurementType,
    RetrievedDocument,
    SARObservation,
    SourceType,
    StepStatus,
)


class StubPatentAgent:
    def run(self, run, workspace):
        doc = RetrievedDocument(
            retrieval_id=new_id("ret"),
            run_id=run.run_id,
            source_id="patent_001",
            chunk_id="patent_001_chunk_02",
            source_type=SourceType.PATENT,
            title="BTK inhibitor analog series",
            text="Analog substitutions around the BTK core scaffold improve selectivity.",
            score=0.89,
            metadata={"jurisdiction": "WO"},
        )
        sar = SARObservation(
            sar_id=new_id("sar"),
            run_id=run.run_id,
            entity=run.query,
            analog_name="analog_x",
            scaffold_key="btk_core_scaffold_A",
            observation="Ring-position substitution appears associated with improved kinase selectivity.",
            source_id="patent_001",
            chunk_id="patent_001_chunk_02",
            confidence=0.78,
        )
        return AgentResult(
            result_id=new_id("result"),
            run_id=run.run_id,
            agent_name=AgentName.PATENT,
            status=StepStatus.SUCCEEDED,
            payload={
                "retrieved_documents": [doc],
                "sar_observations": [sar],
            },
            produced_at=now_utc(),
        )


class StubLiteratureAgent:
    def run(self, run, workspace):
        doc1 = RetrievedDocument(
            retrieval_id=new_id("ret"),
            run_id=run.run_id,
            source_id="paper_001",
            chunk_id="paper_001_chunk_03",
            source_type=SourceType.LITERATURE,
            title="Selective BTK inhibition profile of acalabrutinib",
            text="Biochemical IC50 for BTK was measured at 5.1 nM.",
            score=0.94,
            metadata={"year": 2018},
        )
        doc2 = RetrievedDocument(
            retrieval_id=new_id("ret"),
            run_id=run.run_id,
            source_id="assay_004",
            chunk_id="assay_004_row_01",
            source_type=SourceType.ASSAY,
            title="Assay summary row",
            text="BTK IC50 = 9.7 nM in alternate assay setup.",
            score=0.83,
            metadata={"assay_platform": "cellular"},
        )
        fact1 = EvidenceFact(
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
            source_id="paper_001",
            chunk_id="paper_001_chunk_03",
            confidence=0.88,
            notes="High-confidence extracted potency value",
        )
        fact2 = EvidenceFact(
            evidence_id=new_id("ev"),
            run_id=run.run_id,
            entity=run.query,
            target="BTK",
            fact_type="potency",
            measurement_type=MeasurementType.IC50,
            value=9.7,
            unit="nM",
            assay_category=AssayCategory.CELLULAR,
            assay_context="cellular assay",
            source_id="assay_004",
            chunk_id="assay_004_row_01",
            confidence=0.81,
            notes="Alternate potency value from assay table",
        )
        return AgentResult(
            result_id=new_id("result"),
            run_id=run.run_id,
            agent_name=AgentName.LITERATURE,
            status=StepStatus.SUCCEEDED,
            payload={
                "retrieved_documents": [doc1, doc2],
                "evidence_facts": [fact1, fact2],
            },
            produced_at=now_utc(),
        )


class StubADMETAgent:
    def run(self, run, workspace):
        admet = ADMETSummary(
            admet_id=new_id("admet"),
            run_id=run.run_id,
            entity=run.query,
            solubility_bucket="medium",
            permeability_bucket="high",
            cyp450_liability="low",
            herg_risk="low",
            method="heuristic_v1",
            source_type=SourceType.COMPUTED,
            confidence=0.72,
            notes=["Derived from heuristic rules for V1 prototype"],
        )
        return AgentResult(
            result_id=new_id("result"),
            run_id=run.run_id,
            agent_name=AgentName.ADMET,
            status=StepStatus.SUCCEEDED,
            payload={"admet_summary": admet},
            produced_at=now_utc(),
        )


class StubCrossRefAgent:
    def run(self, run, workspace):
        evidence_ids = [fact.evidence_id for fact in workspace.evidence_facts]
        source_ids = [fact.source_id for fact in workspace.evidence_facts]
        group = ConflictGroup(
            group_key=f"{run.query}|BTK|IC50",
            entity=run.query,
            target="BTK",
            measurement_type=MeasurementType.IC50,
            normalized_unit="nM",
            evidence_ids=evidence_ids,
        )
        conflict = ConflictRecord(
            conflict_id=new_id("conf"),
            run_id=run.run_id,
            group_key=f"{run.query}|BTK|IC50",
            issue_type="value_disagreement",
            normalized_values=[5.1, 9.7],
            unit="nM",
            source_ids=source_ids,
            assay_categories=[AssayCategory.ENZYMATIC, AssayCategory.CELLULAR],
            reason_hint="assay_context_mismatch",
            requires_review=True,
            confidence=0.84,
        )
        return AgentResult(
            result_id=new_id("result"),
            run_id=run.run_id,
            agent_name=AgentName.CROSSREF,
            status=StepStatus.SUCCEEDED,
            payload={
                "conflict_groups": [group],
                "conflicts": [conflict],
            },
            produced_at=now_utc(),
        )