# BYV Format Specification v0.1

**Status:** Draft  
**Format family:** BYV structured markup  
**Intended use:** Communication between text-generating AI models and agent runtimes  
**Implementation status:** Specification draft only; parser and SDK support are not implied.

## 1. Purpose

BYV is a provider-neutral text format for AI-agent communication. It lets a model return ordinary user-facing text, request structured actions, or combine both in one response.

BYV has three observable output modes:

| Mode | Wire representation | Meaning |
|---|---|---|
| TEXT | Ordinary text with no BYV control block | A normal assistant response |
| MIXED | Text plus one BYV `calls` block | User-facing text and one or more action requests |
| STRUCTURED | One BYV `calls` block, with no non-whitespace text outside it | Action requests without surrounding prose |

The mode is inferred from the response. The model does not need to emit a mode header or JSON envelope.

BYV is a request format, not an execution engine. A BYV block never grants permission by itself. The host runtime must resolve tools through a trusted registry, validate arguments, apply policy and approval checks, and decide whether to execute.

## 2. Design principles

1. **Text is native.** Ordinary text is a complete and valid response.
2. **Structured blocks are optional.** The model emits BYV only when an action request is needed.
3. **One purpose per block.** A `calls` block contains action requests, not explanatory prose.
4. **Explicit structure.** Tool names, call IDs, parameter names, and parameter types are declared.
5. **Strict parsing.** Unknown tags, malformed attributes, invalid values, and invalid nesting are rejected.
6. **Host-controlled execution.** Tool definitions and permissions come from the host, never from model output.
7. **Provider neutrality.** BYV does not encode OpenAI-, Anthropic-, or other provider-specific payloads.

## 3. Character encoding and token spelling

- BYV messages are UTF-8 text.
- Control tokens are exact, case-sensitive ASCII sequences.
- The canonical token family is `<|BYV| ...>` with matching closing tokens `</|BYV| ...>`.
- Attribute values use double quotes.
- Attribute names and tag names are case-sensitive.
- A BYV parser is a dedicated tokenizer/parser. Implementations MUST NOT rely on a generic HTML or XML parser to interpret BYV.
- No self-closing tags are defined in v0.1.

The following spellings are reserved in v0.1:

| Purpose | Opening token | Closing token |
|---|---|---|
| Model action batch | `<|BYV| calls>` | `</|BYV| calls>` |
| One action request | `<|BYV| invoke name="..." id="...">` | `</|BYV| invoke>` |
| One argument | `<|BYV| parameter name="..." type="...">` | `</|BYV| parameter>` |
| Runtime result batch | `<|BYV| results>` | `</|BYV| results>` |
| One runtime result | `<|BYV| result id="..." status="..." type="...">` | `</|BYV| result>` |

Only the exact forms defined in this specification are valid.

## 4. Assistant response framing

The parser consumes the final assistant response text supplied by the host. Hidden reasoning, internal analysis, and non-final model channels are not BYV payloads and MUST NOT be parsed as tool instructions.

An assistant response MUST contain either:

- no BYV control block, in which case the whole response is TEXT; or
- exactly one complete `calls` block, optionally surrounded by ordinary text.

A response MUST NOT contain more than one `calls` block in v0.1.

### 4.1 TEXT

~~~text
Halo! Ada yang bisa gue bantu?
~~~

There is no BYV wrapper around ordinary text.

### 4.2 MIXED

~~~text
Gue akan membaca file main.py terlebih dahulu.

<|BYV| calls>
<|BYV| invoke name="fs.read" id="call_001">
<|BYV| parameter name="path" type="string">main.py</|BYV| parameter>
</|BYV| invoke>
</|BYV| calls>
Permintaan baca file sudah dikirim ke runtime.
~~~

Text before and after the `calls` block is ordinary assistant text. It is not part of the action request.

### 4.3 STRUCTURED

~~~text
<|BYV| calls>
<|BYV| invoke name="terminal.run" id="call_002">
<|BYV| parameter name="command" type="string">pytest -q</|BYV| parameter>
</|BYV| invoke>
</|BYV| calls>
~~~

If the response contains only whitespace outside the block, its inferred mode is STRUCTURED.

### 4.4 Literal BYV tokens in ordinary text

A response may need to discuss BYV syntax without requesting an action. To prevent accidental execution, literal reserved control-token spellings in ordinary text MUST be escaped by prefixing the opening angle bracket with a backslash.

