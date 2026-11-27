<p align="left">
  <img src="assets/icon.png" alt="babydocs" width="76" />
</p>

# babydocs

An agent skill and CLI that turns any codebase into browsable, folder-by-folder web documentation written in plain language.

Every folder gets a `README.md` that explains what the code does using everyday analogies, anchored to the real file names, functions, routes, and props underneath. UI folders get automatic screenshots; backend, CLI, and logic folders get flowcharts and real input/output examples.

## Install

No manual Python or `PATH` setup required. The installer checks your machine, installs a standalone Python runtime if none is found, puts `babydocs` on your `PATH`, and links the skill to any installed coding agent (`~/.gemini/antigravity/skills`, `~/.claude/skills`, `~/.gemini/skills`, `~/.codex/skills`, `~/.agents/skills`, `~/.cursor/skills`).

**macOS / Linux:**

```bash
git clone https://github.com/galihtra/babydocs.git ~/babydocs
cd ~/babydocs
./install.sh
```

**Windows:**

Clone or download this repository, then double-click `install.bat` (or run `.\install.ps1` in PowerShell). Reopen your terminal afterwards.

Check that everything is ready:

```bash
babydocs doctor
```

If you use another coding agent (Codex, Cursor, etc.), point it to `~/babydocs/SKILL.md`.

## Usage

Open any project in your coding agent and invoke the skill:

```text
/babydocs       # Claude Code, Antigravity, Gemini CLI
$babydocs       # Codex
```

You can also scope or update it:

```text
Run babydocs only for internal/payments
Update babydocs for changes since the last commit
```

Once generated, preview the docs locally:

```bash
cd /path/to/your-project
babydocs serve --open
```

The local server automatically serves the generated `docs/` folder on `http://localhost:3000` with live reload, keeping your source directories (`src/`, `lib/`, etc.) completely clean.

To publish on GitHub Pages, commit the `docs/` folder and enable **Settings → Pages → Deploy from a branch → `/docs`**.

## CLI commands

| Command | Description |
|---|---|
| `babydocs serve [dir]` | Serve the docs locally with live reload (`-p PORT`, `--open`, `--host 0.0.0.0`, `--no-reload`) |
| `babydocs init [dir]` | Write `index.html` (or `docs.html`) and `.nojekyll` into a project |
| `babydocs scan [dir]` | Generate a compact project map (`--only PATH`, `--json`, `--out FILE`) |
| `babydocs check [dir]` | Verify sidebar links, embedded images, leftover placeholders, and temp files |
| `babydocs doctor` | Check runtime and optional capture tools |
| `babydocs version` | Print CLI version |

If `babydocs` is invoked on a machine without Python, the launcher automatically runs the runtime installer first.

## Supported languages and frameworks

`babydocs` detects the stack from project config files and picks the visual adapter per folder:

| Ecosystem | Examples detected | Visual adapter |
|---|---|---|
| Go | Gin, Echo, Fiber, Chi, Templ, Cobra, Bubbletea | Mermaid diagrams (or web capture for Templ) |
| Python | FastAPI, Flask, Django, Litestar, Streamlit, Gradio, Typer, Click | Mermaid diagrams; web capture for templates/UI |
| Rust | Axum, Actix, Rocket, Warp, Leptos, Yew, Dioxus, Tauri, Clap | Mermaid diagrams; web capture for UI |
| Java / Kotlin | Spring Boot, Quarkus, Micronaut, Ktor, Thymeleaf, Android | Mermaid diagrams; web or emulator capture for UI |
| C# / .NET | ASP.NET Core, Blazor, Razor Pages, MAUI | Mermaid diagrams; web or simulator capture for UI |
| PHP | Laravel, Livewire, Inertia, Symfony, CodeIgniter | Mermaid diagrams; web capture for Blade/Twig |
| Ruby | Rails, ViewComponent, Sinatra, Hanami | Mermaid diagrams; web capture for views |
| Elixir | Phoenix, LiveView | Mermaid diagrams; web capture for LiveView |
| Swift | SwiftUI, UIKit, Vapor | Simulator capture for UI; Mermaid for Vapor/libs |
| JavaScript / TypeScript | React, Next.js, Vue, Nuxt, Svelte, Angular, Astro, NestJS, Express, Fastify, Hono, React Native | Web/simulator capture for UI; Mermaid for APIs/logic |
| Dart | Flutter, Shelf, Dart Frog | Simulator/golden capture for UI; Mermaid for logic |
| C / C++ / Zig / Scala / Lua | CMake, Meson, `build.zig`, `build.sbt`, scripts | Mermaid diagrams |

Projects with no recognized manifest fall back to file-extension detection and Mermaid diagrams. Monorepos are classified per package.

## How it stays fast on large codebases

Instead of opening hundreds of files one by one, the skill runs `babydocs scan` first. In a single pass (using Python's standard library), it extracts:

- Stack, scripts, and bottom-up folder order
- Per-file skeletons: exported symbols, classes, functions, HTTP routes, local imports, line counts, and UI hints
- Content hashes per folder, compared against `<!-- babydocs:hash=... -->` in existing READMEs so unchanged folders are skipped on re-runs

The agent reads files in tiers (skeleton-only for small files/DTOs, full read for medium files, targeted grep for files over 400 lines) and splits large trees across parallel sub-agents when supported.

## Optional tools

Nothing extra is required—if a screenshot tool is missing, `babydocs` falls back to Mermaid component diagrams.

- **Web screenshots:** Playwright (`npx playwright install chromium`) or Playwright MCP
- **Android screenshots:** `adb` (Android SDK Platform Tools)
- **iOS screenshots:** `xcrun simctl` (Xcode on macOS)
- **Flutter widget snapshots:** `flutter test`

## Guarantees

- Source code is never modified. Only `README.md`, `assets/*.png`, `_sidebar.md`, `index.html`/`docs.html`, and `.nojekyll` are written.
- Generated sections are wrapped in `<!-- babydocs:start -->` … `<!-- babydocs:end -->`, so hand-written README content is preserved on updates.
- Temporary capture scripts and snapshot tests are deleted after each run.

## Repository layout

```text
babydocs/
├── SKILL.md
├── README.md
├── assets/
│   └── icon.png
├── install.sh
├── install.ps1
├── install.bat
├── bin/
│   ├── babydocs
│   └── babydocs.cmd
├── scripts/
│   ├── cli.py
│   └── scan.py
└── templates/
    ├── index.html
    ├── folder-readme-template.md
    ├── root-readme-template.md
    └── _sidebar-template.md
```

## License

MIT
