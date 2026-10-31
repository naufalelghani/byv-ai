# BYV-AI BYV-FP v0.2.1 — GitHub + Colab quickstart

## Open notebooks directly from GitHub

Repository: [naufalelghani/byv-ai](https://github.com/naufalelghani/byv-ai), branch `main`.

- [Open training notebook in Google Colab](https://colab.research.google.com/github/naufalelghani/byv-ai/blob/main/notebooks/BYV-AI_Training_BYV-FP_v0.2.1_Qwen3-4B-Thinking-2507_T4_QLoRA.ipynb)
- [Open held-out evaluation notebook in Google Colab](https://colab.research.google.com/github/naufalelghani/byv-ai/blob/main/notebooks/BYV-AI_Test_Evaluation_BYV-FP_v0.2.1_Qwen3-4B-Thinking-2507.ipynb)

You do **not** need to upload the notebooks to Colab. Open the links above and run them from GitHub.

## Dataset setup (one-time)

The first run needs `BYV-AI_dataset_BYV-FP_v0.2.1.zip`. On the first training run, select that ZIP when Colab asks for it. The notebook saves it under `MyDrive/BYV-AI/data/byv-fp-v0.2.1/`. Evaluation reuses the same saved ZIP; you do not need to upload it again.

The training notebook extracts and reads only `train.jsonl` and `eval.jsonl`. It never reads the held-out `test.jsonl`. The evaluation notebook opens only `test.jsonl` from the same archive and checks its SHA-256 before inference.

## Run training

1. Open the **Training notebook** using the Colab link above.
2. Select **Runtime → Change runtime type → GPU**.
3. Run all cells.
4. The notebook mounts Google Drive, validates dataset hashes, and saves the LoRA adapter and experiment logs there.

Adapter output:

`MyDrive/BYV-AI/outputs/byv-ai-qwen3-4b-thinking-2507-byvfp-qlora-t4-fp16-v0.2.1/`

## Run held-out evaluation

1. Open the **Evaluation notebook** using the Colab link above.
2. Select GPU and run all cells.
3. It reuses the dataset ZIP and adapter from Google Drive, then evaluates the 35 held-out test records.
4. Review `manual_review.csv`, `test_predictions_adapter.jsonl`, and `test_summary.json` in `MyDrive/BYV-AI/experiments/`.

## Hardware note

The notebook targets a Colab T4 with 4-bit NF4 QLoRA, FP16, batch size 1, gradient accumulation 8, and sequence length 1024. T4 VRAM is not guaranteed to be sufficient in every runtime. If CUDA runs out of memory, restart runtime, set `MAX_LENGTH=512`, and run all cells again; otherwise use a larger GPU.

## Dataset and safety caveats

- Dataset contains 280 train, 35 eval, and 35 held-out test records, including 100 BYV-FP assistant-message targets.
- This dataset is a mechanical migration of an earlier synthetic seed. It is structurally and schema validated, but still requires human semantic/code review. It is a pipeline smoke-test dataset, not a high-quality benchmark and not proof of SOTA capability.
- No BYV-FP adapter has been trained yet. The notebook creates it only after you run training with an available GPU.
- Tool calls are never executed by either notebook. The evaluation measures generated format/schema behavior only. Test execution through the BYV-FP SDK and a permissioned host application.
- Train/eval/test boundaries are retained. Never move held-out test examples into training.
