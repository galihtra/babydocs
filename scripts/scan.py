#!/usr/bin/env python3
"""
babydocs scanner — membuat "Peta Proyek" ringkas dalam SATU perintah.

Tujuan: agent tidak perlu membuka ratusan file satu per satu hanya untuk
memahami struktur. Script ini (hanya Python standard library, tanpa install):

  1. Mengambil daftar file sah (git ls-files, menghormati .gitignore;
     fallback ke os.walk + daftar folder abaikan).
  2. Mendeteksi bahasa, framework, dan tipe proyek dari file penanda.
  3. Memilih kandidat "Folder Dok" dan mengurutkannya bottom-up.
  4. Mengekstrak "kerangka" setiap file: class/fungsi/export, route API,
     dan import lokal — tanpa isi fungsi.
  5. Menghitung hash isi per folder dan membandingkannya dengan penanda
     `<!-- babydocs:hash=... -->` di README.md agar folder yang tidak
     berubah bisa DILEWATI.

Pemakaian:
  python3 scan.py [PROJECT_ROOT] [--only src/features] [--json]
                  [--max-symbols 25] [--out peta.md]

Output default: Markdown ke stdout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# --------------------------------------------------------------------------
# Konfigurasi
# --------------------------------------------------------------------------
IGNORE_DIRS = {
    ".git", ".svn", ".hg", ".idea", ".vscode", ".vs", "node_modules",
    "bower_components", "jspm_packages", ".pnpm-store", ".yarn", "dist",
    "build", "out", "output", "target", "bin", "obj", "coverage",
    ".nyc_output", ".next", ".nuxt", ".svelte-kit", ".astro", ".output",
    ".vercel", ".netlify", ".turbo", ".parcel-cache", ".cache", ".angular",
    "storybook-static", ".dart_tool", ".pub-cache", "Pods", ".symlinks",
    ".gradle", ".expo", ".expo-shared", "venv", ".venv", "env",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox",
    "site-packages", "vendor", "Carthage", "DerivedData", ".terraform",
    "tmp", "temp", "logs", "assets", ".babydocs",
}
IGNORE_FILE_RE = re.compile(
    r"(\.min\.(js|css)$|\.map$|\.lock$|-lock\.(json|yaml)$|\.g\.dart$|"
    r"\.freezed\.dart$|\.generated\.|\.pb\.go$|_pb2\.py$|\.d\.ts$)"
)
SOURCE_EXT = {
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".astro",
    ".py", ".go", ".dart", ".rs", ".cs", ".java", ".kt", ".kts", ".php",
    ".rb", ".swift", ".ex", ".exs", ".c", ".h", ".cpp", ".hpp", ".cc",
    ".m", ".mm", ".scala", ".lua", ".sh", ".zig", ".r", ".R", ".jl",
    ".html", ".erb", ".heex", ".templ", ".razor", ".cshtml", ".twig", ".xaml",
    ".sql", ".graphql", ".proto",
}
TEST_RE = re.compile(r"(^|/)(tests?|__tests__|spec|e2e|integration_test)(/|$)|"
                     r"(\.|_)(test|spec)\.[a-z]+$|_test\.(go|dart|py)$|^test_.*\.py$")
UI_DIR_NAMES = {"components", "component", "ui", "widgets", "widget", "pages",
                "views", "view", "screens", "screen", "layouts", "layout",
                "app", "routes", "templates", "presentation"}
MAX_DEPTH = 5

# --------------------------------------------------------------------------
# Deteksi stack
# --------------------------------------------------------------------------
def read(p: Path, limit: int = 400_000) -> str:
    try:
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(limit)
    except OSError:
        return ""


def detect_stack(root: Path, files: list[str]) -> dict:
    found = []

    def has(*names):
        return [f for f in files if Path(f).name in names and f.count("/") <= 2]

    for pj in has("package.json"):
        txt = read(root / pj)
        try:
            data = json.loads(txt)
        except ValueError:
            data = {}
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        fw, typ = [], "cli-library"
        for name, label, t in [
            ("next", "Next.js", "web-ui"), ("nuxt", "Nuxt", "web-ui"),
            ("@angular/core", "Angular", "web-ui"), ("svelte", "Svelte", "web-ui"),
            ("astro", "Astro", "web-ui"), ("vue", "Vue", "web-ui"),
            ("react-native", "React Native", "mobile-ui"), ("expo", "Expo", "mobile-ui"),
            ("react", "React", "web-ui"), ("solid-js", "Solid", "web-ui"),
            ("@nestjs/core", "NestJS", "backend-api"), ("express", "Express", "backend-api"),
            ("fastify", "Fastify", "backend-api"), ("koa", "Koa", "backend-api"),
            ("hono", "Hono", "backend-api"),
        ]:
            if name in deps:
                fw.append(label)
                if typ == "cli-library" or (t == "mobile-ui"):
                    typ = t
        lang = "TypeScript" if "typescript" in deps else "JavaScript"
        found.append({"marker": pj, "language": lang, "frameworks": fw, "type": typ,
                      "scripts": data.get("scripts", {})})

    for ps in has("pubspec.yaml"):
        txt = read(root / ps)
        flutter = re.search(r"^\s+flutter:\s*\n\s+sdk:\s*flutter", txt, re.M)
        fw = ["Flutter"] if flutter else []
        for pkg in ["flutter_bloc", "provider", "riverpod", "get", "go_router", "dio",
                    "dart_frog", "shelf"]:
            if re.search(rf"^\s+{pkg}:", txt, re.M):
                fw.append(pkg)
        found.append({"marker": ps, "language": "Dart", "frameworks": fw,
                      "type": "mobile-ui" if flutter else "cli-library"})

    simple = [
        ("go.mod", "Go", [("a-h/templ", "Templ", "web-ui"), ("gin-gonic", "Gin", "backend-api"),
                          ("labstack/echo", "Echo", "backend-api"), ("gofiber", "Fiber", "backend-api"),
                          ("go-chi", "Chi", "backend-api"), ("charmbracelet/bubbletea", "Bubbletea", "cli-library"),
                          ("spf13/cobra", "Cobra", "cli-library")]),
        ("Cargo.toml", "Rust", [("axum", "Axum", "backend-api"), ("actix-web", "Actix", "backend-api"),
                                ("rocket", "Rocket", "backend-api"), ("warp", "Warp", "backend-api"),
                                ("poem", "Poem", "backend-api"), ("leptos", "Leptos", "web-ui"),
                                ("yew", "Yew", "web-ui"), ("dioxus", "Dioxus", "web-ui"),
                                ("tauri", "Tauri", "web-ui"), ("ratatui", "Ratatui", "cli-library"),
                                ("clap", "Clap", "cli-library")]),
        ("requirements.txt", "Python", None), ("pyproject.toml", "Python", None),
        ("Pipfile", "Python", None), ("setup.py", "Python", None),
        ("composer.json", "PHP", [("livewire/livewire", "Livewire", "web-ui"),
                                  ("inertiajs/", "Inertia", "web-ui"),
                                  ("laravel/framework", "Laravel", "backend-api"),
                                  ("symfony/", "Symfony", "backend-api"),
                                  ("codeigniter4/", "CodeIgniter", "backend-api")]),
        ("Gemfile", "Ruby", [("view_component", "ViewComponent", "web-ui"),
                             ("rails", "Rails", "backend-api"), ("sinatra", "Sinatra", "backend-api"),
                             ("hanami", "Hanami", "backend-api")]),
        ("mix.exs", "Elixir", [("phoenix_live_view", "LiveView", "web-ui"), ("phoenix", "Phoenix", "backend-api")]),
        ("pom.xml", "Java", [("spring-boot-starter-thymeleaf", "Thymeleaf", "web-ui"),
                             ("spring-boot", "Spring Boot", "backend-api"),
                             ("quarkus", "Quarkus", "backend-api"),
                             ("micronaut", "Micronaut", "backend-api")]),
        ("build.gradle", "Java/Kotlin", [("com.android.application", "Android", "mobile-ui"),
                                         ("spring-boot", "Spring Boot", "backend-api"),
                                         ("io.ktor", "Ktor", "backend-api"),
                                         ("quarkus", "Quarkus", "backend-api")]),
        ("build.gradle.kts", "Kotlin", [("com.android.application", "Android", "mobile-ui"),
                                        ("spring-boot", "Spring Boot", "backend-api"),
                                        ("io.ktor", "Ktor", "backend-api"),
                                        ("quarkus", "Quarkus", "backend-api")]),
        ("Package.swift", "Swift", [("vapor/vapor", "Vapor", "backend-api")]),
        ("build.zig", "Zig", []), ("build.sbt", "Scala", [("play", "Play", "backend-api")]),
        ("CMakeLists.txt", "C/C++", [("qt", "Qt", "web-ui")]), ("meson.build", "C/C++", []),
    ]
    py_rules = [("streamlit", "Streamlit", "web-ui"), ("gradio", "Gradio", "web-ui"),
                ("nicegui", "NiceGUI", "web-ui"), ("fastapi", "FastAPI", "backend-api"),
                ("litestar", "Litestar", "backend-api"), ("starlette", "Starlette", "backend-api"),
                ("flask", "Flask", "backend-api"), ("django", "Django", "backend-api"),
                ("tornado", "Tornado", "backend-api"), ("typer", "Typer", "cli-library"),
                ("click", "Click", "cli-library")]
    for marker, lang, rules in simple:
        for m in has(marker):
            txt = read(root / m).lower()
            fw, typ = [], "cli-library"
            for needle, label, t in (rules if rules is not None else py_rules):
                if needle.lower() in txt:
                    fw.append(label)
                    if typ == "cli-library":
                        typ = t
            found.append({"marker": m, "language": lang, "frameworks": fw, "type": typ})

    for f in files:
        if f.endswith(".csproj") and f.count("/") <= 3:
            txt = read(root / f)
            if "Microsoft.Maui" in txt or "<UseMaui>" in txt:
                typ, fw = "mobile-ui", ["MAUI"]
            elif "Microsoft.NET.Sdk.Web" in txt:
                typ, fw = "backend-api", ["ASP.NET Core"]
                if "Blazor" in txt or "Razor" in txt:
                    typ, fw = "web-ui", ["Blazor/Razor"]
            else:
                typ, fw = "cli-library", []
            found.append({"marker": f, "language": "C#", "frameworks": fw, "type": typ})

    # Buang penanda di dalam folder platform native (android/, ios/, ...) jika
    # ada penanda utama di root (Flutter / React Native / Capacitor).
    platform_dirs = {"android", "ios", "macos", "linux", "windows", "web"}
    if any("/" not in p["marker"] for p in found):
        found = [p for p in found if p["marker"].split("/")[0] not in platform_dirs]

    if not found:
        exts = defaultdict(int)
        for f in files:
            exts[Path(f).suffix] += 1
        top = max(exts, key=exts.get) if exts else ""
        typ = "web-ui" if top in {".html", ".css"} else "cli-library"
        found.append({"marker": "(tidak ada)", "language": f"mayoritas {top or '?'}",
                      "frameworks": [], "type": typ})
    return {"packages": found, "monorepo": len(found) > 1}

# --------------------------------------------------------------------------
# Ekstraksi kerangka (skeleton)
# --------------------------------------------------------------------------
R = lambda p, f=re.M: re.compile(p, f)  # noqa: E731
JS = [R(r"^export\s+(?:default\s+)?(?:async\s+)?(?:function\*?|class|const|let|var|interface|type|enum)\s+(\w+)"),
      R(r"^(?:async\s+)?function\s+(\w+)"), R(r"^class\s+(\w+)"),
      R(r"^export\s+default\s+(\w+)")]
LANG = {
    "js": {"sym": JS,
           "route": [R(r"\b(?:app|router|server|api)\.(get|post|put|patch|delete|all)\(\s*['\"`]([^'\"`]+)"),
                     R(r"@(Get|Post|Put|Patch|Delete|Controller)\(\s*['\"]?([^'\")]*)"),
                     R(r"^export\s+(?:async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE)\b()")],
           "imp": [R(r"""(?:from|import)\s+['"](\.{1,2}/[^'"]+|@/[^'"]+|~/[^'"]+)['"]"""),
                   R(r"""require\(\s*['"](\.{1,2}/[^'"]+)['"]""")]},
    "py": {"sym": [R(r"^(?:async\s+)?def\s+(\w+)"), R(r"^class\s+(\w+)")],
           "route": [R(r"@\w+\.(get|post|put|patch|delete|route|api_route)\(\s*['\"]([^'\"]+)"),
                     R(r"\b(path|re_path)\(\s*r?['\"]([^'\"]*)")],
           "imp": [R(r"^from\s+(\.[\w.]*|[\w]+(?:\.[\w]+)+)\s+import"), R(r"^import\s+([\w.]+)")]},
    "go": {"sym": [R(r"^func\s+(?:\([^)]*\)\s+)?(\w+)"), R(r"^type\s+(\w+)\s+(?:struct|interface)")],
           "route": [R(r"\.(GET|POST|PUT|PATCH|DELETE|Get|Post|Put|Patch|Delete|HandleFunc|Handle)\(\s*\"([^\"]+)")],
           "imp": [R(r"^\s*(?:\w+\s+)?\"([\w.-]+/[^\"]+)\"\s*$")]},
    "dart": {"sym": [R(r"^(?:abstract\s+|sealed\s+|final\s+|base\s+|interface\s+)*class\s+(\w+)"),
                     R(r"^(?:mixin|extension|enum)\s+(\w+)"),
                     R(r"^(?:Future<[^>]*>|Stream<[^>]*>|void|[A-Z]\w*(?:<[^>]*>)?\??|int|double|bool|String)\s+(\w+)\s*\(")],
             "route": [R(r"GoRoute\(\s*(?:name:\s*['\"][^'\"]*['\"],\s*)?path:\s*['\"]([^'\"]+)()"),
                       R(r"\.(get|post|put|patch|delete)\(\s*['\"]([^'\"]+)")],
             "imp": [R(r"^import\s+['\"]((?:\.{1,2}/|package:)[^'\"]+)['\"]")]},
    "rs": {"sym": [R(r"^\s*pub(?:\([^)]*\))?\s+(?:async\s+)?fn\s+(\w+)"),
                   R(r"^\s*(?:pub\s+)?(?:struct|enum|trait)\s+(\w+)"), R(r"^fn\s+(main)")],
           "route": [R(r"\.route\(\s*\"([^\"]+)\"()"), R(r"#\[(get|post|put|patch|delete)\(\"([^\"]+)")],
           "imp": [R(r"^use\s+((?:crate|super|self)::[\w:]+)")]},
    "cs": {"sym": [R(r"(?:public|internal)\s+(?:static\s+|abstract\s+|sealed\s+|partial\s+)*(?:class|interface|record|struct|enum)\s+(\w+)"),
                   R(r"^\s+public\s+(?:static\s+|async\s+|virtual\s+|override\s+)*[\w<>\[\],?]+\s+(\w+)\s*\(")],
           "route": [R(r"\[(HttpGet|HttpPost|HttpPut|HttpPatch|HttpDelete|Route)\(?\"?([^\"\)\]]*)"),
                     R(r"\.Map(Get|Post|Put|Patch|Delete)\(\s*\"([^\"]+)")],
           "imp": [R(r"^using\s+([\w.]+);")]},
    "jvm": {"sym": [R(r"^\s*(?:public\s+|internal\s+|data\s+|abstract\s+|open\s+|sealed\s+)*(?:class|interface|object|enum class)\s+(\w+)"),
                    R(r"^\s*(?:public\s+|suspend\s+|override\s+)*fun\s+(\w+)"),
                    R(r"^\s+public\s+(?:static\s+)?[\w<>\[\],]+\s+(\w+)\s*\(")],
            "route": [R(r"@(Get|Post|Put|Patch|Delete|Request)Mapping\(?\s*(?:value\s*=\s*)?\"?([^\"\)]*)")],
            "imp": []},
    "php": {"sym": [R(r"^\s*(?:abstract\s+|final\s+)?class\s+(\w+)"), R(r"^\s*(?:public\s+|private\s+|protected\s+)?(?:static\s+)?function\s+(\w+)")],
            "route": [R(r"Route::(get|post|put|patch|delete|resource|apiResource)\(\s*['\"]([^'\"]+)")],
            "imp": [R(r"^use\s+(App\\[\w\\]+)")]},
    "rb": {"sym": [R(r"^\s*(?:class|module)\s+([\w:]+)"), R(r"^\s*def\s+(?:self\.)?(\w+[?!]?)")],
           "route": [R(r"^\s*(get|post|put|patch|delete|resources?|namespace)\s+['\":]([\w/:]+)")],
           "imp": [R(r"^require_relative\s+['\"]([^'\"]+)")]},
    "swift": {"sym": [R(r"^\s*(?:public\s+|final\s+|open\s+)*(?:class|struct|enum|protocol|actor)\s+(\w+)"),
                      R(r"^\s*(?:public\s+|private\s+|static\s+)*func\s+(\w+)")],
              "route": [], "imp": []},
    "ex": {"sym": [R(r"^\s*defmodule\s+([\w.]+)"), R(r"^\s*def\s+(\w+[?!]?)")],
           "route": [R(r"^\s*(get|post|put|patch|delete|live|resources)\s+\"([^\"]+)")], "imp": []},
    "c": {"sym": [R(r"^(?:static\s+|inline\s+|extern\s+)*[\w*]+\s+(\w+)\s*\([^;]*\)\s*\{"),
                  R(r"^(?:typedef\s+)?(?:struct|enum|class)\s+(\w+)")],
          "route": [], "imp": [R(r'^#include\s+"([^"]+)"')]},
    "zig": {"sym": [R(r"^\s*(?:pub\s+)?fn\s+(\w+)"), R(r"^\s*pub\s+const\s+(\w+)\s*=")],
            "route": [], "imp": [R(r'@import\("([^"]+)"\)')]},
    "lua": {"sym": [R(r"^(?:local\s+)?function\s+([\w.:]+)")],
            "route": [], "imp": [R(r"""require\s*\(?\s*['"]([^'"]+)['"]""")]},
}
EXT_LANG = {".js": "js", ".jsx": "js", ".ts": "js", ".tsx": "js", ".mjs": "js", ".cjs": "js",
            ".vue": "js", ".svelte": "js", ".astro": "js", ".py": "py", ".go": "go",
            ".dart": "dart", ".rs": "rs", ".cs": "cs", ".java": "jvm", ".kt": "jvm",
            ".kts": "jvm", ".scala": "jvm", ".php": "php", ".rb": "rb", ".swift": "swift",
            ".ex": "ex", ".exs": "ex", ".c": "c", ".h": "c", ".cpp": "c", ".hpp": "c",
            ".cc": "c", ".zig": "zig", ".lua": "lua"}
