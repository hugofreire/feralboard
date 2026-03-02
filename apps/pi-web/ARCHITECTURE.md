# FeralBoard Developer Portal — Architecture Overview

How the Pi Coding Agent, the web portal, and the FeralBoard Workbench fit together to create an on-device AI-powered kiosk app development environment.

## The Three Layers

```
┌─────────────────────────────────────────────────────────────────┐
│  Developer's Browser (laptop/phone on local network)            │
│  http://10.9.0.20:5173                                         │
│                                                                 │
│  React + Tailwind + Vite                                        │
│  ├── Dashboard: list/create/delete kiosk apps                   │
│  ├── Config editor: edit app.json per app                       │
│  ├── Env editor: edit .env per app                              │
│  ├── Agent view: chat with AI, file explorer, sessions          │
│  └── System actions: restart GUI, screenshot device             │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP + SSE (Server-Sent Events)
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│  Express Server (pi-web/server/index.ts)                        │
│  Port 3001, running on the Pi                                   │
│                                                                 │
│  Two responsibilities:                                          │
│  1. App CRUD — reads/writes kiosk_apps/ directly (pure file IO) │
│  2. Agent proxy — manages Pi RPC processes, streams responses   │
└──────────────────────┬──────────────────────────────────────────┘
                       │ stdin/stdout (JSON lines over pipes)
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│  Pi Coding Agent (pi --mode rpc)                                │
│  A Node.js CLI tool from github.com/badlogic/pi-mono            │
│                                                                 │
│  ├── Talks to LLM (OpenAI, Anthropic, etc.) via API keys        │
│  ├── Has tools: read, write, edit, bash                         │
│  ├── Scoped to a working directory (CWD)                        │
│  └── Loads context files: CLAUDE.md from CWD + parent dirs      │
└──────────────────────┬──────────────────────────────────────────┘
                       │ reads/writes files, runs commands
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│  FeralBoard Workbench (/home/pi/apps/feralboard/apps/workbench) │
│  The actual kiosk system running on the Pi                      │
│                                                                 │
│  ├── firmware/     — ATmega4809 firmware (serial protocol)      │
│  ├── lib/          — Python: serial, RFID, protocol, GPIO       │
│  ├── gui/          — GTK3 app (fullscreen kiosk UI)             │
│  │   ├── app.py    — main window, page navigation, serial       │
│  │   ├── pages/    — one .py per page (home, outputs, kiosk...) │
│  │   └── style.css — dark theme                                 │
│  ├── kiosk_apps/   — app manifests + per-app config             │
│  │   ├── CLAUDE.md — agent context for kiosk app development    │
│  │   ├── hello-world/app.json                                   │
│  │   └── expedicao/app.json                                     │
│  └── scripts/      — run.sh, screenshot.sh, send.sh             │
└─────────────────────────────────────────────────────────────────┘
```

## How They Connect

### 1. Pi Coding Agent ↔ Express Server (RPC Protocol)

The Pi agent runs as a child process spawned by the Express server:

```
spawn("pi", ["--mode", "rpc", "--provider", "openai", "--model", "o3-mini"])
```

Communication is JSON lines over stdin/stdout:

**Server → Agent (stdin):**
```json
{"type": "prompt", "message": "Add a countdown timer to the page", "id": "req-1"}
```

**Agent → Server (stdout), streamed line by line:**
```json
{"type": "message_update", "assistantMessageEvent": {"type": "text_delta", "delta": "I'll add..."}}
{"type": "tool_execution_start", "toolName": "read", "args": {"path": "gui/pages/expedicao.py"}}
{"type": "tool_execution_end", "toolName": "read", "isError": false}
{"type": "message_update", "assistantMessageEvent": {"type": "text_delta", "delta": "Here's the plan..."}}
{"type": "agent_end", "messages": [...]}
```

The server converts this to SSE for the browser:
```
data: {"type": "delta", "text": "I'll add..."}
data: {"type": "tool_start", "tool": "read"}
data: {"type": "tool_end", "tool": "read"}
data: {"type": "done"}
```

