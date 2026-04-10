import json
import time
from typing import Any


def log_event(event: str, **fields: Any) -> None:
    payload = {
        "event": event,
        "ts": time.time(),
        **fields,
    }
    print(json.dumps(payload, default=str))


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