TEMPLATE_UI_EXT = {".erb", ".heex", ".templ", ".razor", ".cshtml", ".twig", ".xaml", ".vue", ".svelte", ".astro"}
UI_HINT = {
    "jsx": re.compile(r"(<[A-Z]\w*[\s/>]|return\s*\(\s*<|<template>|<div[\s>]|JSX\.Element|React\.FC|StyleSheet\.create)"),
    "dart": re.compile(r"(extends\s+(?:Stateless|Stateful|Consumer|Hook|ConsumerStateful)Widget|Widget\s+build\s*\()"),
    "jvm": re.compile(r"@Composable"),
    "swift": re.compile(r"(some\s+View\b|UIViewController)"),
    "py": re.compile(r"(\bst\.\w+\(|gr\.Blocks|render_template\(|render\s*\(\s*request)"),
    "php": re.compile(r"(return\s+view\(|@extends\(|@section\()"),
}
UI_EXT = {".jsx": "jsx", ".tsx": "jsx", ".vue": "jsx", ".svelte": "jsx", ".astro": "jsx",
          ".html": "jsx", ".dart": "dart", ".kt": "jvm", ".swift": "swift", ".py": "py", ".php": "php"}


def short_import(s: str) -> str:
    s = re.sub(r"^(\.\./)+|^\./|^package:[\w_]+/|^@/|^~/", "", s)
    s = re.sub(r"\.(dart|js|ts|tsx|jsx|mjs)$", "", s)
    return "/".join(s.split("/")[-2:])


