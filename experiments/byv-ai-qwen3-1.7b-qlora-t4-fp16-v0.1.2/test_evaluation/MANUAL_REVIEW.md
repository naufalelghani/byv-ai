# BYV-AI Test Evaluation v0.1 — Manual Review

**Evaluation run:** `byv-ai-qwen3-1.7b-qlora-t4-fp16-v0.1.2`  
**Base model:** `Qwen/Qwen3-1.7B`  
**Test split:** `data/test.jsonl` — 35 examples across 13 categories  
**Date reviewed:** 2026-11-01

## Automated results from the uploaded Colab run

| Metric | Result |
|---|---:|
| Test examples processed | 35 / 35 |
| Non-empty predictions | 35 / 35 |
| Unfinished thinking outputs | 0 |
| Reference examples expecting DSML | 6 |
| Predictions containing DSML | 6 |
| DSML-presence behavior match | 35 / 35 |
| Basic DSML wrapper checks | 6 valid, 0 invalid |
| Mean inference latency | 9.46 seconds / example |

These results confirm that the inference loop completed and returned non-empty outputs. **The 35/35 behavior match is only a binary check for whether DSML appears when the reference contains DSML. It is not semantic accuracy.** The original validator checked wrappers and parameter JSON formatting, but did not verify required parameters or correctness of argument values.

## Findings from manual inspection

### High-priority DSML issues

- `byv-0251`: the generated `GetRepository` invoke omits required `repository`; `ListFiles` omits required `path`. Both invokes are unusable as emitted.
- `byv-0244`: `GetRepository` uses `repository="."` instead of the repository identifier in the reference (`naufalelghani/byv-ai`). The wrapper is well-formed, but the argument value is wrong.
- The other DSML examples inspected use the expected tool and argument names. No DSML tool was executed during evaluation.

### Grounding and tool-result interpretation

- `byv-0345`: the tool result says `APP_NAME = 'Demo'` and `DEBUG = False`. The answer does not report the actual `APP_NAME` value and over-interprets `DEBUG = False` as proof that the app is in production.
- `byv-0352`: the source only says Q4_K_M is the initial CPU quantization candidate. The answer invents a technical explanation instead of carefully stating that it is a candidate, not proof of export or CPU testing.
- `byv-0303`: the tool result explicitly supplies host `127.0.0.1`, port `8080`, and debug `false`. The answer incorrectly says the host and port values are not specified.

### Code-generation issues

- `byv-0133` (JavaScript): treats the string `path` as an iterable array of characters rather than splitting it on dots; it does not implement the requested nested-property lookup.
- `byv-0148` (JavaScript): the requested function should accept an ISO date string, but the prediction expects a Date object and omits invalid-date handling.
- `byv-0156` (Python): the slug function only lowercases and replaces spaces; it does not normalize accents or remove punctuation as a normal slugifier should.
- `byv-0192` (Rust): the declared return type is `Option<T>`, while `values.iter().max()` returns an optional reference; the generic bound is also weaker than the `Ord` bound required by `max`. The code is not type-correct as written.
- `byv-0090` (HTML): the requested minimal profile page contains literal ellipses in the header, main, and footer, so it is only a placeholder rather than useful markup.
- `byv-0105` (HTML/CSS): a working-looking login form is produced, but it drops the requested email label/type/autocomplete semantics from the reference and is less accessible than intended.

### Instruction-following and content quality

- `byv-0087`: asked for a dataset quality checklist; the output changes it into a generic table and misses several specific checks.
- `byv-0076`: asked for a reusable ADR template; the output invents a specific testing-tools topic instead of preserving the template structure.
- `byv-0080`: the acceptance-criteria list is relevant but generic and omits useful edge conditions such as empty results and access controls.
- `byv-0022`: the explanation of idempotency is broadly understandable, but “adding an item to a cart” is not necessarily idempotent when repeated; this is a risky example.
- `byv-0297`: the answer includes the Python version but adds an unnecessary statement about whether the version is mismatched, despite the instruction to report only the result.
- `byv-0316`: safe refusal when no web-search tool is listed, but it could better invite the user to provide a source or enable search.

### Test-label issue

- `byv-0218`: the user explicitly requested the file content `Catatan eksperimen BYV-AI`. The prediction uses that exact content. The reference target instead adds a Markdown heading and changes capitalization (`# Catatan Eksperimen BYV-AI`). This is a test-label mismatch, not a model failure against the actual user instruction. Correct the reference in a future dataset revision; preserve the original v0.1 artifact for reproducibility.

## Interpretation

The run is **operationally successful**: 35 examples completed, predictions are non-empty, and no generation ended with unfinished thinking. The test does **not** establish high semantic or code quality. Manual inspection found serious misses in evidence-grounded answers, code correctness, Markdown template following, and DSML argument completeness. The model should remain an experimental prototype, not be described as release-ready.

## Recommended next actions

1. Keep the held-out v0.1 run immutable and fix the `byv-0218` reference label in a new dataset revision.
2. Use the updated evaluation notebook, which checks tool names and required/allowed parameter names from each request's system prompt.
3. Add targeted training examples for multi-turn tool-result grounding, complete DSML arguments, exact-template following, and code correctness.
4. Run code-specific syntax/unit tests and conduct human review; formatting checks alone are insufficient.
