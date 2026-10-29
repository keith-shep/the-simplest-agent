import subprocess
from datetime import UTC, datetime

from abstractions.types import SimpleTool

# the repo container from docker-compose.yml; your repo is mounted at /app/repo inside it.
# every tool below runs in there, so the container is the boundary: no path checks needed,
# and the harness code and API key aren't in it to be read or edited
REPO = "repo"


def in_repo(*command: str, stdin: str | None = None, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    """Run a command inside the repo container, from /app/repo."""
    docker = ["docker", "exec", "-i", "-w", "/app/repo", REPO, *command]
    return subprocess.run(
        docker, input=stdin, capture_output=True, text=True, timeout=timeout, check=False
    )  # check=False: each tool decides whether a non-zero exit is an error


def checked(result: subprocess.CompletedProcess[str]) -> str:
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout


def get_current_time() -> str:
    now = datetime.now(UTC)
    return now.isoformat()


def read_file(path: str) -> str:
    return checked(in_repo("cat", "--", path))


def list_files(path: str) -> str:
    # -A: include dotfiles but not . and .., -p: folders end with /
    return checked(in_repo("ls", "-Ap", "--", path)).strip() or "(empty folder)"


SKIP = [".venv", ".git", "__pycache__", "node_modules"]  # thousands of files that are never the answer


def search(pattern: str, path: str) -> str:
    excludes = [f"--exclude-dir={folder}" for folder in SKIP]
    result = in_repo("grep", "-rnIE", *excludes, "--", pattern, path)
    if result.returncode == 1:  # grep's way of saying it ran fine and found nothing
        return "no matches"
    return checked(result).strip()


def write_file(path: str, content: str) -> str:
    # path is passed as $1, not pasted into the script, so a weird file name can't run as code
    checked(in_repo("sh", "-c", 'mkdir -p "$(dirname "$1")" && cat > "$1"', "sh", path, stdin=content))
    return f"wrote {len(content.splitlines())} lines to {path}"


def edit_file(path: str, old_text: str, new_text: str) -> str:
    content = read_file(path)
    count = content.count(old_text)
    # exactly one match, so the edit can't land in the wrong place
    if count == 0:
        raise ValueError(f"old_text not found in {path}")
    if count > 1:
        raise ValueError(f"old_text appears {count} times in {path}; include more surrounding text")
    write_file(path, content.replace(old_text, new_text))
    return f"edited {path}"


def run_command(command: str) -> str:
    # a person still approves every command: the sandbox limits the damage, it doesn't judge intent
    answer = input(f"⚠️  run `{command}`? [y/N] ")
    if answer.strip().lower() != "y":
        raise PermissionError("the user declined to run this command")
    # longer timeout than the file tools: installs like apt-get or npm take a while
    result = in_repo("sh", "-c", command, timeout=300)
    # a failing command is a result for Claude to read, not an error
    return f"exit code {result.returncode}\n{result.stdout}{result.stderr}"


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
        description="read the content of a file in the repo",
        properties={
            "path": {"type": "string", "description": "the path to a file to read, relative to the repo"},
        },
        required=["path"],
        handler=read_file,
    ),
    SimpleTool(
        name="list_files",
        description="list the files and folders in a repo directory; folders end with /",
        properties={
            "path": {"type": "string", "description": "the directory to list, relative to the repo, e.g. ."},
        },
        required=["path"],
        handler=list_files,
    ),
    SimpleTool(
        name="search",
        description="search file contents under a repo directory; returns matching lines as file:line: text",
        properties={
            "pattern": {
                "type": "string",
                "description": "a regular expression, e.g. def run_tools",
            },
            "path": {
                "type": "string",
                "description": "the directory to search, relative to the repo, e.g. .",
            },
        },
        required=["pattern", "path"],
        handler=search,
    ),
    SimpleTool(
        name="write_file",
        description="write content to a file in the repo, creating it or replacing everything already in it",
        properties={
            "path": {"type": "string", "description": "the path to the file to write, relative to the repo"},
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
            "replace one exact piece of text in a repo file; old_text must appear exactly once, "
            "so include enough surrounding lines to make it unique. Prefer this to write_file for changes"
        ),
        properties={
            "path": {"type": "string", "description": "the path to the file to edit, relative to the repo"},
            "old_text": {"type": "string", "description": "the exact text to replace, including whitespace"},
            "new_text": {"type": "string", "description": "the text to put in its place"},
        },
        required=["path", "old_text", "new_text"],
        handler=edit_file,
    ),
    SimpleTool(
        name="run_command",
        description=(
            "run a shell command in the sandboxed Linux container (python:3.13-slim) "
            "from the repo (/app/repo), after the user approves it; returns the exit code and output"
        ),
        properties={
            "command": {"type": "string", "description": "the shell command to run, e.g. ls -la"},
        },
        required=["command"],
        handler=run_command,
    ),
]
