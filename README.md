# BYV-AI

Eksperimen membangun model bahasa yang dapat menghasilkan **teks biasa** atau **DSML sebagai teks**, sesuai instruksi pengguna. Model tidak bergantung pada native tool-calling API. Jika keluaran berisi DSML, aplikasi terpisah dapat mem-parse, memvalidasi, dan—dengan izin yang sesuai—mengeksekusinya.

> **Status:** training QLoRA pertama dan inference held-out test 35 contoh sudah berhasil dijalankan. Manual review menemukan isu penting pada grounding tool-result, kelengkapan argumen DSML, dan kualitas kode/Markdown; model masih prototipe eksperimental dan belum siap rilis.
>
> **Hasil training:** Qwen3-1.7B, 280 contoh train, 35 contoh eval, 2 epoch / 70 steps, aggregate train loss **0.8291**, dan eval loss akhir **0.7142**.
>
> **Hasil test:** 35/35 prediksi non-empty, 0 unfinished thinking, 6 contoh meminta DSML dan 6 prediksi mengeluarkan DSML; pemeriksaan otomatis awal mencatat 35/35 kecocokan kehadiran DSML. Angka tersebut bukan semantic accuracy. Manual review menemukan pemanggilan DSML yang argumennya tidak lengkap/salah serta beberapa jawaban konten dan kode yang keliru.

## Tujuan

- Jawaban normal tetap berupa teks biasa.
- DSML hanya digunakan ketika diminta atau ketika protokol aplikasi secara eksplisit mengarahkannya.
- Menjaga sintaks DSML yang disepakati secara konsisten.
- Melatih adapter dengan QLoRA di Google Colab gratis bila GPU tersedia.
- Menguji hasil dan menyiapkan inference CPU-only pada VPS.

## Keputusan awal

| Area | Keputusan awal |
|---|---|
| Baseline | Qwen3-1.7B; bandingkan model lain setelah baseline terukur |
| Training | Supervised fine-tuning (SFT) dengan QLoRA/PEFT |
| Data | Percakapan user/assistant; DSML ditempatkan di teks assistant, bukan native tool_calls |
| Format | Pertahankan contoh DSML yang disepakati; jangan desain ulang tanpa alasan |
| Runtime training | Google Colab free, GPU bila tersedia |
| Deployment target | VPS CPU-only; konversi/quantization GGUF dan uji dengan llama.cpp/Ollama |
| Safety | DSML parser/executor terpisah; validasi izin dan parameter sebelum menjalankan aksi |

## Train in Google Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/naufalelghani/byv-ai/blob/main/notebooks/BYV-AI_Training_v0.1.2_T4_FP16_DTYPE_FIX.ipynb)

Open the BYV-AI v0.1.2 QLoRA notebook directly in Google Colab. The notebook detects the available GPU and selects a compatible compute dtype; for Tesla T4 it uses FP16. Mount Google Drive and provide `train.jsonl` and `eval.jsonl` in `MyDrive/BYV-AI/data/` before training.

Notebook source: [`notebooks/BYV-AI_Training_v0.1.2_T4_FP16_DTYPE_FIX.ipynb`](notebooks/BYV-AI_Training_v0.1.2_T4_FP16_DTYPE_FIX.ipynb).

## Evaluate the held-out test set

[![Open Evaluation in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/naufalelghani/byv-ai/blob/main/notebooks/BYV-AI_Test_Evaluation_v0.1.ipynb)

The evaluation notebook runs inference only; it does **not** train the model or execute DSML tools. The first run completed all 35 examples across 13 categories (35 non-empty predictions, 0 unfinished thinking, mean latency 9.46 s). These automatic checks are not semantic accuracy. See the [test summary](experiments/byv-ai-qwen3-1.7b-qlora-t4-fp16-v0.1.2/test_evaluation/test_summary.json) and [manual review](experiments/byv-ai-qwen3-1.7b-qlora-t4-fp16-v0.1.2/test_evaluation/MANUAL_REVIEW.md) for the discovered DSML-argument, grounding, code-generation, and Markdown issues.

- Notebook: [`notebooks/BYV-AI_Test_Evaluation_v0.1.ipynb`](notebooks/BYV-AI_Test_Evaluation_v0.1.ipynb)
- Held-out test data: [`data/test.jsonl`](data/test.jsonl)
- Training metrics: [`train_metrics.json`](experiments/byv-ai-qwen3-1.7b-qlora-t4-fp16-v0.1.2/train_metrics.json)
- Per-step training/evaluation history: [`trainer_log_history.json`](experiments/byv-ai-qwen3-1.7b-qlora-t4-fp16-v0.1.2/trainer_log_history.json)

Before running, keep the trained adapter in `MyDrive/BYV-AI/outputs/byv-ai-qwen3-1.7b-qlora-t4-fp16-v0.1.2/`. The notebook downloads the held-out test split from this repository and checks for ID overlap with train/eval files when those files are present. The current notebook also inspects tool names and required/allowed parameter names; argument values and semantic/code quality still require manual review.

## Mulai dari sini

1. [Rencana proyek dan tahapan](docs/PLAN.md)
2. [Spesifikasi perilaku dan DSML](docs/DSML_SPEC.md)
3. [Contoh dynamic tool instructions dan prompt DSML](docs/DYNAMIC_TOOL_PROMPT.md)
4. [Rencana training Colab](docs/TRAINING_PLAN.md)
5. [Log eksperimen](experiments/README.md)

## Batasan

Fine-tuning dapat meningkatkan kepatuhan format, tetapi tidak menjamin output selalu valid. Evaluasi otomatis dalam notebook test terutama memeriksa struktur dan perilaku format; ia tidak membuktikan kebenaran semantik. Gunakan review manusia dan validator aplikasi. DSML sebagai teks tidak otomatis lebih hemat daripada native tool calling; pendekatan ini terutama memberi kontrol protokol, kompatibilitas, dan modularitas. Biaya inference tetap ditentukan model, konteks/output, runtime, dan hardware.
