#!/bin/bash
# Install dependencies for the Feralboard Workbench
# Run with: sudo bash setup.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MONOREPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
SDK_DIR="$MONOREPO_ROOT/packages/feralboard-sdk-py"

echo "Installing dependencies..."
apt-get update
apt-get install -y \
    python3 \
    python3-venv \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-3.0 \
    python3-serial \
    grim \
    socat

echo "Creating virtual environment at $VENV_DIR..."
python3 -m venv --system-site-packages "$VENV_DIR"

echo "Installing Python packages into virtual environment..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
"$VENV_DIR/bin/pip" install "$SDK_DIR"

echo "Done. Run the app with: bash scripts/run.sh"
