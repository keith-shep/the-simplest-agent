# via https://platform.claude.com/docs/en/get-started

import argparse
from pathlib import Path
from typing import Any, cast

import anthropic
from anthropic.types import Message, ToolUseBlock
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from rich.console import Console

client = anthropic.Anthropic()
from anthropic.types import MessageParam, ToolResultBlockParam

from abstractions import convert
from abstractions.anthropic_model import AnthropicModel
from abstractions.role import Role
from abstractions.stop_reason import StopReason
from abstractions.types import SimpleToolResult
from logger import open_terminal, tty_logger
from tools import get_current_time

handlers = {"get_current_time": get_current_time}

parser = argparse.ArgumentParser()
parser.add_argument(
    "--debug",
    action="store_true",
    help="open a terminal showing each request and response",
)
args = parser.parse_args()
log = tty_logger(open_terminal("debug") if args.debug else None)


def get_text(message: Message) -> str:
    return "".join(block.text for block in message.content if block.type == "text")


def get_tool_uses(message: Message) -> list[ToolUseBlock]:
    return [block for block in message.content if block.type == "tool_use"]


def run_tools(message: Message) -> list[ToolResultBlockParam]:
    tool_results: list[ToolResultBlockParam] = []
    for block in get_tool_uses(message):
        tool_input = cast(dict[str, Any], block.input)
        result = handlers[block.name](**tool_input)
        print(f"🔧 {block.name}({tool_input}) → {result}")
        tool_results.append(
            convert.tool_result(
                SimpleToolResult(tool_use_id=block.id, content=result)
            )
        )
    return tool_results


SYSTEM_PROMPT = (Path(__file__).parent / "system_prompt.md").read_text().strip()

console = Console()

try:
    messages: list[MessageParam] = []
    while True:
        user_input = console.input(f"😃 {Role.USER}: ")

        messages.append(MessageParam(role=Role.USER, content=user_input))
        request: MessageCreateParamsNonStreaming = {
            "model": AnthropicModel.HAIKU,
            "max_tokens": 1000,
            "tools": [
                {
                    "name": "get_current_time",  # needs to be the tool name get_current_time()
                    "description": "get the current time in UTC",
                    "input_schema": {
                        "type": "object",
                        "properties": {},
                    },
                }
            ],
            "system": SYSTEM_PROMPT,
            "messages": messages,
        }
        try:
            response = client.messages.create(**request)
            log(request=request, response=response)

            while response.stop_reason == StopReason.TOOL_USE:
                messages.append(
                    MessageParam(role=Role.ASSISTANT, content=response.content)
                )
                messages.append(
                    MessageParam(role=Role.USER, content=run_tools(response))
                )

                response = client.messages.create(**request)
                log(request=request, response=response)

            assistant_output = get_text(response)
            print(f"🤖 {Role.ASSISTANT}: {assistant_output}")
            messages.append(MessageParam(role=Role.ASSISTANT, content=assistant_output))
        except anthropic.APIError as error:
            log(request=request, error=str(error))
            print(error)
except (KeyboardInterrupt, EOFError):
    print("\ngoodbye!")
