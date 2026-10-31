# BYV Format Protocol (BYV-FP) v1.0

**Status:** Draft reference specification for the BYV-FP SDK v0.1.

BYV-FP is a provider-neutral, text-serialized protocol. A model emits either
ordinary text or one strict JSON envelope. A host-side SDK parses and validates
the envelope, applies policy, and optionally converts approved calls into a
provider-native tool-call representation.

## 1. Wire framing

The protocol header is exactly:

```text
BYV-FP/1.0
```

It must be the first line of the model's final assistant text. The next line
starts one JSON object. No Markdown fence, prefix prose, suffix prose, or
second JSON document is permitted.

Text without a BYV-FP header is ordinary text. A response beginning with
BYV-FP/ but containing an unknown version or malformed body is a protocol
error and must fail closed; it must not silently fall back to plain text.

The parser consumes only the final assistant text channel. Hidden reasoning
or thinking-channel content is not part of the BYV-FP payload.

## 2. Final response

```text
BYV-FP/1.0
{"type":"final","content":"The answer is 42."}
```

Rules: type is final, content is a string, and no other top-level keys are
allowed. The content is delivered to the application as user-facing text.

## 3. Tool-call response

```text
BYV-FP/1.0
{"type":"tool_calls","calls":[{"id":"call_01","tool":"weather.lookup","arguments":{"city":"Martapura","days":2}}]}
```

Rules:
- type must equal tool_calls.
- calls is a non-empty array of at most 32 calls.
- Each call has exactly id, tool, and arguments.
- id is unique within the envelope and uses 1–64 ASCII letters, digits,
  dot, underscore, colon, or hyphen; its first character is alphanumeric.
- tool uses an ASCII identifier beginning with a letter or underscore and
  continuing with letters, digits, underscore, dot, colon, or hyphen.
- arguments must be a JSON object. Values retain their JSON types.
- Each tool must exist in the trusted host registry, be enabled, be allowed
  for the current request, and pass the registered input schema.

## 4. JSON constraints

- UTF-8 JSON; duplicate object keys are rejected.
- Non-standard values such as NaN and Infinity are rejected.
- Default payload limit is 1 MiB.
- Envelope keys are exact; unknown fields are rejected.
- Tool schemas come from the trusted host registry, never from the model.

## 5. Provider bridge contract

The protocol itself contains no provider-specific fields. The SDK maps
validated calls to:
- OpenAI Chat Completions function tool-call objects and tool result messages.
- OpenAI Responses API function_call and function_call_output items.
- Anthropic Messages API tool_use and tool_result content blocks.

Call IDs are preserved for correlation. The host should maintain an explicit
ID mapping if a provider-specific constraint requires IDs to be rewritten.

## 6. Approval and execution

BYV-FP calls are requests, not permissions. The SDK parses the envelope,
resolves tools against the trusted registry, validates arguments, applies
the per-request allowlist, and separates calls requiring approval. It maps
only approved calls to provider-native structures.

The SDK does not execute tools. The application owns authorization,
sandboxing, user confirmation, idempotency, rate limits, timeouts, audit logs,
and output limits. A command-like tool must never run with ambient host
privileges merely because a model requested it.

## 7. Versioning

Breaking wire-format changes require a new major protocol header. SDK version
and protocol version are distinct; the SDK may evolve without changing the
wire contract as long as the format remains backward compatible.
