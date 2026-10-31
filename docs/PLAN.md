# BYV-AI — Project Plan

## 1. Visi

Membangun model text-generation yang:
- Menjawab dengan teks biasa secara default.
- Menghasilkan BYV-FP sebagai teks hanya ketika protokol/aplikasi meminta tool action.
- Menggunakan BYV-FP SDK sebagai lapisan parsing, validasi, policy, dan provider bridge.
- Dapat dihubungkan ke provider OpenAI dan Anthropic tanpa mengikat format output model ke salah satu provider.
- Dapat dievaluasi secara reproducible sebelum deployment.

Target model eksperimen berikutnya: Qwen/Qwen3-4B-Thinking-2507. Ini adalah target, bukan klaim bahwa BYV-FP adapter sudah dilatih.

## 2. Arsitektur target

User → BYV-AI text generation → output:
- Plain text → host menampilkan jawaban.
- BYV-FP envelope → parser → schema validation → tool registry / request allowlist → approval gate → provider adapter → host application.

Provider bridge wajib:
1. OpenAI Chat Completions.
2. OpenAI Responses API.
3. Anthropic Messages API.

SDK menghasilkan payload native dan menormalisasi hasil provider. SDK tidak menjalankan tools dan tidak melakukan network request. Host application memiliki tanggung jawab eksekusi.

## 3. Scope SDK v0.1

- BYV-FP/1.0 strict parser dan serializer.
- Plain text fallback hanya ketika header protokol tidak ada.
- Malformed/unknown protocol header harus fail closed.
- Typed JSON arguments.
- Trusted tool registry.
- JSON Schema subset validator dengan keyword support terdokumentasi.
- Request-level allowlist.
- Per-call approval gate.
- OpenAI Chat Completions mapping.
- OpenAI Responses API mapping.
- Anthropic Messages API mapping.
- Provider result mapping / call ID correlation.
- Unit test dan CI.

Di luar scope v0.1:
- Tool execution engine.
- Provider network client / agent loop.
- Full JSON Schema draft conformance.
- Streaming BYV-FP parser.
- TypeScript/Rust SDK parity.
- SOTA/performance claims tanpa benchmark.

## 4. Tahapan kerja

### Phase 0 — Protocol and SDK core
- [x] Tentukan BYV-FP envelope untuk final response dan tool calls.
- [x] Implement strict parser dan serializer Python.
- [x] Implement trusted registry, schema subset, allowlist, approval gate.
- [x] Tambahkan OpenAI dan Anthropic bridge awal.
- [ ] Jalankan seluruh unit test dan CI pada branch.
- [ ] Review detail API payload terhadap API version yang ditargetkan.
- [ ] Tambahkan test untuk malformed provider payload, multi-tool, approval, dan errors.

Exit criteria: test suite passing; examples verified; spec and implementation agree.

### Phase 1 — Dataset migration
- [ ] Migrasikan dataset DSML lama ke BYV-FP secara mekanis pada revision baru.
- [ ] Audit semua contoh tool-call terhadap tool registry/schema.
- [ ] Perbaiki argumen wajib, parameter hallucination, semantic values, dan tool outputs.
- [ ] Human review train/eval examples.
- [ ] Pastikan held-out test tidak bocor ke train/eval.
- [ ] Bekukan dataset revision sebelum training.

Exit criteria: tidak ada schema violation; label semantic direview; split reproducible dan test tetap held out.

### Phase 2 — Base model and QLoRA
- [ ] Gunakan Qwen/Qwen3-4B-Thinking-2507 sebagai kandidat utama.
- [ ] Verifikasi model card, revision, license, tokenizer, dan chat template.
- [ ] Jalankan baseline inference tanpa adapter.
- [ ] Uji QLoRA feasibility pada GPU aktual, termasuk T4 jika tersedia.
- [ ] Pilih context length dan batch berdasarkan memory probe, bukan asumsi.
- [ ] Training SFT hanya setelah dataset lolos review.
- [ ] Simpan adapter, training config, revision, library versions, seed, dan logs.

Exit criteria: training selesai, adapter tersimpan, dan semua metadata eksperimen tersedia.

### Phase 3 — Evaluation
- [ ] BYV-FP emission precision/recall sesuai prompt.
- [ ] Plain-text false-positive rate.
- [ ] Protocol parse validity.
- [ ] Tool-name allowlist pass rate.
- [ ] Required/allowed argument schema pass rate.
- [ ] Semantic correctness dan grounding review.
- [ ] OpenAI dan Anthropic adapter mapping tests.
- [ ] Baseline vs fine-tuned comparison.
- [ ] Latency, throughput, memory, and token counts.

Exit criteria: report reproducible, manual review selesai, tidak hanya berdasarkan loss atau format presence.

### Phase 4 — Deployment
- [ ] Integrasikan model melalui text-generation endpoint.
- [ ] Jalankan BYV-FP SDK di host backend.
- [ ] Hubungkan provider bridge OpenAI/Anthropic.
- [ ] Terapkan authentication, approval, sandbox, rate limit, timeout, audit logs.
- [ ] Benchmark inference di CPU/GPU target.
- [ ] Evaluasi quantization setelah ada quality baseline.

## 5. Prinsip teknis

- Model mengeluarkan teks; SDK yang menangani protokol/provider mapping.
- Tool schema dan permission berasal dari aplikasi.
- Selalu fail closed terhadap invalid envelope, tool tak dikenal, schema violation, dan allowlist violation.
- Approval adalah per-call dan harus dilakukan oleh host.
- Provider IDs harus tetap terkorelasi dengan BYV-FP call IDs.
- Jangan menjalankan kode/tool dari model secara langsung.
- Satu eksperimen mengubah sesedikit mungkin variabel.
- Pisahkan metrik struktural dari semantic quality.

## 6. Status eksperimen lama

Run Qwen3-1.7B/DSML adalah baseline historis saja. Angka training/evaluation di dalam experiment log tidak mewakili performa BYV-FP atau Qwen3-4B-Thinking-2507.

## 7. Model references

- Qwen3-4B-Thinking-2507: https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507
- Qwen3-4B-Instruct-2507: https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507 (non-thinking variant)
