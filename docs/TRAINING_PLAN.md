# QLoRA Training Plan — BYV-FP / Qwen3-4B-Thinking-2507

## Goal

Fine-tune a thinking-capable instruction model to answer in ordinary text by
default and emit the strict BYV-FP/1.0 text envelope when the application
requires tool routing. This plan is prospective; no BYV-FP adapter has been
trained yet.

## Target model

- Candidate: Qwen/Qwen3-4B-Thinking-2507.
- Model card: https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507
- Parameters: 4B class; thinking-only release.
- License, revision, tokenizer, and chat template must be re-verified at run time.
- Do not load the old Qwen3-1.7B DSML adapter onto this 4B base; it is not a compatible adapter or target format.

The related Qwen3-4B-Instruct-2507 is a separate non-thinking variant, not a mode switch for the thinking-only 2507 checkpoint.

## Colab / QLoRA feasibility

- Target runtime: Google Colab, GPU availability variable.
- Candidate hardware: Tesla T4 16 GB class, if assigned.
- Quantization: 4-bit NF4 QLoRA; FP16 compute on T4.
- Start with per-device batch size 1, gradient checkpointing, and conservative sequence length.
- Run a memory probe before the full training job.
- Do not assume 4B QLoRA will fit every free-tier runtime/configuration. Reduce context length or use a larger GPU if OOM.
- Record peak VRAM, GPU model, and actual throughput.

## Workflow

1. Verify exact model revision, license, tokenizer, chat template, and generation defaults.
2. Complete the BYV-FP dataset migration and human/schema review.
3. Keep train, validation, and held-out test splits strictly separate.
4. Run baseline inference on the held-out prompt list before training.
5. Tokenize with the model's own chat template; verify how the thinking and final channels are represented.
6. Train SFT with explicit loss masking and no contamination of hidden reasoning data.
7. Save adapter, tokenizer assets if required, trainer config, seed, library versions, dataset revision, logs, and hardware metadata.
8. Compare base and fine-tuned model on the same test set.
9. Validate emitted BYV-FP using the SDK and validate semantic correctness manually.
10. Test CPU/GPU deployment and quantization separately.

## Dataset requirements

Dataset must be revised from legacy DSML to BYV-FP:
- Plain text questions with plain text answers.
- BYV-FP final envelopes.
- BYV-FP calls with valid IDs, registered tools, and typed JSON arguments.
- Multi-call envelopes with distinct IDs.
- Multi-turn cases where tool results are returned before final answer.
- Tool results must be explicitly supplied in context; never teach the model to invent results.
- Missing arguments must lead to a clarification or safe non-call, not fabrication.
- Include invalid/unsupported-tool cases and plain-text quoted protocol strings.
- Audit every tool schema and every required argument.
- Human review all examples before training.

The existing synthetic DSML dataset is not ready for direct training on BYV-FP. A mechanical migration alone is insufficient.

## Evaluation

Report separately:
- Plain-text false-positive protocol rate.
- BYV-FP requested emission rate.
- Parser validity rate.
- Unknown-tool rejection rate.
- Schema pass rate.
- Allowlist and approval-gate behavior.
- Tool argument semantic correctness.
- Grounding in tool results.
- Final answer quality.
- Latency, throughput, context use, and VRAM/RAM peak.
- Base model vs fine-tuned model comparisons.

Structural validity is not semantic accuracy. Small synthetic seed datasets are pipeline smoke tests, not proof of broad capability.

## CPU deployment

Test the base model / merged model and quantized variants on actual target CPU hardware.
Record RAM, latency, tokens per second, context length, and task quality. Do
not assume an exported GGUF preserves chat template or reasoning-channel
behavior without an end-to-end test.
