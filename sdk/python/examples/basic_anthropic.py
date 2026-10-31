"""Illustrative Anthropic Messages API mapping; no network calls are made."""

from byv_fp import ToolDefinition, ToolRegistry, parse_model_output, validate_response
from byv_fp.providers.anthropic import (
    anthropic_tool_result,
    anthropic_tool_results_message,
    to_messages_tools,
    to_tool_use_blocks,
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

print("Tool definitions:", to_messages_tools(registry))
print("Assistant content blocks:", to_tool_use_blocks(report))
result = anthropic_tool_result("call_01", {"temp_c": 30})
print("Tool result message:", anthropic_tool_results_message([result]))
