# BYV-AI

Eksperimen membangun model bahasa yang dapat menghasilkan **teks biasa** atau **DSML sebagai teks**, sesuai instruksi pengguna. Model tidak bergantung pada native tool-calling API. Jika keluaran berisi DSML, aplikasi terpisah dapat mem-parse, memvalidasi, dan—dengan izin yang sesuai—mengeksekusinya.

> Status: tahap perencanaan. Belum ada model fine-tuned atau dataset final.

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

## Mulai dari sini

1. [Rencana proyek dan tahapan](docs/PLAN.md)
2. [Spesifikasi perilaku dan DSML](docs/DSML_SPEC.md)
3. [Contoh dynamic tool instructions dan prompt DSML](docs/DYNAMIC_TOOL_PROMPT.md)
4. [Rencana training Colab](docs/TRAINING_PLAN.md)
5. [Log eksperimen](experiments/README.md)

## Batasan

Fine-tuning dapat meningkatkan kepatuhan format, tetapi tidak menjamin output selalu valid. Gunakan evaluasi dan validator. DSML sebagai teks tidak otomatis lebih hemat daripada native tool calling; pendekatan ini terutama memberi kontrol protokol, kompatibilitas, dan modularitas. Biaya inference tetap ditentukan model, konteks/output, runtime, dan hardware.
