from pathlib import Path
import sys

from app.observability.replay import list_run_ids, replay_run


EVENT_LOG = Path("output/logs/events.jsonl")


def main() -> None:
    if not EVENT_LOG.exists():
        print("No event log found at output/logs/events.jsonl")
        return

    if len(sys.argv) < 2:
        print("Usage: python scripts/replay_run.py <run_id>")
        print("\nAvailable run_ids:")
        for run_id in list_run_ids(EVENT_LOG):
            print(f"  - {run_id}")
        return

    run_id = sys.argv[1]
    replay = replay_run(EVENT_LOG, run_id)

    print("\n=== REPLAY SUMMARY ===")
    print(replay.summary())

    print("\n=== REPLAY TIMELINE ===")
    for line in replay.pretty_timeline():
        print(line)


if __name__ == "__main__":
    main()