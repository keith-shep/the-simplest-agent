import re
from datetime import UTC, datetime
from pathlib import Path

from abstractions.types import SimpleTool


def get_current_time() -> str:
    now = datetime.now(UTC)
    return now.isoformat()


def read_file(path: str) -> str:
    file = Path(path)
    if (
        file.name == ".env"
    ):  # holds the API key, which would otherwise end up in the conversation
        raise PermissionError(".env is off limits")
    return file.read_text()


def list_files(path: str) -> str:
    folder = Path(path)
    names = [
        f"{entry.name}/" if entry.is_dir() else entry.name for entry in folder.iterdir()
    ]
    return "\n".join(sorted(names))


SKIP = {".venv", ".git", "__pycache__"}  # thousands of files that are never the answer


def search(pattern: str, path: str) -> str:
    matches: list[str] = []
    for file in sorted(Path(path).rglob("*")):
        if not file.is_file() or SKIP & set(file.parts) or file.name == ".env":
            continue
        for number, line in enumerate(file.read_text(errors="ignore").splitlines(), 1):
            if re.search(pattern, line):
                matches.append(f"{file}:{number}: {line.strip()}")
    return "\n".join(matches) or "no matches"


def write_file(path: str, content: str) -> str:
    file = Path(path)
    if file.name == ".env":  # overwriting it would lose the API key
        raise PermissionError(".env is off limits")
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(content)
    return f"wrote {len(content.splitlines())} lines to {path}"


def edit_file(path: str, old_text: str, new_text: str) -> str:
    file = Path(path)
    if file.name == ".env":  # overwriting it would lose the API key
        raise PermissionError(".env is off limits")
    content = file.read_text()
    count = content.count(old_text)
    # exactly one match, so the edit can't land in the wrong place
    if count == 0:
        raise ValueError(f"old_text not found in {path}")
    if count > 1:
        raise ValueError(f"old_text appears {count} times in {path}; include more surrounding text")
    file.write_text(content.replace(old_text, new_text))
    return f"edited {path}"


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
    SimpleTool(
        name="list_files",
        description="list the files and folders in a directory; folders end with /",
        properties={
            "path": {"type": "string", "description": "the directory to list, e.g. ."},
        },
        required=["path"],
        handler=list_files,
    ),
    SimpleTool(
        name="search",
        description="search file contents under a directory; returns matching lines as file:line: text",
        properties={
            "pattern": {
                "type": "string",
                "description": "a regular expression, e.g. def run_tools",
            },
            "path": {
                "type": "string",
                "description": "the directory to search, e.g. .",
            },
        },
        required=["pattern", "path"],
        handler=search,
    ),
    SimpleTool(
        name="write_file",
        description="write content to a file, creating it or replacing everything already in it",
        properties={
            "path": {"type": "string", "description": "the path to the file to write"},
            "content": {
                "type": "string",
                "description": "the complete new content of the file",
            },
        },
        required=["path", "content"],
        handler=write_file,
    ),
    SimpleTool(
        name="edit_file",
        description=(
            "replace one exact piece of text in a file; old_text must appear exactly once, "
            "so include enough surrounding lines to make it unique. Prefer this to write_file for changes"
        ),
        properties={
            "path": {"type": "string", "description": "the path to the file to edit"},
            "old_text": {"type": "string", "description": "the exact text to replace, including whitespace"},
            "new_text": {"type": "string", "description": "the text to put in its place"},
        },
        required=["path", "old_text", "new_text"],
        handler=edit_file,
    ),
]
