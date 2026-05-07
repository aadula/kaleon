#!/usr/bin/env bash
# macOS launcher for Chandra-backed server (PORT defaults to 3010).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PORT="${PORT:-3010}"
export CHANDRA_SERVER_NO_DELEGATE=1

if [[ -f "$SCRIPT_DIR/.venv/bin/activate" ]]; then
  # shellcheck source=/dev/null
  source "$SCRIPT_DIR/.venv/bin/activate"
fi

exec python3 "$SCRIPT_DIR/marker_server.py"
