"""Illustrative OpenAI Chat Completions mapping; no network calls are made."""

from byv_fp import ToolDefinition, ToolRegistry, parse_model_output, validate_response
from byv_fp.providers.openai import (
    chat_completions_tool_result,
    to_chat_completions_assistant_message,
    to_chat_completions_tools,
)

registry = ToolRegistry([
    ToolDefinition(
        name="weather.lookup",
        description="Look up current weather for a city.",
        input_schema={
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
            "additionalProperties": False,
        },
    )
])

model_text = (
    'BYV-FP/1.0\n'
    '{"type":"tool_calls","calls":[{"id":"call_01","tool":"weather.lookup",'
    '"arguments":{"city":"Martapura"}}]}'
)
parsed = parse_model_output(model_text)
report = validate_response(parsed, registry, allowed_tools={"weather.lookup"})

print("Tool definitions:", to_chat_completions_tools(registry))
print("Assistant message:", to_chat_completions_assistant_message(report))
print("Tool result:", chat_completions_tool_result("call_01", {"temp_c": 30}))
