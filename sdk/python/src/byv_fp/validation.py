"""Fail-closed validation and policy gating for BYV-FP responses."""

from __future__ import annotations

from collections.abc import Iterable

from .errors import ProtocolValidationError
from .registry import ToolRegistry
from .schema import validate_json_schema
from .types import BYVFPResponse, ValidationReport


def validate_response(
    response: BYVFPResponse,
    registry: ToolRegistry,
    *,
    allowed_tools: Iterable[str] | None = None,
    approved_call_ids: Iterable[str] = (),
) -> ValidationReport:
    """Validate tools, arguments, allowlist, and per-call approval state.

    No handler is executed. Unknown, disabled, disallowed, or invalid calls
    reject the entire envelope; calls requiring approval are held separately.
    """
    if response.kind != "tool_calls":
        return ValidationReport(response=response)

    allowed = set(allowed_tools) if allowed_tools is not None else None
    approved_ids = set(approved_call_ids)
    accepted = []
    pending = []

    for call in response.calls:
        definition = registry.get(call.tool)
        if definition is None:
            raise ProtocolValidationError(f"Unknown tool: {call.tool}")
        if not definition.enabled:
            raise ProtocolValidationError(f"Tool is disabled: {call.tool}")
        if allowed is not None and call.tool not in allowed:
            raise ProtocolValidationError(f"Tool is not allowed in this request: {call.tool}")

        errors = validate_json_schema(call.arguments, definition.input_schema)
        if errors:
            raise ProtocolValidationError(
                f"Invalid arguments for {call.tool} ({call.id}): " + "; ".join(errors)
            )

        if definition.requires_approval and call.id not in approved_ids:
            pending.append(call)
        else:
            accepted.append(call)

    return ValidationReport(
        response=response,
        approved_calls=tuple(accepted),
        pending_approval=tuple(pending),
    )
