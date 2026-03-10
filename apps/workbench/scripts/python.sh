#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKBENCH_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PYTHON="$WORKBENCH_ROOT/.venv/bin/python"

if [[ ! -x "$VENV_PYTHON" ]]; then
    echo "Missing virtualenv at $WORKBENCH_ROOT/.venv" >&2
    echo "Run: sudo bash $WORKBENCH_ROOT/setup.sh" >&2
    exit 1
fi

exec "$VENV_PYTHON" "$@"
