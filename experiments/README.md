# Experiment Log

Record every training/evaluation run here or in a separate file per run.

## Run 1 — `byv-ai-qwen3-1.7b-qlora-t4-fp16-v0.1.2`

- Base model: `Qwen/Qwen3-1.7B`
- Dataset: BYV-AI dataset v0.1; 280 train examples and 35 eval examples.
- Colab GPU: NVIDIA Tesla T4, 14.56 GB VRAM, compute capability 7.5.
- Quantization: QLoRA 4-bit NF4; FP16 compute.
- LoRA config: rank 16, alpha 32, dropout 0.05.
- Training config: 2 epochs, learning rate 0.0002, max sequence length 1024, per-device batch size 1, gradient accumulation 8.
- Training steps: 70.
- Training duration: 510.5487 seconds (about 8.51 minutes).
- Aggregate trainer-reported train loss: **0.829058**.
- Eval loss: **0.740587** at epoch 1; **0.714249** at epoch 2.
- Eval mean token accuracy at epoch 2: 0.828855 (this is token-level, not semantic answer accuracy).
- DSML-requested success rate, plain-text false-DSML rate, semantic correctness, and CPU inference performance: **not measured yet**.
- Adapter / Drive path: `MyDrive/BYV-AI/outputs/byv-ai-qwen3-1.7b-qlora-t4-fp16-v0.1.2/`.
- Logs committed in this repository:
  - [`train_metrics.json`](byv-ai-qwen3-1.7b-qlora-t4-fp16-v0.1.2/train_metrics.json)
  - [`trainer_log_history.json`](byv-ai-qwen3-1.7b-qlora-t4-fp16-v0.1.2/trainer_log_history.json)
- Notes: initial training run completed and adapter was saved to Google Drive. The held-out test split contains 35 examples across 13 categories; test inference has not yet been run.

## Test evaluation v0.1 — completed

- Test split: 35 examples across 13 categories.
- Non-empty predictions: 35 / 35.
- Unfinished thinking: 0.
- DSML expected: 6; DSML produced: 6.
- Initial automated DSML-presence behavior match: 35 / 35.
- Initial basic wrapper check: 6 valid, 0 invalid.
- Mean inference latency: 9.46 seconds per example.
- **Important:** these checks are not semantic accuracy and the original wrapper validator did not verify required parameters or semantic argument values. Manual review found missing required fields in `byv-0251`, an incorrect repository value in `byv-0244`, plus grounding/code/Markdown issues. See [test summary](byv-ai-qwen3-1.7b-qlora-t4-fp16-v0.1.2/test_evaluation/test_summary.json) and [manual review](byv-ai-qwen3-1.7b-qlora-t4-fp16-v0.1.2/test_evaluation/MANUAL_REVIEW.md).
- A test-label mismatch was also found in `byv-0218`: the generated content follows the literal user request, while the reference target differs. Keep v0.1 immutable and correct this label in a future dataset revision.

## Next evaluation

Run [the test evaluation notebook](../notebooks/BYV-AI_Test_Evaluation_v0.1.ipynb) in Colab with the saved adapter and [the held-out test split](../data/test.jsonl). The notebook exports predictions, a CSV review sheet, and an automated structural summary. Automated metrics do not replace manual semantic, code, Markdown, and DSML review.

## Run template

- Run ID:
- Date:
- Model and revision:
- Dataset version / split:
- Colab GPU:
- Library versions:
- Quantization:
- LoRA config (rank, alpha, dropout, target modules):
- Training config (epochs, learning rate, batch, gradient accumulation, max length):
- Seed:
- Training duration:
- Final train/validation loss:
- DSML-requested success rate:
- Plain-text false DSML rate:
- DSML syntax validity:
- CPU inference hardware / runtime:
- RAM peak:
- Tokens per second:
- Artifacts / Drive path:
- Notes and failures:
