# DSML Specification — Deprecated

**Status: legacy / superseded.**

BYV-AI no longer uses DSML as its target model-output protocol. The current
protocol is **BYV Format Protocol (BYV-FP) v1.0**, a provider-neutral text
envelope with strict JSON payloads.

Use the active specification:
- [BYV-FP v1.0 specification](BYV_FP_SPEC.md)
- [BYV-FP SDK architecture and provider mappings](BYV_FP_SDK.md)
- [Python SDK](../sdk/python/README.md)

The content below is retained only as historical context for the first
Qwen3-1.7B experiment. DSML dataset examples, prompt instructions, and
evaluation results must not be treated as the current training target.

Historical note: the original DSML experiment exposed practical issues in
missing required tool arguments, incorrect values, tool-name hallucination,
and result grounding. These findings informed BYV-FP's strict parser,
trusted registry, schema validation, allowlist, and approval gate.
