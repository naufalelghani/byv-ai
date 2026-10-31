# BYV-AI

BYV-AI adalah proyek model text-generation yang menghasilkan jawaban teks biasa atau **BYV Format Protocol (BYV-FP)** sebagai teks. Model tidak wajib menggunakan native tool-calling API. BYV-FP diproses oleh SDK terpisah yang memvalidasi permintaan lalu menjembatani format tersebut ke provider.

> **Status pengembangan:** fondasi Python SDK BYV-FP v0.1 sudah dibuat pada branch kerja. Unit tests **23 passed**; CI matrix Python **3.10, 3.11, dan 3.12 semuanya sukses**. Review edge cases provider dan integrasi end-to-end masih diperlukan sebelum rilis.

## Arsitektur

```text
BYV-AI model (text generation)
        |
        | plain text OR BYV-FP/1.0 text envelope
        v
     BYV-FP SDK
        |
        +-- strict parser + schema validation
        +-- trusted tool registry + allowlist
        +-- approval / policy gate
        |
        +-- OpenAI Chat Completions bridge
        +-- OpenAI Responses API bridge
        +-- Anthropic Messages API bridge
        |
        v
Host application executes approved tools
```

**BYV-AI model hanya menghasilkan teks. SDK tidak mengeksekusi tool.** Host aplikasi tetap bertanggung jawab atas autentikasi, izin, persetujuan pengguna, sandbox, timeout, audit log, dan eksekusi aksi.

## BYV-FP SDK

Implementasi awal tersedia pada branch kerja:

- [Python SDK source](https://github.com/naufalelghani/byv-ai/tree/feature/byv-fp-sdk-v0.1/sdk/python)
- [SDK installation and usage](https://github.com/naufalelghani/byv-ai/blob/feature/byv-fp-sdk-v0.1/sdk/python/README.md)
- [BYV-FP v1.0 protocol specification](https://github.com/naufalelghani/byv-ai/blob/feature/byv-fp-sdk-v0.1/docs/BYV_FP_SPEC.md)
- [SDK architecture and provider mapping](https://github.com/naufalelghani/byv-ai/blob/feature/byv-fp-sdk-v0.1/docs/BYV_FP_SDK.md)
- [CI run — Python 3.10/3.11/3.12](https://github.com/naufalelghani/byv-ai/actions/runs/41238775697)

Provider wajib di v0.1:
- **OpenAI Chat Completions**
- **OpenAI Responses API**
- **Anthropic Messages API**

Core BYV-FP tidak bergantung pada format internal salah satu provider. Provider bridge bertugas mengubah definisi tool, tool invocation, dan tool result di antara format netral dan payload native provider.

## Format ringkas

Jawaban akhir:

```text
BYV-FP/1.0
{"type":"final","content":"Halo! Ada yang bisa dibantu?"}
```

Satu atau beberapa tool call:

```text
BYV-FP/1.0
{"type":"tool_calls","calls":[{"id":"call_01","tool":"weather.lookup","arguments":{"city":"Martapura"}}]}
```

Tanpa header BYV-FP, output diperlakukan sebagai teks biasa. Jika header BYV-FP ada tetapi JSON/envelope rusak, parser harus gagal tertutup (fail closed). Tool calls tetap dianggap request tidak tepercaya, bukan izin untuk mengeksekusi tool.

## Model target eksperimen berikutnya

Target model yang dipilih untuk eksperimen berikutnya adalah **Qwen/Qwen3-4B-Thinking-2507** (4B class, thinking-only). Model ini belum dilatih untuk BYV-FP. Dataset dan training recipe harus dimigrasikan/divalidasi terlebih dahulu; adapter Qwen3-1.7B lama tidak dapat langsung digunakan pada base model 4B atau format protokol baru.

Model card: https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507

QLoRA di Colab T4 akan diperlakukan sebagai eksperimen feasibility, bukan jaminan muat atau cepat. Konfigurasi harus diuji dengan memory probe dan sequence length konservatif.

## Eksperimen legacy DSML

Run pertama Qwen3-1.7B dengan dataset DSML lama tetap disimpan sebagai baseline historis:

- 280 train examples, 35 eval examples, 2 epochs / 70 steps.
- Aggregate train loss 0.8291; final eval loss 0.7142.
- Held-out test awal: 35/35 output non-empty dan 6/6 contoh DSML terdeteksi.
- Metrik itu **bukan semantic accuracy**. Manual review menemukan missing/incorrect tool arguments, grounding errors, dan issue kualitas kode/Markdown.

Lihat [legacy experiment log](experiments/README.md), [test summary](experiments/byv-ai-qwen3-1.7b-qlora-t4-fp16-v0.1.2/test_evaluation/test_summary.json), dan [manual review](experiments/byv-ai-qwen3-1.7b-qlora-t4-fp16-v0.1.2/test_evaluation/MANUAL_REVIEW.md).

## Mulai dari sini

1. [Project plan](docs/PLAN.md)
2. [BYV-FP specification](docs/BYV_FP_SPEC.md)
3. [BYV-FP SDK guide](docs/BYV_FP_SDK.md)
4. [QLoRA training plan](docs/TRAINING_PLAN.md)
5. [Experiment log](experiments/README.md)

Dokumen DSML lama dipertahankan sebagai catatan historis; DSML tidak lagi menjadi protokol target BYV-AI.

## Prinsip kualitas dan keamanan

- Jangan klaim SOTA tanpa benchmark yang terdefinisi, reproducible, dan dibandingkan dengan baseline relevan.
- Fine-tuning tidak menjamin output selalu valid; tetap gunakan parser dan validator.
- Tool schema harus berasal dari aplikasi, bukan dari model.
- Unknown tool, parameter invalid, allowlist violation, dan approval yang belum diberikan harus ditolak/ditahan.
- Jangan pernah menganggap output tool sebagai fakta tepercaya tanpa pemeriksaan.
