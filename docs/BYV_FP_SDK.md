# BYV-FP SDK v0.1 — Architecture and integration

## Architecture

```text
                 BYV-AI model
                      |
             final assistant text
                      |
                BYV-FP parser
                      |
            strict envelope validation
                      |
          host ToolRegistry + JSON Schema
                      |
        allowlist / approval / policy gate
                      |
               validated calls
                      |
            +---------+----------+
            |                    |
      OpenAI bridge        Anthropic bridge
      Chat Completions     Messages API
      Responses API        tool_use/tool_result
            |                    |
            +---------+----------+
                      |
              host application
          executes approved tools only
                      |
              provider result adapter
                      |
            next model conversation
```

The core protocol is provider-neutral. Provider bridges serialize and
normalize payloads but do not make provider API calls.

## Public modules

| Module | Responsibility |
|---|---|
| byv_fp.protocol | Strict BYV-FP parse and serialize |
| byv_fp.types | Provider-neutral data classes |
| byv_fp.registry | Trusted tool contracts |
| byv_fp.schema | Built-in JSON Schema subset validator |
| byv_fp.validation | Tool, schema, allowlist and approval checks |
| byv_fp.providers.openai | Chat Completions and Responses API mappings |
| byv_fp.providers.anthropic | Messages API mappings |

## JSON Schema subset in v0.1

Validation keywords:
- type: object, array, string, integer, number, boolean, null
- properties, required, additionalProperties
- items
- enum, const
- minimum, maximum
- minLength, maxLength, pattern
- minItems, maxItems
- minProperties, maxProperties

Annotation-only keywords title, description, default, examples, deprecated,
readOnly, writeOnly, $schema, and $id are accepted and ignored for validation.
Unsupported assertion keywords raise an error. This is not full JSON Schema
draft conformance.

## Provider mapping overview

| BYV-FP concept | OpenAI Chat Completions | OpenAI Responses | Anthropic Messages |
|---|---|---|---|
| Tool definition | function / parameters | function / parameters | name / input_schema |
| Invocation | tool_calls[].function | function_call | tool_use block |
| Correlation ID | tool_calls[].id | call_id | tool_use.id |
| Result | role=tool / tool_call_id | function_call_output / call_id | tool_result / tool_use_id |

See official provider docs:
- https://developers.openai.com/api/docs/guides/function-calling
- https://platform.claude.com/docs/en/api/messages/create

## Thinking-model integration

When a model exposes separate thinking and final channels, only the final
answer text is passed to the BYV-FP parser. Thinking content is not a protocol
envelope and must not be interpreted as a tool instruction.
