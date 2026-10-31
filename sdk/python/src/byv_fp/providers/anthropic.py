"""Anthropic Messages API bridge for tool_use and tool_result blocks."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from ..errors import ProviderAdapterError, ProtocolValidationError
from ..registry import ToolRegistry
from ..types import ToolCall, ValidationReport


def _assert_approvals_cleared(report: ValidationReport) -> None:
    if report.pending_approval:
        ids = ", ".join(call.id for call in report.pending_approval)
        raise ProtocolValidationError(f"Approval required before mapping tool uses: {ids}")


def to_messages_tools(
    registry: ToolRegistry, *, allowed_tools: set[str] | None = None
) -> list[dict[str, Any]]:
    """Convert trusted tool definitions to Anthropic Messages API tools."""
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "input_schema": dict(tool.input_schema),
        }
        for tool in registry
        if tool.enabled and (allowed_tools is None or tool.name in allowed_tools)
    ]


def to_tool_use_blocks(report: ValidationReport) -> list[dict[str, Any]]:
    """Map approved BYV-FP requests to Anthropic assistant tool_use blocks."""
    _assert_approvals_cleared(report)
    return [
        {
            "type": "tool_use",
            "id": call.id,
            "name": call.tool,
            "input": dict(call.arguments),
        }
        for call in report.approved_calls
    ]


def anthropic_tool_result(
    call_id: str, result: Any, *, is_error: bool = False
) -> dict[str, Any]:
    content = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, default=str)
    return {
        "type": "tool_result",
        "tool_use_id": call_id,
        "content": content,
        "is_error": is_error,
    }


def anthropic_tool_results_message(results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Wrap tool_result blocks in the user message expected by the Messages API."""
    if not results or any(item.get("type") != "tool_result" for item in results):
        raise ProviderAdapterError("results must be a non-empty sequence of tool_result blocks")
    return {"role": "user", "content": [dict(item) for item in results]}


def from_content_blocks(content_blocks: Sequence[Mapping[str, Any]]) -> tuple[ToolCall, ...]:
    """Normalize Anthropic tool_use blocks to provider-neutral calls."""
    calls = []
    for index, block in enumerate(content_blocks):
        if block.get("type") != "tool_use":
            continue
        try:
            call_input = block["input"]
            if not isinstance(call_input, dict):
                raise ProviderAdapterError(f"tool_use input at index {index} must be an object")
            calls.append(ToolCall(
                id=str(block["id"]),
                tool=str(block["name"]),
                arguments=call_input,
            ))
        except (KeyError, TypeError) as exc:
            raise ProviderAdapterError(f"Malformed Anthropic tool_use block at index {index}") from exc
    return tuple(calls)
