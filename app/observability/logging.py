import json
import os
import time
from pathlib import Path
from typing import Any

LOG_DIR = Path("output/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

EVENT_LOG_PATH = LOG_DIR / "events.jsonl"


def log_event(event: str, **fields: Any) -> None:
    payload = {
        "event": event,
        "ts": time.time(),
        **fields,
    }

    line = json.dumps(payload, default=str)

    print(line)

    with open(EVENT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def snapshot_workspace(workspace) -> dict:
    return {
        "docs": len(workspace.retrieved_documents),
        "facts": len(workspace.evidence_facts),
        "sar": len(workspace.sar_observations),
        "admet": workspace.admet_summary is not None,
        "conflicts": len(workspace.conflicts),
    }


def diff_snapshot(before: dict, after: dict) -> dict:
    delta = {}
    for key in before:
        if before[key] != after[key]:
            delta[key] = f"{before[key]} → {after[key]}"
    return delta