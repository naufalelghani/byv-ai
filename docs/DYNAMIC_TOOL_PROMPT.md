# Dynamic Tool Instructions & DSML Prompt

Status: **draft reference**. This document records the `toolsToPrompt(tools)` prompt builder supplied for BYV-AI. The example is an instruction contract for text generation; it does not enable native tool calling.

## 1. Purpose

BYV-AI receives the available tool definitions from the application at prompt time. The model reads those definitions, reasons about the user's request, and returns either:

- ordinary assistant text when no tool is needed; or
- DSML markup inside the assistant's **text content** when a listed tool is required.

The model does not execute tools. It does not use OpenAI `tool_calls`, Anthropic tool-use blocks, function-calling metadata, MCP, or a built-in agent runtime. A separate BYV-AI gateway may parse, validate, authorize, and execute DSML.

## 2. Reference prompt builder

The following is the example supplied for BYV-AI. Keep the DSML marker spelling and whitespace unchanged unless the DSML grammar is deliberately revised.

```javascript
function toolsToPrompt(tools) {
    if (!tools || !tools.length) return '';

    const lines = [];
    lines.push('You have access to the tools listed below. These are the only tools available to you for this request.');
    lines.push('');

    for (const tool of tools) {
        const schema = tool.input_schema || tool.parameters || {};
        const properties = schema.properties || {};
        const required = schema.required || [];
        const params = Object.keys(properties).map((key) => {
            const value = properties[key] || {};
            return `${key}${required.includes(key) ? '*' : ''}: ${value.type || 'any'}` +
                (value.description ? ` (${value.description})` : '');
        }).join('; ');
        lines.push(`- ${tool.name}(${params}): ${tool.description || ''}`);
    }

    lines.push('');
    lines.push('MANDATORY RULES:');
    lines.push('1. If the task requires file access, shell commands, search, or an action that one of the tools above can perform, you MUST use the appropriate tool.');
    lines.push('2. If the tool results already received are sufficient to complete the task, provide the final answer without another tool call. Otherwise, continue with the next appropriate tool.');
    lines.push('3. Use the gateway DSML markup format for tool calls. Do not use the legacy <TOOL_CALL> JSON wrapper.');
    lines.push('4. Emit exactly ONE outer calls block for the whole assistant tool response, with one invoke block per requested tool. Do not repeat the calls wrapper.');
    lines.push('5. Use this DSML structure (the leading space after the DSML token in calls/invoke/parameter is intentional):');
    lines.push('<｜DSML｜ calls>');
    lines.push('<｜DSML｜ invoke name="Bash">');
    lines.push('<｜DSML｜ parameter name="command" string="true">npm run check</｜DSML｜ parameter>');
    lines.push('<｜DSML｜ parameter name="description" string="true">Run npm run check in the repository root</｜DSML｜ parameter>');
    lines.push('</｜DSML｜ invoke>');
    lines.push('</｜DSML｜ calls>');
    lines.push('6. For string arguments, set string="true" and write the raw string value without JSON quoting or escaping.');
    lines.push('7. For numbers, booleans, null, arrays, and objects, set string="false" and write the value as valid JSON.');
    lines.push('8. Use each parameter name exactly as declared in the selected tool schema. Do not duplicate parameter names, invent tools, or add prose/Markdown inside the calls block.');
    lines.push('9. Do NOT write anything outside the DSML calls block when calling tools.');
    lines.push('10. Use plain text when the task is complete or no additional tool is needed.');
    lines.push('');
    lines.push('VALID DSML TOOL CALL EXAMPLE (formatting example only):');
    lines.push('<｜DSML｜ calls><｜DSML｜ invoke name="Bash"><｜DSML｜ parameter name="command" string="true">npm run check</｜DSML｜ parameter><｜DSML｜ parameter name="description" string="true">Run npm run check in the repository root</｜DSML｜ parameter></｜DSML｜ invoke></｜DSML｜ calls>');
    lines.push('Put all requested tool invocations inside one calls block. Do not append closing DSML tags a second time.');
    lines.push('');
    lines.push('EXAMPLE: TOOL REQUIRED');
    lines.push(`User: "Please help me use ${tools[0].name}."`);
    lines.push('Assistant: Use the single DSML calls block shown above, with the exact selected tool name and its declared parameter names/types.');
    lines.push('');
    lines.push('EXAMPLE: NO TOOL NEEDED');
    lines.push('User: "Who are you? Please answer in my language."');
    lines.push('Assistant: I am an assistant ready to help...');
    return lines.join('\n');
}
```

