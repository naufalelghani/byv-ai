# DSML Behavior & Format Specification

Status: **draft**. Dokumen ini merekam tujuan yang disepakati; grammar lengkap masih perlu dikonfirmasi dengan contoh implementasi nyata.

## 1. Perilaku model

Model harus mendukung dua mode berdasarkan instruksi:

### Plain text mode
Jika pengguna meminta jawaban biasa atau tidak meminta DSML, assistant menjawab dengan teks biasa. Jangan tambahkan DSML tags secara otomatis.

### DSML text mode
Jika instruksi dan konteks tool yang diberikan aplikasi menunjukkan bahwa suatu tool diperlukan, assistant menghasilkan DSML sebagai teks di dalam assistant content. Jika tidak ada tool yang diperlukan, assistant menjawab dengan teks biasa.

DSML merupakan bagian dari assistant text content. Ini bukan native tool call, bukan OpenAI `tool_calls`, dan bukan Anthropic tool-use content block. Model hanya menghasilkan teks; parser dan executor berada di aplikasi BYV-AI.

## 2. Dynamic tool instructions

Aplikasi dapat menyisipkan daftar tool yang tersedia ke prompt untuk setiap request. Setiap definisi tool memberikan nama, deskripsi, dan parameter/schema yang boleh digunakan model untuk menyusun DSML.

Contoh implementasi prompt builder dari pemilik proyek, aturan wajib, contoh plain-text, dan contoh DSML dicatat di [Dynamic Tool Instructions & DSML Prompt](DYNAMIC_TOOL_PROMPT.md).

Prinsip:

- Daftar tool adalah konteks dinamis per request, bukan kemampuan tool bawaan model.
- Model hanya boleh memilih tool yang tercantum pada prompt saat itu.
- Model harus menggunakan nama tool dan nama parameter persis seperti definisi yang diberikan.
- Jika tidak ada tool, model harus menjawab dengan teks biasa.
- Jika hasil tool sebelumnya sudah cukup, model harus memberikan jawaban akhir tanpa membuat invoke tambahan.
- Jika invoke berikutnya bergantung pada hasil invoke sebelumnya, model harus menunggu hasil tersebut sebelum melanjutkan.
- Seluruh DSML tetap berada dalam assistant text content; jangan gunakan native function/tool-call metadata.

## 3. Contoh DSML referensi

Gunakan sintaks contoh berikut sebagai bentuk referensi; jangan mengganti tag atau nama tanpa revisi spesifikasi:

```text
The structure checks all pass and the CRLF artifact is gone.

One last check: I'll compare against the reference with CRs stripped, then run the script.

<｜DSML｜ calls>
<｜DSML｜ invoke name="Bash">
<｜DSML｜ parameter name="command" string="true">npm run check</｜DSML｜ parameter>
<｜DSML｜ parameter name="description" string="true">Run npm run check in the repository root</｜DSML｜ parameter>
</｜DSML｜ invoke>
</｜DSML｜ calls>
```

Contoh Bash ini mengikuti format kanonis yang diberikan pemilik BYV-AI. Parameter `description` disertakan karena parameter tersebut dideklarasikan pada schema Bash dalam contoh. Nama tool dan command hanya contoh tekstual; keduanya tidak dianggap tersedia atau dijalankan tanpa schema aktif dan executor yang sesuai.

## 4. Aturan training data

- Plain text examples harus benar-benar tidak memiliki DSML.
- DSML examples harus memakai format yang benar dan konsisten.
- Sertakan contoh yang meminta DSML secara eksplisit atau menyediakan daftar tool dan instruksi yang membutuhkan tool.
- Sertakan contoh yang meminta teks biasa, termasuk setelah turn DSML sebelumnya.
- Jangan memasukkan native tool-call metadata; seluruh output assistant berada pada content.
- Assistant response dapat berisi penjelasan sebelum DSML hanya jika prompt mengizinkannya; aturan dynamic tool prompt saat ini melarang prose di dalam tool calls response.
- Jangan ajarkan model mengarang hasil eksekusi. Jika tool belum dijalankan, model tidak boleh menyatakan hasil seolah-olah sudah terjadi.
- Sertakan contoh ketika tool tidak tersedia, parameter wajib belum ada, atau hasil tool belum tersedia; model tidak boleh mengarang tool maupun nilai parameter.

## 5. Validasi dan keamanan

Parser harus memeriksa:
- Pembukaan dan penutupan blok.
- Struktur invoke dan parameter.
- Tool name dari allowlist untuk request saat ini.
- Parameter berdasarkan schema tool yang sebenarnya.
- Ukuran input dan batas jumlah aksi.
- Izin dan policy sebelum eksekusi.
- Penanganan output tool dan error.

Jangan mengandalkan model sebagai lapisan keamanan. Output model adalah data yang tidak tepercaya.

## 6. Pertanyaan terbuka sebelum grammar dibekukan

- Apakah marker tag memiliki spasi persis seperti contoh?
- Apakah satu output boleh berisi beberapa invoke independen?
- Bagaimana escaping untuk teks parameter yang mengandung marker DSML atau tag penutup?
- Bagaimana menandai akhir satu aksi dan akhir satu batch?
- Apakah reasoning harus ditampilkan, diringkas, atau hanya jawaban akhir?
- Bagaimana menandai aksi yang belum disetujui atau memerlukan konfirmasi?

Jangan membuat asumsi grammar yang belum diputuskan; catat keputusan berikutnya di changelog.
