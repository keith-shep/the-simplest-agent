from datetime import UTC, datetime


def get_current_time() -> str:
    now = datetime.now(UTC)
    return now.isoformat()
