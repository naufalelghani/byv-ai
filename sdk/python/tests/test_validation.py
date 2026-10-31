import pytest

from byv_fp import (
    ToolCall, ToolDefinition, ToolRegistry, parse_model_output,
    serialize_tool_calls, validate_response,
)
from byv_fp.errors import ProtocolValidationError


SCHEMA = {
    "type": "object",
    "properties": {
        "city": {"type": "string", "minLength": 1},
        "days": {"type": "integer", "minimum": 1, "maximum": 7},
    },
    "required": ["city"],
    "additionalProperties": False,
}


def make_registry(requires_approval=False):
    return ToolRegistry([ToolDefinition(
        name="weather.lookup",
        description="Look up weather.",
        input_schema=SCHEMA,
        requires_approval=requires_approval,
    )])


def test_validation_accepts_valid_arguments():
    parsed = parse_model_output(serialize_tool_calls([
        ToolCall("call_1", "weather.lookup", {"city": "Banjarbaru", "days": 2})
    ]))
    report = validate_response(parsed, make_registry())
    assert len(report.approved_calls) == 1


def test_validation_rejects_unknown_tool():
    parsed = parse_model_output(serialize_tool_calls([
        ToolCall("call_1", "shell.run", {"command": "whoami"})
    ]))
    with pytest.raises(ProtocolValidationError, match="Unknown tool"):
        validate_response(parsed, make_registry())


def test_validation_rejects_extra_argument():
    parsed = parse_model_output(serialize_tool_calls([
        ToolCall("call_1", "weather.lookup", {"city": "X", "admin": True})
    ]))
    with pytest.raises(ProtocolValidationError, match="additional property"):
        validate_response(parsed, make_registry())


def test_approval_is_per_call():
    parsed = parse_model_output(serialize_tool_calls([
        ToolCall("call_1", "weather.lookup", {"city": "X"})
    ]))
    report = validate_response(parsed, make_registry(requires_approval=True))
    assert not report.approved_calls
    assert len(report.pending_approval) == 1
    approved = validate_response(
        parsed, make_registry(requires_approval=True), approved_call_ids={"call_1"}
    )
    assert len(approved.approved_calls) == 1
