<!-- babydocs:start -->
<!-- babydocs:hash={{HASH_FILE}} -->
<!--
  HALAMAN DETAIL KOMPONEN / CLASS / FILE (fleksibel — hapus bagian yang tidak relevan, tambah bagian ekstra bila membantu)
-->

# `{{NAMA_KOMPONEN_ATAU_CLASS}}`

> {{SATU_KALIMAT_NATURAL — apa fungsinya dan kapan sebaiknya dipakai}}

📁 `{{PATH_FILE_DARI_ROOT}}` · ← Kembali ke [{{NAMA_FOLDER}}](./README.md)

---

<!-- OPSIONAL (WAJIB untuk komponen UI): screenshot ter-crop ke komponennya saja, tampilkan variasi utama -->
## Tampilan

![Tampilan {{NAMA_KOMPONEN_ATAU_CLASS}}](/assets/{{path-folder}}/{{nama-komponen}}.png)

*{{Varian/keadaan yang tampil di gambar, mis. filled, tonal, outlined, text, loading, disabled.}}*

---

## Cara Kerjanya di Dalam Kode

{{2–4 kalimat pengantar yang santai, lalu uraikan alur nyata di dalam kode (if/else, validasi, state, fallback, alasan desain):}}

1. **{{Alur utama}}** — {{penjelasan singkat}} (`{{method/baris logika}}`)
2. **{{Saat loading / disabled / kosong}}** — {{penjelasan singkat}} (`{{kondisi}}`)
3. **{{Kasus khusus / kompatibilitas / layar kecil-besar}}** — {{penjelasan singkat}} (`{{kondisi}}`)

---

## Dipakai di Mana Saja

<!-- Hasil pencarian nyata dari rg/grep di codebase -->
Dipakai di **{{JUMLAH}} file**, antara lain:
- `{{path/file_1}}` — {{dipakai untuk apa}}
- `{{path/file_2}}` — {{dipakai untuk apa}}

---

## Props / Parameter & Varian

| Parameter | Tipe | Default / Wajib | Fungsinya |
|---|---|---|---|
| `{{param1}}` | `{{String}}` | **Wajib** | {{penjelasan}} |
| `{{param2}}` | `{{bool}}` | `false` | {{efeknya jika true}} |

<!-- OPSIONAL: jika punya named constructor / enum varian -->
### Varian / Named Constructor

| Varian | Kapan Dipakai | Bedanya |
|---|---|---|
| `{{Komponen.varianA}}` | {{skenario}} | {{perbedaan utama}} |

---

<!-- OPSIONAL: jika punya method/helper publik -->
## Method & Fungsi

| Nama | Input | Output / Efek | Cara Kerjanya |
|---|---|---|---|
| `{{methodA(x)}}` | `{{x: Tipe}}` | `{{Return / efek}}` | {{penjelasan}} |

---

## Contoh Pakai

**Dasar:**

```{{bahasa}}
{{CONTOH_DASAR}}
```

**Skenario khusus (mis. loading / disabled / custom):**

```{{bahasa}}
{{CONTOH_LANJUTAN}}
```

<!-- babydocs:end -->
