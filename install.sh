#!/usr/bin/env sh
# Installer 1-langkah babydocs (macOS / Linux).
# Dirancang untuk pengguna awam:
#   1. Auto-install Python 3 jika belum ada (tanpa perlu konfigurasi manual).
#   2. Pasang perintah `babydocs` ke ~/.local/bin dan otomatis tambahkan ke PATH.
#   3. Otomatis hubungkan skill ke coding agent yang terdeteksi (Antigravity, Claude Code, Gemini CLI).
#
# Pemakaian:
#   ./install.sh                  # pasang lengkap
#   ./install.sh /usr/local/bin   # pasang ke folder lain
#   ./install.sh --python-only    # hanya pastikan Python tersedia
#   ./install.sh --no-skill       # jangan tautkan ke folder skill agent
set -e

HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.local/bin"
PYTHON_ONLY=0
LINK_SKILL=1

for arg in "$@"; do
  case "$arg" in
    --python-only) PYTHON_ONLY=1 ;;
    --no-skill)    LINK_SKILL=0 ;;
    -h|--help)
      echo "Pemakaian: ./install.sh [FOLDER_BIN] [--no-skill] [--python-only]"
      exit 0
      ;;
    *) DEST="$arg" ;;
  esac
done

find_python() {
  for cand in python3 /opt/homebrew/bin/python3 /usr/local/bin/python3 python; do
    if command -v "$cand" >/dev/null 2>&1; then
      if "$cand" -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >/dev/null 2>&1; then
        command -v "$cand"
        return 0
      fi
    fi
  done
  for uv_bin in "$(command -v uv 2>/dev/null || true)" "$HOME/.local/bin/uv" "$HOME/.cargo/bin/uv"; do
    if [ -n "$uv_bin" ] && [ -x "$uv_bin" ]; then
      found="$("$uv_bin" python find '>=3.8' 2>/dev/null || true)"
      if [ -n "$found" ] && [ -x "$found" ]; then
        printf '%s\n' "$found"
        return 0
      fi
    fi
  done
  return 1
}

ensure_python() {
  PY="$(find_python || true)"
  if [ -n "$PY" ]; then
    echo "✓ Sistem siap ($PY)"
    return 0
  fi

  echo "⏳ Kebutuhan sistem (Python 3) belum ada. Memasang secara otomatis…"
  OS="$(uname -s 2>/dev/null || echo unknown)"

  # 1. macOS dengan Homebrew
  if [ "$OS" = "Darwin" ] && command -v brew >/dev/null 2>&1; then
    echo "   → Memasang lewat Homebrew…"
    brew install python3 && PY="$(find_python || true)"
  fi

  # 2. Portable tanpa sudo lewat uv (berjalan di macOS & Linux)
  if [ -z "$PY" ] && command -v curl >/dev/null 2>&1; then
    echo "   → Mengunduh runtime Python mandiri (tanpa butuh password admin)…"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    UV_BIN="$HOME/.local/bin/uv"
    [ -x "$UV_BIN" ] || UV_BIN="$(command -v uv 2>/dev/null || true)"
    if [ -n "$UV_BIN" ] && [ -x "$UV_BIN" ]; then
      "$UV_BIN" python install 3.12
      PY="$(find_python || true)"
    fi
  fi

  # 3. Fallback package manager Linux
  if [ -z "$PY" ] && [ "$OS" = "Linux" ]; then
    if command -v apt-get >/dev/null 2>&1; then
      echo "   → Memasang lewat apt…"
      sudo apt-get update -qq && sudo apt-get install -y -qq python3
    elif command -v dnf >/dev/null 2>&1; then
      echo "   → Memasang lewat dnf…"
      sudo dnf install -y -q python3
    elif command -v pacman >/dev/null 2>&1; then
      echo "   → Memasang lewat pacman…"
      sudo pacman -Sy --noconfirm python
    fi
    PY="$(find_python || true)"
  fi

  if [ -z "$PY" ]; then
    echo "✗ Gagal memasang Python otomatis (cek koneksi internet)."
    echo "  Unduh manual dari https://www.python.org/downloads/ lalu jalankan ./install.sh lagi."
    exit 1
  fi
  echo "✓ Berhasil terpasang ($PY)"
}

add_to_path() {
  case ":$PATH:" in
    *":$DEST:"*) return 0 ;;
  esac

  LINE="export PATH=\"$DEST:\$PATH\" # babydocs"
  UPDATED=""
  for rc in "$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.profile"; do
    if [ -f "$rc" ]; then
      if ! grep -Fq "$DEST" "$rc" 2>/dev/null; then
        printf '\n%s\n' "$LINE" >> "$rc"
        UPDATED="$UPDATED $rc"
      fi
    fi
  done

  if [ -z "$UPDATED" ]; then
    # Buat ~/.zshrc (default macOS) atau ~/.bashrc jika belum ada
    TARGET_RC="$HOME/.bashrc"
    [ "$(uname -s)" = "Darwin" ] && TARGET_RC="$HOME/.zshrc"
    if ! grep -Fq "$DEST" "$TARGET_RC" 2>/dev/null; then
      printf '\n%s\n' "$LINE" >> "$TARGET_RC"
      UPDATED="$TARGET_RC"
    fi
  fi

  if [ -n "$UPDATED" ]; then
    echo "✓ PATH otomatis ditambahkan ke:$UPDATED"
    echo "  (Buka ulang terminal, atau jalankan: export PATH=\"$DEST:\$PATH\")"
  fi
}

link_agent_skills() {
  LINKED=""
  for base in "$HOME/.gemini/antigravity" "$HOME/.claude" "$HOME/.gemini"; do
    if [ -d "$base" ]; then
      mkdir -p "$base/skills"
      target="$base/skills/babydocs"
      if [ ! -e "$target" ] && [ ! -L "$target" ]; then
        ln -s "$HERE" "$target"
        LINKED="$LINKED $target"
      fi
    fi
  done
  if [ -n "$LINKED" ]; then
    echo "✓ Skill babydocs otomatis terhubung ke:$LINKED"
  fi
}

echo ""
echo "  🧸 Memasang babydocs…"
echo ""

ensure_python
[ "$PYTHON_ONLY" -eq 1 ] && exit 0

chmod +x "$HERE/bin/babydocs" "$HERE/scripts/cli.py" "$HERE/scripts/scan.py"
mkdir -p "$DEST"
ln -sf "$HERE/bin/babydocs" "$DEST/babydocs"
echo "✓ Perintah 'babydocs' terpasang di $DEST/babydocs"

add_to_path
[ "$LINK_SKILL" -eq 1 ] && link_agent_skills

echo ""
echo "🎉 Selesai! Cara pakai:"
echo "   1. Minta AI agent di proyekmu:  /babydocs"
echo "   2. Buka web dokumentasinya:     babydocs serve --open"
echo ""
