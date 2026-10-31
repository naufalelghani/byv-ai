# Experiment Log

## Legacy Run 1 — Qwen3-1.7B / DSML

This is a completed historical pipeline experiment. It is not a BYV-FP
training run and its metrics must not be attributed to the new 4B model.

- Base model: Qwen/Qwen3-1.7B.
- Dataset: legacy BYV-AI dataset v0.1; 280 train examples and 35 eval examples.
- Colab GPU: NVIDIA Tesla T4, 14.56 GB VRAM, compute capability 7.5.
- Quantization: QLoRA 4-bit NF4; FP16 compute.
- LoRA: rank 16, alpha 32, dropout 0.05.
- Training: 2 epochs, learning rate 0.0002, max sequence length 1024, batch size 1, gradient accumulation 8.
- Training steps: 70; duration: 510.5487 seconds.
- Aggregate train loss: 0.829058.
- Eval loss: 0.740587 at epoch 1; 0.714249 at epoch 2.
- Eval mean token accuracy at epoch 2: 0.828855 (token-level, not semantic accuracy).
- Adapter location: MyDrive/BYV-AI/outputs/byv-ai-qwen3-1.7b-qlora-t4-fp16-v0.1.2/.
- The adapter is specific to the old base model and old DSML task; it is not reusable as a Qwen3-4B-Thinking-2507 BYV-FP adapter.

## Legacy test evaluation v0.1

- Test split: 35 examples across 13 categories.
- Non-empty predictions: 35 / 35.
- Unfinished thinking: 0.
- DSML expected: 6; DSML produced: 6.
- Initial DSML-presence behavior match: 35 / 35.
- Initial basic wrapper check: 6 valid, 0 invalid.
- Mean inference latency: 9.46 seconds per example.
- **Important:** these checks are not semantic accuracy and the original validator did not verify required parameters or semantic argument values. Manual review found missing required fields, incorrect repository values, grounding/code/Markdown issues, and one tool hallucination.
- The uploaded summary predates the enhanced structural/schema validator. See [test summary](byv-ai-qwen3-1.7b-qlora-t4-fp16-v0.1.2/test_evaluation/test_summary.json) and [manual review](byv-ai-qwen3-1.7b-qlora-t4-fp16-v0.1.2/test_evaluation/MANUAL_REVIEW.md).

## BYV-FP SDK implementation

A first Python SDK implementation has been added on branch feature/byv-fp-sdk-v0.1:
- Strict BYV-FP/1.0 parser/serializer.
- Host tool registry and supported JSON Schema subset validator.
- Per-request allowlist and per-call approval gate.
- OpenAI Chat Completions and Responses API bridges.
- Anthropic Messages API bridge.
- Provider result helpers and unit tests.

**CI status:** GitHub Actions run [41238775697](https://github.com/naufalelghani/byv-ai/actions/runs/41238775697) completed successfully. Python 3.10, 3.11, and 3.12 matrix jobs all passed; the Python 3.11 log reports 23 passed. The workflow ran on source commit 35875017e8c4c0abd96a9ba33f0264558abccd71. API integration tests with live provider calls are not included.

No BYV-FP model adapter or training metrics are claimed.

## Next experiments

1. Review provider-specific API payload nuances and add integration tests.
2. Complete BYV-FP dataset migration and human review.
3. Run Qwen3-4B-Thinking-2507 base-model baseline.
4. Probe QLoRA VRAM requirements before training.
5. Train only after dataset review and baseline capture.

## Run template

- Run ID:
- Date:
- Model and exact revision:
- Dataset version / split:
- GPU / VRAM:
- Library versions:
- Quantization:
- LoRA configuration:
- Training configuration:
- Seed:
- Duration:
- Train/validation loss:
- BYV-FP parser validity:
- Schema pass rate:
- Tool selection and argument correctness:
- Semantic correctness / review rubric:
- Latency / throughput:
- VRAM/RAM peak:
- Artifacts:
- Failures and notes:
