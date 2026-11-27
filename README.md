# 🧸 babydocs

**Agent Skill universal** yang mengubah seluruh codebase (bahasa & framework apa pun) menjadi **web dokumentasi interaktif** ala Swagger/Docsify — dijelaskan dengan gaya **ELI5** (analogi sehari-hari, bahasa super sederhana), dilengkapi **visual otomatis**, dan terstruktur **per folder**.

```
Kode rumit  ──►  🤖 Agent + skill ini  ──►  📚 Web docs yang bisa dibaca nenekmu
```

## ✨ Fitur

| Fitur | Penjelasan |
|---|---|
| 🔍 Auto-detect stack | Baca `package.json`, `pubspec.yaml`, `go.mod`, `*.csproj`, `requirements.txt`, `Cargo.toml`, dll. lalu tentukan tipe: `web-ui`, `mobile-ui`, `backend-api`, `cli-library` |
| 🧸 Gaya ELI5 + akurat | Setiap analogi wajib diikuti baris `🔧 Aslinya:` berisi nama file/fungsi/props asli |
| 📸 Visual otomatis | Web → screenshot Playwright · Mobile → golden test / simulator · Backend/CLI → diagram Mermaid + contoh input/output |
| 📂 Per folder, bottom-up | `README.md` di tiap folder fitur, lalu dirangkum ke atas |
| 🌐 Web tanpa build | `index.html` Docsify + `_sidebar.md` + Search + Copy Code + Mermaid, siap GitHub Pages |
| ♻️ Aman & bisa diulang | Tidak menyentuh source code; konten dibungkus penanda sehingga README buatan manusia tidak tertimpa |

## 📁 Struktur Repo

```
babydocs/
├── SKILL.md                            # Instruksi utama untuk AI agent
├── README.md                           # File ini
├── install.sh                          # Pasang perintah `babydocs` ke PATH
├── bin/
│   ├── babydocs                        # CLI: serve, init, check, scan
│   └── babydocs.cmd                    # Versi Windows
├── scripts/
│   └── scan.py                         # Scanner cepat: stack + peta folder + kerangka kode (Python stdlib)
└── templates/
    ├── index.html                      # Docsify (Search, Copy Code, Mermaid, Zoom)
    ├── folder-readme-template.md       # Template README per sub-folder
    ├── root-readme-template.md         # Template halaman depan
    └── _sidebar-template.md            # Contoh format sidebar
```

## 📦 Instalasi

Skill ini mengikuti format standar **Agent Skills** (folder berisi `SKILL.md` dengan frontmatter `name` + `description`). Salin/clone foldernya ke direktori skill milik agent yang kamu pakai:

| Agent | Lokasi skill global | Lokasi skill per proyek |
|---|---|---|
| Antigravity | `~/.gemini/antigravity/skills/babydocs/` | `<proyek>/.agents/skills/babydocs/` |
| Claude Code | `~/.claude/skills/babydocs/` | `<proyek>/.claude/skills/babydocs/` |
| Gemini CLI | `~/.gemini/skills/babydocs/` | `<proyek>/.gemini/skills/babydocs/` |
| Codex / Cursor / lainnya | Folder skill/rules agent tsb. | Atau rujuk langsung: *"ikuti instruksi di `/path/babydocs/SKILL.md`"* |

Contoh (global, via symlink agar mudah di-update):

```bash
git clone <url-repo-ini> ~/skills/babydocs
mkdir -p ~/.claude/skills
ln -s ~/skills/babydocs ~/.claude/skills/babydocs
```

> Pastikan folder `templates/`, `scripts/`, dan `bin/` ikut tersalin — `SKILL.md` merujuk ke sana.

### Pasang perintah `babydocs` di terminal

```bash
cd ~/skills/babydocs
./install.sh                 # memasang ke ~/.local/bin/babydocs
babydocs --help
```

Windows: tambahkan folder `bin/` ke `PATH` (berisi `babydocs.cmd`).

## 🚀 Cara Memanggil

Buka proyek yang ingin didokumentasikan di coding agent, lalu ketik salah satu:

```text
/babydocs
```

```text
Pakai skill babydocs untuk mendokumentasikan seluruh codebase ini.
```

```text
Jalankan babydocs, tapi hanya untuk folder src/features/payment.
```

```text
Update dokumentasi babydocs untuk perubahan sejak commit terakhir.
```

Agent akan menjalankan:

```mermaid
flowchart LR
    f1["Fase 1: Deteksi stack & peta folder"] --> f2["Fase 2: README per folder (bottom-up) + visual"]
    f2 --> f3["Fase 3: README root, _sidebar.md, index.html"]
    f3 --> f4["Fase 4: Verifikasi tautan, gambar, Mermaid"]
```

