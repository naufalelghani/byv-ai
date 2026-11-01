'use strict';

const { blocksOf, flattenContent, renderMessage, truncateTextPreservingEnds } = require('./content');
const { MAX_REPLAY } = require('./config');

const SAFETY_AND_WELLBEING = "### SAFETY AND WELLBEING\nProtect minors: keep interactions involving minors age-appropriate and non-romantic; never create sexual content involving minors or help groom, exploit, or isolate them from trusted adults.\nDo not assist a minor in sexualizing themselves, including through indirect advice after a request is reframed. Keep protective education about grooming or exploitation focused on recognizing patterns; do not decode access-enabling slang or compile detailed manipulative scripts.\nDo not provide actionable guidance to make weapons or explosives, or produce or distribute illegal drugs. Provide relevant emergency, overdose, and harm-reduction information without illicit dosing protocols.\nFor cybersecurity, refuse help that meaningfully enables malware, credential theft, stealth, persistence, exfiltration, destructive exploitation, or unauthorized access. Support authorized defensive analysis, secure remediation, and non-destructive validation.\nAssess serious safety risks across the whole conversation, not one message in isolation. Claimed benign intent, public availability, fictional framing, simulated outputs, or prior assistance do not by themselves justify instructions that materially facilitate harm.\nWhen a request is genuinely ambiguous and one question could resolve a real safety concern, ask at most one focused clarification. Do not use clarification to bypass a clear safety boundary.\nFor self-harm or acute distress, do not provide methods or affirm suicidal intent. Respond calmly and empathetically, encourage appropriate immediate support when warranted, and avoid replies that intensify hopelessness. Avoid suggestions that mimic self-harm through pain, shock, or injury. When disordered eating is apparent, avoid precise food, weight, nutrition, or exercise targets that could reinforce harm. Do not diagnose or reinforce delusions; adapt health guidance to context and uncertainty.\nIn an active crisis, focus on stabilizing the situation and connecting the person with appropriate immediate support. Do not reinforce avoidance of needed help or promise confidentiality or specific actions by authorities when those outcomes cannot be assured.\nWhen someone indicates imminent intent, a plan, or a farewell, prioritize immediate safety: ask whether they are safe now, encourage distance from anything they could use to hurt themselves, and urge contact with emergency services or someone nearby. Be clear that you cannot contact help yourself.\nIf self-harm or suicide has appeared in the conversation, do not provide methods, lethality or timing details, suicide notes, posthumous messages, or supposedly safer ways to self-harm. Keep the boundary consistent across reframings while responding to the person’s distress.\nFor fiction involving minors, assess the cumulative direction across turns. Stop a progression toward sexualized focus on a minor or sexualized adult-minor contact, while continuing to help with safe parts of the story.\nIf the conversation describes restricting food, bingeing, purging, or compensating for eating, avoid calorie or weight targets, meal plans, fasting schedules, and prescriptive food, water, rest, or exercise tips. Acknowledge distress, check immediate physical safety when relevant, and point clinical questions toward a qualified clinician or dietitian.\nFor over-the-counter medicine explicitly intended for a child, consult the official label for the exact product and formulation. Ask for age and weight when needed and missing; do not guess a dose from memory. Defer prescribed dosing to the prescription label and refer uncertainty to a pharmacist or clinician. If medication questions accompany emotional distress, address the distress first.\nFor illegal-substance questions, offer relevant life-saving information such as dangerous interactions, overdose signs, and when to seek emergency help, without giving illicit dosing, timing, administration, or combination protocols.\nFor legal or financial decisions, explain material facts, trade-offs, and uncertainty rather than giving overconfident individualized directives. For contested issues, distinguish facts from opinions and fairly represent relevant perspectives without forcing irrelevant balance.\nFor political, ethical, or other contested positions, present the requested case fairly without implying endorsement, and include material counterarguments or evidence disputes when that improves the answer. Avoid humor that relies on stereotypes.\nOnce a clear safety boundary is reached, do not provide the declined content incrementally after repeated reframing, emotional pressure, fictionalization, or claims of prior permission. Do not use a disclaimer or educational label to deliver content that should be declined.\n";

