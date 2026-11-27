#!/usr/bin/env python3
"""
babydocs — CLI untuk dokumentasi ELI5.

Perintah:
  babydocs serve  [DIR] [-p PORT] [--open] [--no-reload]  Buka web dokumentasi secara lokal
  babydocs init   [DIR] [--name NAMA]                     Pasang index.html + .nojekyll
  babydocs scan   [DIR] [opsi scan.py ...]                Buat Peta Proyek (dipakai agent)
  babydocs check  [DIR]                                   Cek link, gambar, placeholder
  babydocs doctor                                         Cek kesiapan sistem
  babydocs version

Hanya memakai Python standard library (3.8+).
"""
from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
import re
import runpy
import shutil
import socket
import socketserver
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

VERSION = "1.0.0"
HOME = Path(__file__).resolve().parent.parent          # folder repo babydocs
TEMPLATES = HOME / "templates"
SCAN = HOME / "scripts" / "scan.py"
MARK = "generated-by: babydocs"
SKIP_DIRS = {".git", "node_modules", ".dart_tool", "build", "dist", ".next", "venv",
             ".venv", "__pycache__", "vendor", "Pods", ".gradle", "target", "bin", "obj"}

C = sys.stdout.isatty() and os.name != "nt"
def c(code: str, s: str) -> str:
    return f"\033[{code}m{s}\033[0m" if C else s


# --------------------------------------------------------------------------
# serve
# --------------------------------------------------------------------------
class _State:
    version = ""
    checked = 0.0
    lock = threading.Lock()