METHOD_RE = {
    "js": R(r"^\s+(?:public\s+|async\s+|static\s+|get\s+|set\s+)*(\w+)\s*\([^)]*\)\s*(?::[^{;]+)?\{"),
    "py": R(r"^\s+(?:async\s+)?def\s+([a-zA-Z]\w*)\s*\("),
    "dart": R(r"^\s+(?:Future<[^>]*>|Stream<[^>]*>|void|[A-Z]\w*(?:<[^>]*>)?\??|int|double|bool|String)\s+([a-z]\w*)\s*\("),
    "go": R(r"^func\s+\([^)]+\)\s+([A-Z]\w*)\s*\("),
    "rs": R(r"^\s+pub(?:\([^)]*\))?\s+(?:async\s+)?fn\s+(\w+)\s*\("),
    "cs": R(r"^\s+public\s+(?:static\s+|async\s+|virtual\s+|override\s+)*[\w<>\[\],?]+\s+(\w+)\s*\("),
    "jvm": R(r"^\s+(?:public\s+|suspend\s+|override\s+)*(?:fun\s+)?(\w+)\s*\("),
    "php": R(r"^\s+public\s+(?:static\s+)?function\s+(\w+)\s*\("),
    "rb": R(r"^\s+def\s+(?:self\.)?([a-zA-Z]\w*[?!]?)"),
    "swift": R(r"^\s+(?:public\s+|open\s+|static\s+)*func\s+(\w+)\s*\("),
}
PROP_RE = {
    "dart": R(r"^\s+final\s+[\w<>?,\s]+\s+([a-z]\w*)\s*;"),
    "js": R(r"^\s+(?:readonly\s+)?([a-zA-Z]\w*)\??\s*:\s*[^;={\n]+[;,]"),
    "py": R(r"^\s+([a-zA-Z]\w*)\s*:\s*[\w\[\]|., ]+(?:\s*=|$)"),
    "swift": R(r"^\s+(?:@\w+\s+)?(?:let|var)\s+([a-zA-Z]\w*)\s*:"),
    "cs": R(r"^\s+public\s+[\w<>?\[\]]+\s+(\w+)\s*\{\s*get;"),
}
IGNORE_METH = {"if", "for", "while", "switch", "catch", "constructor", "build", "createState",
               "initState", "dispose", "didUpdateWidget", "toString", "hashCode", "equals", "super"}


