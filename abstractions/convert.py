from anthropic.types import MessageParam, ToolParam, ToolResultBlockParam

from abstractions.types import SimpleMessage, SimpleTool, SimpleToolResult


def messages(msgs: list[SimpleMessage]) -> list[MessageParam]:
    return [{"role": m.role, "content": m.content} for m in msgs]


def tools(simple_tools: list[SimpleTool]) -> list[ToolParam]:
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "input_schema": {
                "type": "object",
                "properties": tool.properties,
                "required": tool.required,
            },
        }
        for tool in simple_tools
    ]


def tool_result(result: SimpleToolResult) -> ToolResultBlockParam:
    return {
        "type": "tool_result",
        "tool_use_id": result.tool_use_id,
        "content": result.content,
        "is_error": result.is_error,
    }