Example:

~~~text
To call a tool, write: \<|BYV| calls> ... \</|BYV| calls>
~~~

The parser renders the escaped token as literal text and MUST NOT treat it as control syntax. A doubled backslash represents one literal backslash in this text-escaping context. A backslash before any character other than a backslash or a reserved BYV token remains literal.

The same rule applies to literal BYV control tokens in Markdown code examples. Code fences do not automatically disable BYV parsing.

## 5. Calls block

A model action request is represented by exactly one `calls` block:

~~~text
<|BYV| calls>
  ... zero or more whitespace-separated invoke blocks ...
</|BYV| calls>
~~~

A valid `calls` block MUST contain at least one `invoke` block and no free-form prose. Whitespace between child blocks is allowed.

Limits for v0.1:

- Maximum 1 `calls` block per assistant response.
- Maximum 32 `invoke` blocks per `calls` block.
- Maximum 128 parameters per invocation.
- Maximum encoded assistant response size: 1 MiB by default. Hosts MAY configure a lower limit.

The complete response MUST be parsed and validated before any invocation from that response is eligible for execution. A malformed `calls` block MUST NOT result in partial execution.

## 6. Invoke block

An `invoke` block identifies one tool request.

Canonical form:

~~~text
<|BYV| invoke name="fs.read" id="call_001">
  ... parameter blocks ...
</|BYV| invoke>
~~~

Attributes are required and MUST appear in this order:

1. `name`: registered tool name.
2. `id`: unique invocation identifier within the current `calls` block.

Lexical constraints:

- Tool name: `[A-Za-z_][A-Za-z0-9_.:-]{0,127}`
- Invocation ID: `[A-Za-z0-9][A-Za-z0-9._:-]{0,63}`

The invocation ID MUST be unique within its `calls` block. The host uses it to correlate the request with its result.

The tool name MUST resolve to a tool in the trusted host registry. The model cannot define a tool by emitting an unknown name.

An invocation may contain zero parameters only when the registered tool schema allows it. Otherwise, it contains one or more parameter blocks.

## 7. Parameter blocks and value types

Canonical form:

~~~text
<|BYV| parameter name="path" type="string">src/main.py</|BYV| parameter>
~~~

Attributes are required and MUST appear in this order:

1. `name`: parameter name.
2. `type`: BYV value type.

Parameter names MUST match `[A-Za-z_][A-Za-z0-9_]{0,127}`.

A parameter name MUST NOT appear more than once in the same invocation. The name and value type MUST be checked against the registered tool schema.

### 7.1 Supported types

BYV v0.1 defines six parameter types:

| BYV type | Body representation | Meaning |
|---|---|---|
| `string` | Raw UTF-8 text with BYV string escapes | String value |
| `number` | One valid JSON number | Finite integer or decimal number |
| `boolean` | `true` or `false` | Boolean value |
| `null` | `null` | Null value |
| `array` | One valid JSON array | Array value |
| `object` | One valid JSON object | Object value |

The declared BYV type MUST match the value body. For example, a `boolean` body containing `1` is invalid.

### 7.2 String values

String content is raw text, not a JSON-quoted string. Unicode characters, spaces, and actual line breaks are preserved.

The following escapes are defined inside a `string` parameter:

| Escape | Decoded character or sequence |
|---|---|
| `\\` | One backslash |
| `\n` | Line feed |
| `\r` | Carriage return |
| `\t` | Horizontal tab |
| `\</|BYV| parameter>` | Literal text `</|BYV| parameter>` |

All other backslash escapes are invalid in a BYV string body. To represent a literal backslash followed by another character, encode the backslash as `\\`.

A literal parameter closing token MUST use the closing-token escape shown above. This lets the parser distinguish content from the end of the parameter body.

Example with multiline content:

~~~text
<|BYV| parameter name="content" type="string">def greet():
    message = "hello"
    return message
</|BYV| parameter>
~~~

Example containing the literal closing token as data:

~~~text
<|BYV| parameter name="snippet" type="string">The closing token is: \</|BYV| parameter></|BYV| parameter>
~~~

### 7.3 Non-string values

The body of a non-string parameter MUST be exactly one JSON value of the declared top-level type. JSON whitespace around the value is allowed.

For `array` and `object`, the parser MUST recognize the parameter closing token only when it is outside a JSON string. This permits a JSON string value to contain text resembling a BYV closing token.