def skeleton(path: Path, max_symbols: int) -> dict:
    txt = read(path)
    lines = txt.count("\n") + (1 if txt and not txt.endswith("\n") else 0)
    suf = path.suffix.lower()
    is_tpl_ui = suf in TEMPLATE_UI_EXT or path.name.endswith(".blade.php")
    info = {"loc": lines, "symbols": [], "methods": [], "props": [], "routes": [], "imports": [], "ui": is_tpl_ui}
    lang = EXT_LANG.get(suf)
    if not lang:
        return info
    rules = LANG[lang]
    seen = set()
    for rx in rules["sym"]:
        for m in rx.finditer(txt):
            name = m.group(1)
            if not name or name in seen or name.startswith("_"):
                continue
            seen.add(name)
            info["symbols"].append(name)
    info["symbols"] = info["symbols"][:max_symbols]
    m_rx = METHOD_RE.get(lang)
    if m_rx:
        m_seen = set(info["symbols"]) | IGNORE_METH
        for m in m_rx.finditer(txt):
            name = m.group(1)
            if name and name not in m_seen and not name.startswith("_"):
                m_seen.add(name)
                info["methods"].append(name)
        info["methods"] = info["methods"][:max_symbols]
    p_rx = PROP_RE.get(lang)
    if p_rx:
        p_seen = set()
        for m in p_rx.finditer(txt):
            name = m.group(1)
            if name and name not in p_seen and not name.startswith("_"):
                p_seen.add(name)
                info["props"].append(name)
        info["props"] = info["props"][:15]
    for rx in rules["route"]:
        for m in rx.finditer(txt):
            g = [x for x in m.groups() if x is not None]
            info["routes"].append(" ".join(x for x in g if x).strip())
    info["routes"] = sorted(set(info["routes"]))[:max_symbols]
    info["imports"] = sorted({short_import(m.group(1)) for rx in rules["imp"] for m in rx.finditer(txt)})
    if len(info["imports"]) > 10:
        info["imports"] = info["imports"][:10] + [f"+{len(info['imports']) - 10} lagi"]
    ui_rx = UI_HINT.get(UI_EXT.get(suf, ""))
    info["ui"] = is_tpl_ui or bool(ui_rx and ui_rx.search(txt))
    return info

