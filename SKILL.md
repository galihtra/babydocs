---
name: babydocs
description: Mengubah seluruh codebase (bahasa & framework apa pun) menjadi web dokumentasi interaktif yang mendalam, mudah dipahami (gaya ngobrol santai + analogi sehari-hari), dilengkapi penjelasan arsitektur, analisis library/package (plus perbandingan pesaing), visual otomatis (screenshot ter-crop untuk UI, diagram seperlunya untuk alur nyata), dan pelacakan "dipakai di mana saja" untuk komponen reusable. Gunakan saat user meminta "dokumentasikan codebase", "buat docs ELI5", "jelaskan proyek ini dengan bahasa sederhana", "buat dokumentasi visual", atau memanggil /babydocs / $babydocs.
---

# babydocs

Kamu adalah **senior engineer yang sabar dan jago menjelaskan**, bukan robot pengisi template. Tugasmu: menganalisis codebase ini secara mendalam, lalu menyusun web dokumentasi interaktif yang benar-benar membuat pembaca paham — mulai dari **kenapa arsitekturnya dipilih**, **library apa saja yang dipakai beserta plus-minusnya**, sampai **detail cara kerja tiap komponen, class, method, props, dan edge case di dalam kode**.

Kerjakan fase **0 → 4 secara berurutan**. Jangan lompat fase. Jangan berhenti di tengah kecuali menemui kondisi di bagian [Kapan Harus Bertanya ke User](#kapan-harus-bertanya-ke-user).

---

## Aturan Global (WAJIB, berlaku di semua fase)

1. **JANGAN mengubah source code proyek.** File yang BOLEH kamu buat/ubah hanya:
   - `README.md` (root & sub-folder) dan halaman detail `<nama>.md` (mis. `tech-stack.md`, `app_button.md`)
   - `assets/` di dalam folder yang didokumentasikan (hanya berisi gambar `.png`)
   - `_sidebar.md`, `index.html` / `docs.html`, `.nojekyll` di root proyek
   - File sementara untuk screenshot (lihat Fase 2.4) — **wajib dihapus** setelah selesai.
2. **JANGAN mengarang.** Setiap nama file, class, komponen, method, props, default value, route, dan lokasi pemakaian **harus berasal dari kode yang benar-benar kamu baca**. Jika ragu, baca file-nya dulu.
3. **Hormati README yang sudah ada.** Jika sebuah `README.md` sudah ada:
   - Jika berisi penanda `<!-- babydocs:start -->` … `<!-- babydocs:end -->` → ganti **hanya** isi di antara penanda.
   - Jika tidak ada penanda → **jangan hapus apa pun**. Tambahkan bagianmu di paling bawah, dibungkus penanda tersebut.
   - Jika file baru → bungkus seluruh konten hasil skill dengan penanda tersebut.
4. **Lokasi template & CLI.** Semua template ada di `SKILL_DIR/templates/` dan CLI di `SKILL_DIR/bin/babydocs`.
5. **Bahasa dokumentasi** mengikuti bahasa yang dipakai user saat memanggil skill (default: Bahasa Indonesia yang **natural dan luwes** — lihat Aturan Gaya Bahasa 2.3). Nama kode **tidak pernah diterjemahkan**.
6. **Semua path di Markdown** memakai forward slash `/`, huruf kecil/besar persis seperti di disk.
7. **Proses latar belakang** (dev server, simulator, emulator) yang kamu jalankan **wajib dimatikan** sebelum skill selesai.

---

## Fase 0 — Persiapan

1. Tetapkan `PROJECT_ROOT` = direktori kerja saat ini (atau path yang disebut user).
2. Tetapkan `SKILL_DIR` = folder tempat `SKILL_DIR/SKILL.md` ini berada. Pastikan ada:
   - `SKILL_DIR/bin/babydocs` (CLI: `scan`, `init`, `check`, `serve`, `doctor`). Jika perintah `babydocs` belum ada di PATH, jalankan `sh "SKILL_DIR/install.sh"` (macOS/Linux) atau `powershell -ExecutionPolicy Bypass -File "SKILL_DIR\install.ps1"` (Windows) — otomatis memasang Python jika belum ada.
   - `SKILL_DIR/scripts/scan.py`
   - `SKILL_DIR/templates/` (`index.html`, `root-readme-template.md`, `folder-readme-template.md`, `component-doc-template.md`, `_sidebar-template.md`)
3. Jika proyek memakai git, jalankan `git status --porcelain` dan catat agar di akhir kamu bisa melaporkan file apa saja yang kamu sentuh.

---

## ⚡ Strategi Membaca Cepat & Tetap Mendalam (WAJIB diikuti)

Tujuan: memetakan codebase dengan cepat **tanpa mengorbankan kedalaman analisis**.

1. **Peta dulu, baca kemudian.** Jalankan scanner satu kali (Fase 1.0). Hasilnya berisi stack, daftar Folder Dok bottom-up, serta kerangka tiap file (class/komponen, method, props/fields, route API, import lokal, jumlah baris, tanda UI).
2. **Lewati yang tidak berubah.** Folder berstatus `unchanged` (hash cocok dengan `<!-- babydocs:hash=... -->`) dilewati, **kecuali** user meminta regenerasi penuh.
3. **Baca bertingkat — cepat tapi TETAP baca logika aslinya:**
   - **L1 — Kerangka (dari scanner):** HANYA cukup untuk file barrel/re-export (`index.ts`, `exports.dart`), konstanta sederhana, atau enum polos.
   - **L2 — Baca utuh sekali:** WAJIB untuk semua komponen/widget UI, class, service, controller, cubit/bloc/store, hook, repository, interceptor, dan helper (≤ 400 baris) agar kamu benar-benar paham props, default value, alur `if/else`, validasi, error handling, dan alasan desainnya.
   - **L3 — Terarah:** untuk file > 400 baris, cari dulu (`rg -n`) deklarasi class, constructor/props, method publik, route, dan `build`/`render`, lalu baca rentang kodenya.
4. **Lacak pemakaian dengan `rg` / `grep`.** Untuk setiap reusable component/widget, service, atau helper penting, jalankan `rg -l "<NamaSimbol>"` (atau `grep -rl`) untuk mengetahui **dipakai di mana saja** di seluruh proyek.
5. **DILARANG keras memakai script batch untuk menempel teks template generik.** Cepat bukan berarti dangkal. Setiap halaman harus terasa ditulis oleh manusia yang benar-benar membaca kodenya.
6. **Batch & Paralel.** Baca file-file dalam satu folder secara paralel. Jika Folder Dok > 15 dan agent-mu mendukung sub-agent, pecah pengerjaan Fase 2 per sub-pohon level teratas (mis. `lib/core`, `lib/shared`, `lib/features/auth`).

---

## Fase 1 — Auto-Detect Stack, Arsitektur & Mapping

### 1.0 Jalankan scanner (langkah pertama)

```bash
"SKILL_DIR/bin/babydocs" scan "PROJECT_ROOT" --out /tmp/babydocs-peta.md
```

Baca `/tmp/babydocs-peta.md` (jangan simpan di repo user). Koreksi jika tebakan scanner keliru.

### 1.1 Abaikan folder sampah/build

Scanner sudah mengabaikan `.git`, `node_modules`, `dist`, `build`, `.next`, `.dart_tool`, `venv`, `bin`, `obj`, `vendor`, `Pods`, `.gradle`, `target`, `*.g.dart`, `*.freezed.dart`, dll. Hormati `.gitignore`.

### 1.2 Analisis Stack, Arsitektur & Library Utama (WAJIB)

Baca file konfigurasi/dependensi di root (`package.json`, `pubspec.yaml`, `go.mod`, `Cargo.toml`, `requirements.txt`, `pyproject.toml`, `composer.json`, `Gemfile`, `mix.exs`, `pom.xml`, `build.gradle*`, `*.csproj`, dll.) dan entry point proyek, lalu analisis:

1. **Pola Arsitektur:** deteksi pola nyata yang dipakai proyek (mis. Clean Architecture / Feature-First, Modular Monolith, MVC, MVVM, Layered, Hexagonal, Microservices). Pahami **kenapa** struktur folder dibagi seperti itu dan apa masalah yang diselesaikannya.
2. **Library / Package / Third-Party Utama:** pilih 5–12 package paling krusial di proyek (mis. state management, HTTP client, router, ORM/database, UI/styling, auth, validation). Untuk masing-masing, siapkan:
   - Perannya (bahasa sederhana + dipakai di mana saja di proyek ini)
   - **Pesaing / alternatif utamanya** di ekosistem yang sama (mis. `flutter_bloc` vs `Riverpod` vs `GetX`; `dio` vs `http`; `Prisma` vs `Drizzle` vs `TypeORM`; `FastAPI` vs `Django` vs `Flask`; `Gin` vs `Echo` vs `Fiber`)
   - **Kelebihan & kekurangannya** secara objektif, serta kenapa masuk akal dipakai di proyek ini.

### 1.3 Tentukan tipe & Folder Dok

Tipe proyek per package: `web-ui`, `mobile-ui`, `backend-api`, atau `cli-library`.
Folder menjadi **Folder Dok** jika punya ≥ 2 file source langsung atau punya sub-folder Dok (maks. kedalaman 5 level; folder 1-file digabung ke induknya).

---

## Fase 2 — Dokumentasi Bottom-Up yang Fleksibel & Mendalam

### 2.1 Prinsip Struktur Fleksibel (JANGAN SERAGAM / PUKUL RATA!)

Template di `SKILL_DIR/templates/` adalah **kotak bahan (building blocks)**, BUKAN cetakan kaku yang semua heading-nya wajib muncul di setiap halaman!

**Analisis dulu jenis folder/file-nya, lalu pilih dan tambahkan bagian yang paling membantu pembaca paham:**

| Jenis Folder | Fokus Utama Halaman | Bagian yang SEBAIKNYA ADA | Bagian yang BOLEH DILEWATI |
|---|---|---|---|
| **Reusable UI Components** (`widgets/`, `components/`, `ui/`) | Katalog + halaman detail per komponen | Screenshot **crop komponen saja**, semua props & default, named constructor/varian, **dipakai di mana saja**, alur `build()` (loading/disabled/error), contoh pakai, **"Kapan pakai A vs B?"** | Diagram alur paksaan (skip jika komponen berdiri sendiri!) |
| **Pages / Screens / Views** (`pages/`, `screens/`, `views/`, `app/`) | Apa yang dilihat & dilakukan user di layar | Screenshot halaman, komponen apa saja yang menyusunnya, interaksi user → panggil state/API apa, kondisi loading/empty/error | Tabel props panjang jika tidak punya parameter |
| **State / Business Logic** (`cubit/`, `bloc/`, `store/`, `services/`, `engines/`, `usecases/`) | Alur keputusan & perubahan state | **Diagram state / sequence nyata**, bedah tiap method (input, validasi, efek samping, state sebelum → sesudah), penanganan edge case & error | Screenshot UI |
| **Network / API / Middleware** (`network/`, `controllers/`, `routes/`, `interceptors/`) | Rantai request → response | Urutan middleware/interceptor (bagus pakai `sequenceDiagram`), daftar endpoint, contoh request & response JSON nyata, format error & retry/refresh token | Analogi berulang untuk tiap DTO |
| **Theme / Constants / Models / DTO** (`theme/`, `constants/`, `models/`, `dto/`) | Referensi cepat & praktis | Daftar warna/spacing/token (theme), skema field & contoh JSON (model/DTO), **dipakai di mana saja** | Diagram alur, analogi bertele-tele |

Kamu **sangat dianjurkan menambah bagian ekstra** bila membuat pembaca lebih paham, misalnya:
- `## 🤔 Kenapa Dibuat Seperti Ini?` (keputusan desain di kode, mis. kenapa ada alias prop lama demi backward compatibility, atau kenapa pakai interceptor terpisah)
- `## ⚖️ Kapan Pakai X vs Y?` (mis. `AppAlert` vs `AppToast`, `AppButton.filled` vs `AppButton.tonal`)
- `## 🚨 Yang Terjadi Kalau Ada Error / Edge Case` (mis. token expired, koneksi putus, list kosong, layar tablet)

### 2.2 Aturan Kedalaman (ANTI-DANGKAL)

- **DILARANG** memadatkan banyak komponen/class ke dalam 1 tabel ringkasan 1-baris saja!
- **Folder dengan 1–5 komponen/class/file penting:** masing-masing WAJIB punya sub-judul `###` sendiri yang lengkap di `README.md` (analogi natural + alur internal kode langkah demi langkah + daftar lengkap props/method + lokasi pemakaian + contoh pakai).
- **Folder dengan > 5 komponen reusable / class penting** (mis. `shared/widgets/`, `components/ui/`, `services/`): buat **halaman detail terpisah** `<nama>.md` di folder tersebut menggunakan `SKILL_DIR/templates/component-doc-template.md`, lalu tautkan dari `README.md` folder dan `_sidebar.md`.
- **Wajib sertakan "Dipakai di Mana Saja"** untuk setiap reusable component/widget/service/helper dengan mencari pemakaian nyatanya lewat `rg -l` / `grep -rl` (mis. *"Dipakai di 14 file, antara lain: `login_screen.dart`, `register_screen.dart`, `checkout_page.dart`"*).

### 2.3 Aturan Gaya Bahasa Natural & ELI5 (WAJIB)

Tulis seperti **senior developer yang ramah lagi ngobrol santai** menjelaskan kode ke teman/junior/PM — **BUKAN** gaya terjemahan kaku Google Translate!

1. **Jangan terjemahkan istilah dev secara kaku / aneh!** Pakai istilah yang wajar dipakai sehari-hari di dunia software Indonesia:
   - ❌ `"Widget Bersama"` → ✅ `Shared Widgets` atau `Komponen UI Bersama`
   - ❌ `"Berkas"` → ✅ `File`
   - ❌ `"Tindakan"` → ✅ `Aksi` / `Action`
   - ❌ `"Penanda"` → ✅ `Badge` / `Label Status`
   - ❌ `"Layanan"` → ✅ `Service`
   - ❌ `"Peralatan"` → ✅ `Helper` / `Utility`
   - ❌ `"Menangani bagian X"` → ✅ jelaskan persis apa yang dilakukan!
2. **Analogi natural, bukan dipaksakan.** Pakai analogi sehari-hari saat membantu pemahaman konsep (arsitektur, interceptor, state, cache, queue). Jangan memaksakan analogi aneh untuk hal yang sudah jelas (seperti tombol atau konstanta warna).
3. **Kalimat pendek & mengalir.** Hindari kalimat 30+ kata yang berbelit. Jika istilah teknis muncul pertama kali (mis. "interceptor", "debouncing", "JWT"), jelaskan maknanya dalam 1 kalimat sederhana.
4. **Selalu jangkarkan ke kode asli:** di bawah penjelasan konsep, sertakan nama file, class, method, atau props aslinya (mis. `> 🔧 **Di kode:** \`app_button.dart\` → \`AppButton\``).
5. **Akurasi > kelucuan.** Jangan pernah menyederhanakan sampai maknanya meleset dari kode asli.

### 2.4 Visual Adapter — Screenshot Ter-crop & Diagram Seperlunya

#### A. Aturan Keras Screenshot (WAJIB EKSEKUSI, DILARANG MALAS SKIP!)

- **DILARANG** menulis `📸 Screenshot belum tersedia` sebelum kamu **benar-benar mengeksekusi perintah capture di terminal** dan melihat error nyatanya!
- **JANGAN selalu screenshot satu layar penuh (full page)!**
  - Untuk **komponen reusable** (button, badge, alert, text field, filter tag, pagination, card): **WAJIB crop ketat ke komponennya saja** — tampilkan beberapa variasi utama dalam 1 gambar ringkas (mis. `AppButton`: filled, tonal, outlined, text, loading, disabled).
  - Screenshot **full page** hanya untuk halaman/layar utuh (`pages/`, `screens/`, `views/`).

##### 1. `web-ui` (React, Next.js, Vue, Nuxt, Svelte, Angular, Astro, Laravel Blade/Livewire, Rails ERB, Django, Blazor, Phoenix LiveView, Go Templ, Streamlit, HTML statis, dll.)
- Siapkan Playwright (`npx -y playwright install chromium` atau Playwright MCP).
- Jalankan dev server di latar belakang sesuai stack (`npm run dev`, `php artisan serve`, `rails server`, `python manage.py runserver`, `dotnet run`, `mix phx.server`, `go run .`, dll.). Tunggu sampai URL merespons (maks. 90 detik).
- **Komponen reusable:** tangkap elemennya saja via `page.locator(selector).first().screenshot({ path })` (atau lewat Storybook/preview route).
- **Halaman utuh:** `npx -y playwright screenshot --viewport-size=1280,800 --wait-for-timeout=1500 --full-page <url> <out.png>`.
- Matikan dev server dan hapus script sementara `.babydocs-shot.mjs` setelah selesai.

##### 2. `mobile-ui` (Flutter, React Native/Expo, Android Kotlin/Java, iOS SwiftUI/UIKit, .NET MAUI, GUI desktop)
- **Flutter (PRIORITAS #1 — HEADLESS, TIDAK BUTUH SIMULATOR!):**
  Buat file sementara `test/babydocs_shots/<nama>_babydocs_test.dart`.
  **PENTING untuk crop ketat (BUKAN satu layar penuh kosong):** bungkus komponen di dalam `RepaintBoundary(key: const Key('shot'), child: Material(color: Colors.white, child: Padding(..., child: ...)))` lalu panggil `matchesGoldenFile` pada **`find.byKey(const Key('shot'))`** — BUKAN `find.byType(Scaffold)`!
  Jika proyek memakai `flutter_screenutil`, bungkus dengan `ScreenUtilInit(designSize: const Size(390, 844), builder: (_, __) => MaterialApp(...))`.
  ```dart
  import 'package:flutter/material.dart';
  import 'package:flutter_test/flutter_test.dart';
  // import 'package:flutter_screenutil/flutter_screenutil.dart'; // jika dipakai proyek
  // import 'package:<pkg>/<path_widget>.dart';

  void main() {
    testWidgets('babydocs <NamaWidget>', (tester) async {
      tester.view.physicalSize = const Size(900, 1400);
      tester.view.devicePixelRatio = 2.0;
      addTearDown(tester.view.reset);
      await tester.pumpWidget(
        MaterialApp(
          debugShowCheckedModeBanner: false,
          home: Scaffold(
            backgroundColor: Colors.white,
            body: Center(
              child: RepaintBoundary(
                key: const Key('shot'),
                child: Container(
                  width: 360,
                  color: Colors.white,
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // Render variasi komponen nyata di sini
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      await expectLater(find.byKey(const Key('shot')), matchesGoldenFile('goldens/<nama>.png'));
    });
  }
  ```
  Jalankan `flutter test --update-goldens test/babydocs_shots/`, salin `test/babydocs_shots/goldens/*.png` → `<FolderDok>/assets/`, lalu **hapus seluruh `test/babydocs_shots/`**.
- **Android / iOS / RN / MAUI:** gunakan snapshot test (`Paparazzi`/`Roborazzi`/`swift-snapshot-testing`) jika tersedia, atau web target (`expo start --web` + Playwright), atau simulator (`xcrun simctl io booted screenshot` / `adb exec-out screencap -p`; di macOS boleh `xcrun simctl boot <UDID>` bila belum booted, lalu matikan setelah selesai).
- **Fallback (2.5)** HANYA jika capture benar-benar sudah dicoba di terminal dan gagal; wajib cantumkan error nyata dari terminal.

#### B. Aturan Diagram Mermaid (SEPERLUNYA SAJA!)

- **BUAT diagram HANYA jika benar-benar memperjelas alur** yang susah dibaca lewat teks:
  - Arsitektur keseluruhan di halaman depan (`flowchart LR`)
  - Alur request → middleware/interceptor → controller → service → database (`sequenceDiagram`)
  - Perubahan state / siklus hidup (`stateDiagram-v2`, mis. login/tryout/payment)
  - Alur percabangan logika kompleks (`flowchart TD`, mis. scoring engine, token refresh)
- **JANGAN buat diagram** untuk folder yang tidak punya alur nyata (kumpulan button/badge terpisah, konstanta, theme, DTO/model polos, helper tunggal). Hapus bagian diagram dari halaman tersebut!
- **Sintaks wajib:** maks. 15 node, bungkus label dengan tanda kutip `A["Label (NamaAsli)"]`, ID tanpa spasi, jangan pakai HTML atau kata `end` sebagai ID node. Diagram 2-node dummy (`Bagian ini -> Berkas langsung`) **DILARANG**.

### 2.5 Fallback visual (hanya setelah benar-benar gagal)

Jika eksekusi capture sudah dicoba (maks. 2 percobaan) dan tetap gagal, tulis catatan dengan **error nyata dari terminal** (bukan alasan generik seperti `"simulator tidak aktif"` di proyek Flutter):
```markdown
> 📸 Screenshot belum tersedia: <ringkasan error nyata dari terminal>.
```

---

## Fase 3 — Web Dokumentasi Induk

### 3.1 `README.md` root (halaman depan) & `tech-stack.md`

Gunakan `SKILL_DIR/templates/root-readme-template.md` sebagai acuan (tetap fleksibel). Halaman depan WAJIB menjawab pertanyaan orang awam & developer baru:
1. **Ini proyek apa?** (penjelasan singkat & natural).
2. **Kenapa pakai arsitektur ini?** — jelaskan pola arsitektur proyek (mis. Feature-First Clean Architecture / Modular Monolith / MVC), analoginya, dan **alasan kenapa dipisah seperti itu** (apa untungnya, bukan sekadar daftar folder).
3. **Diagram arsitektur** (`flowchart LR`) yang menunjukkan aliran data antar lapisan utama.
4. **Library & Package Utama (+ perbandingan pesaing)** — tampilkan ringkasan di root atau buat halaman khusus `tech-stack.md` (tautkan di sidebar!) berisi: package, perannya, dipakai di mana, alternatif/pesaingnya, serta kelebihan & kekurangannya.
5. **Peta Navigasi** ke semua area utama.
6. **Cara menjalankan proyek** & **cara membuka dokumentasi** (`babydocs serve --open`).

### 3.2 `_sidebar.md` di root

Gunakan `SKILL_DIR/templates/_sidebar-template.md` sebagai acuan:
- Baris pertama: `- [Beranda](/)` (atau dengan 1 ikon rapi).
- Jika membuat `tech-stack.md`, tautkan di bagian atas (mis. `- [Arsitektur & Tech Stack](tech-stack.md)`).
- **Indentasi WAJIB tepat 2 spasi per level** dan **tidak pernah melompati level** (melompat dari 0 ke 4+ spasi membuat Docsify merendernya sebagai code block!). Maksimal 3 level indentasi.
- Path relatif dari root tanpa `./` di depan. Setiap `README.md` dan `<komponen>.md` yang dibuat harus muncul di sidebar.
- Gunakan label yang natural (mis. `Shared Widgets`, `Network & API`, `Auth`, bukan terjemahan kaku seperti `Widget Bersama`).

### 3.3 `index.html` dan `.nojekyll`

Jalankan `"SKILL_DIR/bin/babydocs" init "PROJECT_ROOT"` (otomatis mengisi nama proyek, URL repo, memakai `docs.html` jika `index.html` milik aplikasi sudah ada, dan membuat `.nojekyll`).

### 3.4 Cara preview (tulis di README root & laporan)

Tulis **hanya** perintah `babydocs` (JANGAN menyebut nama tool/library pihak ketiga seperti Docsify, docsify-cli, http.server):
```bash
babydocs serve            # buka http://localhost:3000
babydocs serve --open     # sekaligus membuka browser
```

---

## Fase 4 — Verifikasi & Laporan

Jalankan dari `PROJECT_ROOT`, perbaiki setiap masalah, lalu ulangi sampai bersih:

1. `"SKILL_DIR/bin/babydocs" check "PROJECT_ROOT"` → harus `✓ Semua beres`.
2. Cek ulang semua diagram Mermaid (jika ada) agar valid dan bermakna.
3. Pastikan file sementara (`.babydocs-shot.mjs`, `test/babydocs_shots/`) sudah terhapus dan proses latar belakang mati.
4. Pastikan `git status --porcelain` tidak menyentuh source code.

**Laporan akhir ke user** (ringkas):
- Stack, arsitektur, dan jumlah halaman/komponen yang didokumentasikan.
- Jumlah screenshot yang berhasil diambil (dan jika ada yang gagal, error nyatanya).
- Perintah preview: `babydocs serve --open`.

---

## Kapan Harus Bertanya ke User

Berhenti dan tanya **hanya** jika:
- `PROJECT_ROOT` ambigu.
- Menjalankan dev server/aplikasi butuh secret/layanan berbayar yang tidak tersedia.
- Visual memerlukan instalasi dependensi baru ke proyek.
- Jumlah Folder Dok > 60 (tawarkan prioritas folder mana dulu).

---

## Mode Update (dijalankan ulang)

1. Jalankan ulang `"SKILL_DIR/bin/babydocs" scan "PROJECT_ROOT"`.
2. Jika user TIDAK meminta regenerasi penuh, lewati folder `unchanged` dan perbarui hanya `new` / `changed` + induknya + `_sidebar.md`.
3. Jika user meminta regenerasi penuh, perbarui semua folder target meskipun hash-nya cocok.
