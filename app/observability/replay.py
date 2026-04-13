from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ReplayEvent:
    ts: float
    event: str
    payload: dict[str, Any]


@dataclass
class RunReplay:
    run_id: str
    events: list[ReplayEvent] = field(default_factory=list)

    def add_event(self, event: ReplayEvent) -> None:
        self.events.append(event)

    def sort(self) -> None:
        self.events.sort(key=lambda e: e.ts)

    def summary(self) -> dict[str, Any]:
        step_transitions = [
            e for e in self.events if e.event == "step_transition"
        ]
        tool_calls = [
            e for e in self.events if e.event == "tool_call_end"
        ]
        workspace_updates = [
            e for e in self.events if e.event == "workspace_update"
        ]
        review_events = [
            e for e in self.events if e.event == "review_created"
        ]
        completed = [
            e for e in self.events if e.event == "run_completed"
        ]

        final_status = None
        if completed:
            final_status = completed[-1].payload.get("run_status")

        return {
            "run_id": self.run_id,
            "event_count": len(self.events),
            "step_transition_count": len(step_transitions),
            "tool_call_count": len(tool_calls),
            "workspace_update_count": len(workspace_updates),
            "review_created": len(review_events) > 0,
            "final_status": final_status,
        }

    def pretty_timeline(self) -> list[str]:
        lines: list[str] = []

        for e in self.events:
            p = e.payload

            if e.event == "run_created":
                lines.append(
                    f"[run_created] query={p.get('query')}"
                )

            elif e.event == "step_transition":
                lines.append(
                    f"[step_transition] agent={p.get('agent')} "
                    f"{p.get('from_status')} → {p.get('to_status')}"
                )

            elif e.event == "tool_call_start":
                lines.append(
                    f"[tool_call_start] tool={p.get('tool_name')}"
                )

            elif e.event == "tool_call_end":
                lines.append(
                    f"[tool_call_end] tool={p.get('tool_name')} "
                    f"status={p.get('status')} "
                    f"results={p.get('result_count')} "
                    f"latency_ms={p.get('latency_ms')}"
                )

            elif e.event == "workspace_update":
                lines.append(
                    f"[workspace_update] agent={p.get('agent')} "
                    f"delta={p.get('delta')}"
                )

            elif e.event == "review_created":
                lines.append(
                    f"[review_created] reasons={p.get('reasons')}"
                )

            elif e.event == "run_completed":
                lines.append(
                    f"[run_completed] status={p.get('run_status')} "
                    f"artifact_ready={p.get('artifact_ready')}"
                )

            else:
                lines.append(f"[{e.event}] {p}")

        return lines


def load_events(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))

    return rows


def replay_run(path: str | Path, run_id: str) -> RunReplay:
    rows = load_events(path)
    replay = RunReplay(run_id=run_id)

    for row in rows:
        if row.get("run_id") != run_id:
            continue

        replay.add_event(
            ReplayEvent(
                ts=float(row["ts"]),
                event=row["event"],
                payload=row,
            )
        )

    replay.sort()
    return replay


def list_run_ids(path: str | Path) -> list[str]:
    rows = load_events(path)
    run_ids = {
        row["run_id"]
        for row in rows
        if "run_id" in row
    }
    return sorted(run_ids)