# via https://platform.claude.com/docs/en/get-started

import argparse
from pathlib import Path

import anthropic
from anthropic.types import Message
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from rich.console import Console

client = anthropic.Anthropic()
from anthropic.types import MessageParam

from abstractions.anthropic_model import AnthropicModel
from abstractions.role import Role
from logger import open_terminal, tty_logger

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
                    "name": "get_current_time",
                    "description": "get current time in users timezone",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "timezone": {
                                "type": "string",
                                "description": "timezone that user requested for",
                            },
                        },
                        "required": ["timezone"],
                    },
                }
            ],
            "system": SYSTEM_PROMPT,
            "messages": messages,
        }
        try:
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
