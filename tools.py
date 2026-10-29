from datetime import UTC, datetime
from pathlib import Path

from abstractions.types import SimpleTool


def get_current_time() -> str:
    now = datetime.now(UTC)
    return now.isoformat()


def read_file(path: str) -> str:
    file = Path(path)
    return file.read_text()


TOOLS = [
    SimpleTool(
        name="get_current_time",
        description="get the current time in UTC",
        properties={},
        required=[],
        handler=get_current_time,
    ),
    SimpleTool(
        name="read_file",
        description="read the content of a file on a machine",
        properties={
            "path": {"type": "string", "description": "the path to a file to read"},
        },
        required=["path"],
        handler=read_file,
    ),
]
