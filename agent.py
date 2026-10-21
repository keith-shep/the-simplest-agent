# via https://platform.claude.com/docs/en/get-started

import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": "how heavy is the earth?",
        }
    ],
)

for block in message.content:
    if block.type == "text":
        print(block.text)
