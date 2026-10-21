# via https://platform.claude.com/docs/en/get-started

import anthropic

client = anthropic.Anthropic()
from abstractions import convert
from abstractions.anthropic_model import AnthropicModel
from abstractions.role import Role
from abstractions.types import SimpleMessage

message = client.messages.create(
    model=AnthropicModel.HAIKU,
    max_tokens=1000,
    messages=convert.messages(
        [SimpleMessage(role=Role.USER, content="how is the earth?")]
    ),
)

for block in message.content:
    if block.type == "text":
        print(block.text)
