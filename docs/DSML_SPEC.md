# DSML Behavior & Format Specification

Status: **draft**. Dokumen ini merekam tujuan yang disepakati; grammar lengkap masih perlu dikonfirmasi dengan contoh implementasi nyata.

## 1. Perilaku model

Model harus mendukung dua mode berdasarkan instruksi:

### Plain text mode
Jika pengguna meminta jawaban biasa atau tidak meminta DSML, assistant menjawab dengan teks biasa. Jangan tambahkan DSML tags secara otomatis.

### DSML text mode
Jika pengguna secara eksplisit meminta DSML, assistant boleh menghasilkan teks natural-language diikuti blok DSML sesuai protokol yang ditetapkan.

DSML merupakan bagian dari assistant text content. Ini bukan native tool call, bukan OpenAI tool_calls, dan bukan Anthropic tool-use content block.

## 2. Contoh DSML referensi

Gunakan sintaks contoh berikut sebagai bentuk referensi; jangan mengganti tag atau nama tanpa revisi spesifikasi:

```text
The structure checks all pass and the CRLF artifact is gone.

One last check: I'll compare against the reference with CRs stripped, then run the script.

<｜DSML｜ calls>
<｜DSML｜ invoke name="mcp__workspace__bash">
<｜DSML｜ parameter name="command" string="true">cd /workspace/project && python3 fmt.py</｜DSML｜ parameter>
<｜DSML｜ invoke>
<｜DSML｜ calls>
```

Nama tool dan command hanya contoh tekstual. Tidak boleh dianggap tersedia atau dijalankan tanpa executor yang sesuai.

## 3. Aturan training data

- Plain text examples harus benar-benar tidak memiliki DSML.
- DSML examples harus memakai format yang benar dan konsisten.
- Sertakan contoh yang meminta DSML secara eksplisit.
- Sertakan contoh yang meminta teks biasa, termasuk setelah turn DSML sebelumnya.
- Jangan memasukkan native tool-call metadata; seluruh output assistant berada pada content.
- Assistant response dapat berisi penjelasan sebelum DSML jika protokol mengizinkan.
- Jangan ajarkan model mengarang hasil eksekusi. Jika tool belum dijalankan, model tidak boleh menyatakan hasil seolah-olah sudah terjadi.

## 4. Validasi dan keamanan

Parser harus memeriksa:
- Pembukaan dan penutupan blok.
- Struktur invoke dan parameter.
- Tool name dari allowlist.
- Parameter berdasarkan schema.
- Ukuran input dan batas jumlah aksi.
- Izin dan policy sebelum eksekusi.
- Penanganan output tool dan error.

Jangan mengandalkan model sebagai lapisan keamanan. Output model adalah data yang tidak tepercaya.

## 5. Pertanyaan terbuka sebelum grammar dibekukan

- Apakah marker tag memiliki spasi persis seperti contoh?
- Apakah satu output boleh berisi beberapa invoke?
- Bagaimana escaping untuk teks yang mengandung marker DSML?
- Bagaimana menandai akhir satu aksi dan akhir satu batch?
- Apakah reasoning harus ditampilkan, diringkas, atau hanya jawaban akhir?
- Bagaimana menandai aksi yang belum disetujui atau memerlukan konfirmasi?

Jangan membuat asumsi grammar yang belum diputuskan; catat keputusan berikutnya di changelog.
