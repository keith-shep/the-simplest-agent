import atexit
import os
import select
import subprocess
import sys
import tempfile
from collections.abc import Callable
from datetime import datetime

from pydantic_core import to_jsonable_python
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.table import Table

TtyLog = Callable[..., None]


def _launch(command: str) -> int:
    """Run a shell command in a new Terminal.app window and return the window's id."""
    if sys.platform != "darwin":
        raise RuntimeError("the tty logger only supports macOS")

    script = command.replace("\\", "\\\\").replace('"', '\\"')
    result = subprocess.run(
        [
            "osascript",
            "-e",
            'tell application "Terminal"',
            "-e",
            f'do script "{script}; exit"',
            "-e",
            "id of front window",  # do script opens the new window in front
            "-e",
            "end tell",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return int(result.stdout)


def _close_later(window_id: int) -> None:
    """Close a Terminal.app window once its shell has exited.

    Terminal keeps a window open after its shell exits, so it has to be closed explicitly. Waiting
    until the shell is gone (it checks for us every second) avoids a "terminate processes?" prompt.
    """
    close = f"sleep 2; osascript -e 'tell application \"Terminal\" to close window id {window_id}'"
    subprocess.Popen(
        ["sh", "-c", close],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def open_terminal(title: str, timeout: float = 10) -> str:
    """Open a new terminal, closed again when this process exits, and return its tty path."""
    fifo = os.path.join(tempfile.mkdtemp(), "tty")
    os.mkfifo(fifo)

    # the new terminal tells us its tty through the fifo, then waits for us to exit
    window_id = _launch(
        f"printf '\\033]0;{title}\\007'; clear; tty > {fifo}; "
        f"while kill -0 {os.getpid()} 2>/dev/null; do sleep 1; done"
    )
    atexit.register(_close_later, window_id)

    reader = os.open(fifo, os.O_RDONLY | os.O_NONBLOCK)
    try:
        ready, _, _ = select.select([reader], [], [], timeout)
        if not ready:
            raise RuntimeError(f"the {title} terminal didn't start within {timeout}s")
        return os.read(reader, 1024).decode().strip()
    finally:
        os.close(reader)
        os.remove(fifo)
        os.rmdir(os.path.dirname(fifo))


def _snapshot(value: object) -> object:
    """Copy a value as it is now, so later changes (e.g. to the messages list) don't rewrite history."""
    return to_jsonable_python(
        value, exclude_none=True
    )  # also converts SDK objects nested in dicts and lists


def _side_by_side(data: dict[str, object]) -> Table:
    grid = Table.grid(expand=True, padding=(0, 1))
    panels: list[Panel | str] = []
    for title, value in data.items():
        if (
            panels
        ):  # point each panel at the next, level with the titles: request → response
            grid.add_column()
            panels.append("[bold]→[/bold]")
        json = JSON.from_data(value, default=str)
        json.text.no_wrap = False  # rich's JSON doesn't wrap by default, so long strings overflow the panel
        json.text.overflow = "fold"
        grid.add_column(ratio=1)
        panels.append(Panel(json, title=title))
    grid.add_row(*panels)
    return grid


def tty_logger(tty_path: str | None) -> TtyLog:
    """Log each call's values side by side, one column per keyword."""
    if not tty_path:

        def ignore(**data: object) -> None:
            pass

        return ignore

    file = open(tty_path, "w")  # noqa: SIM115 - kept open for the life of the process
    console = Console(file=file, force_terminal=True)
    entries: list[tuple[dict[str, object], datetime]] = []
    width = 0

    def show(turn: int) -> None:
        data, at = entries[turn - 1]
        if turn > 1:
            console.line(3)
        console.rule(f"[bold]turn {turn}[/bold] · {at:%H:%M:%S}")
        console.print(_side_by_side(data))

    def log(**data: object) -> None:
        nonlocal width
        entries.append(
            ({title: _snapshot(value) for title, value in data.items()}, datetime.now())
        )

        # rich measures the agent's own terminal, so measure the tty we write to
        try:
            new_width = os.get_terminal_size(file.fileno()).columns
        except OSError:  # a plain file, not a terminal
            new_width = console.width

        if new_width == width:
            show(len(entries))
            return

        # the terminal can't reflow what's already printed, so redraw everything at the new width
        width = console.width = new_width
        file.write("\033[H\033[2J\033[3J")  # clear the screen and its scrollback
        for turn in range(1, len(entries) + 1):
            show(turn)

    return log
