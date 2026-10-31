"""Host-owned tool registry. Registration never executes tools."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping

from .errors import ProtocolValidationError
from .types import ToolDefinition

_TOOL_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.:-]{0,127}$")


class ToolRegistry:
    """An allowlist of trusted tool contracts available to a BYV-FP session."""

    def __init__(self, tools: Iterable[ToolDefinition] = ()) -> None:
        self._tools: dict[str, ToolDefinition] = {}
        for tool in tools:
            self.register(tool)

    def register(self, tool: ToolDefinition) -> None:
        if not isinstance(tool.name, str) or not _TOOL_NAME_RE.fullmatch(tool.name):
            raise ProtocolValidationError("Tool name has an invalid format")
        if not isinstance(tool.description, str):
            raise ProtocolValidationError(f"Tool {tool.name!r} description must be a string")
        if tool.name in self._tools:
            raise ProtocolValidationError(f"Tool already registered: {tool.name}")
        if not isinstance(tool.input_schema, Mapping):
            raise ProtocolValidationError(f"Tool {tool.name!r} input_schema must be an object")
        if tool.input_schema.get("type") != "object":
            raise ProtocolValidationError(
                f"Tool {tool.name!r} input_schema root must have type='object'"
            )
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition | None:
        return self._tools.get(name)

    def require(self, name: str) -> ToolDefinition:
        tool = self.get(name)
        if tool is None:
            raise ProtocolValidationError(f"Unknown tool: {name}")
        return tool

    def __iter__(self):
        return iter(self._tools.values())

    def __len__(self) -> int:
        return len(self._tools)
