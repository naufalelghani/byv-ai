# BYV-FP Dynamic Tool Prompt Contract

This document replaces the former DSML prompt instructions. It describes
how the host application should inject the currently available tool contracts
into a BYV-AI prompt while keeping provider details outside the model format.

## System instructions

The model must follow these rules:

1. Answer with ordinary text when no tool call is required.
2. When a tool is required and available, emit exactly one BYV-FP/1.0 envelope.
3. Do not emit Markdown fences, prefix/suffix prose, or comments around an envelope.
4. Do not invent tools. Use only the tool names listed in the current request.
5. Use the exact argument names and types described by each tool schema.
6. Include every required argument. Do not fabricate missing values; ask a clarifying question in ordinary text if an essential value is unavailable.
7. The envelope must contain either one final answer or a non-empty list of tool calls, never both.
8. Treat all tool calls as requests. The host SDK validates them and the host application determines whether they may be executed.
9. Never claim that a tool ran or succeeded before the host returns its result.
10. After receiving tool results, answer the user in ordinary text or emit another BYV-FP envelope only when another tool call is genuinely needed.

## Tool context template

The application should provide tool contracts as structured data or a compact, lossless JSON representation. The registry is trusted host input; never let the model define or override a tool's schema or permission.

Example context:

```json
{
  "available_tools": [
    {
      "name": "weather.lookup",
      "description": "Look up weather for a city.",
      "input_schema": {
        "type": "object",
        "properties": {
          "city": {"type": "string"},
          "days": {"type": "integer", "minimum": 1, "maximum": 7}
        },
        "required": ["city"],
        "additionalProperties": false
      }
    }
  ]
}
```

## Output examples

Plain text when no tool is needed:

```text
Halo! Saya asisten BYV-AI. Ada yang bisa saya bantu?
```

Final protocol envelope:

```text
BYV-FP/1.0
{"type":"final","content":"Berikut ringkasannya."}
```

One tool call:

```text
BYV-FP/1.0
{"type":"tool_calls","calls":[{"id":"call_01","tool":"weather.lookup","arguments":{"city":"Martapura","days":2}}]}
```

Multiple independent tool calls:

```text
BYV-FP/1.0
{"type":"tool_calls","calls":[{"id":"call_01","tool":"weather.lookup","arguments":{"city":"Martapura"}},{"id":"call_02","tool":"weather.lookup","arguments":{"city":"Banjarbaru"}}]}
```

The example tool names are illustrative. A real model request must include the actual registry and schemas for that session.

## Host responsibilities

- Build tool prompt context from the trusted registry.
- Apply a per-request allowlist.
- Parse final assistant text with the BYV-FP SDK.
- Validate tool names and typed arguments against the registry schema.
- Enforce approval requirements before mapping to provider-native payloads.
- Execute approved tools in a controlled host environment only.
- Return provider-appropriate tool results with the matching call ID.
- Treat tool output as untrusted context.