**Key RPC commands used:**
| Command | Purpose |
|---------|---------|
| `prompt` | Send user message, triggers agent turn |
| `abort` | Stop current agent operation |
| `new_session` | Start fresh conversation |
| `get_state` | Current model, session ID, thinking level |
| `get_messages` | Retrieve conversation history |
| `switch_session` | Load a previous session |
| `set_model` | Change LLM provider/model |
| `compact` | Compress conversation history |

### 2. Express Server ↔ FeralBoard Workbench (File System)

The server reads and writes files directly in the workbench repo. No agent involved for CRUD operations — this is pure `fs.readFileSync` / `fs.writeFileSync`.

```
FERALBOARD_PATH = /home/pi/apps/feralboard/apps/workbench

GET  /api/apps          → scan kiosk_apps/*/app.json
POST /api/apps          → mkdir kiosk_apps/<slug>/, write app.json, generate gui/pages/<slug>.py
PUT  /api/apps/:slug    → overwrite app.json
DELETE /api/apps/:slug  → rm -rf kiosk_apps/<slug>/, rm gui/pages/<slug>.py

GET /api/apps/:slug/env → parse .env as key-value
PUT /api/apps/:slug/env → write .env from key-value

POST /api/system/restart-gui  → pkill + bash scripts/run.sh
POST /api/system/screenshot   → bash scripts/screenshot.sh
GET  /api/system/screenshot   → serve screen.png
```

### 3. Pi Agent ↔ FeralBoard Workbench (Context + File Editing)

This is where the magic happens. The agent's CWD is set to the workbench root:

```
CWD: /home/pi/apps/feralboard/apps/workbench
```

**Context loading (automatic, by Pi):**

Pi walks up from CWD and loads every `CLAUDE.md` it finds:

1. `feralboard-workbench/CLAUDE.md` — full project context (serial protocol, I/O naming, page architecture, IPC commands, display constraints, iterative dev workflow)
2. `feralboard-workbench/kiosk_apps/CLAUDE.md` — kiosk app development guide (scope rules, page class contract, available libraries, GTK patterns, testing)

These are concatenated into the agent's system context automatically. The agent "knows" the entire project without us sending a massive prompt.

**Scoping (by instruction, not filesystem):**

When the user opens the agent for a specific app, the portal prepends a scoping context to their first message:

```
[Context: You are working on the kiosk app "Expedição" (slug: "expedicao").
Files in scope: kiosk_apps/expedicao/app.json, kiosk_apps/expedicao/.env, gui/pages/expedicao.py
Read kiosk_apps/CLAUDE.md for the full development guide.]

<user's actual message here>
```

The agent CAN read anything in the workbench (it needs to read `lib/` to understand APIs, read `gui/pages/expedicao.py` as a reference). But it's TOLD to only modify files within the app's scope. This is the same approach Claude Code uses — trust-based scoping, not sandboxing.

### 4. Browser ↔ Express Server (HTTP + SSE)

Standard web app communication:

- **Dashboard**: `GET /api/apps` → render cards
- **Config editor**: `GET /api/apps/:slug` → show JSON, `PUT` to save
- **Env editor**: `GET /api/apps/:slug/env` → show key-value, `PUT` to save
- **File explorer**: `GET /api/apps/:slug/files` → list app files + page file
- **File preview**: `GET /api/files/read?path=...` → return file content
- **Agent chat**: `POST /api/chat/stream` → SSE stream of deltas/tool events
- **Sessions**: `GET /api/sessions` → list all, `POST /api/sessions/switch` → restore

## The Kiosk App Architecture

### Two App Types

**Greeting app** — just config, no code:
```
kiosk_apps/hello-world/
└── app.json  →  {"name": "Hello World", "greeting": "Olá Mundo!"}
```
The GTK app reads `greeting` and displays it on the lock screen. No dynamic page loaded.

**Custom page app** — config + Python GTK page:
```
kiosk_apps/expedicao/
├── app.json  →  {"name": "Expedição", "page": "expedicao", "order": {...}}
└── .env      →  READER_HOST=192.168.50.2

gui/pages/expedicao.py  →  class ExpedicaoPage(Gtk.Box)
```
The GTK app uses `importlib.import_module(f"gui.pages.{page}")` to dynamically load the page class.