## ⚡ Kenapa Cepat di Codebase Besar

Agent **tidak** membuka file satu per satu. Alurnya begini:

1. **Scanner satu perintah**: `scripts/scan.py` (hanya Python standard library, tidak perlu install apa-apa) menghasilkan *Peta Proyek* berisi stack, Folder Dok yang sudah diurutkan bottom-up, dan **kerangka** tiap file (class/fungsi/export, route API, import lokal, jumlah baris, tanda UI). Di proyek ±700 file / 110 ribu baris, scanner selesai dalam beberapa detik.
2. **Baca bertingkat**: file kecil/DTO cukup dari kerangka, file sedang dibaca utuh sekali, file besar hanya bagian yang dicari dengan `grep`.
3. **Lewati yang tidak berubah**: setiap README menyimpan `<!-- babydocs:hash=... -->`. Saat skill dijalankan ulang, folder yang hash-nya cocok langsung dilewati.
4. **Kerja paralel**: kalau agent-mu mendukung sub-agent, tiap sub-pohon besar (mis. `src/modules/auth`) dikerjakan sub-agent terpisah secara bersamaan.

Coba scanner-nya langsung:

```bash
babydocs scan /path/ke/proyek --out /tmp/peta.md
babydocs scan /path/ke/proyek --only src/features --json
```

## 🧰 Dependensi Opsional

Tidak ada dependensi wajib. Visual dipilih otomatis; jika alat tidak tersedia, skill jatuh ke diagram Mermaid.

| Untuk | Alat | Instalasi |
|---|---|---|
| Scanner cepat (disarankan) | Python 3.8+ | biasanya sudah ada di macOS/Linux |
| Screenshot web | [Playwright](https://playwright.dev) (CLI atau MCP) | `npx playwright install chromium` |
| Screenshot Flutter | Flutter SDK (golden test) | sudah termasuk `flutter_test` |
| Screenshot iOS | Xcode + Simulator | `xcrun simctl` |
| Screenshot Android | Android SDK Platform Tools | `adb` |
| Preview docs | Python 3.8+ | `babydocs serve` (sudah termasuk) |
| Validasi Mermaid (opsional) | `@mermaid-js/mermaid-cli` | `npx @mermaid-js/mermaid-cli` |

## 💻 Perintah `babydocs`

| Perintah | Fungsi |
|---|---|
| `babydocs serve` | Buka web dokumentasi di `http://localhost:3000` (live reload otomatis) |
| `babydocs serve --open` | Sama, sekaligus membuka browser |
| `babydocs serve -p 8080` | Pakai port lain (jika port terpakai, otomatis pindah ke port berikutnya) |
| `babydocs serve --host 0.0.0.0` | Bisa dibuka dari HP/laptop lain di Wi-Fi yang sama |
| `babydocs init` | Pasang `index.html` + `.nojekyll` di proyek |
| `babydocs check` | Cek link sidebar, gambar, placeholder yang tertinggal |
| `babydocs scan` | Buat Peta Proyek (dipakai agent) |

## 👀 Preview Web Dokumentasi Secara Lokal

Setelah skill selesai, di root proyek kamu akan ada `index.html`, `_sidebar.md`, `README.md`, dan `.nojekyll`. Jalankan:

```bash
cd /path/ke/proyek
babydocs serve
# buka http://localhost:3000
```

> ⚠️ Jangan buka `index.html` dengan klik dua kali (`file://`) — dokumentasi harus dibuka lewat `babydocs serve` atau GitHub Pages.
>
> Jika proyek sudah punya `index.html` sendiri (mis. Vite), skill membuat `docs.html` sebagai gantinya — `babydocs serve` otomatis membuka halaman yang benar.

### Publikasi ke GitHub Pages

1. Commit & push `index.html`, `_sidebar.md`, `.nojekyll`, semua `README.md` dan folder `assets/`.
2. GitHub → **Settings → Pages → Build and deployment → Deploy from a branch** → pilih branch dan folder `/ (root)`.
3. Buka `https://<user>.github.io/<repo>/`.

## 🛡️ Jaminan Keamanan

- Tidak pernah mengubah source code — hanya `README.md`, `assets/*.png`, `_sidebar.md`, `index.html`/`docs.html`, `.nojekyll`.
- File sementara (script screenshot, golden test) dihapus otomatis.
- Konten buatan skill dibungkus `<!-- babydocs:start -->` … `<!-- babydocs:end -->`, sehingga isi README yang ditulis manusia tetap aman saat skill dijalankan ulang.
- Kredensial asli tidak pernah dimasukkan ke dokumentasi atau screenshot.

## 📝 Lisensi

MIT