# --------------------------------------------------------------------------
# Daftar file
# --------------------------------------------------------------------------
def list_files(root: Path) -> list[str]:
    files: list[str] = []
    try:
        out = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=root,
                             capture_output=True, text=True, timeout=60, check=True).stdout
        files = [l for l in out.splitlines() if l]
    except (OSError, subprocess.SubprocessError):
        for dp, dns, fns in os.walk(root):
            dns[:] = [d for d in dns if d not in IGNORE_DIRS and not d.endswith(".egg-info")]
            rel = os.path.relpath(dp, root)
            for fn in fns:
                files.append(fn if rel == "." else f"{rel}/{fn}".replace(os.sep, "/"))
    keep = []
    for f in files:
        parts = f.split("/")
        if any(p in IGNORE_DIRS or p.endswith(".egg-info") for p in parts[:-1]):
            continue
        if IGNORE_FILE_RE.search(f):
            continue
        if (root / f).is_file():
            keep.append(f)
    return sorted(keep)

# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
HASH_RE = re.compile(r"babydocs:hash=([0-9a-f]{8,64})")


def main() -> int:
    ap = argparse.ArgumentParser(description="babydocs project scanner")
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--only", default="", help="batasi ke sub-path tertentu, mis. src/features")
    ap.add_argument("--json", action="store_true", help="output JSON, bukan Markdown")
    ap.add_argument("--max-symbols", type=int, default=25)
    ap.add_argument("--out", default="", help="tulis ke file, bukan stdout")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    all_files = list_files(root)
    stack = detect_stack(root, all_files)
    only = a.only.strip("/")
    src = [f for f in all_files if Path(f).suffix.lower() in SOURCE_EXT
           and (not only or f == only or f.startswith(only + "/"))]

    # Kelompokkan per folder (dibatasi MAX_DEPTH)
    folders: dict[str, dict] = defaultdict(lambda: {"files": {}, "tests": [], "children": set()})
    skel: dict[str, dict] = {}
    for f in src:
        parts = f.split("/")
        d = "/".join(parts[:-1][:MAX_DEPTH]) or "."
        if TEST_RE.search(f):
            folders[d]["tests"].append(f)
            continue
        folders[d]["files"][f] = skel[f] = skeleton(root / f, a.max_symbols)
    # hubungan parent-child
    for d in list(folders):
        p = d
        while p not in (".", ""):
            parent = "/".join(p.split("/")[:-1]) or "."
            folders[parent]["children"].add(p)
            p = parent

    def is_doc(d: str) -> bool:
        info = folders[d]
        return len(info["files"]) >= 2 or any(is_doc(c) for c in info["children"])

    doc_dirs = [d for d in folders if d != "." and is_doc(d)]
    # gabungkan folder 1-file ke induk
    merged = defaultdict(list)
    for d, info in folders.items():
        if d != "." and d not in doc_dirs and info["files"]:
            parent = "/".join(d.split("/")[:-1]) or "."
            while parent not in doc_dirs and parent != ".":
                parent = "/".join(parent.split("/")[:-1]) or "."
            merged[parent].extend(info["files"].keys())

    pkg_type = stack["packages"][0]["type"]
    result = []
    for d in sorted(doc_dirs, key=lambda x: (-x.count("/"), x)):
        info = folders[d]
        files = dict(info["files"])
        for mf in merged.get(d, []):
            files[mf] = skel[mf]
        h = hashlib.sha1()
        for f in sorted(files):
            h.update(f.encode())
            try:
                h.update((root / f).read_bytes())
            except OSError:
                pass
        digest = h.hexdigest()[:12]
        readme = root / d / "README.md"
        old = HASH_RE.search(read(readme, 20_000)) if readme.exists() else None
        status = "new" if not readme.exists() else ("unchanged" if old and old.group(1) == digest else "changed")
        name = d.split("/")[-1].lower()
        ui_files = sum(1 for s in files.values() if s["ui"])
        visual = "screenshot" if pkg_type in ("web-ui", "mobile-ui") and (
            name in UI_DIR_NAMES or ui_files * 2 >= max(1, len(files))) else "mermaid"
        result.append({
            "folder": d, "depth": d.count("/") + 1, "status": status, "hash": digest,
            "visual": visual, "loc": sum(s["loc"] for s in files.values()),
            "children": sorted(c for c in info["children"] if c in doc_dirs),
            "tests": sorted(info["tests"]), "files": files,
        })

    root_files = {f: s for f, s in folders["."]["files"].items()}
    root_files.update({f: skel[f] for f in merged.get(".", [])})
    data = {"root": str(root), "stack": stack, "total_source_files": len(src),
            "total_loc": sum(r["loc"] for r in result) + sum(s["loc"] for s in root_files.values()),
            "doc_folders": result, "root_files": root_files}

    if a.json:
        out = json.dumps(data, indent=2, ensure_ascii=False)
    else:
        out = render_md(data)
    if a.out:
        Path(a.out).write_text(out, encoding="utf-8")
        print(f"Peta proyek ditulis ke {a.out} ({len(result)} Folder Dok, {len(src)} file source)")
    else:
        sys.stdout.write(out)
    return 0


