# via https://platform.claude.com/docs/en/get-started

import argparse

import anthropic
from anthropic.types import Message
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from rich.console import Console

client = anthropic.Anthropic()
from abstractions import convert
from abstractions.anthropic_model import AnthropicModel
from abstractions.role import Role
from abstractions.types import SimpleMessage
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


console = Console()

try:
    while True:
        user_input = console.input(f"😃 {Role.USER}: ")

        request: MessageCreateParamsNonStreaming = {
            "model": AnthropicModel.HAIKU,
            "max_tokens": 1000,
            "messages": convert.messages(
                [SimpleMessage(role=Role.USER, content=user_input)]
            ),
        }
        try:
            assistant_output = client.messages.create(**request)
            log(request=request, response=assistant_output)
            print(f"🤖 {Role.ASSISTANT}: {get_text(assistant_output)}")
        except anthropic.APIError as error:
            log(request=request, error=str(error))
            print(error)
except (KeyboardInterrupt, EOFError):
    print("\ngoodbye!")
