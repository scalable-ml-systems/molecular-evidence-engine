from app.agents.base import RunRequest
from app.common.clock import now_utc
from app.common.ids import new_id
from app.observability.logging import (
    log_event,
    snapshot_workspace,
    diff_snapshot,
)
from app.repositories.base import RunRepository
from app.schemas import (
    AgentName,
    ArtifactEnvelope,
    ArtifactType,
    EvidenceBrief,
    ReviewDecision,
    ReviewItem,
    Run,
    RunStatus,
    RunStep,
    RunWorkspace,
    StepStatus,
)


class InMemoryRunRepository:
    def __init__(self) -> None:
        self.runs = {}
        self.steps = {}
        self.workspaces = {}
        self.results = {}
        self.artifacts = {}
        self.reviews = {}

    def save_run(self, run):
        self.runs[run.run_id] = run

    def save_step(self, step):
        self.steps[step.step_id] = step

    def save_workspace(self, workspace):
        self.workspaces[workspace.run_id] = workspace

    def save_agent_result(self, result):
        self.results[result.result_id] = result

    def save_artifact(self, artifact):
        self.artifacts[artifact.artifact_id] = artifact

    def save_review_item(self, review_item):
        self.reviews[review_item.review_id] = review_item


def compute_review_reasons(workspace: RunWorkspace) -> list[str]:
    reasons: list[str] = []

    if workspace.conflicts:
        reasons.append("conflicts_detected")

    if not workspace.evidence_facts:
        reasons.append("no_evidence_facts")

    low_conf = [fact for fact in workspace.evidence_facts if fact.confidence < 0.5]
    if low_conf:
        reasons.append("low_confidence_evidence")

    return reasons


