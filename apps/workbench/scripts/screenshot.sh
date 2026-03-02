#!/bin/bash
# Take a screenshot of the Sway display and save to a fixed path
# Usage: bash screenshot.sh [output_path]

export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export WAYLAND_DISPLAY="wayland-1"
export SWAYSOCK=$(ls /run/user/$(id -u)/sway-ipc.*.sock 2>/dev/null | head -1)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKBENCH_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

OUT="${1:-$WORKBENCH_ROOT/screen.png}"
grim "$OUT" && echo "Screenshot saved to $OUT"