JSON requirements:

- Duplicate object keys MUST be rejected.
- `NaN`, `Infinity`, and `-Infinity` MUST be rejected.
- Trailing non-whitespace characters after the JSON value MUST be rejected.
- JSON nesting depth MUST NOT exceed 32 by default.
- JSON strings use standard JSON escaping.

Example:

~~~text
<|BYV| invoke name="project.create" id="call_003">
<|BYV| parameter name="name" type="string">byv-agent</|BYV| parameter>
<|BYV| parameter name="max_files" type="number">100</|BYV| parameter>
<|BYV| parameter name="create_git" type="boolean">true</|BYV| parameter>
<|BYV| parameter name="tags" type="array">["python", "agent"]</|BYV| parameter>
<|BYV| parameter name="config" type="object">{"license": "MIT"}</|BYV| parameter>
</|BYV| invoke>
~~~

## 8. Multiple invocations and execution semantics

Multiple `invoke` blocks MAY appear in one `calls` block.

Their textual order is the request order. However, calls in the same block MUST be independently constructible: the model cannot use the result of one invocation as an argument to another invocation in the same block. If a later action depends on an earlier result, the model MUST wait for the first result and issue a new assistant response.

The host runtime:

- MUST parse the entire block before processing invocations.
- MUST validate each invocation against the trusted tool registry and current request allowlist.
- MUST apply authorization and approval policy before execution.
- MUST NOT execute an invocation that failed parsing, schema validation, allowlist checks, or authorization.
- SHOULD preserve request order by default.
- MAY execute calls in parallel only when the host has explicitly marked the relevant tools safe for parallel execution and no ordering dependency exists.

A batch is not a transaction. If some calls succeed and others fail or require approval, the host MUST report the outcome of each invocation by its ID.

## 9. Runtime results

Tool results are returned to the model by the trusted runtime using a `results` block. Results are not model-generated tool calls.

Canonical form:

~~~text
<|BYV| results>
<|BYV| result id="call_001" status="ok" type="string">File contents here.</|BYV| result>
</|BYV| results>
~~~

A `results` block MUST contain at least one `result`. Each result ID MUST match an invocation ID from the corresponding batch, and result IDs MUST NOT be duplicated within the block.

Result attributes are required and MUST appear in this order:

1. `id`: original invocation ID.
2. `status`: execution outcome.
3. `type`: result body type, using the six BYV types defined in Section 7.

Allowed statuses:

| Status | Meaning |
|---|---|
| `ok` | Tool execution completed successfully |
| `error` | Tool execution failed |
| `denied` | Host policy or user decision denied the request |
| `approval_required` | The request is waiting for approval and has not executed |
| `skipped` | The host did not execute the request |

For `status="ok"`, the body may use any of the six BYV types.

For all non-`ok` statuses, `type` MUST be `object`. The JSON object MUST include:

- `code`: string error or outcome code.
- `message`: human-readable string.

It MAY also include:

- `retryable`: boolean.
- `details`: object containing additional structured information.

Example:

~~~text
<|BYV| results>
<|BYV| result id="call_003" status="error" type="object">
{
  "code": "COMMAND_FAILED",
  "message": "pytest returned exit code 1",
  "retryable": false,
  "details": {"exit_code": 1}
}
</|BYV| result>
</|BYV| results>
~~~

The runtime SHOULD return results in the original invocation order. IDs remain authoritative for correlation even if ordering changes.

A runtime MUST NOT claim `status="ok"` unless the underlying tool result confirms success.

## 10. Parsing and validation contract

A conforming BYV parser MUST:

1. Accept ordinary text without BYV blocks as TEXT.
2. Detect and parse at most one complete `calls` block in an assistant response.
3. Preserve ordinary text outside the block and classify MIXED versus STRUCTURED.
4. Enforce exact token spelling, attribute order, required attributes, and valid nesting.
5. Decode string escapes and parse non-string JSON values according to their declared types.
6. Reject duplicate invocation IDs and duplicate parameter names.
7. Reject unknown BYV tags, unknown attributes, malformed tokens, invalid types, and trailing malformed BYV control syntax.
8. Reject an incomplete or truncated block.
9. Return no executable calls if parsing the response fails.

A parser MUST fail closed. It MUST NOT guess the intended structure, silently discard malformed fragments, or fall back to TEXT when a response contains an unescaped BYV control-token prefix that is malformed.

