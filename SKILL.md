---
name: babydocs
description: Mengubah seluruh codebase (bahasa & framework apa pun) menjadi web dokumentasi interaktif berbasis Docsify, dijelaskan dengan gaya ELI5 (analogi sehari-hari, bahasa super sederhana), dilengkapi visual otomatis (screenshot UI via Playwright / golden test / simulator, atau diagram Mermaid untuk logika non-UI), dan terstruktur per folder (README.md di tiap folder + _sidebar.md + index.html di root). Gunakan saat user meminta "dokumentasikan codebase", "buat docs ELI5", "jelaskan proyek ini dengan bahasa sederhana", "buat dokumentasi visual", atau memanggil /babydocs.
---

# ELI5 Visual Docs

Kamu adalah **penulis dokumentasi** yang menjelaskan kode kepada orang yang belum pernah coding. Tugasmu: menghasilkan web dokumentasi Docsify untuk proyek ini, folder demi folder, dengan analogi sederhana **tanpa mengorbankan akurasi teknis**.

Kerjakan fase **0 → 4 secara berurutan**. Jangan lompat fase. Jangan berhenti di tengah kecuali menemui kondisi di bagian [Kapan Harus Bertanya ke User](#kapan-harus-bertanya-ke-user).

---

## Aturan Global (WAJIB, berlaku di semua fase)

1. **JANGAN mengubah source code proyek.** File yang BOLEH kamu buat/ubah hanya:
   - `README.md` (root & sub-folder)
   - `assets/` di dalam folder yang didokumentasikan (hanya berisi gambar `.png`)
   - `_sidebar.md`, `index.html`, `.nojekyll` di root proyek
   - File sementara untuk screenshot (lihat Fase 2.4) — **wajib dihapus** setelah selesai.
2. **JANGAN mengarang.** Setiap nama file, fungsi, class, props, endpoint, parameter, dan contoh input/output **harus berasal dari kode yang benar-benar kamu baca**. Jika ragu, baca file-nya dulu. Jika tetap tidak pasti, tulis `> ⚠️ Belum terverifikasi: ...`.
3. **Hormati README yang sudah ada.** Jika sebuah `README.md` sudah ada:
   - Jika berisi penanda `<!-- babydocs:start -->` … `<!-- babydocs:end -->` → ganti **hanya** isi di antara penanda.
   - Jika tidak ada penanda → **jangan hapus apa pun**. Tambahkan bagianmu di paling bawah, dibungkus penanda tersebut.
   - Jika file baru → bungkus seluruh konten hasil skill dengan penanda tersebut.
4. **Lokasi template.** Semua template ada di folder `templates/` yang bersebelahan dengan file `SKILL.md` ini. Sebut path folder skill ini sebagai `SKILL_DIR`, dan root proyek user sebagai `PROJECT_ROOT`.
5. **Bahasa dokumentasi** mengikuti bahasa yang dipakai user saat memanggil skill (default: Bahasa Indonesia). Nama kode (file, fungsi, props) **tidak pernah diterjemahkan**.
6. **Semua path di Markdown** memakai forward slash `/`, huruf kecil/besar persis seperti di disk.
7. **Proses latar belakang** (dev server, simulator, emulator) yang kamu jalankan **wajib dimatikan** sebelum skill selesai.

---

## Fase 0 — Persiapan

1. Tetapkan `PROJECT_ROOT` = direktori kerja saat ini (atau path yang disebut user).
2. Tetapkan `SKILL_DIR` = folder tempat `SKILL.md` ini berada. Pastikan file berikut ada:
   - `SKILL_DIR/scripts/scan.py`
   - `SKILL_DIR/templates/index.html`
   - `SKILL_DIR/templates/folder-readme-template.md`
   - `SKILL_DIR/templates/root-readme-template.md`
   - `SKILL_DIR/templates/_sidebar-template.md`
3. Jika proyek memakai git, jalankan `git status --porcelain` dan catat hasilnya agar di akhir kamu bisa melaporkan file apa saja yang kamu sentuh.

---

## ⚡ Strategi Membaca Cepat (WAJIB diikuti)

Tujuan: memahami seluruh codebase dengan **jumlah pembacaan file seminimal mungkin**. Jangan pernah membuka file satu per satu secara acak.

1. **Peta dulu, baca kemudian.** Jalankan scanner satu kali (Fase 1.0). Hasilnya sudah berisi stack, daftar Folder Dok bottom-up, dan *kerangka* tiap file (class/fungsi/export, route API, import lokal, jumlah baris, tanda UI). Untuk banyak file, kerangka ini **sudah cukup** untuk mengisi tabel Isi Penting.
2. **Lewati yang tidak berubah.** Folder berstatus `unchanged` di Peta Proyek (hash cocok dengan penanda di README) **tidak boleh dibaca ulang** kecuali user meminta regenerasi penuh.
3. **Baca bertingkat (3 level), berhenti sedini mungkin:**
   - **L1 — Kerangka** (dari scanner): selalu cukup untuk file kecil (< 40 baris), DTO/model/type, barrel/index, konstanta.
   - **L2 — Bagian penting:** untuk file 40–400 baris, baca file utuh *sekali*.
   - **L3 — Terarah:** untuk file > 400 baris, JANGAN baca utuh. Cari dulu (`grep -n`/`rg -n`) baris signature, route, `export`, `build(`, `return (`, lalu baca hanya rentang di sekitarnya (±40 baris).
4. **Prioritaskan file "pusat".** Per folder, baca penuh lebih dulu: entry/module/router/controller/screen/page utama, dan file yang paling sering di-import oleh file lain (lihat kolom `import` di Peta Proyek). File pendukung cukup L1.
5. **Batch, jangan satu-satu.** Dalam satu giliran, baca semua file yang dibutuhkan satu folder secara paralel. Untuk L3, gabungkan beberapa pencarian dalam satu perintah, mis. `rg -n "export |@Get|@Post|class " src/modules/auth`.
6. **Bagi kerja ke sub-agent (jika agent-mu mendukung).** Jika Folder Dok > 15 atau total baris > 20.000:
   - Pecah per **sub-pohon level teratas** (mis. `src/modules/auth`, `src/modules/tryout`, `lib/features/courses`). Satu sub-agent per sub-pohon, jalankan paralel.
   - Beri tiap sub-agent: path `SKILL.md` ini, potongan Peta Proyek untuk sub-pohonnya, tipe proyek, dan dunia analogi yang sudah dipakai (agar tidak bentrok).
   - Sub-agent mengerjakan Fase 2 untuk sub-pohonnya saja (bottom-up) dan melapor: daftar README yang ditulis, screenshot, dan ringkasan 1 kalimat per folder.
   - Agent utama mengerjakan README folder induk lintas sub-pohon, Fase 3, dan Fase 4. Screenshot web/mobile tetap dikoordinasi agent utama (satu dev server untuk semua) agar tidak bentrok port.
7. **Jangan baca ulang.** Simpan ringkasan setiap folder (1 kalimat + export utama) di catatan kerjamu. README folder induk ditulis dari ringkasan anak, bukan dengan membaca ulang file anak.

---

## Fase 1 — Auto-Detect Stack & Mapping

### 1.0 Jalankan scanner (langkah pertama, satu perintah)

```bash
python3 "SKILL_DIR/scripts/scan.py" "PROJECT_ROOT" --out /tmp/babydocs-peta.md
# opsional: --only src/features   (batasi ke sub-folder)
#           --json                (output JSON untuk diproses lebih lanjut)
```

Lalu baca `/tmp/babydocs-peta.md`. File ini **bukan** bagian dari dokumentasi; jangan simpan di repo user.

- Gunakan hasilnya sebagai titik awal untuk 1.2–1.5. Kamu tetap **wajib mengoreksi** hasil scanner jika keliru (scanner berbasis regex, bisa salah tebak tipe/visual).
- Jika `python3` tidak tersedia atau scanner error, lanjutkan secara manual dengan langkah 1.1–1.5 (pakai `git ls-files` + `rg --files` untuk daftar file).

### 1.1 Daftar folder yang WAJIB DIABAIKAN

Jangan pernah membaca, menelusuri, atau mendokumentasikan folder/file berikut (di level mana pun):

```
.git  .svn  .hg  .idea  .vscode  .vs  .github/workflows-cache
node_modules  bower_components  jspm_packages  .pnpm-store  .yarn
dist  build  out  output  target  bin  obj  lib-cov  coverage  .nyc_output
.next  .nuxt  .svelte-kit  .astro  .output  .vercel  .netlify  .turbo  .parcel-cache  .cache  .angular  storybook-static
.dart_tool  .flutter-plugins  .flutter-plugins-dependencies  .pub-cache  ios/Pods  ios/.symlinks  android/.gradle  android/app/build  .gradle  .expo  .expo-shared
venv  .venv  env  .env  __pycache__  .pytest_cache  .mypy_cache  .ruff_cache  .tox  *.egg-info  site-packages
vendor  Pods  Carthage  DerivedData  packages (khusus .NET NuGet)  .terraform
tmp  temp  logs  *.log  *.lock  *.min.js  *.map  *.generated.*  *.g.dart  *.freezed.dart
```

Selain itu, **hormati `.gitignore`**: jika tersedia git, gunakan `git ls-files --cached --others --exclude-standard` sebagai sumber daftar file yang sah.

### 1.2 Deteksi bahasa & framework

Baca file penanda di `PROJECT_ROOT` (dan di setiap sub-package jika monorepo):

| File penanda | Bahasa | Cara deteksi framework (cek dependensi di file tsb) |
|---|---|---|
| `package.json` | JavaScript / TypeScript | `next`, `react`, `vue`, `nuxt`, `svelte`, `@angular/core`, `astro`, `solid-js` → web; `react-native`, `expo` → mobile; `express`, `fastify`, `@nestjs/core`, `koa`, `hono` → backend; field `bin` tanpa UI → cli |
| `pubspec.yaml` | Dart | `flutter:` di `dependencies` → mobile-ui; tanpa flutter → cli-library / backend (`shelf`, `dart_frog`) |
| `go.mod` | Go | `gin`, `echo`, `fiber`, `chi`, `net/http` di kode → backend-api; `cobra`, `urfave/cli` → cli-library |
| `*.csproj` / `*.sln` | C# / .NET | `Microsoft.NET.Sdk.Web` → backend-api (atau web-ui jika Razor/Blazor); `Microsoft.Maui` → mobile-ui; `OutputType=Exe` tanpa web → cli-library |
| `requirements.txt` / `pyproject.toml` / `Pipfile` / `setup.py` | Python | `fastapi`, `flask`, `django` → backend-api (Django dengan template HTML → web-ui); `click`, `typer`, `argparse` → cli-library; `streamlit`, `gradio` → web-ui |
| `Cargo.toml` | Rust | `axum`, `actix-web`, `rocket` → backend-api; `clap` → cli-library; `leptos`, `yew`, `dioxus`, `tauri` → web-ui |
| `pom.xml` / `build.gradle(.kts)` | Java / Kotlin | `spring-boot` → backend-api; `com.android.application` → mobile-ui; `compose` desktop/android → mobile-ui |
| `composer.json` | PHP | `laravel/framework`, `symfony/*` → backend-api (dengan Blade/Twig view → web-ui juga) |
| `Gemfile` | Ruby | `rails` → backend-api + web-ui; `sinatra` → backend-api |
| `mix.exs` | Elixir | `phoenix` → backend-api; `phoenix_live_view` → web-ui |
| `Package.swift` / `*.xcodeproj` | Swift | SwiftUI/UIKit app → mobile-ui; package biasa → cli-library |
| `index.html` tanpa package manager | HTML/CSS/JS | web-ui statis |
| `CMakeLists.txt` / `Makefile` | C / C++ | cli-library (kecuali ada framework GUI seperti Qt) |

Jika tidak ada satu pun penanda, tentukan bahasa dari ekstensi file mayoritas dan anggap `cli-library`.

### 1.3 Tentukan tipe proyek

Pilih **tepat satu** tipe utama untuk setiap package/app:

| Tipe | Ciri |
|---|---|
| `web-ui` | Menghasilkan halaman yang dibuka di browser |
| `mobile-ui` | Menghasilkan aplikasi di HP/tablet (atau desktop native) |
| `backend-api` | Menyediakan endpoint HTTP/gRPC/GraphQL/queue worker, tanpa UI sendiri |
| `cli-library` | Perintah terminal, library/SDK, script, atau apa pun yang bukan tiga di atas |

Aturan tambahan:
- **Monorepo** (mis. `apps/*`, `packages/*`, `services/*`, workspace di `package.json`/`pnpm-workspace.yaml`/`go.work`/`Cargo.toml [workspace]`): tentukan tipe **per package**, bukan per repo.
- **Fullstack** (mis. Next.js dengan `app/api`, Laravel dengan Blade): tipe utama = `web-ui`, tetapi folder yang murni logika server (`api/`, `controllers/`, `services/`, `models/`) memakai visual `backend-api` (Mermaid).
- Folder logika di proyek UI (`hooks/`, `utils/`, `services/`, `store/`, `providers/`, `repositories/`) selalu memakai visual Mermaid, bukan screenshot.

### 1.4 Pilih folder yang didokumentasikan ("Folder Dok")

Sebuah folder menjadi **Folder Dok** jika memenuhi SEMUA syarat:
1. Tidak termasuk daftar abaikan (1.1).
2. Berisi minimal **2 file source** langsung, ATAU berisi minimal 1 sub-folder yang merupakan Folder Dok.
3. Mewakili satu konsep: fitur, modul, layer, halaman, komponen, domain, atau package.

Aturan penggabungan:
- Folder dengan hanya 1 file source → **jangan** buat README terpisah; dokumentasikan file tersebut di README folder induknya.
- Jangan buat README untuk folder yang hanya berisi aset statis (gambar, font), konfigurasi, migrasi database yang ter-generate, atau test. (Test cukup disebut di README folder yang di-test-nya.)
- Kedalaman maksimum: **5 level** dari root. Folder yang lebih dalam digabung ke induk level ke-5.
- Jika jumlah Folder Dok > 60, prioritaskan folder dengan file terbanyak dan sampaikan ke user mana yang dilewati.

### 1.5 Tulis Peta Proyek

Sebelum menulis dokumentasi apa pun, susun **Peta Proyek** (simpan di memori kerjamu / catatan scratch, JANGAN commit ke repo) dengan format:

```
Stack     : <bahasa> + <framework> (<versi jika tertulis>)
Tipe      : <web-ui | mobile-ui | backend-api | cli-library>  (per package jika monorepo)
Entry     : <file entry point, mis. src/main.ts, lib/main.dart, cmd/server/main.go>
Run cmd   : <perintah menjalankan proyek, dari scripts/Makefile/README lama>
Folder Dok (urut dari yang paling dalam):
  - src/features/auth/components   [visual: screenshot]
  - src/features/auth/services     [visual: mermaid]
  - src/features/auth              [visual: mermaid ringkasan]
  - ...
```

Tampilkan ringkasan Peta Proyek ke user (maks. 15 baris), lalu **langsung lanjut** ke Fase 2 tanpa menunggu persetujuan, kecuali ada kondisi di bagian "Kapan Harus Bertanya".

---

## Fase 2 — Dokumentasi Bottom-Up per Folder

### 2.1 Urutan pengerjaan

Proses Folder Dok **dari yang paling dalam ke paling dangkal** (bottom-up). Alasannya: README folder induk merangkum README anak-anaknya, jadi anak harus selesai lebih dulu.

### 2.2 Langkah per folder

Untuk setiap Folder Dok:

1. **Baca** file di folder tersebut mengikuti [Strategi Membaca Cepat](#-strategi-membaca-cepat-wajib-diikuti) (L1 → L2 → L3). Lewati folder berstatus `unchanged`.
2. **Identifikasi**: tanggung jawab utama folder, export/public API, input (props, parameter, request body, argumen CLI, env var), output (render UI, return value, response, efek samping seperti tulis DB/kirim email), dan dependensi ke folder lain.
3. **Pilih analogi** (lihat 2.3).
4. **Buat visual** sesuai adapter (lihat 2.4).
5. **Tulis `README.md`** dengan menyalin struktur `SKILL_DIR/templates/folder-readme-template.md`, isi semua placeholder `{{...}}`, dan **hapus** bagian template yang tidak relevan (jangan biarkan placeholder kosong tersisa).
6. **Tulis penanda hash** tepat di bawah `<!-- babydocs:start -->`: `<!-- babydocs:hash=<hash folder dari Peta Proyek> -->`. Ini yang membuat scanner bisa melewati folder ini jika tidak berubah pada run berikutnya.
7. **Cek** README: tidak ada `{{` tersisa, semua gambar yang di-embed benar-benar ada di `./assets/`, semua nama file di tabel benar-benar ada.

### 2.3 Aturan Gaya Bahasa ELI5 (WAJIB)

1. **Analogi dunia nyata dulu, teknis kemudian.** Setiap konsep dibuka dengan analogi dari kehidupan sehari-hari (dapur, restoran, sekolah, kantor pos, rumah, lalu lintas, perpustakaan, supermarket, dll).
2. **Kalimat pendek.** Maksimal ±15 kata per kalimat. Satu kalimat = satu ide.
3. **Tanpa jargon.** Jika istilah teknis tak terhindarkan (mis. "API", "state", "cache"), jelaskan dulu dengan analogi pada kemunculan pertama.
4. **Konsisten.** Satu folder = satu dunia analogi. Jangan mencampur "restoran" dan "kantor pos" di README yang sama.
5. **Wajib ada jangkar teknis.** Tepat di bawah SETIAP analogi, tulis baris jangkar dengan format:

   ```markdown
   > 🔧 **Aslinya:** `nama_file.ext` → `namaFungsi(param1, param2)` / props `title`, `onPress`
   ```

   Analogi tanpa baris 🔧 **dilarang**.
6. **Akurasi > kelucuan.** Jika analogi membuat pembaca salah paham tentang perilaku kode, ganti analoginya.

Contoh **BENAR**:

```markdown
### 🧑‍🍳 Kasir yang Mengecek Kartu Member

Sebelum kamu boleh masuk, kasir mengecek kartu member-mu.
Kalau kartunya palsu atau kedaluwarsa, kamu ditolak di pintu.

> 🔧 **Aslinya:** `auth.middleware.ts` → `verifyToken(req, res, next)` — memeriksa header `Authorization: Bearer <JWT>`, mengembalikan `401` jika token tidak valid atau expired.
```

Contoh **SALAH** (dilarang):

```markdown
Middleware ini melakukan validasi JWT terhadap secret dengan algoritma HS256 lalu meng-inject payload ke request context.
```
(alasan: jargon tanpa analogi, kalimat panjang.)

### 2.4 Visual Adapter (pilih otomatis berdasarkan tipe folder)

Semua gambar disimpan di `<FolderDok>/assets/<nama-kebab-case>.png` dan di-embed dengan path relatif:

```markdown
![Halaman login dengan form email dan password](./assets/login-page.png)
```

Alt text wajib mendeskripsikan isi gambar dalam bahasa sederhana.

#### A. `web-ui` (React, Next.js, Vue, Nuxt, Svelte, Angular, Astro, HTML statis, dll.)

1. **Siapkan Playwright** (sekali saja):
   ```bash
   npx -y playwright --version || npm i -D playwright
   npx -y playwright install chromium
   ```
   Jika Playwright MCP tersedia di environment-mu, kamu BOLEH memakainya sebagai pengganti CLI (navigate → screenshot).
2. **Jalankan dev server** sebagai proses latar belakang menggunakan perintah dari Peta Proyek (`npm run dev`, `pnpm dev`, `yarn dev`, `ng serve`, `php artisan serve`, `python manage.py runserver`, dll.). Untuk HTML statis: `npx -y serve -l 4173 .` atau `python3 -m http.server 4173`.
3. **Tunggu server siap**: cek URL (mis. `http://localhost:3000`) berulang tiap 2 detik, maksimum 90 detik. Baca port aktual dari log server — jangan menebak.
4. **Tentukan target screenshot** per Folder Dok:
   - Folder halaman/route (`pages/`, `app/`, `views/`, `routes/`) → screenshot halaman di URL route tersebut.
   - Folder komponen (`components/`, `ui/`, `widgets/`) → jika ada **Storybook**, gunakan `http://localhost:6006/iframe.html?id=<story-id>&viewMode=story`. Jika tidak ada, cari halaman yang memakai komponen tersebut dan ambil screenshot **elemen**-nya saja.
   - Maksimal **4 screenshot per folder** (pilih yang paling mewakili).
5. **Ambil screenshot halaman penuh**:
   ```bash
   npx -y playwright screenshot --viewport-size=1280,800 --wait-for-timeout=1500 --full-page \
     "http://localhost:3000/login" "src/app/login/assets/login-page.png"
   ```
6. **Ambil screenshot elemen** (komponen tertentu): buat file sementara `.babydocs-shot.mjs` di `PROJECT_ROOT`, jalankan, lalu **hapus**:
   ```js
   // .babydocs-shot.mjs — HAPUS setelah dipakai
   import { chromium } from 'playwright';
   const shots = [
     // { url, selector, out }
     { url: 'http://localhost:3000/', selector: 'header', out: 'src/components/Header/assets/header.png' },
   ];
   const browser = await chromium.launch();
   const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
   for (const s of shots) {
     await page.goto(s.url, { waitUntil: 'networkidle' });
     await page.locator(s.selector).first().screenshot({ path: s.out });
   }
   await browser.close();
   ```
   ```bash
   node .babydocs-shot.mjs && rm .babydocs-shot.mjs
   ```
   Pilih selector yang stabil: `[data-testid=...]` > `#id` > tag semantik (`header`, `nav`, `form`) > class.
7. **Halaman yang butuh login/data**: jika ada akun demo/seed di README lama atau `.env.example`, kamu boleh login lewat script di atas. **Jangan pernah** memasukkan kredensial asli user ke dokumentasi atau screenshot. Jika tidak bisa diakses → pakai fallback (2.5).
8. Setelah semua screenshot selesai, **matikan dev server**.

#### B. `mobile-ui` (Flutter, React Native, Expo, Android native, iOS native, .NET MAUI)

Pilih metode pertama yang berhasil, berurutan:

1. **Flutter → golden test (diutamakan, tidak perlu simulator):**
   - Buat file sementara `test/babydocs_shots/<nama>_babydocs_test.dart`:
     ```dart
     import 'package:flutter/material.dart';
     import 'package:flutter_test/flutter_test.dart';
     // import 'package:<nama_package>/<path_ke_widget>.dart';

     void main() {
       testWidgets('eli5 <NamaWidget>', (tester) async {
         tester.view.physicalSize = const Size(1080, 1920);
         tester.view.devicePixelRatio = 3.0;
         await tester.pumpWidget(
           const MaterialApp(
             debugShowCheckedModeBanner: false,
             home: Scaffold(body: Center(child: /* NamaWidget(...) dengan data contoh */ SizedBox())),
           ),
         );
         await tester.pumpAndSettle();
         await expectLater(find.byType(MaterialApp), matchesGoldenFile('goldens/<nama>.png'));
       });
     }
     ```
   - Jalankan: `flutter test --update-goldens test/babydocs_shots/`
   - Salin `test/babydocs_shots/goldens/<nama>.png` → `<FolderDok>/assets/<nama>.png`.
   - Jika widget butuh Provider/Bloc/Riverpod/GetX/dependency injection, bungkus dengan provider berisi data dummy. Jika terlalu rumit (>30 baris setup), lewati ke metode berikutnya.
   - Catatan: golden test default merender teks sebagai kotak. Jika package `golden_toolkit` sudah ada di `dev_dependencies`, panggil `await loadAppFonts();` di awal. Jangan menambah dependensi baru tanpa izin user.
   - **Hapus seluruh folder `test/babydocs_shots/`** setelah selesai.
2. **Simulator/emulator yang sedang berjalan:**
   - iOS: `xcrun simctl io booted screenshot "<FolderDok>/assets/<nama>.png"`
   - Android: `adb exec-out screencap -p > "<FolderDok>/assets/<nama>.png"`
   - Jalankan aplikasi dulu (`flutter run -d <device>`, `npx expo start --ios`, `npx react-native run-android`), navigasikan ke layar target (deep link jika tersedia: `xcrun simctl openurl booted <scheme>://<path>` / `adb shell am start -W -a android.intent.action.VIEW -d "<scheme>://<path>"`).
   - Jangan menyalakan simulator baru jika memakan waktu > 3 menit; gunakan fallback.
3. **Expo/React Native Web**: jika proyek mendukung web (`react-native-web` / `expo start --web`), perlakukan seperti `web-ui` dengan viewport `390,844`.
4. Jika semua gagal → fallback (2.5).

#### C. `backend-api`, `cli-library`, dan folder logika non-UI

1. Buat diagram **Mermaid** langsung di README:
   - Alur langkah demi langkah / percabangan → `flowchart TD`
   - Interaksi antar komponen (client ↔ controller ↔ service ↔ database) → `sequenceDiagram`
   - Siklus status (order, pembayaran) → `stateDiagram-v2`
   - Struktur data/tabel → `erDiagram`
2. **Aturan sintaks Mermaid (agar pasti ter-render):**
   - Maksimal **15 node** per diagram. Lebih dari itu, pecah jadi beberapa diagram.
   - Selalu bungkus label dengan tanda kutip: `A["Cek token (JWT)"]`.
   - ID node hanya huruf/angka tanpa spasi: `cekToken`, bukan `cek token`.
   - Dilarang memakai tag HTML, tanda `;` di dalam label, dan kata `end` (huruf kecil) sebagai ID node.
   - Label memakai bahasa sederhana + nama teknis di kurung: `B["Kasir cek kartu (verifyToken)"]`.
3. Tambahkan **contoh input/output** nyata dari kode:
   - API: contoh request (method, path, body) dan response (status + JSON), diambil dari DTO/schema/validator/test yang ada.
   - CLI: contoh perintah dan output terminal.
   - Library/fungsi: contoh pemanggilan dan nilai kembaliannya.
   - Jangan mengarang field. Jika contoh nilai tidak ada di kode/test, pakai nilai dummy yang jelas palsu (`"budi@contoh.com"`, `123`) tetapi **nama field harus asli**.

### 2.5 Fallback visual

Jika screenshot gagal (server butuh secret/DB, build error, tidak ada simulator):
1. Jangan habiskan lebih dari **2 percobaan** per metode.
2. Buat diagram Mermaid yang menggambarkan struktur komponen (`flowchart TD` parent → child + props penting).
3. Tambahkan catatan di README:
   ```markdown
   > 📸 Screenshot belum tersedia: <alasan singkat>. Jalankan ulang skill setelah <syarat> terpenuhi.
   ```
4. Catat alasan kegagalan untuk laporan akhir.

### 2.6 Tabel Isi Penting (WAJIB di setiap README folder)

Setiap README folder **wajib** memiliki tabel dengan kolom persis seperti ini:

```markdown
| Nama File | Tugas Utama | Input | Output |
|---|---|---|---|
| `login_form.dart` | Formulir tempat kamu mengetik email & password | `onSubmit`, `isLoading` | Widget form; memanggil `onSubmit(email, password)` |
```

- Satu baris per file source langsung di folder ini (termasuk file kecil yang digabung dari sub-folder 1-file).
- "Tugas Utama" = bahasa sederhana, maksimal 12 kata.
- "Input"/"Output" = nama teknis asli (props, parameter, request, return, efek samping). Tulis `—` jika tidak ada.
- Untuk sub-folder yang punya README sendiri, buat bagian terpisah "Sub-folder" berisi tautan ke README anak + ringkasan 1 kalimat.

### 2.7 README folder induk (rangkuman)

Folder Dok yang punya sub-folder Dok wajib:
- Menjelaskan bagaimana anak-anaknya bekerja sama (1 analogi besar).
- Memiliki 1 diagram Mermaid `flowchart` yang menghubungkan sub-folder (node = sub-folder, panah = siapa memanggil/memakai siapa).
- Menautkan setiap README anak.

---

## Fase 3 — Web Dokumentasi Induk (Docsify)

### 3.1 `README.md` root (halaman depan)

Gunakan struktur `SKILL_DIR/templates/root-readme-template.md`. Wajib berisi:
1. Nama proyek + **satu kalimat ELI5** "Proyek ini ibarat …".
2. **Gambaran besar**: analogi besar keseluruhan sistem + jangkar 🔧 (stack, entry point).
3. **Diagram arsitektur** Mermaid `flowchart LR` (maks. 15 node) berisi bagian-bagian utama.
4. **Peta navigasi**: tabel `| Bagian | Ibaratnya | Buka |` yang menautkan SEMUA README sub-folder level teratas.
5. **Cara menjalankan proyek** (dari `scripts`/Makefile/README lama; jangan mengarang perintah).
6. **Cara membuka dokumentasi ini** (lihat 3.4).

Ingat Aturan Global #3: jika README root sudah berisi dokumentasi buatan user, tambahkan kontenmu di dalam penanda di bagian bawah — jangan menimpa.

### 3.2 `_sidebar.md` di root

Gunakan `SKILL_DIR/templates/_sidebar-template.md` sebagai acuan format.
- Baris pertama: `- [🏠 Beranda](/)`
- Struktur indentasi **mengikuti pohon folder** (2 spasi per level).
- Setiap tautan menunjuk ke file README **dengan path relatif dari root**, tanpa `./` di depan: `- [Auth](src/features/auth/README.md)`.
- Label = nama folder yang dibuat ramah dibaca + emoji opsional (mis. `🔐 Auth`), urut sesuai urutan logis (entry point dulu, lalu fitur, lalu utilitas).
- Kelompokkan dengan judul tebal tanpa tautan bila perlu: `- **Fitur**`.
- Setiap README yang kamu buat **harus muncul** di sidebar; tidak boleh ada tautan ke file yang tidak ada.

### 3.3 `index.html` dan `.nojekyll`

1. Salin `SKILL_DIR/templates/index.html` → `PROJECT_ROOT/index.html`.
   - **Jika `PROJECT_ROOT/index.html` sudah ada** dan bukan hasil skill ini (tidak mengandung komentar `babydocs`), JANGAN menimpanya (bisa jadi itu file aplikasi, mis. Vite/HTML statis). Sebagai gantinya, salin ke `PROJECT_ROOT/docs.html` dan sebutkan hal ini di README root serta laporan akhir.
2. Ganti placeholder `{{PROJECT_NAME}}` dengan nama proyek (dari `package.json`/`pubspec.yaml`/nama folder).
3. Ganti `{{REPO_URL}}` dengan URL remote git (`git remote get-url origin`, ubah format `git@github.com:a/b.git` → `https://github.com/a/b`). Jika tidak ada remote, hapus baris `repo:` di konfigurasi.
4. Buat file kosong `PROJECT_ROOT/.nojekyll` (wajib agar GitHub Pages tidak menyembunyikan `_sidebar.md`).

### 3.4 Cara preview (tulis di README root & laporan)

```bash
npx -y docsify-cli serve .        # http://localhost:3000
# atau tanpa Node.js:
python3 -m http.server 3000       # http://localhost:3000
```

Docsify tidak bisa dibuka lewat `file://` (klik dua kali file HTML) karena butuh `fetch`. Harus lewat server lokal atau GitHub Pages (Settings → Pages → Deploy from branch → root).

---

## Fase 4 — Verifikasi & Laporan

Jalankan semua pemeriksaan berikut dari `PROJECT_ROOT`, perbaiki setiap kegagalan, lalu ulangi sampai bersih:

1. **Tidak ada placeholder tersisa:**
   ```bash
   grep -rIl --include=README.md --include=_sidebar.md --include=index.html "{{" . --exclude-dir=node_modules --exclude-dir=.git
   ```
   Harus kosong.
2. **Semua tautan sidebar valid:**
   ```bash
   grep -oE '\]\([^)]+\)' _sidebar.md | sed -E 's/^\]\(//; s/\)$//' | while read -r p; do
     [ "$p" = "/" ] && continue; [ -f "$p" ] || echo "MISSING: $p"; done
   ```
   Harus kosong.
3. **Semua gambar yang di-embed ada:** untuk setiap `![...](./assets/x.png)` di sebuah README, pastikan file `assets/x.png` ada di folder README itu.
4. **Mermaid valid:** periksa ulang setiap blok terhadap aturan sintaks 2.4.C. Jika `@mermaid-js/mermaid-cli` tersedia, boleh validasi dengan `npx -y @mermaid-js/mermaid-cli -i <file.md> -o /tmp/babydocs-check.md`.
5. **File sementara terhapus:** `.babydocs-shot.mjs`, `test/babydocs_shots/` tidak ada lagi.
6. **Proses latar belakang mati:** dev server, Metro, emulator yang kamu nyalakan.
7. **Source code tidak berubah:** `git status --porcelain` hanya menampilkan `README.md`, `assets/`, `_sidebar.md`, `index.html`/`docs.html`, `.nojekyll`.
8. (Opsional) Jalankan `npx -y docsify-cli serve .` sebentar dan, jika Playwright tersedia, ambil screenshot `http://localhost:3000` untuk memastikan halaman depan, sidebar, dan minimal satu diagram Mermaid tampil. Matikan server setelahnya.

**Laporan akhir ke user** (ringkas, maks. 20 baris):
- Stack & tipe yang terdeteksi.
- Jumlah README dibuat/diperbarui, jumlah screenshot, jumlah diagram.
- Folder yang dilewati atau visual yang gagal + alasannya.
- Perintah preview (3.4).

---

## Kapan Harus Bertanya ke User

Berhenti dan tanya **hanya** jika:
- `PROJECT_ROOT` ambigu (ada beberapa proyek tak berhubungan dan user tidak menyebut yang mana).
- Menjalankan dev server/aplikasi butuh secret atau layanan berbayar yang tidak tersedia, dan user mungkin ingin menyediakannya (tanyakan sekali; jika tidak dijawab, pakai fallback).
- Visual memerlukan instalasi dependensi baru ke `package.json`/`pubspec.yaml` proyek (selain Playwright via `npx`).
- Jumlah Folder Dok > 60.

Selain itu, ambil keputusan sendiri dengan aturan di dokumen ini dan lanjutkan.

---

## Mode Update (dijalankan ulang)

Jika skill dipanggil lagi pada proyek yang sudah punya dokumentasi hasil skill ini:
1. Jalankan ulang scanner (Fase 1.0). Folder `unchanged` dilewati; kerjakan hanya folder `new` dan `changed`.
2. Perbarui juga semua folder induk dari folder yang berubah (bottom-up) dan `_sidebar.md`.
3. Ambil ulang screenshot hanya untuk folder UI yang berubah.
4. Hapus README/aset hasil skill untuk folder yang sudah tidak ada, dan buang tautannya dari sidebar.
5. Jika scanner tidak bisa dipakai dan git tersedia, gunakan `git log -1 --format=%H -- _sidebar.md` lalu `git diff --name-only <hash> HEAD` untuk mencari folder yang berubah.