class SupervisorRuntime:
    def __init__(
        self,
        repository: RunRepository,
        patent_agent,
        literature_agent,
        admet_agent,
        crossref_agent,
    ) -> None:
        self.repository = repository
        self.agents = {
            AgentName.PATENT: patent_agent,
            AgentName.LITERATURE: literature_agent,
            AgentName.ADMET: admet_agent,
            AgentName.CROSSREF: crossref_agent,
        }

    def run(self, request: RunRequest) -> ArtifactEnvelope:
        run = self._create_run(request)
        workspace = self._create_workspace(run.run_id)
        steps = self._create_steps(run.run_id)

        self.repository.save_run(run)
        self.repository.save_workspace(workspace)
        for step in steps.values():
            self.repository.save_step(step)

        log_event("run_created", run_id=run.run_id, query=run.query)

        execution_order = [
            AgentName.PATENT,
            AgentName.LITERATURE,
            AgentName.ADMET,
            AgentName.CROSSREF,
        ]

        for agent_name in execution_order:
            step = steps[agent_name]
            self._mark_step_running(run, step)
            self._log_state("before_agent", run, workspace)

            agent = self.agents[agent_name]
            result = agent.run(run, workspace)
            self.repository.save_agent_result(result)

            if result.status == StepStatus.FAILED:
                self._mark_step_failed(run, step, result)
                run.status = RunStatus.FAILED
                self.repository.save_run(run)
                raise RuntimeError(f"{agent_name.value} failed: {result.errors}")

            workspace = self._merge_result_into_workspace(workspace, result)
            self.repository.save_workspace(workspace)
            self._mark_step_succeeded(run, step, result)
            self._log_state("after_agent", run, workspace)

        artifact = self._assemble_artifact(run, workspace)
        self.repository.save_artifact(artifact)

        review_item = self._maybe_create_review_item(run, artifact.payload, workspace)
        if review_item is not None:
            self.repository.save_review_item(review_item)
            run.status = RunStatus.REVIEW_REQUIRED
            run.requires_review = True
        else:
            run.status = RunStatus.SUCCEEDED
            run.requires_review = False

        run.artifact_ready = True
        run.updated_at = now_utc()
        self.repository.save_run(run)
        self._log_state("run_completed", run, workspace)

        return artifact

    def _create_run(self, request: RunRequest) -> Run:
        ts = now_utc()
        return Run(
            run_id=new_id("run"),
            query=request.query,
            entity_type=request.entity_type,
            status=RunStatus.PENDING,
            current_phase=None,
            has_conflicts=False,
            requires_review=False,
            artifact_ready=False,
            created_at=ts,
            updated_at=ts,
        )

    def _create_workspace(self, run_id: str) -> RunWorkspace:
        return RunWorkspace(
            run_id=run_id,
            retrieved_documents=[],
            evidence_facts=[],
            sar_observations=[],
            admet_summary=None,
            conflict_groups=[],
            conflicts=[],
            interim_notes=[],
            updated_at=now_utc(),
        )

    def _create_steps(self, run_id: str) -> dict:
        ordered_agents = [
            AgentName.PATENT,
            AgentName.LITERATURE,
            AgentName.ADMET,
            AgentName.CROSSREF,
            AgentName.REPORT,
        ]
        return {
            agent_name: RunStep(
                step_id=new_id("step"),
                run_id=run_id,
                agent_name=agent_name,
                status=StepStatus.PENDING,
                attempt_count=0,
            )
            for agent_name in ordered_agents
        }

    def _mark_step_running(self, run: Run, step: RunStep) -> None:
        step.status = StepStatus.RUNNING
        step.attempt_count += 1
        step.started_at = now_utc()
        run.status = RunStatus.RUNNING
        run.current_phase = step.agent_name.value
        run.updated_at = now_utc()
        self.repository.save_step(step)
        self.repository.save_run(run)
        
        log_event(
        "step_transition",
        run_id=run.run_id,
        agent=step.agent_name.value,
        from_status="pending" if step.attempt_count == 1 else "retrying",
        to_status="running",
        attempt_count=step.attempt_count,
        )
        
    def _mark_step_succeeded(self, run: Run, step: RunStep, result) -> None:
        step.status = StepStatus.SUCCEEDED
        step.completed_at = now_utc()
        step.output_ref = result.result_id
        run.current_phase = None
        if step.agent_name == AgentName.CROSSREF and result.payload.get("conflicts"):
            run.has_conflicts = True
            run.requires_review = True
        run.updated_at = now_utc()
        self.repository.save_step(step)
        self.repository.save_run(run)

        log_event(
        "step_transition",
        run_id=run.run_id,
        agent=step.agent_name.value,
        from_status="running",
        to_status="succeeded",
        output_ref=result.result_id,
        )

    def _mark_step_failed(self, run: Run, step: RunStep, result) -> None:
        step.status = StepStatus.FAILED
        step.completed_at = now_utc()
        step.error_code = "agent_failed"
        step.error_message = "; ".join(result.errors)
        run.updated_at = now_utc()
        self.repository.save_step(step)
        self.repository.save_run(run)

        log_event(
        "step_transition",
        run_id=run.run_id,
        agent=step.agent_name.value,
        from_status="running",
        to_status="failed",
        error_code="agent_failed",
        error_message="; ".join(result.errors),
        )
    
    
    def _merge_result_into_workspace(self, workspace, result):
        before = snapshot_workspace(workspace)

        payload = result.payload

        if result.agent_name == AgentName.PATENT:
            workspace.sar_observations.extend(payload.get("sar_observations", []))
            workspace.retrieved_documents.extend(payload.get("retrieved_documents", []))

        elif result.agent_name == AgentName.LITERATURE:
            workspace.evidence_facts.extend(payload.get("evidence_facts", []))
            workspace.retrieved_documents.extend(payload.get("retrieved_documents", []))

        elif result.agent_name == AgentName.ADMET:
            workspace.admet_summary = payload.get("admet_summary")

        elif result.agent_name == AgentName.CROSSREF:
            workspace.conflict_groups = payload.get("conflict_groups", [])
            workspace.conflicts = payload.get("conflicts", [])

        workspace.updated_at = now_utc()

        after = snapshot_workspace(workspace)
        delta = diff_snapshot(before, after)

        log_event(
            "workspace_update",
            run_id=result.run_id,
            agent=result.agent_name,
            before=before,
            after=after,
            delta=delta,
        )

        return workspace 

    def _assemble_artifact(self, run: Run, workspace: RunWorkspace) -> ArtifactEnvelope:
        summary = (
            f"Evidence brief for {run.query}: "
            f"{len(workspace.evidence_facts)} evidence facts, "
            f"{len(workspace.sar_observations)} SAR observations, "
            f"{len(workspace.conflicts)} conflicts detected."
        )

        brief = EvidenceBrief(
            artifact_id=new_id("artifact"),
            run_id=run.run_id,
            entity=run.query,
            analogs=[obs.analog_name for obs in workspace.sar_observations if obs.analog_name],
            evidence_facts=workspace.evidence_facts,
            sar_observations=workspace.sar_observations,
            admet_summary=workspace.admet_summary,
            conflicts=workspace.conflicts,
            sources=sorted({
                *[fact.source_id for fact in workspace.evidence_facts],
                *[obs.source_id for obs in workspace.sar_observations],
            }),
            final_summary=summary,
            requires_review=bool(compute_review_reasons(workspace)),
            review_decision=ReviewDecision.PENDING,
            created_at=now_utc(),
        )

        return ArtifactEnvelope(
            artifact_id=brief.artifact_id,
            artifact_type=ArtifactType.EVIDENCE_BRIEF,
            payload=brief,
            created_at=now_utc(),
        )

    def _maybe_create_review_item(self, run: Run, brief: EvidenceBrief, workspace: RunWorkspace):
        reasons = compute_review_reasons(workspace)
        if not reasons:
            return None

        review_item = ReviewItem(
            review_id=new_id("review"),
            run_id=run.run_id,
            artifact_id=brief.artifact_id,
            requires_review=True,
            reasons=reasons,
            decision=ReviewDecision.PENDING,
            reviewer_notes=None,
            created_at=now_utc(),
            decided_at=None,
        )

        log_event(
            "review_created",
            run_id=run.run_id,
            artifact_id=brief.artifact_id,
            reasons=reasons,
        )
        return review_item

    def _log_state(self, event: str, run: Run, workspace: RunWorkspace) -> None:
        log_event(
            event,
            run_id=run.run_id,
            run_status=run.status,
            current_phase=run.current_phase,
            has_conflicts=run.has_conflicts,
            requires_review=run.requires_review,
            artifact_ready=run.artifact_ready,
            docs=len(workspace.retrieved_documents),
            facts=len(workspace.evidence_facts),
            sar=len(workspace.sar_observations),
            admet_present=workspace.admet_summary is not None,
            conflicts=len(workspace.conflicts),
        )