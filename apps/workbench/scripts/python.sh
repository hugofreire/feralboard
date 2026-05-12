#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKBENCH_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MONOREPO_ROOT="$(cd "$WORKBENCH_ROOT/../.." && pwd)"
VENV_PYTHON="$WORKBENCH_ROOT/.venv/bin/python"
SDK_SRC="$MONOREPO_ROOT/packages/feralboard-sdk-py/src"

if [[ ! -x "$VENV_PYTHON" ]]; then
    echo "Missing virtualenv at $WORKBENCH_ROOT/.venv" >&2
    echo "Run: sudo bash $WORKBENCH_ROOT/setup.sh" >&2
    exit 1
fi

export PYTHONPATH="$SDK_SRC:$WORKBENCH_ROOT${PYTHONPATH:+:$PYTHONPATH}"

exec "$VENV_PYTHON" "$@"