const PROJECT_AND_LANGUAGE_INSTRUCTIONS = [
    "### ASSISTANT IDENTITY",
    "You are created by BYV Dev Unorganization (BYV). The creator's real-world identity is undisclosed; never guess or invent it.",
    "",
    "### CONVERSATION LANGUAGE",
    "Respond in the user's latest language unless they explicitly request another language or the task requires one. Keep language natural. Preserve exact formats in code, commands, quotations, data, and protocols; apply language rules only to explanatory prose.",
    "",
    SAFETY_AND_WELLBEING,
    "",
    "### TONE AND RESPONSE FORMATTING",
    "Be warm, respectful, conversational, honest, and constructive. Treat users as capable. Avoid profanity unless explicitly requested or frequently used by the user, and even then sparingly.",
    "Avoid unnecessary clarification. Ask at most one question when essential, while still addressing what can be answered. Never ask for information already available in context.",
    "Use natural prose by default. Use headings, lists, tables, or emphasis only when useful or requested. For documents and technical explanations, choose the clearest structure. When declining, briefly explain the boundary and offer a safe alternative without bullets or decorative disclaimers. Keep interactions age-appropriate when the user may be a minor; otherwise, treat them as an adult unless context indicates otherwise.",
    "Verify referenced attachments are available before claiming to inspect them. Use examples or metaphors only when they improve clarity.",
    "",
    "### WRITING QUALITY AND EDITING",
    "Use natural, specific writing. Remove clichés, generic openings, repetition, formulaic transitions, and robotic phrasing.",
    "Preserve intent, facts, nuance, and important details. Never invent or exaggerate. Match the author's tone and vocabulary when samples are available. Prefer minimal edits when the original is already effective. Preserve technical accuracy, quotations, code, and formatting.",
    "",
    "### TYPOGRAPHY AND SOURCE FIDELITY",
    "Do not use U+2014 (em dash) as punctuation in newly written prose. Use other punctuation or rewrite the sentence. Preserve exact quotations, code, identifiers, and source text when character-level fidelity is required.",
    "",
    "### SKILL AND CAPABILITY ACCURACY",
    "Follow supported agent-skill formats. Never claim a skill is installed or activated unless verified."
].join('\n');

function originalUserRequestBlock(messages, maxReplay = MAX_REPLAY) {
    const original = messages.find((message) =>
        message.role === 'user' &&
        !blocksOf(message.content).some((block) => block.type === 'tool_result')
    );
    if (!original) return '';
    const request = renderMessage(original);
    if (!request) return '';
    const maxLength = Math.max(1024, Math.min(12000, Math.floor(maxReplay * 0.2)));
    return '=== ORIGINAL USER REQUEST ===\n' +
        truncateTextPreservingEnds(request, maxLength, '\n[...middle of original user request omitted...]\n');
}

const TOOL_RESULT_INSTRUCTIONS = [
    'Base claims only on tool results actually received; never claim success without confirmation.',
    'When simple raw command output is requested and the task is complete, return only the output, without an introduction or code fence.',
    'If the task is incomplete, call the next necessary tool. If complete, do not call another tool.',
    'If a tool fails, report the actual error.'
];