def fmt_file(f: str, s: dict) -> str:
    bits = [f"`{Path(f).name}` ({s['loc']} baris{', UI' if s['ui'] else ''})"]
    if s["symbols"]:
        bits.append("sym: " + ", ".join(s["symbols"]))
    if s.get("methods"):
        bits.append("methods: " + ", ".join(s["methods"]))
    if s.get("props"):
        bits.append("props/fields: " + ", ".join(s["props"]))
    if s["routes"]:
        bits.append("route: " + "; ".join(s["routes"]))
    if s["imports"]:
        bits.append("import: " + ", ".join(s["imports"]))
    return "  - " + " · ".join(bits)


def render_md(d: dict) -> str:
    L = ["# babydocs — Peta Proyek", "", f"Root: `{d['root']}`",
         f"File source: {d['total_source_files']} · Total baris: {d['total_loc']}", "", "## Stack", ""]
    for p in d["stack"]["packages"]:
        fw = ", ".join(p["frameworks"]) or "-"
        L.append(f"- `{p['marker']}` → {p['language']} · {fw} · **{p['type']}**")
        if p.get("scripts"):
            L.append("  - scripts: " + ", ".join(f"`{k}`=`{v}`" for k, v in list(p["scripts"].items())[:8]))
    if d["stack"]["monorepo"]:
        L.append("- ⚠️ Lebih dari satu penanda → kemungkinan monorepo; tentukan tipe per package.")
    todo = [r for r in d["doc_folders"] if r["status"] != "unchanged"]
    skip = [r for r in d["doc_folders"] if r["status"] == "unchanged"]
    L += ["", f"## Folder Dok (bottom-up) — {len(todo)} perlu dikerjakan, {len(skip)} tidak berubah", ""]
    for r in d["doc_folders"]:
        L.append(f"- [{r['status']}] `{r['folder']}` · visual: {r['visual']} · {len(r['files'])} file · "
                 f"{r['loc']} baris · hash={r['hash']}")
    L += ["", "## Kerangka per Folder", ""]
    for r in todo:
        L.append(f"### `{r['folder']}`  (hash={r['hash']}, visual={r['visual']})")
        if r["children"]:
            L.append("- sub-folder dok: " + ", ".join(f"`{c}`" for c in r["children"]))
        if r["tests"]:
            L.append(f"- test: {len(r['tests'])} file (" + ", ".join(f"`{Path(t).name}`" for t in r["tests"][:5]) + ")")
        for f, s in sorted(r["files"].items()):
            L.append(fmt_file(f, s))
        L.append("")
    if d["root_files"]:
        L += ["### `(root)`"] + [fmt_file(f, s) for f, s in sorted(d["root_files"].items())] + [""]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
