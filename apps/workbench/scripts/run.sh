#!/bin/bash
# Launch the Feralboard Workbench GUI on the Sway/Wayland desktop
# Use this when running over SSH — it sets the env vars needed to reach the compositor

export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export WAYLAND_DISPLAY="wayland-1"
export GDK_BACKEND="wayland"

# Auto-detect the Sway IPC socket
export SWAYSOCK=$(ls /run/user/$(id -u)/sway-ipc.*.sock 2>/dev/null | head -1)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
"$SCRIPT_DIR/python.sh" "$SCRIPT_DIR/../gui/app.py" &
APP_PID=$!

# Wait for the window to appear, then fullscreen it via sway
sleep 2
swaymsg '[pid='"$APP_PID"'] fullscreen enable' 2>/dev/null

wait $APP_PID
