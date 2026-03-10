#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$APP_DIR"

SERVER_PID=""
CLIENT_PID=""

cleanup() {
  for pid in "$CLIENT_PID" "$SERVER_PID"; do
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
    fi
  done
}

trap cleanup EXIT INT TERM

echo "[pi-web] starting API server on :3001"
npm run dev:server &
SERVER_PID=$!

echo "[pi-web] starting Vite client on :5173"
npm run dev:client &
CLIENT_PID=$!

wait -n "$SERVER_PID" "$CLIENT_PID"
