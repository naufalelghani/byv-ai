"""Exceptions raised by the BYV-FP SDK."""


class BYVFPError(Exception):
    """Base class for SDK errors."""


class ProtocolParseError(BYVFPError):
    """The model output declares BYV-FP but is not a valid envelope."""


class ProtocolValidationError(BYVFPError):
    """A BYV-FP envelope or tool invocation failed validation."""


class UnsupportedSchemaError(ProtocolValidationError):
    """A tool schema uses a keyword not supported by the built-in validator."""


class ProviderAdapterError(BYVFPError):
    """A provider-native payload could not be parsed or generated."""
