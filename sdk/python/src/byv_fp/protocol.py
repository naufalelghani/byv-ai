"""Strict parser and serializer for BYV Format Protocol."""

from __future__ import annotations

import json
import math
import re
from typing import Any

from .errors import ProtocolParseError
from .types import BYVFPResponse, ToolCall

PROTOCOL_HEADER = "BYV-FP/1.0"
_HEADER_PREFIX = "BYV-FP/"
_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
_TOOL_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.:-]{0,127}$")
MAX_TOOL_CALLS = 32
DEFAULT_MAX_PAYLOAD_BYTES = 1_048_576


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProtocolParseError(f"Duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def _reject_non_json_constant(value: str) -> None:
    raise ProtocolParseError(f"Non-standard JSON constant is not allowed: {value}")


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ProtocolParseError(f"Non-finite JSON number is not allowed: {value}")
    return number


def _loads_strict(payload: str) -> Any:
    try:
        return json.loads(
            payload,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_non_json_constant,
            parse_float=_finite_float,
        )
    except ProtocolParseError:
        raise
    except (json.JSONDecodeError, UnicodeError, ValueError, OverflowError) as exc:
        raise ProtocolParseError(f"Invalid BYV-FP JSON: {exc}") from exc


def parse_model_output(
    text: str,
    *,
    max_payload_bytes: int = DEFAULT_MAX_PAYLOAD_BYTES,
) -> BYVFPResponse:
    """Parse the model's final text channel; malformed declared protocol fails closed."""
    if not isinstance(text, str):
        raise TypeError("model output must be str")

    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith(_HEADER_PREFIX):
        return BYVFPResponse(kind="plain_text", content=text, raw=text)

    first_line, separator, payload = normalized.partition("\n")
    if not separator:
        raise ProtocolParseError("BYV-FP header must be followed by a JSON object")
    if first_line != PROTOCOL_HEADER:
        raise ProtocolParseError(f"Unsupported BYV-FP header: {first_line!r}")

    try:
        payload_size = len(payload.encode("utf-8"))
    except UnicodeEncodeError as exc:
        raise ProtocolParseError("BYV-FP payload is not valid UTF-8 text") from exc
    if max_payload_bytes < 0 or payload_size > max_payload_bytes:
        raise ProtocolParseError(
            f"BYV-FP payload exceeds the {max_payload_bytes}-byte limit"
        )

    envelope = _loads_strict(payload)
    if not isinstance(envelope, dict):
        raise ProtocolParseError("BYV-FP envelope must be a JSON object")

    kind = envelope.get("type")
    if kind == "final":
        if set(envelope) != {"type", "content"}:
            raise ProtocolParseError("A final envelope must contain only type and content")
        if not isinstance(envelope["content"], str):
            raise ProtocolParseError("final.content must be a string")
        return BYVFPResponse(kind="final", content=envelope["content"], raw=text)

    if kind == "tool_calls":
        if set(envelope) != {"type", "calls"}:
            raise ProtocolParseError("A tool_calls envelope must contain only type and calls")
        calls_value = envelope["calls"]
        if not isinstance(calls_value, list) or not calls_value:
            raise ProtocolParseError("tool_calls.calls must be a non-empty array")
        if len(calls_value) > MAX_TOOL_CALLS:
            raise ProtocolParseError(f"At most {MAX_TOOL_CALLS} tool calls are allowed")

        calls: list[ToolCall] = []
        seen_ids: set[str] = set()
        for index, item in enumerate(calls_value):
            if not isinstance(item, dict) or set(item) != {"id", "tool", "arguments"}:
                raise ProtocolParseError(
                    f"calls[{index}] must contain exactly id, tool, and arguments"
                )
            call_id, tool_name, arguments = item["id"], item["tool"], item["arguments"]
            if not isinstance(call_id, str) or not _ID_RE.fullmatch(call_id):
                raise ProtocolParseError(f"calls[{index}].id has an invalid format")
            if call_id in seen_ids:
                raise ProtocolParseError(f"Duplicate tool call id: {call_id}")
            seen_ids.add(call_id)
            if not isinstance(tool_name, str) or not _TOOL_RE.fullmatch(tool_name):
                raise ProtocolParseError(f"calls[{index}].tool has an invalid format")
            if not isinstance(arguments, dict):
                raise ProtocolParseError(f"calls[{index}].arguments must be a JSON object")
            calls.append(ToolCall(id=call_id, tool=tool_name, arguments=arguments))

        return BYVFPResponse(kind="tool_calls", calls=tuple(calls), raw=text)

    raise ProtocolParseError("Envelope type must be 'final' or 'tool_calls'")


def serialize_final(content: str) -> str:
    if not isinstance(content, str):
        raise TypeError("content must be str")
    body = json.dumps(
        {"type": "final", "content": content},
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    )
    return f"{PROTOCOL_HEADER}\n{body}"


def serialize_tool_calls(calls: list[ToolCall] | tuple[ToolCall, ...]) -> str:
    body_calls = [
        {"id": call.id, "tool": call.tool, "arguments": dict(call.arguments)}
        for call in calls
    ]
    body = json.dumps(
        {"type": "tool_calls", "calls": body_calls},
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    )
    return f"{PROTOCOL_HEADER}\n{body}"