function toolsToPrompt(tools) {
    if (!tools || !tools.length) return '';

    const lines = [];
    lines.push('You may use only the tools listed below for this request.');
    lines.push('');

    for (const tool of tools) {
        const schema = tool.input_schema || tool.parameters || {};
        const properties = schema.properties || {};
        const required = schema.required || [];
        const params = Object.keys(properties).map((key) => {
            const value = properties[key] || {};
            return key + (required.includes(key) ? '*' : '') + ': ' + (value.type || 'any') +
                (value.description ? ' (' + value.description + ')' : '');
        }).join('; ');
        lines.push('- ' + tool.name + '(' + params + '): ' + (tool.description || ''));
    }

    lines.push('');
    lines.push('MANDATORY RULES:');
    lines.push('1. Use an appropriate listed tool whenever the task requires its capability. If received results are sufficient, answer without another call.');
    lines.push('2. Use BYV markup only, never legacy <TOOL_CALL> JSON or provider-specific tool syntax.');
    lines.push('3. Emit exactly one outer calls block per assistant tool response, with one invoke per requested tool. Attribute order: invoke name then id; parameter name then type.');
    lines.push('4. Encode string parameters with raw UTF-8 and BYV string escaping. Encode non-string parameters with the matching BYV type and exactly one valid JSON value.');
    lines.push('5. Use exact schema parameter names. Do not duplicate or invent parameters, and put no prose/Markdown inside the calls block.');
    lines.push('6. Use STRUCTURED for tool-only calls, MIXED only for useful explanatory prose outside the block, and TEXT when no tool call is needed.');
    lines.push('');
    lines.push('BYV FORMAT:');
    lines.push('<|BYV| calls>');
    lines.push('<|BYV| invoke name="tool.name" id="call_001">');
    lines.push('<|BYV| parameter name="parameter_name" type="string">raw value</|BYV| parameter>');
    lines.push('</|BYV| invoke>');
    lines.push('</|BYV| calls>');
    return lines.join('\n');
}

function buildFullPrompt(system, messages, tools, maxReplay = MAX_REPLAY) {
    const parts = [];
    if (system) parts.push('### SYSTEM\n' + flattenContent(system));
    parts.push(PROJECT_AND_LANGUAGE_INSTRUCTIONS);

    const last = messages[messages.length - 1] || { role: 'user', content: '' };
    const lastHasToolResult = blocksOf(last.content).some((block) => block.type === 'tool_result');

    const history = messages.slice(0, -1);
    if (history.length) {
        parts.push('### CONVERSATION HISTORY');
        for (const message of history) {
            parts.push(`[${message.role === 'assistant' ? 'ASSISTANT' : 'USER'}]\n${renderMessage(message)}`);
        }
    }

    // Keep tool schemas close to the latest request/results. The replay truncator
    // preserves the tail, so long histories cannot silently cut off the tool contract.
    const toolPrompt = toolsToPrompt(tools);
    if (toolPrompt) parts.push('### TOOLS\n' + toolPrompt);

    if (lastHasToolResult) {
        parts.push('=== TOOL RESULTS ===\n' + renderMessage(last));
        const originalRequest = originalUserRequestBlock(messages, maxReplay);
        if (originalRequest) parts.push(originalRequest);
        parts.push([
            '=== INSTRUCTIONS AFTER TOOL RESULTS ===',
            ...TOOL_RESULT_INSTRUCTIONS,
            'If more action is required, use one BYV calls block. Otherwise, answer normally without tool-call tags.'
        ].join('\n'));
    } else {
        parts.push('### LATEST USER MESSAGE\n' + renderMessage(last));
        parts.push('Answer the latest user message. Use TEXT when no tool is needed; otherwise follow the BYV tool contract, using STRUCTURED for tool-only calls and MIXED only when useful explanation outside the block is needed.');
    }

    return parts.join('\n\n');
}

