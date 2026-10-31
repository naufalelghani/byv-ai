"""Typed, provider-neutral BYV-FP data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class ToolCall:
    """One tool request emitted inside a BYV-FP envelope."""

    id: str
    tool: str
    arguments: Mapping[str, Any]


@dataclass(frozen=True)
class BYVFPResponse:
    """Parsed model response. One final body or a collection of tool calls."""

    kind: str
    content: str | None = None
    calls: tuple[ToolCall, ...] = ()
    raw: str = field(default="", repr=False)

    @property
    def is_final(self) -> bool:
        return self.kind in {"final", "plain_text"}

    @property
    def has_tool_calls(self) -> bool:
        return self.kind == "tool_calls"


@dataclass(frozen=True)
class ToolDefinition:
    """Trusted tool contract owned by the host application.

    This SDK does not execute a registered tool.
    """

    name: str
    description: str
    input_schema: Mapping[str, Any]
    enabled: bool = True
    requires_approval: bool = False


@dataclass(frozen=True)
class ValidationReport:
    """Validated calls split by policy approval state."""

    response: BYVFPResponse
    approved_calls: tuple[ToolCall, ...] = ()
    pending_approval: tuple[ToolCall, ...] = ()
