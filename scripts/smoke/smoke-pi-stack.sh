#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORKBENCH_DIR="$ROOT/apps/workbench"
PI_WEB_DIR="$ROOT/apps/pi-web"
SOCKET_PATH="/tmp/feralboard-workbench.sock"
SERVER_PORT="${PI_WEB_SERVER_PORT:-3001}"
CLIENT_PORT="${PI_WEB_CLIENT_PORT:-5173}"
DEFAULT_LOCAL_NODE="/home/pi/.local/node-v20.19.0-package/node_modules/.bin/node"
if [ -z "${NODE_BIN:-}" ] && [ -x "$DEFAULT_LOCAL_NODE" ]; then
  NODE_BIN="$DEFAULT_LOCAL_NODE"
else
  NODE_BIN="${NODE_BIN:-node}"
fi
if [ -n "${NPM_BIN:-}" ]; then
  NPM_BIN="$NPM_BIN"
else
  NPM_BIN="npm"
fi

WORKBENCH_LOG="$(mktemp)"
SERVER_LOG="$(mktemp)"
CLIENT_LOG="$(mktemp)"
WORKBENCH_PID=""
SERVER_PID=""
CLIENT_PID=""

cleanup() {
  for pid in "$CLIENT_PID" "$SERVER_PID" "$WORKBENCH_PID"; do
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
}
trap cleanup EXIT

wait_for_http() {
  local url="$1"
  local attempts="${2:-30}"
  local delay="${3:-1}"
  local i
  for ((i = 1; i <= attempts; i++)); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep "$delay"
  done
  return 1
}

wait_for_socket() {
  local path="$1"
  local attempts="${2:-30}"
  local delay="${3:-1}"
  local i
  for ((i = 1; i <= attempts; i++)); do
    if [ -S "$path" ]; then
      return 0
    fi
    sleep "$delay"
  done
  return 1
}

socket_cmd() {
  python3 - "$SOCKET_PATH" "$1" <<'PY'
import socket
import sys

path, message = sys.argv[1], sys.argv[2]
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect(path)
sock.sendall(message.encode())
chunks = []
while True:
    data = sock.recv(4096)
    if not data:
        break
    chunks.append(data)
sock.close()
sys.stdout.write(b"".join(chunks).decode())
PY
}

wait_for_ipc() {
  local attempts="${1:-30}"
  local delay="${2:-1}"
  local i
  for ((i = 1; i <= attempts; i++)); do
    if PAGE_OUTPUT="$(socket_cmd 'page' 2>/dev/null)"; then
      printf '%s\n' "$PAGE_OUTPUT"
      return 0
    fi
    sleep "$delay"
  done
  return 1
}

json_get() {
  python3 - "$1" "$2" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
path = sys.argv[2].split(".")
value = payload
for part in path:
    value = value[part]
if isinstance(value, (dict, list)):
    print(json.dumps(value))
else:
    print(value)
PY
}

echo "[1/8] Node runtime"
"$NODE_BIN" --version
"$NPM_BIN" --version

echo "[2/8] Starting workbench"
bash "$WORKBENCH_DIR/scripts/run.sh" >"$WORKBENCH_LOG" 2>&1 &
WORKBENCH_PID=$!
wait_for_socket "$SOCKET_PATH" 20 1
PAGE="$(wait_for_ipc 20 1)"
WIDGETS="$(socket_cmd 'widgets')"
echo "Workbench page: $PAGE"
printf '%s\n' "$WIDGETS" | sed -n '1,8p'

echo "[3/8] Capturing screenshot"
bash "$WORKBENCH_DIR/scripts/screenshot.sh" >/dev/null
test -s "$WORKBENCH_DIR/screen.png"

echo "[4/8] Starting pi-web server"
(
  cd "$PI_WEB_DIR"
  PATH="$(dirname "$NODE_BIN"):$PATH" "$NPM_BIN" run dev:server
) >"$SERVER_LOG" 2>&1 &
SERVER_PID=$!
wait_for_http "http://127.0.0.1:$SERVER_PORT/api/health" 30 1

HEALTH="$(curl -fsS "http://127.0.0.1:$SERVER_PORT/api/health")"
STATE="$(curl -fsS "http://127.0.0.1:$SERVER_PORT/api/state")"
APPS="$(curl -fsS "http://127.0.0.1:$SERVER_PORT/api/apps")"
curl -fsS "http://127.0.0.1:$SERVER_PORT/api/system/screenshot" >/dev/null
echo "Server health: $HEALTH"
echo "Server state: $STATE"
echo "App count: $(python3 -c 'import json,sys; print(len(json.loads(sys.stdin.read())))' <<<"$APPS")"

echo "[5/8] Agent chat"
CHAT_BODY='{"message":"Reply with exactly: pong"}'
CHAT_RESPONSE="$(curl -fsS -X POST "http://127.0.0.1:$SERVER_PORT/api/chat" -H 'Content-Type: application/json' --data "$CHAT_BODY")"
CHAT_TEXT="$(json_get "$CHAT_RESPONSE" response)"
if [ "$CHAT_TEXT" != "pong" ]; then
  echo "Unexpected chat response: $CHAT_RESPONSE" >&2
  exit 1
fi
echo "Chat response: $CHAT_TEXT"

echo "[6/8] Checking Node requirement for Vite"
if ! "$NODE_BIN" -e 'const [maj,min]=process.versions.node.split(".").map(Number); process.exit(maj > 20 || (maj === 20 && min >= 19) ? 0 : 1)'; then
  echo "Node $( "$NODE_BIN" --version ) is too old for Vite 7; skipping client startup." >&2
  exit 2
fi

echo "[7/8] Starting pi-web client"
(
  cd "$PI_WEB_DIR"
  PATH="$(dirname "$NODE_BIN"):$PATH" "$NPM_BIN" run dev:client -- --host 127.0.0.1
) >"$CLIENT_LOG" 2>&1 &
CLIENT_PID=$!
wait_for_http "http://127.0.0.1:$CLIENT_PORT" 30 1
curl -fsS "http://127.0.0.1:$CLIENT_PORT" >/dev/null

echo "[8/8] Smoke test passed"
echo "Workbench log: $WORKBENCH_LOG"
echo "Server log: $SERVER_LOG"
echo "Client log: $CLIENT_LOG"
