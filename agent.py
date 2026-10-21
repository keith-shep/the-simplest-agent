# via https://platform.claude.com/docs/en/get-started

import anthropic
from anthropic.types import Message
from rich.console import Console

client = anthropic.Anthropic()
from abstractions import convert
from abstractions.anthropic_model import AnthropicModel
from abstractions.role import Role
from abstractions.types import SimpleMessage


def get_text(message: Message) -> str:
    return "".join(block.text for block in message.content if block.type == "text")


console = Console()
user_input = console.input(f"😃 {Role.USER}: ")

assistant_output = client.messages.create(
    model=AnthropicModel.HAIKU,
    max_tokens=1000,
    messages=convert.messages(
        [SimpleMessage(role=Role.USER, content=user_input)]
    ),
)

print(f"🤖 {Role.ASSISTANT}: {get_text(assistant_output)}")


user_input = console.input(f"😃 {Role.USER}: ")

assistant_output = client.messages.create(
    model=AnthropicModel.HAIKU,
    max_tokens=1000,
    messages=convert.messages(
        [SimpleMessage(role=Role.USER, content=user_input)]
    ),
)

print(f"🤖 {Role.ASSISTANT}: {get_text(assistant_output)}")
