# System prompt sources

This folder stores the versioned BYV-AI prompt source for future fine-tuning runs.

## Files

- `BYV_SYSTEM_PROMPT_BUILDER_v0.1.js`: the original JavaScript prompt-builder source supplied for this task, with the DSML/tool-call contract converted to BYV. The assistant instructions are compacted while retaining the existing safety and wellbeing rules. Tool schemas remain dynamically injected by `toolsToPrompt(tools)`.
- `BYV_SYSTEM_PROMPT_TEMPLATE_v0.1.md`: a plain-text prompt reference for future runtime integrations or dataset builders. Replace `{{AVAILABLE_TOOLS}}` with the exact tool list and schemas relevant to each sample when using this template.

## Source and compatibility notes

The JavaScript builder retains the host application's original imports, `./content` and `./config`. Those modules are not included in this repository. The file is preserved as the prompt-builder source/reference and is not a standalone Node package here.

The current BYV Markup training and evaluation notebooks do **not** download or load either prompt file. They define compact BYV instructions inline and insert each record's `tools` schema directly from the dataset. The files in this folder remain versioned references for future use; keep them aligned with `docs/BYV_FORMAT_SPEC_v0.1.md` when the BYV contract changes.

The legacy DSML source is not included in the active training prompt files. The current prompt target is BYV markup with TEXT, MIXED, and STRUCTURED modes.