def docs_version(root: Path) -> str:
    """Sidik jari semua file dokumentasi (untuk live reload). Di-cache 1 detik."""
    with _State.lock:
        if time.time() - _State.checked < 1.0:
            return _State.version
        h = hashlib.sha1()
        for dp, dns, fns in os.walk(root):
            dns[:] = sorted(d for d in dns if d not in SKIP_DIRS and not d.startswith("."))
            for fn in sorted(fns):
                if fn.endswith((".md", ".html", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")):
                    p = os.path.join(dp, fn)
                    try:
                        st = os.stat(p)
                    except OSError:
                        continue
                    h.update(f"{p}:{st.st_mtime_ns}:{st.st_size}".encode())
        _State.version = h.hexdigest()[:16]
        _State.checked = time.time()
        return _State.version


def make_handler(root: Path, reload: bool):
    class Handler(http.server.SimpleHTTPRequestHandler):
        server_version = "babydocs"
        sys_version = ""

        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(root), **kw)

        def end_headers(self):
            self.send_header("Cache-Control", "no-store, must-revalidate")
            super().end_headers()

        def do_GET(self):
            if self.path.startswith("/__babydocs__/ping"):
                if not reload:
                    self.send_error(404)
                    return
                body = docs_version(root).encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            super().do_GET()

        def log_message(self, fmt, *args):  # senyap, kecuali error
            if len(args) > 1 and str(args[1])[:1] in "45" and "__babydocs__" not in str(args[0]):
                sys.stderr.write(c("33", f"  ⚠ {args[1]} {args[0]}\n"))

    return Handler


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def find_entry(root: Path) -> str:
    for name in ("index.html", "docs.html"):
        p = root / name
        if p.exists() and MARK in p.read_text(encoding="utf-8", errors="ignore")[:2000]:
            return name
    return ""


def cmd_serve(a) -> int:
    root = Path(a.dir).resolve()
    if not root.is_dir():
        print(c("31", f"✗ Folder tidak ditemukan: {root}"))
        return 1
    entry = find_entry(root)
    if not entry:
        print(c("31", "✗ Dokumentasi belum dipasang di folder ini."))
        print(f"  Jalankan dulu: {c('1', 'babydocs init')}  (atau minta agent menjalankan skill babydocs)")
        return 1
    port = a.port
    for _ in range(20):
        try:
            httpd = Server((a.host, port), make_handler(root, not a.no_reload))
            break
        except OSError:
            port += 1
    else:
        print(c("31", f"✗ Tidak ada port kosong mulai dari {a.port}"))
        return 1

    url = f"http://localhost:{port}/" + ("" if entry == "index.html" else entry)
    lan = ""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        lan = s.getsockname()[0]
        s.close()
    except OSError:
        pass
    print()
    print(c("1;35", "  🧸 babydocs") + c("2", f"  v{VERSION}"))
    print()
    print(f"  {c('2', 'Lokal  :')} {c('1;36', url)}")
    if a.host in ("0.0.0.0", "") and lan:
        print(f"  {c('2', 'Jaringan:')} http://{lan}:{port}/" + ("" if entry == "index.html" else entry))
    print(f"  {c('2', 'Folder :')} {root}")
    if port != a.port:
        print(c("33", f"  (port {a.port} sedang dipakai, pindah ke {port})"))
    print(f"  {c('2', 'Live reload:')} {'aktif' if not a.no_reload else 'mati'}  ·  {c('2', 'Ctrl+C untuk berhenti')}")
    print()
    if a.open:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(c("2", "\n  Sampai jumpa 👋"))
    finally:
        httpd.server_close()
    return 0


# --------------------------------------------------------------------------
# init
# --------------------------------------------------------------------------
def project_name(root: Path) -> str:
    pj = root / "package.json"
    if pj.exists():
        try:
            n = json.loads(pj.read_text(encoding="utf-8")).get("name")
            if n:
                return n
        except ValueError:
            pass
    ps = root / "pubspec.yaml"
    if ps.exists():
        m = re.search(r"^name:\s*([\w-]+)", ps.read_text(encoding="utf-8", errors="ignore"), re.M)
        if m:
            return m.group(1)
    return root.name


def repo_url(root: Path) -> str:
    try:
        u = subprocess.run(["git", "remote", "get-url", "origin"], cwd=root, capture_output=True,
                           text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""
    m = re.match(r"git@([^:]+):(.+?)(\.git)?$", u)
    if m:
        return f"https://{m.group(1)}/{m.group(2)}"
    return re.sub(r"\.git$", "", u) if u.startswith("http") else ""


def cmd_init(a) -> int:
    root = Path(a.dir).resolve()
    html = (TEMPLATES / "index.html").read_text(encoding="utf-8")
    html = html.replace("{{PROJECT_NAME}}", a.name or project_name(root))
    url = repo_url(root)
    html = html.replace("{{REPO_URL}}", url) if url else re.sub(r'\n\s*repo: "\{\{REPO_URL\}\}",', "", html)
    target = root / "index.html"
    if target.exists() and MARK not in target.read_text(encoding="utf-8", errors="ignore")[:2000]:
        target = root / "docs.html"
        print(c("33", "  index.html milik aplikasi sudah ada → memakai docs.html"))
    target.write_text(html, encoding="utf-8")
    (root / ".nojekyll").touch()
    print(c("32", f"✓ {target.name} dan .nojekyll terpasang di {root}"))
    if not (root / "README.md").exists():
        print(c("33", "  README.md belum ada — jalankan skill babydocs lewat agent untuk mengisinya."))
    return 0


# --------------------------------------------------------------------------
# check
# --------------------------------------------------------------------------
LINK_RE = re.compile(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")


def cmd_check(a) -> int:
    root = Path(a.dir).resolve()
    problems: list[str] = []
    readmes = []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".")]
        if "README.md" in fns:
            readmes.append(Path(dp) / "README.md")
    targets = readmes + [p for p in (root / "_sidebar.md", root / "index.html", root / "docs.html") if p.exists()]
    for p in targets:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        if "babydocs:start" not in txt and p.name == "README.md":
            continue
        rel = p.relative_to(root)
        if "{{" in txt:
            problems.append(f"placeholder tersisa: {rel}")
        if p.suffix == ".md":
            for img in IMG_RE.findall(txt):
                if img.startswith(("http://", "https://", "data:")):
                    continue
                if not (p.parent / img.split("#")[0]).exists():
                    problems.append(f"gambar hilang: {rel} → {img}")
    sb = root / "_sidebar.md"
    if not sb.exists():
        problems.append("_sidebar.md tidak ada")
    else:
        for link in LINK_RE.findall(sb.read_text(encoding="utf-8", errors="ignore")):
            link = link.split("#")[0]
            if link in ("", "/") or link.startswith(("http://", "https://")):
                continue
            path = root / link.lstrip("/")
            if not (path.exists() or (path / "README.md").exists() or path.with_suffix(".md").exists()):
                problems.append(f"link sidebar rusak: {link}")
    if not find_entry(root):
        problems.append("index.html/docs.html babydocs belum dipasang (jalankan: babydocs init)")
    if not (root / ".nojekyll").exists():
        problems.append(".nojekyll tidak ada (dibutuhkan GitHub Pages)")
    for leftover in (".babydocs-shot.mjs", "test/babydocs_shots"):
        if (root / leftover).exists():
            problems.append(f"file sementara belum dihapus: {leftover}")
    if problems:
        print(c("31", f"✗ {len(problems)} masalah:"))
        for x in problems:
            print("  - " + x)
        return 1
    print(c("32", f"✓ Semua beres ({len(readmes)} README dicek)"))
    return 0


# --------------------------------------------------------------------------
# doctor
# --------------------------------------------------------------------------
def cmd_doctor() -> int:
    print(c("1;35", f"\n  🧸 babydocs doctor  v{VERSION}\n"))
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(c("32", f"  ✓ Runtime siap") + c("2", f" (Python {py_ver})"))
    print(c("32", f"  ✓ Folder babydocs") + c("2", f" ({HOME})"))
    for label, cmd, note in [
        ("Git", "git", "opsional — mempercepat scan & update"),
        ("Node.js (npx)", "npx", "opsional — untuk screenshot halaman web"),
        ("Flutter", "flutter", "opsional — untuk screenshot aplikasi Flutter"),
    ]:
        if shutil.which(cmd):
            print(c("32", f"  ✓ {label} tersedia"))
        else:
            print(c("33", f"  ○ {label} tidak ditemukan") + c("2", f" ({note})"))
    print()
    return 0


# --------------------------------------------------------------------------
def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "scan":
        sys.argv = [str(SCAN)] + sys.argv[2:]
        runpy.run_path(str(SCAN), run_name="__main__")
        return 0

    ap = argparse.ArgumentParser(prog="babydocs", description="🧸 babydocs — dokumentasi ELI5")
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("serve", help="buka web dokumentasi secara lokal")
    s.add_argument("dir", nargs="?", default=".")
    s.add_argument("-p", "--port", type=int, default=3000)
    s.add_argument("--host", default="127.0.0.1", help="pakai 0.0.0.0 agar bisa dibuka dari HP di jaringan sama")
    s.add_argument("-o", "--open", action="store_true", help="langsung buka browser")
    s.add_argument("--no-reload", action="store_true", help="matikan live reload")
    i = sub.add_parser("init", help="pasang index.html + .nojekyll")
    i.add_argument("dir", nargs="?", default=".")
    i.add_argument("--name", default="")
    k = sub.add_parser("check", help="cek link, gambar, placeholder")
    k.add_argument("dir", nargs="?", default=".")
    sub.add_parser("scan", help="buat Peta Proyek (lihat: babydocs scan --help)")
    sub.add_parser("doctor", help="cek kesiapan sistem")
    sub.add_parser("version", help="tampilkan versi")
    a = ap.parse_args()

    if a.cmd == "serve":
        return cmd_serve(a)
    if a.cmd == "init":
        return cmd_init(a)
    if a.cmd == "check":
        return cmd_check(a)
    if a.cmd == "doctor":
        return cmd_doctor()
    if a.cmd == "version":
        print(f"babydocs {VERSION}")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
