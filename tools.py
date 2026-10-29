from datetime import UTC, datetime
from pathlib import Path


def get_current_time() -> str:
    now = datetime.now(UTC)
    return now.isoformat()


def read_file(path: str) -> str:
    file = Path(path)
    return file.read_text()
