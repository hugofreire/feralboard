# 🥧 Pi Web

A web interface for [Pi Coding Agent](https://github.com/badlogic/pi-mono) — interact with an AI coding assistant from your browser.

## Architecture

```
┌─────────────────┐     HTTP/JSON    ┌──────────────────────────┐
│  Vite + React    │ ──────────────→  │  Express API Server      │
│  (Frontend)      │ ←──────────────  │  (Node.js + TypeScript)  │
│  :5173           │                  │  :3001                   │
└─────────────────┘                  └────────────┬─────────────┘
                                                  │ JSON-RPC
                                                  │ stdin/stdout
                                                  ▼
                                     ┌──────────────────────────┐
                                     │  Pi Coding Agent          │
                                     │  (--mode rpc)             │
                                     │  Persistent session       │
                                     └──────────────────────────┘
```

## How It Works

### RPC Protocol (not PTY scraping)

Instead of spawning a new Pi process per message and scraping terminal output, we use Pi's **RPC mode** — a clean JSON protocol over stdin/stdout:

1. On first request, the server spawns `pi --mode rpc` as a long-lived child process
2. User messages are sent as `{"type": "prompt", "message": "..."}` to stdin
3. Pi streams events back as JSON lines on stdout (text deltas, tool calls, etc.)
4. The server accumulates the assistant's response and returns it as JSON

### Session Persistence

Because the Pi process stays alive, **conversation context is preserved** across messages. Pi remembers what you said earlier in the session — just like a real chat.

Sessions are stored by Pi in `~/.pi/agent/sessions/` and can be resumed.

### What Pi Can Do

Pi is a coding agent with built-in tools:

- **read** — Read file contents
- **bash** — Execute shell commands
- **edit** — Edit files with find/replace
- **write** — Create or overwrite files

When you ask Pi to write code, fix bugs, or explore a codebase, it uses these tools autonomously — reading files, running commands, and making edits. You see the final response in the chat UI.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send a message, get the full response |
| `/api/state` | GET | Current session state (model, thinking level, message count) |
| `/api/stats` | GET | Token usage and cost for the session |
| `/api/model` | POST | Switch model (`{ provider, modelId }`) |
| `/api/thinking` | POST | Set thinking level (`{ level }`) |
| `/api/abort` | POST | Abort current agent operation |
| `/api/new-session` | POST | Start a fresh conversation |
| `/api/compact` | POST | Compact context to reduce token usage |
| `/api/health` | GET | Health check |

## Setup

### Prerequisites

- Node.js 22+
- Pi Coding Agent: `npm install -g @mariozechner/pi-coding-agent`
- An API key for at least one provider (e.g., `OPENAI_API_KEY`)
- Optional: `BRAVE_SEARCH_API_KEY` to enable the agent's `web_search` tool via Brave Search
- Optional: `DEEPGRAM_API_KEY` to transcribe attached audio files such as `.m4a`

### Install & Run

```bash
git clone https://github.com/hugofreire/pi-web.git
cd pi-web
npm install
npm run dev
```

This starts both the API server (`:3001`) and the Vite dev server (`:5173`).

Open http://localhost:5173

If `BRAVE_SEARCH_API_KEY` is configured in `apps/pi-web/.env`, the in-browser coding agent also gets a `web_search` tool for live web lookups. The chat UI shows an in-progress search card while Brave queries are running.

If `DEEPGRAM_API_KEY` is configured in `apps/pi-web/.env`, audio attachments such as `.m4a` are transcribed on upload and the resulting transcript file is attached to the chat context automatically.

### Access from another device

```bash
npx vite --host 0.0.0.0
```

Then access via your machine's IP on port 5173.

## Tech Stack

- **Frontend:** React + TypeScript + Vite
- **Backend:** Express + TypeScript (tsx)
- **Agent:** Pi Coding Agent (RPC mode)
- **No PTY, no ANSI stripping, no subprocess-per-message**

## Roadmap

- [ ] Token streaming (SSE/WebSocket — events are already there in RPC)
- [ ] Tool call visualization (show when Pi reads/edits files)
- [ ] Model selector in UI
- [ ] Thinking level toggle
- [ ] File browser / workspace view
- [ ] Multiple sessions
