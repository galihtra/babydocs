#!/usr/bin/env sh
# Pasang perintah `babydocs` ke PATH (macOS / Linux).
#   ./install.sh               → ~/.local/bin/babydocs
#   ./install.sh /usr/local/bin
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="${1:-$HOME/.local/bin}"

command -v python3 >/dev/null 2>&1 || { echo "✗ python3 tidak ditemukan. Install Python 3.8+ dulu."; exit 1; }

chmod +x "$HERE/bin/babydocs" "$HERE/scripts/scan.py"
mkdir -p "$DEST"
ln -sf "$HERE/bin/babydocs" "$DEST/babydocs"
echo "✓ babydocs terpasang di $DEST/babydocs"

case ":$PATH:" in
  *":$DEST:"*) ;;
  *)
    echo ""
    echo "⚠ $DEST belum ada di PATH. Tambahkan baris ini ke ~/.zshrc atau ~/.bashrc:"
    echo "    export PATH=\"$DEST:\$PATH\""
    ;;
esac
echo ""
echo "Coba:  babydocs --help"