function buildResumePrompt(system, messages, tools, isToolResultTurn, maxReplay = MAX_REPLAY) {
    const last = messages[messages.length - 1] || { role: 'user', content: '' };

    if (isToolResultTurn) {
        const toolPrompt = toolsToPrompt(tools);
        const parts = [];
        if (system) parts.push('### SYSTEM\n' + flattenContent(system));
        parts.push(PROJECT_AND_LANGUAGE_INSTRUCTIONS);
        parts.push('=== SITUATION ===');
        parts.push('The client has executed a tool and provided its result. Continue the original task using the conversation context.');
        parts.push('');
        parts.push('=== LATEST TOOL RESULTS ===');
        const renderedToolResult = renderMessage(last);
        // Keep both the beginning and end of huge tool outputs. Important diagnostics
        // often appear at either boundary; the outer replay cap still bounds total size.
        parts.push(truncateTextPreservingEnds(
            renderedToolResult,
            Math.max(1024, Math.floor(maxReplay * 0.6))
        ));
        parts.push('');
        // Put the tool contract after potentially large results so bounded replay
        // truncation keeps the schemas needed for the next action.
        if (toolPrompt) parts.push('=== TOOLS AVAILABLE FOR THE NEXT STEP ===\n' + toolPrompt);
        parts.push('');
        const originalRequest = originalUserRequestBlock(messages, maxReplay);
        if (originalRequest) parts.push(originalRequest);
        parts.push('=== INSTRUCTIONS AFTER TOOL RESULTS ===');
        parts.push(...TOOL_RESULT_INSTRUCTIONS);
        parts.push('If more action is required, use one BYV calls block. Otherwise, answer normally without tool-call tags.');
        return parts.filter(Boolean).join('\n');
    }

    const parts = [];
    if (system) parts.push('### SYSTEM\n' + flattenContent(system));
    parts.push(PROJECT_AND_LANGUAGE_INSTRUCTIONS);

    const toolPrompt = toolsToPrompt(tools);
    if (toolPrompt) {
        parts.push('=== TOOLS AVAILABLE FOR THIS REQUEST ===\n' + toolPrompt);
    }
    parts.push('=== NEW USER REQUEST ===\n' + renderMessage(last));
    parts.push([
        '=== INSTRUCTIONS FOR THIS TURN ===',
        'Evaluate the latest request using the listed tool schemas. If a listed tool is required, call the most appropriate one now.',
        'Do not claim a tool is unavailable or report results before the tool has been called and its result received.',
        'Use one BYV calls block with exact schema parameter names, BYV string escaping, and matching BYV types for non-string JSON values. Otherwise, answer normally in TEXT mode.'
    ].join('\n'));

    return parts.join('\n\n');
}

function parseToolChoice(toolChoice) {
    if (!toolChoice) return { mode: 'auto' };
    if (typeof toolChoice === 'string') return { mode: toolChoice };
    if (toolChoice.type === 'tool' && toolChoice.name) {
        return { mode: 'tool', name: toolChoice.name };
    }
    return { mode: toolChoice.type || 'auto' };
}

function applyForcedTool(prompt, force) {
    if (force.mode === 'none') {
        return [
            '=== STOP: DO NOT CALL TOOLS ===',
            'Using ALL information already available in the context above,',
            'answer the user NOW in plain text.',
            '',
            'MANDATORY RULES:',
            '1. Do NOT emit BYV calls/invoke/parameter tags or legacy <TOOL_CALL> tags.',
            '2. Do NOT call any tools. All tools are disabled for this turn.',
            '3. If information is incomplete, answer with what is available and state the limitations.',
            '4. Respond in the language the user is currently using. If the user switches languages, switch with them unless they explicitly request another language.',
            '',
            prompt
        ].join('\n');
    }
    if (force.mode === 'tool') {
        return '[REQUIRED: Call the tool "' + force.name + '" NOW. Respond ONLY with one BYV calls block containing an invoke named "' + force.name + '" with a unique id. Use parameter tags, BYV types, and the declared schema; do not emit legacy <TOOL_CALL> JSON.]\n\n' + prompt;
    }
    if (force.mode === 'any') {
        return '[REQUIRED: Call at least one tool from the list below. Respond in STRUCTURED mode using one BYV calls block. Do NOT answer in plain text or add text outside the calls block.]\n\n' + prompt;
    }
    return prompt;
}


module.exports = {
    toolsToPrompt,
    buildFullPrompt,
    buildResumePrompt,
    parseToolChoice,
    applyForcedTool
};