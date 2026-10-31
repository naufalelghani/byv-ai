# System prompt sources

This folder stores the versioned BYV-AI prompt source for future fine-tuning runs.

## Files

- `BYV_SYSTEM_PROMPT_BUILDER_v0.1.js`: the original JavaScript prompt-builder source supplied for this task, with the DSML/tool-call contract converted to BYV. The `PROJECT_AND_LANGUAGE_INSTRUCTIONS` block is preserved verbatim. Tool schemas remain dynamically injected by `toolsToPrompt(tools)`.
- `BYV_SYSTEM_PROMPT_TEMPLATE_v0.1.md`: a plain-text counterpart for future training notebooks. Replace `{{AVAILABLE_TOOLS}}` with the exact tool list and schemas relevant to each training sample. The post-tool-result and forced-tool overlays are separate so a dataset builder can include them only when appropriate.

## Source and compatibility notes

The JavaScript builder retains the host application's original imports, `./content` and `./config`. Those modules are not included in this repository. The file is preserved as the prompt-builder source/reference and is not a standalone Node package here.

The plain-text template is intended for future training notebooks to load directly. Keep it aligned with the JavaScript builder and `docs/BYV_FORMAT_SPEC_v0.1.md` whenever the prompt or BYV grammar changes.

The legacy DSML source is not included in the active training prompt files. The current prompt target is BYV markup with TEXT, MIXED, and STRUCTURED modes.
