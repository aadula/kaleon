#!/usr/bin/env bash
# Local macOS launcher for marker_server.py — same defaults as the Python entrypoint (PORT 3010).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PORT="${PORT:-3010}"
# Prevents marker_server.py from re-invoking this script when started via `python marker_server.py`.
export MARKER_SERVER_NO_DELEGATE=1

if [[ -f "$SCRIPT_DIR/.venv/bin/activate" ]]; then
  # shellcheck source=/dev/null
  source "$SCRIPT_DIR/.venv/bin/activate"
fi

exec python3 "$SCRIPT_DIR/marker_server.py"
