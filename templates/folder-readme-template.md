<!-- babydocs:start -->
<!-- babydocs:hash={{HASH_FOLDER_DARI_PETA_PROYEK}} -->
<!--
  KOTAK BAHAN (BUILDING BLOCKS) README SUB-FOLDER — FLEKSIBEL, JANGAN PUKUL RATA!
  - Pilih HANYA bagian yang relevan untuk jenis folder ini. Hapus bagian yang tidak perlu (mis. skip diagram jika folder cuma kumpulan komponen independen/konstanta).
  - Boleh menambah bagian ekstra seperti "Kenapa Dibuat Seperti Ini?", "Kapan Pakai A vs B?", atau "Penanganan Error & Edge Case".
  - Pakai bahasa Indonesia yang santai & natural (hindari terjemahan kaku seperti "Widget Bersama" atau "Berkas").
  - Jika folder berisi > 5 komponen reusable/class penting, buat halaman detail terpisah (<nama>.md) dan tautkan dari sini & _sidebar.md.
-->

# {{NAMA_FOLDER_NATURAL}}

> {{SATU_KALIMAT_JELAS — peran nyata folder ini}}

📁 `{{PATH_FOLDER_DARI_ROOT}}` · `{{web-ui | mobile-ui | backend-api | cli-library}}`

---

## Gambaran Singkat

{{2–5 kalimat santai (dengan analogi jika membantu) menjelaskan cara kerja folder ini secara keseluruhan.}}

> 🔧 **Di kode:** {{entry/class/komponen utama dan hubungannya dengan bagian lain}}

---

<!-- OPSIONAL: tampilkan jika ada screenshot (crop komponen untuk reusable UI, full page untuk screen) -->
## Tampilan

![{{Deskripsi gambar}}](./assets/{{nama-gambar}}.png)

*{{Keterangan singkat apa yang tampil di gambar.}}*

---

<!-- OPSIONAL: HANYA buat diagram jika benar-benar ada alur multi-langkah / state / interaksi nyata. HAPUS jika tidak perlu! -->
## Alur Kerja

```mermaid
flowchart TD
    masuk["{{Langkah awal nyata}} ({{SimbolAwal}})"] --> proses["{{Proses nyata}} ({{MethodProses}})"]
    proses --> cek{"{{Kondisi nyata}}?"}
    cek -- "Ya" --> ok["{{Hasil sukses}} ({{OutputOk}})"]
    cek -- "Tidak" --> gagal["{{Hasil gagal}} ({{OutputGagal}})"]
```

---

<!-- WAJIB untuk folder yang punya komponen/class/fungsi: bedah satu per satu, ATAU tautkan ke halaman detail ./<nama>.md -->
## Bedah Komponen, Class & Fungsi

### 1. `{{NamaKomponenAtauClass}}`

{{Penjelasan santai + analogi bila membantu.}}

> 🔧 **Di kode:** `{{nama_file.ext}}` → `{{deklarasi asli}}`

<!-- OPSIONAL: screenshot crop khusus komponen ini -->
![Tampilan {{NamaKomponenAtauClass}}](./assets/{{nama-komponen}}.png)

**Dipakai di mana saja:** {{hasil pencarian rg/grep nyata, mis. "Dipakai di 9 layar: `login_screen.dart`, `register_screen.dart`, ..."}}

**Cara kerja di dalam kode:**
1. {{Alur nyata langkah 1}} (`{{kondisi/method}}`)
2. {{Alur nyata langkah 2 — termasuk kasus khusus seperti loading, disabled, error, fallback}} (`{{kondisi/method}}`)

**Props / Parameter:**

| Nama | Tipe | Default / Wajib | Fungsinya |
|---|---|---|---|
| `{{prop1}}` | `{{String}}` | **Wajib** | {{penjelasan singkat}} |

**Method / Aksi:**

| Method | Input | Output / Efek | Cara Kerjanya |
|---|---|---|---|
| `{{methodA(x)}}` | `{{x: Tipe}}` | `{{Return / state / API call}}` | {{penjelasan singkat}} |

**Contoh pakai:**

```{{bahasa}}
{{CONTOH_NYATA}}
```

---

<!-- OPSIONAL: bagian tambahan yang bikin pembaca makin paham -->
## Kapan Pakai X vs Y?

| Situasi | Pakai | Alasannya |
|---|---|---|
| {{kasus 1}} | `{{KomponenA}}` | {{alasan singkat}} |
| {{kasus 2}} | `{{KomponenB}}` | {{alasan singkat}} |

---

## Daftar File

| File | Isi Utama | Detail |
|---|---|---|
| `{{file_1.ext}}` | `{{ClassA}}` | [Lihat](#_1-classa) *(atau `[Lihat](./class_a.md)`)* |

<!-- OPSIONAL: hapus jika tidak punya sub-folder ber-README -->
### Sub-folder

| Folder | Fokusnya | Buka |
|---|---|---|
| `{{nama-subfolder}}` | {{ringkasan 1 kalimat}} | [Lihat]({{path/dari/root/ke/subfolder/README.md}}) |

<!-- babydocs:end -->
