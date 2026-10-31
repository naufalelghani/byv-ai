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
_ANNOTATIONS = {
    "title", "description", "default", "examples", "deprecated",
    "readOnly", "writeOnly", "$schema", "$id",
}
_TYPES = {"object", "array", "string", "integer", "number", "boolean", "null"}
_INTEGER_LIMITS = {"minLength", "maxLength", "minItems", "maxItems", "minProperties", "maxProperties"}
_NUMBER_LIMITS = {"minimum", "maximum"}


def validate_schema_definition(schema: Mapping[str, Any], *, path: str = "$") -> None:
    """Validate schema syntax before accepting it into the trusted registry."""
    if not isinstance(schema, Mapping):
        raise ProtocolValidationError(f"{path}: schema must be an object")
    unknown = set(schema) - _SUPPORTED - _ANNOTATIONS
    if unknown:
        raise UnsupportedSchemaError(
            f"{path}: unsupported schema keyword(s): {', '.join(sorted(unknown))}"
        )

    expected = schema.get("type")
    if expected is not None and expected not in _TYPES:
        raise UnsupportedSchemaError(f"{path}: unsupported JSON Schema type: {expected!r}")

    required = schema.get("required", [])
    if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
        raise UnsupportedSchemaError(f"{path}: required must be an array of strings")
    if len(set(required)) != len(required):
        raise UnsupportedSchemaError(f"{path}: required contains duplicate names")

    properties = schema.get("properties", {})
    if not isinstance(properties, Mapping):
        raise UnsupportedSchemaError(f"{path}: properties must be an object")
    for name, child_schema in properties.items():
        if not isinstance(name, str):
            raise UnsupportedSchemaError(f"{path}: property names must be strings")
        validate_schema_definition(child_schema, path=f"{path}.{name}")

    additional = schema.get("additionalProperties", True)
    if not isinstance(additional, (bool, Mapping)):
        raise UnsupportedSchemaError(f"{path}: additionalProperties must be boolean or schema")
    if isinstance(additional, Mapping):
        validate_schema_definition(additional, path=f"{path}.*")

    if "items" in schema:
        validate_schema_definition(schema["items"], path=f"{path}[]")

    if "enum" in schema and not isinstance(schema["enum"], list):
        raise UnsupportedSchemaError(f"{path}: enum must be an array")
    if "pattern" in schema:
        if not isinstance(schema["pattern"], str):
            raise UnsupportedSchemaError(f"{path}: pattern must be a string")
        try:
            re.compile(schema["pattern"])
        except re.error as exc:
            raise UnsupportedSchemaError(f"{path}: invalid pattern: {exc}") from exc

    for key in _INTEGER_LIMITS:
        if key in schema:
            value = schema[key]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise UnsupportedSchemaError(f"{path}: {key} must be a non-negative integer")

    for key in _NUMBER_LIMITS:
        if key in schema:
            value = schema[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise UnsupportedSchemaError(f"{path}: {key} must be a number")
            if isinstance(value, float) and not math.isfinite(value):
                raise UnsupportedSchemaError(f"{path}: {key} must be finite")

    for lower, upper in (
        ("minimum", "maximum"),
        ("minLength", "maxLength"),
        ("minItems", "maxItems"),
        ("minProperties", "maxProperties"),
    ):
        if lower in schema and upper in schema and schema[lower] > schema[upper]:
            raise UnsupportedSchemaError(f"{path}: {lower} cannot exceed {upper}")


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
    return checks[expected](value)


def validate_json_schema(
    value: Any,
    schema: Mapping[str, Any],
    *,
    path: str = "$",
) -> list[str]:
    """Return errors under the supported subset; unsupported keywords fail closed."""
    validate_schema_definition(schema, path=path)

    errors: list[str] = []
    expected = schema.get("type")
    if expected is not None and not _matches_type(value, expected):
        return [f"{path}: expected {expected}, got {type(value).__name__}"]

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: value does not match const")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value is not in enum")

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        additional = schema.get("additionalProperties", True)

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
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            errors.append(f"{path}: string does not match pattern")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and not math.isfinite(value):
            errors.append(f"{path}: non-finite numbers are not allowed")
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: number is below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: number is above maximum")

    return errors