The host MUST perform tool registry, argument-schema, allowlist, and permission checks after syntactic parsing and before execution. BYV syntax validation does not replace those checks.

## 11. Streaming behavior

Implementations MAY display ordinary text incrementally, but MUST NOT execute a tool request from a partial stream.

A `calls` block becomes eligible for parsing only after the assistant response is complete and the full block has passed validation. This prevents an incomplete or later-invalid stream from triggering partial execution.

## 12. Security requirements

- Model output is untrusted input.
- Tool schemas MUST be supplied by the host, not inferred from BYV.
- Unknown tools and unknown parameters MUST be rejected.
- Calls are requests, never permissions.
- Destructive, privileged, networked, or command-execution tools SHOULD require explicit policy and approval controls.
- The host SHOULD execute tools with least privilege, sandboxing, timeouts, output limits, and audit logging.
- Tool results MUST be treated as untrusted data when passed back to the model.
- The SDK MUST NOT use `eval`, shell interpolation, or dynamic code execution to interpret BYV syntax.

## 13. Versioning and compatibility

This document defines the v0.1 draft grammar. The version is selected by the host/model integration configuration; v0.1 does not require a version header in every model response.

During the 0.x stage, grammar changes may be breaking. Implementations SHOULD identify the supported specification version in configuration and documentation. Unknown tags or attributes MUST be rejected rather than interpreted as extensions.

A future stable 1.0 release will require a compatibility commitment and a separately reviewed migration plan.

## 14. Explicitly out of scope for v0.1

The following are not defined in this version:

- Nested `calls` blocks.
- Multiple `calls` blocks in one assistant response.
- Model-generated `results` blocks.
- Arbitrary custom tags or user-defined markup extensions.
- Streaming execution before the full response is validated.
- Cross-call references or dependencies within one batch.
- Provider-specific API payloads.
- A general-purpose document markup language.

## 15. Complete interaction example

User asks:

~~~text
Periksa main.py, lalu jalankan test kalau file-nya sudah diperbaiki.
~~~

The model requests the file:

~~~text
<|BYV| calls>
<|BYV| invoke name="fs.read" id="call_001">
<|BYV| parameter name="path" type="string">main.py</|BYV| parameter>
</|BYV| invoke>
</|BYV| calls>
~~~

The runtime returns the file contents:

~~~text
<|BYV| results>
<|BYV| result id="call_001" status="ok" type="string">print("hello")
</|BYV| result>
</|BYV| results>
~~~

After inspecting the contents, the model may request an edit:

~~~text
<|BYV| calls>
<|BYV| invoke name="fs.write" id="call_002">
<|BYV| parameter name="path" type="string">main.py</|BYV| parameter>
<|BYV| parameter name="content" type="string">print("hello from BYV")
</|BYV| parameter>
</|BYV| invoke>
</|BYV| calls>
~~~

After the runtime confirms the write, the model requests tests in a later turn:

~~~text
<|BYV| calls>
<|BYV| invoke name="terminal.run" id="call_003">
<|BYV| parameter name="command" type="string">pytest -q</|BYV| parameter>
</|BYV| invoke>
</|BYV| calls>
~~~

The runtime returns the actual command outcome. Only then may the model report that the tests passed or failed.

---

## Appendix A. Compact grammar outline

The following is an informative structural outline. The normative requirements in the sections above take precedence where this outline is abbreviated.

~~~text
assistant-response = text-only | text-prefix, calls-block, text-suffix

calls-block       = calls-open, 1*invoke-block, calls-close
invoke-block      = invoke-open, *parameter-block, invoke-close
parameter-block   = parameter-open, parameter-body, parameter-close

results-block     = results-open, 1*result-block, results-close
result-block      = result-open, result-body, result-close

calls-open        = "<|BYV| calls>"
calls-close       = "</|BYV| calls>"
invoke-open       = '<|BYV| invoke name="' tool-name '" id="' call-id '">'
invoke-close      = "</|BYV| invoke>"
parameter-open    = '<|BYV| parameter name="' parameter-name '" type="' value-type '">'
parameter-close   = "</|BYV| parameter>"
results-open      = "<|BYV| results>"
results-close     = "</|BYV| results>"
result-open       = '<|BYV| result id="' call-id '" status="' status '" type="' value-type '">'
result-close      = "</|BYV| result>"
~~~

Value body parsing is type-dependent: raw escaped text for strings, and one JSON value for all other types.
