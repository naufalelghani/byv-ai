import pytest

from byv_fp import (
    ToolCall, ToolDefinition, ToolRegistry, parse_model_output,
    serialize_tool_calls, validate_response,
)
from byv_fp.errors import ProtocolValidationError
from byv_fp.providers.anthropic import (
    anthropic_tool_result, anthropic_tool_results_message,
    from_content_blocks, to_messages_tools, to_tool_use_blocks,
)
from byv_fp.providers.openai import (
    chat_completions_tool_result, from_chat_completions_tool_calls,
    from_responses_output, responses_function_call_output,
    to_chat_completions_assistant_message, to_chat_completions_tools,
    to_responses_tools, to_responses_function_calls,
)


def make_report(requires_approval=False):
    registry = ToolRegistry([ToolDefinition(
        name="weather.lookup",
        description="Look up weather.",
        input_schema={
            "type": "object",
            "properties": {"city": {"type": "string", "description": "City name."}},
            "required": ["city"],
            "additionalProperties": False,
        },
        requires_approval=requires_approval,
    )])
    parsed = parse_model_output(serialize_tool_calls([
        ToolCall("call_abc", "weather.lookup", {"city": "Martapura"})
    ]))
    return registry, validate_response(parsed, registry)


def test_openai_chat_completions_bridge():
    registry, report = make_report()
    assert to_chat_completions_tools(registry)[0]["function"]["name"] == "weather.lookup"
    native = to_chat_completions_assistant_message(report)
    assert from_chat_completions_tool_calls(native["tool_calls"])[0].arguments == {"city": "Martapura"}
    assert chat_completions_tool_result("call_abc", {"ok": True})["tool_call_id"] == "call_abc"


def test_openai_responses_bridge():
    registry, report = make_report()
    assert to_responses_tools(registry)[0]["name"] == "weather.lookup"
    items = to_responses_function_calls(report)
    assert from_responses_output(items)[0].id == "call_abc"
    assert responses_function_call_output("call_abc", {"ok": True})["call_id"] == "call_abc"


def test_anthropic_messages_bridge():
    registry, report = make_report()
    assert to_messages_tools(registry)[0]["name"] == "weather.lookup"
    blocks = to_tool_use_blocks(report)
    assert from_content_blocks(blocks)[0].arguments == {"city": "Martapura"}
    result = anthropic_tool_result("call_abc", {"ok": True})
    message = anthropic_tool_results_message([result])
    assert message["role"] == "user"
    assert message["content"][0]["tool_use_id"] == "call_abc"


def test_approval_required_call_cannot_be_mapped_to_provider_payloads():
    _, report = make_report(requires_approval=True)
    with pytest.raises(ProtocolValidationError, match="Approval required"):
        to_chat_completions_assistant_message(report)
    with pytest.raises(ProtocolValidationError, match="Approval required"):
        to_responses_function_calls(report)
    with pytest.raises(ProtocolValidationError, match="Approval required"):
        to_tool_use_blocks(report)
