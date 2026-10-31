"""OpenAI Chat Completions and Responses API bridges.

These helpers map payloads only. The host owns network calls, approvals,
conversation state, and all tool execution.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from ..errors import ProviderAdapterError, ProtocolValidationError
from ..registry import ToolRegistry
from ..types import ToolCall, ValidationReport


def _json_arguments(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ProviderAdapterError(f"Invalid OpenAI tool arguments JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ProviderAdapterError("OpenAI tool arguments must decode to an object")
    return value


def _assert_approvals_cleared(report: ValidationReport) -> None:
    if report.pending_approval:
        ids = ", ".join(call.id for call in report.pending_approval)
        raise ProtocolValidationError(f"Approval required before mapping calls: {ids}")


def to_chat_completions_tools(
    registry: ToolRegistry, *, allowed_tools: set[str] | None = None
) -> list[dict[str, Any]]:
    """Convert the registry to OpenAI Chat Completions tool definitions."""
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": dict(tool.input_schema),
            },
        }
        for tool in registry
        if tool.enabled and (allowed_tools is None or tool.name in allowed_tools)
    ]


def to_responses_tools(
    registry: ToolRegistry, *, allowed_tools: set[str] | None = None
) -> list[dict[str, Any]]:
    """Convert the registry to OpenAI Responses API tool definitions."""
    return [
        {
            "type": "function",
            "name": tool.name,
            "description": tool.description,
            "parameters": dict(tool.input_schema),
        }
        for tool in registry
        if tool.enabled and (allowed_tools is None or tool.name in allowed_tools)
    ]


def to_chat_completions_tool_calls(report: ValidationReport) -> list[dict[str, Any]]:
    _assert_approvals_cleared(report)
    return [
        {
            "id": call.id,
            "type": "function",
            "function": {
                "name": call.tool,
                "arguments": json.dumps(
                    dict(call.arguments), ensure_ascii=False, separators=(",", ":")
                ),
            },
        }
        for call in report.approved_calls
    ]


def to_chat_completions_assistant_message(report: ValidationReport) -> dict[str, Any]:
    calls = to_chat_completions_tool_calls(report)
    if not calls:
        raise ProtocolValidationError("No approved tool calls to map")
    return {"role": "assistant", "content": None, "tool_calls": calls}


def to_responses_function_calls(report: ValidationReport) -> list[dict[str, Any]]:
    """Map to Responses API function_call input items."""
    _assert_approvals_cleared(report)
    return [
        {
            "type": "function_call",
            "call_id": call.id,
            "name": call.tool,
            "arguments": json.dumps(
                dict(call.arguments), ensure_ascii=False, separators=(",", ":")
            ),
        }
        for call in report.approved_calls
    ]


def chat_completions_tool_result(call_id: str, result: Any, *, is_error: bool = False) -> dict[str, Any]:
    content = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, default=str)
    if is_error:
        content = f"Tool execution error: {content}"
    return {"role": "tool", "tool_call_id": call_id, "content": content}


def responses_function_call_output(call_id: str, result: Any, *, is_error: bool = False) -> dict[str, Any]:
    output = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, default=str)
    if is_error:
        output = f"Tool execution error: {output}"
    return {"type": "function_call_output", "call_id": call_id, "output": output}


def from_chat_completions_tool_calls(
    tool_calls: Sequence[Mapping[str, Any]],
) -> tuple[ToolCall, ...]:
    """Normalize OpenAI Chat Completions native calls to provider-neutral calls."""
    calls = []
    for index, item in enumerate(tool_calls):
        try:
            function = item["function"]
            calls.append(ToolCall(
                id=str(item["id"]),
                tool=str(function["name"]),
                arguments=_json_arguments(function["arguments"]),
            ))
        except (KeyError, TypeError) as exc:
            raise ProviderAdapterError(f"Malformed Chat Completions tool call at index {index}") from exc
    return tuple(calls)


def from_responses_output(
    output_items: Sequence[Mapping[str, Any]],
) -> tuple[ToolCall, ...]:
    """Normalize Responses API function_call output items."""
    calls = []
    for index, item in enumerate(output_items):
        if item.get("type") != "function_call":
            continue
        try:
            calls.append(ToolCall(
                id=str(item["call_id"]),
                tool=str(item["name"]),
                arguments=_json_arguments(item["arguments"]),
            ))
        except (KeyError, TypeError) as exc:
            raise ProviderAdapterError(f"Malformed Responses function call at index {index}") from exc
    return tuple(calls)
