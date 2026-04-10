from __future__ import annotations

from collections import defaultdict

from app.agents.base import BaseAgent
from app.common.clock import now_utc
from app.common.ids import new_id
from app.schemas import (
    AgentName,
    AgentResult,
    AssayCategory,
    ConflictGroup,
    ConflictRecord,
    MeasurementType,
    StepStatus,
)
from app.tools.contracts import ToolRequest


class CrossRefAgent(BaseAgent):
    agent_name = AgentName.CROSSREF

    def run(self, run, workspace) -> AgentResult:
        normalizer = self.get_tool("measurement_normalizer")

        grouped = defaultdict(list)
        for fact in workspace.evidence_facts:
            group_key = f"{fact.entity}|{fact.target}|{fact.measurement_type.value}"
            grouped[group_key].append(fact)

        conflict_groups = []
        conflicts = []

        for group_key, facts in grouped.items():
            normalized_values = []
            source_ids = []
            assay_categories = []
            evidence_ids = []

            for fact in facts:
                if fact.value is None or not fact.unit:
                    continue

                response = normalizer.execute(
                    ToolRequest(payload={"value": fact.value, "unit": fact.unit})
                )
                if response.status != "ok" or not response.results:
                    continue

                normalized = response.results[0].metadata["normalized_value"]
                normalized_values.append(float(normalized))
                source_ids.append(fact.source_id)
                assay_categories.append(fact.assay_category)
                evidence_ids.append(fact.evidence_id)

            if not normalized_values:
                continue

            first_fact = facts[0]
            conflict_group = ConflictGroup(
                group_key=group_key,
                entity=first_fact.entity,
                target=first_fact.target,
                measurement_type=first_fact.measurement_type,
                normalized_unit="nM",
                evidence_ids=evidence_ids,
            )
            conflict_groups.append(conflict_group)

            if len(normalized_values) >= 2:
                min_v = min(normalized_values)
                max_v = max(normalized_values)

                if min_v > 0 and (max_v / min_v) > 1.5:
                    reason_hint = "value_disagreement"
                    if len(set(assay_categories)) > 1:
                        reason_hint = "assay_context_mismatch"

                    conflicts.append(
                        ConflictRecord(
                            conflict_id=new_id("conf"),
                            run_id=run.run_id,
                            group_key=group_key,
                            issue_type="value_disagreement",
                            normalized_values=normalized_values,
                            unit="nM",
                            source_ids=source_ids,
                            assay_categories=assay_categories,
                            reason_hint=reason_hint,
                            requires_review=True,
                            confidence=0.84,
                        )
                    )

        return AgentResult(
            result_id=new_id("result"),
            run_id=run.run_id,
            agent_name=self.agent_name,
            status=StepStatus.SUCCEEDED,
            payload={
                "conflict_groups": conflict_groups,
                "conflicts": conflicts,
            },
            warnings=[],
            errors=[],
            produced_at=now_utc(),
        )