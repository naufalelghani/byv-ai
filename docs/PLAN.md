# BYV-AI — Project Plan

## 1. Visi

Membangun model text-generation yang fleksibel:
- Menghasilkan jawaban natural-language biasa secara default.
- Menghasilkan DSML hanya ketika instruksi meminta DSML atau protokol aplikasi membutuhkannya.
- Memahami instruksi dan melakukan reasoning yang berguna.
- Mengeluarkan DSML sebagai **teks**, bukan native tool-call payload.
- Dapat dijalankan pada VPS CPU-only setelah model/adapter dipersiapkan.

## 2. Ruang lingkup

### Termasuk
- Menentukan grammar/protokol DSML yang dipakai.
- Dataset supervised fine-tuning (SFT) dengan contoh teks biasa dan DSML.
- Baseline model dan eksperimen QLoRA di Colab.
- Evaluasi perilaku format, kualitas jawaban, dan regression.
- Ekspor adapter/model dan uji inference CPU.

### Tidak termasuk pada fase awal
- Melatih foundation model dari nol.
- Membuat model yang mengeksekusi tool secara langsung.
- Menganggap teks DSML sebagai instruksi aman tanpa pemeriksaan.
- Menjamin reasoning internal model dapat diverifikasi hanya dari output.

## 3. Arsitektur target

User → LLM → output teks:
- Teks biasa → dikirim ke user.
- DSML → parser → schema/permission validation → executor terpisah → hasil tool dikembalikan ke LLM → jawaban akhir.

Model hanya menghasilkan teks. Executor harus memvalidasi tool name, parameter, policy, dan izin pengguna. Jangan menjalankan command mentah dari model tanpa sandbox dan guardrails.

## 4. Tahapan kerja

### Phase 0 — Spesifikasi (sekarang)
- [ ] Konfirmasi format DSML exact (whitespace, tag, terminator, escaping).
- [ ] Definisikan kapan DSML boleh dipakai.
- [ ] Tentukan contoh valid, invalid, dan teks biasa.
- [ ] Tetapkan batas keselamatan executor.

**Exit criteria:** dokumen DSML spec stabil dan contoh referensi dapat divalidasi.

### Phase 1 — Dataset v0
- [ ] Buat dataset kecil untuk menguji pipeline.
- [ ] Tambahkan contoh teks biasa tanpa DSML.
- [ ] Tambahkan contoh DSML hanya saat diminta.
- [ ] Tambahkan konteks multi-turn: setelah DSML, user meminta jawaban biasa.
- [ ] Deduplicate dan cek contoh format.
- [ ] Pisahkan train/validation/test agar contoh evaluasi tidak bocor ke training.

**Exit criteria:** dataset tervalidasi dan split reproducible.

### Phase 2 — Baseline dan QLoRA
- [ ] Jalankan baseline model tanpa fine-tuning.
- [ ] Rekam output pada prompt test.
- [ ] Training QLoRA SFT di Colab GPU yang tersedia.
- [ ] Simpan adapter dan metadata eksperimen ke Drive.
- [ ] Simpan checkpoint berkala untuk mengurangi risiko runtime terputus.

**Exit criteria:** training selesai, adapter tersimpan, loss/log tersedia.

### Phase 3 — Evaluasi
- [ ] Ukur DSML precision: output DSML ketika diminta.
- [ ] Ukur false-positive: DSML muncul pada permintaan teks biasa.
- [ ] Ukur validitas sintaks/struktur.
- [ ] Nilai kualitas isi dan ketepatan instruksi.
- [ ] Bandingkan baseline dengan fine-tuned model.
- [ ] Periksa overfitting dan regresi.

**Exit criteria:** hasil terukur; bukan hanya satu contoh yang terlihat berhasil.

### Phase 4 — Deployment CPU
- [ ] Tentukan apakah adapter digunakan langsung atau di-merge.
- [ ] Merge bila sesuai, lalu export/convert ke GGUF.
- [ ] Quantize (mulai dengan Q4_K_M sebagai percobaan).
- [ ] Uji inference pada VPS CPU-only.
- [ ] Catat RAM, token/s, latency, context size, dan kualitas.
- [ ] Integrasikan model dengan backend melalui text completion.

**Exit criteria:** model berjalan stabil pada VPS dan hasil DSML lolos validator.

### Phase 5 — Iterasi
- [ ] Perbaiki dataset dari error evaluasi.
- [ ] Bandingkan model/ukuran/rank LoRA.
- [ ] Uji constrained decoding atau grammar pada runtime jika diperlukan.
- [ ] Dokumentasikan setiap eksperimen.

## 5. Prinsip eksperimen

- Ubah satu variabel per eksperimen jika memungkinkan.
- Jangan memilih model hanya berdasarkan ukuran; ukur pada tugas BYV-AI.
- Dataset berkualitas dan seimbang lebih penting daripada data duplikat.
- Simpan model ID, revision, library versions, seed, config, dataset revision, dan metrik.
- Jangan simpan API keys, token, data pribadi, atau secrets ke repo.
- Catat kegagalan dan keterbatasan, bukan hanya hasil terbaik.

## 6. Risiko dan mitigasi

| Risiko | Mitigasi |
|---|---|
| Model selalu mengeluarkan DSML | Sertakan contoh teks biasa dan instruksi eksplisit “jawab biasa” |
| DSML rusak/parsial | Validator, contoh konsisten, dan tes format |
| Model mengarang tool/parameter | Allowlist tool dan schema validation |
| Perintah berbahaya | Permission checks, sandbox, approval, policy executor |
| Colab runtime terputus | Checkpoint dan simpan adapter ke Drive |
| Model terlalu lambat di CPU | Quantization, context limit, benchmark model lebih kecil |
| Training mengurangi kemampuan umum | Validation set umum dan baseline comparison |

## 7. Status

- Saat ini: perencanaan.
- Model baseline yang diusulkan: Qwen3-1.7B.
- Belum ada hasil training yang diklaim.
