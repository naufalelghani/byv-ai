"""Dependency-free JSON Schema validator for the documented BYV-FP subset."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from typing import Any

from .errors import ProtocolValidationError, UnsupportedSchemaError

_SUPPORTED = {
    "type", "properties", "required", "additionalProperties", "items",
    "enum", "const", "minimum", "maximum", "minLength", "maxLength",
    "pattern", "minItems", "maxItems", "minProperties", "maxProperties",
}


def _matches_type(value: Any, expected: str) -> bool:
    checks = {
        "object": lambda v: isinstance(v, dict),
        "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
        "boolean": lambda v: isinstance(v, bool),
        "null": lambda v: v is None,
    }
    if expected not in checks:
        raise UnsupportedSchemaError(f"Unsupported JSON Schema type: {expected!r}")
    return checks[expected](value)


def validate_json_schema(
    value: Any,
    schema: Mapping[str, Any],
    *,
    path: str = "$",
) -> list[str]:
    """Return errors under the supported subset; unsupported keywords fail closed."""
    if not isinstance(schema, Mapping):
        raise ProtocolValidationError(f"{path}: schema must be an object")
    unknown = set(schema) - _SUPPORTED
    if unknown:
        raise UnsupportedSchemaError(
            f"{path}: unsupported schema keyword(s): {', '.join(sorted(unknown))}"
        )

    errors: list[str] = []
    expected = schema.get("type")
    if expected is not None:
        if not isinstance(expected, str):
            raise UnsupportedSchemaError(f"{path}: schema type must be a string")
        if not _matches_type(value, expected):
            return [f"{path}: expected {expected}, got {type(value).__name__}"]

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: value does not match const")
    if "enum" in schema:
        choices = schema["enum"]
        if not isinstance(choices, list):
            raise UnsupportedSchemaError(f"{path}: enum must be an array")
        if value not in choices:
            errors.append(f"{path}: value is not in enum")

    if isinstance(value, dict):
        required = schema.get("required", [])
        if not isinstance(required, list) or not all(isinstance(x, str) for x in required):
            raise UnsupportedSchemaError(f"{path}: required must be an array of strings")
        properties = schema.get("properties", {})
        if not isinstance(properties, Mapping):
            raise UnsupportedSchemaError(f"{path}: properties must be an object")
        additional = schema.get("additionalProperties", True)
        if not isinstance(additional, (bool, Mapping)):
            raise UnsupportedSchemaError(f"{path}: additionalProperties must be boolean or schema")

        for name in required:
            if name not in value:
                errors.append(f"{path}.{name}: required property is missing")
        for name, item in value.items():
            if name in properties:
                errors.extend(validate_json_schema(item, properties[name], path=f"{path}.{name}"))
            elif additional is False:
                errors.append(f"{path}.{name}: additional property is not allowed")
            elif isinstance(additional, Mapping):
                errors.extend(validate_json_schema(item, additional, path=f"{path}.{name}"))

        if len(value) < schema.get("minProperties", 0):
            errors.append(f"{path}: object has fewer than minProperties")
        if "maxProperties" in schema and len(value) > schema["maxProperties"]:
            errors.append(f"{path}: object has more than maxProperties")

    if isinstance(value, list):
        if "items" in schema:
            for index, item in enumerate(value):
                errors.extend(validate_json_schema(item, schema["items"], path=f"{path}[{index}]"))
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: array has fewer than minItems")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: array has more than maxItems")

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: string is shorter than minLength")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{path}: string is longer than maxLength")
        if "pattern" in schema:
            try:
                if re.search(schema["pattern"], value) is None:
                    errors.append(f"{path}: string does not match pattern")
            except (TypeError, re.error) as exc:
                raise UnsupportedSchemaError(f"{path}: invalid pattern: {exc}") from exc

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and not math.isfinite(value):
            errors.append(f"{path}: non-finite numbers are not allowed")
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: number is below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: number is above maximum")

    return errors
