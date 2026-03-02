#!/bin/bash
# Install dependencies for the Feralboard Workbench
# Run with: sudo bash setup.sh

set -e

echo "Installing dependencies..."
apt-get update
apt-get install -y \
    python3 \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-3.0 \
    python3-serial \
    grim \
    socat

echo "Done. Run the app with: bash scripts/run.sh"