## 3. Expected behavior

### No tool is needed

User:
```text
Who are you? Please answer in my language.
```

Assistant: respond with ordinary text. Do not emit DSML.

### One tool is needed

Given a tool named `Bash` whose active schema declares string parameters `command` and `description`, a request that requires a shell command may produce the following. The `description` parameter is included because it is part of this example's tool schema; it is not a universal DSML parameter for every tool:

```text
<｜DSML｜ calls>
<｜DSML｜ invoke name="Bash">
<｜DSML｜ parameter name="command" string="true">npm run check</｜DSML｜ parameter>
<｜DSML｜ parameter name="description" string="true">Run npm run check in the repository root</｜DSML｜ parameter>
</｜DSML｜ invoke>
</｜DSML｜ calls>
```

This is an example of **text output only**. It is not an executed call and does not prove that the command succeeded.

### Multiple independent tools are needed

Put all requested invocations in one outer calls block, with one invoke block per tool. Do not repeat the outer calls wrapper.

### A later tool depends on an earlier result

Do not guess the missing result or fabricate dependent arguments. Emit the next appropriate call, wait for the application to return its result, then continue.

## 4. Prompt-time tool definitions

Tool definitions are dynamic context supplied by the application for the current request. The model may use only the listed tools and must use exact tool names and declared parameter names.

The current helper summarizes top-level parameter names, types, and descriptions. It does not serialize the complete JSON Schema. If tools use nested objects, arrays, enums, unions, or detailed validation constraints, consider including the complete schema in the prompt so the model has enough information to produce valid parameters.

If the tool list is empty, the helper returns an empty string. The surrounding system prompt should explicitly tell the model to answer in plain text when no tools are available.

## 5. DSML output rules

- DSML is assistant text, not native tool-call metadata.
- Use exactly one outer calls block per assistant tool response.
- Use one invoke block per requested tool.
- Use exact tool and parameter names from the current tool list. Include every required parameter declared by the active schema; a tool may require multiple string parameters such as `command` and `description`.
- For string parameters, use `string="true"`; for non-string JSON values, use `string="false"`.
- Do not put prose or Markdown inside the calls block.
- Do not append duplicate closing tags.
- Use plain text when no tool is needed or when the available results are sufficient.
- Never claim that a tool ran or succeeded until the application returns an execution result.

## 6. Parser and executor safety

Treat generated DSML as untrusted input. The gateway must independently:

- parse the complete structure and reject malformed or ambiguous markup;
- check tool names against an allowlist for the current request;
- validate parameters against the actual tool schema;
- enforce authorization, policy, and user approval requirements;
- apply timeouts, size limits, and execution isolation where appropriate;
- distinguish generated requests from verified execution results.

The model's prompt instructions are not a security boundary. Never execute arbitrary DSML or shell content solely because the model generated it.

## 7. Open decisions

The following details still need to be finalized in the DSML specification:

- escaping for string values that contain DSML marker text or closing-tag sequences;
- exact treatment of whitespace and line breaks in string parameters;
- whether multiple independent invokes may always share a calls block;
- how the gateway represents a tool error or a denied/approval-required action;
- whether reasoning is hidden, summarized, or exposed separately from final assistant text.

Until these are decided, keep this document as the reference example and do not silently change the grammar.
