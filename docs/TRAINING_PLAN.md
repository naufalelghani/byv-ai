# Colab QLoRA Training Plan

## Goal

Fine-tune an instruction model to respond with plain text by default and emit DSML-as-text only when requested. The initial training run is a pipeline smoke test, not proof of model quality.

## Starting baseline

- Proposed model: Qwen/Qwen3-1.7B (verify current model card, license, tokenizer/chat template, and compatibility before training).
- Method: SFT + PEFT LoRA on a 4-bit quantized base (QLoRA).
- Runtime: Google Colab free; GPU availability is variable.
- Candidate stack: Transformers, Datasets, TRL, PEFT, bitsandbytes, Accelerate.
- Starting LoRA settings to test: rank 16, alpha 32, dropout 0.05; adjust based on VRAM and validation.
- Initial context length: conservative (e.g. 1024) until memory behavior is known.
- Save adapter/checkpoints to Google Drive.

## Workflow

1. Inspect runtime GPU and memory; stop if no compatible GPU is available.
2. Install and record exact library versions.
3. Load and inspect model tokenizer and chat template.
4. Validate dataset schema and DSML examples before training.
5. Split train/validation/test by prompt or task family to avoid leakage.
6. Tokenize using the model's chat template.
7. Train SFT with assistant-response loss masking where supported by the model template.
8. Save adapter, tokenizer files, training config, dataset revision, and logs.
9. Evaluate base model and fine-tuned model on the same held-out prompts.
10. Optionally merge adapter, export to a supported format, quantize, and benchmark CPU inference.

## Dataset design

Dataset needs at least these categories:
- Plain text questions with plain text responses.
- Explicit DSML requests with valid DSML responses.
- Plain-text requests following a previous DSML turn.
- DSML requests without claims of tool execution.
- Reasoning/problem-solving tasks where response format is explicitly specified.
- Refusal/clarification examples for unsupported or ambiguous actions.
- Negative cases where DSML-like strings appear in quoted text but are not instructions, if relevant.

Avoid copying private logs, credentials, personal data, or proprietary data without permission. Review licensing and data provenance.

## Evaluation

Use a held-out set and report:
- DSML-requested → DSML-emitted rate.
- Plain-text-requested → unwanted DSML rate.
- DSML syntax validity rate.
- Required field/parameter schema pass rate.
- Task correctness / instruction adherence (human or rubric review).
- Output length, latency, and memory.
- Baseline versus fine-tuned comparison.

A small handcrafted smoke-test dataset is only for confirming code execution. It is not enough to train robust behavior.

## Colab free constraints

- GPU type and quota are not guaranteed.
- Runtime can disconnect; save checkpoints frequently.
- Keep dataset and checkpoints in Drive, but avoid excessive repeated writes.
- Start with a small model and conservative batch/context settings.
- If OOM: lower context length, batch size, LoRA rank, or use gradient checkpointing.
- Do not assume notebook works unchanged across future library versions; pin versions once a run is reproducible.

## CPU deployment path (planned)

Adapter → optionally merge into base → convert to GGUF using compatible conversion workflow → quantize (Q4_K_M is a candidate, not a guaranteed best) → benchmark on target CPU VPS with llama.cpp/Ollama.

Verify tokenizer/chat-template behavior after conversion. Test plain-text and DSML prompts again after quantization.
