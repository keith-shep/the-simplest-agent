from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, TypedDict

from abstractions.role import RoleName


@dataclass
class SimpleMessage:
    role: RoleName
    content: str


class Property(TypedDict):
    type: Literal["string", "number", "integer", "boolean", "array", "object"]
    description: str


# the name of a handler's parameter, e.g. "path" for read_file(path)
ArgumentName = str


@dataclass
class SimpleTool:
    name: str
    description: str
    properties: dict[ArgumentName, Property]
    required: list[ArgumentName]
    handler: Callable[..., str]


@dataclass
class SimpleToolResult:
    tool_use_id: str
    content: str
    is_error: bool = False
