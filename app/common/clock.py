from datetime import datetime, UTC


def now_utc() -> datetime:
    return datetime.now(UTC)