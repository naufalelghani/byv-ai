import pytest

from byv_fp import ToolCall, parse_model_output, serialize_final, serialize_tool_calls
from byv_fp.errors import ProtocolParseError


def test_plain_text_is_preserved():
    result = parse_model_output("Hello, world.\n")
    assert result.kind == "plain_text"
    assert result.content == "Hello, world.\n"


def test_final_round_trip():
    parsed = parse_model_output(serialize_final("Halo, dunia 🌏"))
    assert parsed.kind == "final"
    assert parsed.content == "Halo, dunia 🌏"


def test_tool_call_round_trip_preserves_json_types():
    wire = serialize_tool_calls([
        ToolCall("call_001", "weather.lookup", {"city": "Martapura", "days": 2, "units": ["C"]})
    ])
    parsed = parse_model_output(wire)
    assert parsed.calls[0].arguments == {"city": "Martapura", "days": 2, "units": ["C"]}


def test_multiple_calls_are_preserved_in_order():
    wire = serialize_tool_calls([
        ToolCall("call_001", "weather.lookup", {"city": "Martapura"}),
        ToolCall("call_002", "weather.lookup", {"city": "Banjarbaru"}),
    ])
    parsed = parse_model_output(wire)
    assert [call.id for call in parsed.calls] == ["call_001", "call_002"]


@pytest.mark.parametrize("wire", [
    "BYV-FP/1.0",
    'BYV-FP/1.0\n{"type":"final","content":"ok","extra":1}',
    'BYV-FP/1.0\n{"type":"final","content":"a","content":"b"}',
    'BYV-FP/1.0\n{"type":"tool_calls","calls":[]}',
    'BYV-FP/2.0\n{"type":"final","content":"ok"}',
    'BYV-FP/1.0\n{"type":"tool_calls","calls":[{"id":"x","tool":"x","arguments":[] }]}',
    'BYV-FP/1.0\n{"type":"final","content":NaN}',
    'BYV-FP/1.0\n{"type":"final","content":"overflow","x":1e999}',
    'BYV-FP/1.0\n{"type":"tool_calls","calls":[{"id":"c1","tool":"x","arguments":{}},{"id":"c1","tool":"x","arguments":{}}]}',
])
def test_malformed_protocol_fails_closed(wire):
    with pytest.raises(ProtocolParseError):
        parse_model_output(wire)
