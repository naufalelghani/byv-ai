# BYV-FP Python SDK

Python-first reference SDK for **BYV Format Protocol v1.0**. The core uses only
the Python standard library. First-class provider bridges:

- OpenAI Chat Completions
- OpenAI Responses API
- Anthropic Messages API (tool_use / tool_result)

The SDK parses and validates model text, applies a host-defined tool allowlist
and approval policy, and maps approved calls to provider-native payloads. It
does not make network requests or execute tools.

## Install

From this directory:

```bash
pip install -e .
pip install -e ".[dev]"
pytest
```

## Wire format

Final answer:

```text
BYV-FP/1.0
{"type":"final","content":"The answer is 42."}
```

Tool calls:

```text
BYV-FP/1.0
{"type":"tool_calls","calls":[{"id":"call_01","tool":"weather.lookup","arguments":{"city":"Martapura","days":2}}]}
```

An output without the protocol header is ordinary assistant text. Once the
header is present, malformed JSON or an invalid envelope raises an error
(fail closed). The body must be a single JSON object; argument values retain
their JSON types.

## Minimal validation flow

```python
from byv_fp import ToolDefinition, ToolRegistry, parse_model_output, validate_response
from byv_fp.providers.openai import to_chat_completions_assistant_message

registry = ToolRegistry([
    ToolDefinition(
        name="weather.lookup",
        description="Look up current weather for a city.",
        input_schema={
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
            "additionalProperties": False,
        },
    )
])

parsed = parse_model_output(model_final_text)
report = validate_response(parsed, registry, allowed_tools={"weather.lookup"})

if report.pending_approval:
    # Obtain host/user approval, then validate again with approved_call_ids.
    ...
elif report.approved_calls:
    native_message = to_chat_completions_assistant_message(report)
    # Host application decides whether and how to execute the calls.
else:
    print(parsed.content)
```

## Provider bridges

### OpenAI Chat Completions

```python
from byv_fp.providers.openai import (
    to_chat_completions_tools, to_chat_completions_assistant_message,
    chat_completions_tool_result,
)

tools = to_chat_completions_tools(registry)
assistant_message = to_chat_completions_assistant_message(report)
tool_message = chat_completions_tool_result("call_01", {"temperature_c": 29})
```

### OpenAI Responses API

```python
from byv_fp.providers.openai import (
    to_responses_tools, to_responses_function_calls,
    responses_function_call_output,
)

tools = to_responses_tools(registry)
function_call_items = to_responses_function_calls(report)
output_item = responses_function_call_output("call_01", {"temperature_c": 29})
```

### Anthropic Messages API

```python
from byv_fp.providers.anthropic import (
    to_messages_tools, to_tool_use_blocks, anthropic_tool_result,
    anthropic_tool_results_message,
)

tools = to_messages_tools(registry)
tool_use_blocks = to_tool_use_blocks(report)
tool_result = anthropic_tool_result("call_01", {"temperature_c": 29})
tool_result_message = anthropic_tool_results_message([tool_result])
```

## Safety contract

1. Model-generated calls are untrusted requests, not authorization.
2. Unknown, disabled, disallowed, or schema-invalid calls are rejected.
3. Approval-required calls are held until the host approves the specific call ID.
4. The SDK never runs shell commands, makes HTTP requests, or invokes handlers.
5. The host must implement least privilege, consent, sandboxing, timeouts,
   output limits, audit logs, and secret handling.
6. Tool results are untrusted input when returned to a model.

The built-in schema validator supports the subset documented in
docs/BYV_FP_SDK.md. Unsupported JSON Schema keywords fail closed.

Pass only the model's final assistant text channel to the parser; do not pass
hidden reasoning/thinking-channel content.