### Page Class Contract

Every custom page must implement:

```python
class MyPage(Gtk.Box):
    def __init__(self, on_unlock=None)   # build UI, store unlock callback
    def load_app(self, app_info)         # receive full app.json dict
    def cleanup(self)                    # stop threads, timers, connections
    def update_from_rx(self, rx_buffer)  # optional: receive serial data
```

The long-press unlock pattern (2s hold on title → call `on_unlock()`) lets operators exit the kiosk screen.

### Dynamic Page Loading Flow

```
User selects app in GTK UI
  → app.py._on_app_selected(app_info)
    → if app_info has "page":
        importlib.import_module("gui.pages.expedicao")
        → ExpedicaoPage(on_unlock=...)
        → page.load_app(app_info)
        → stack.add_named(page, "expedicao")
        → navigate_to("expedicao")
    → else:
        kiosk_page.set_greeting(app_info["greeting"])
        → navigate_to("kiosk")
```

## Key Design Decisions

### Why CWD = project root, not app subfolder?

The agent needs to:
- Read `gui/pages/<slug>.py` (lives outside `kiosk_apps/`)
- Read `lib/rfid_reader.py` to understand the RFID API
- Read `gui/pages/expedicao.py` as a reference implementation
- Read `CLAUDE.md` at the project root

If CWD were `kiosk_apps/expedicao/`, the agent couldn't access any of these without path gymnastics. Scoping by instruction ("only modify these files") is more practical than filesystem restriction.

### Why Pi agent and not direct LLM API calls?

Pi gives us for free:
- **Tool execution**: read, write, edit, bash — the agent can explore the codebase, run the app, check errors
- **Session persistence**: conversations save as JSONL, can be resumed
- **Context files**: CLAUDE.md loading from parent dirs gives automatic project understanding
- **Model flexibility**: switch between OpenAI, Anthropic, etc. via RPC command

Building this from scratch would mean reimplementing tool calling, file sandboxing, context management — Pi handles all of that.

### Why SSE instead of WebSocket?

Pi's RPC protocol is request-response over stdin/stdout. The server reads JSON lines as they arrive and forwards them as SSE events. SSE is simpler than WebSocket for this unidirectional streaming pattern, and it reconnects automatically on network hiccups.

### Why per-app .env instead of global config?

Each kiosk app has its own config scope:
- `expedicao` needs `READER_HOST=192.168.50.2` for the RFID reader
- A future GPIO app might need `RELAY_PIN=17`
- A display app might need `API_URL=http://internal-server/api`

Per-app `.env` keeps these isolated. The web portal's env editor makes them easy to manage without SSH.

## File Map

```
pi-web/                              ← the developer portal
├── server/index.ts                  ← Express API (CRUD + RPC proxy)
├── src/
│   ├── App.tsx                      ← React app (dashboard + agent + editors)
│   ├── components/CodeBlock.tsx     ← Syntax highlighting (Prism)
│   └── components/ui/              ← Button, Badge, Input, Textarea
├── CLAUDE.md                        ← Portal project context
├── PLAN.md                          ← Implementation phases
└── ARCHITECTURE.md                  ← This file

feralboard-workbench/                ← the kiosk system
├── gui/
│   ├── app.py                       ← Main GTK window, navigation, serial
│   └── pages/
│       ├── kiosk.py                 ← Default lock screen
│       ├── expedicao.py             ← Example custom page (RFID validation)
│       └── <slug>.py                ← Generated by portal for new custom apps
├── kiosk_apps/
│   ├── CLAUDE.md                    ← Agent context for kiosk app development
│   ├── hello-world/app.json         ← Greeting app
│   └── expedicao/app.json           ← Custom page app
├── lib/                             ← Python libraries (serial, RFID, protocol)
├── scripts/                         ← run.sh, screenshot.sh, send.sh
└── CLAUDE.md                        ← Full project context
```
