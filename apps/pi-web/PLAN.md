# FeralBoard Kiosk App Developer Portal — Implementation Plan

## Vision

A web-based developer portal running on the Pi that manages kiosk apps for the FeralBoard system.
Developers open a browser, see their apps, create new ones from templates, edit config, and use an
AI coding agent to modify app code — all scoped to the kiosk app ecosystem.

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Browser (any device on local network)          │
│  React + Tailwind + Vite                        │
└──────────────────┬──────────────────────────────┘
                   │ HTTP / SSE
┌──────────────────▼──────────────────────────────┐
│  Express Server (pi-web/server/index.ts)        │
│  ├─ /api/apps/*     → CRUD kiosk apps           │
│  ├─ /api/apps/:slug/env → per-app .env editor   │
│  ├─ /api/chat/stream → Pi RPC proxy (existing)  │
│  ├─ /api/system/restart-gui → restart GTK app   │
│  └─ /api/system/screenshot → capture screen     │
└──────────────────┬──────────────────────────────┘
                   │ stdin/stdout JSON RPC
┌──────────────────▼──────────────────────────────┐
│  Pi Coding Agent (--mode rpc)                   │
│  CWD: /home/pi/apps/feralboard/apps/workbench   │
│  Reads: CLAUDE.md + kiosk_apps/CLAUDE.md        │
│  Provider: openai, Model: configurable          │
└─────────────────────────────────────────────────┘
```

## Configuration

- `FERALBOARD_PATH` env var → path to workbench (default: `/home/pi/apps/feralboard/apps/workbench`)
- `OPENAI_API_KEY` env var → OpenAI API key for Pi agent
- Default provider: `openai`, default model: configurable at startup

## Phases

### Phase 1: Backend — App CRUD + System Actions
**Files:** `server/index.ts`

- [ ] `GET /api/apps` — scan `kiosk_apps/*/app.json`, return list with metadata
- [ ] `GET /api/apps/:slug` — return single app details (app.json + .env + has page file)
- [ ] `POST /api/apps` — create app from template (greeting or custom page)
- [ ] `PUT /api/apps/:slug` — update app.json
- [ ] `DELETE /api/apps/:slug` — delete app directory (+ page file if custom)
- [ ] `GET /api/apps/:slug/env` — read per-app .env as key-value pairs
- [ ] `PUT /api/apps/:slug/env` — write per-app .env
- [ ] `POST /api/system/restart-gui` — kill + restart the GTK app
- [ ] `POST /api/system/screenshot` — capture screen via `scripts/screenshot.sh`
- [ ] `GET /api/system/screenshot` — serve the screenshot image

### Phase 2: App Scaffolding Templates
**Files:** `server/templates/`

- [ ] Greeting app template — generates `app.json` only
- [ ] Custom page app template — generates `app.json` + `gui/pages/<slug>.py` boilerplate
- [ ] Boilerplate page class with: GTK Box, long-press unlock, `load_app()`, `cleanup()`, `update_from_rx()`

### Phase 3: System Prompt / Agent Context
**Files:** `feralboard-workbench/kiosk_apps/CLAUDE.md`

- [ ] Write `kiosk_apps/CLAUDE.md` — kiosk app development guide
- [ ] Agent scope rules (which files to touch, which to leave alone)
- [ ] Page class contract documentation
- [ ] Available libraries reference (serial, RFID, protocol, GPIO)
- [ ] Display constraints and GTK patterns
- [ ] Testing workflow (restart GUI, screenshot)

### Phase 4: Frontend — App Dashboard
**Files:** `src/App.tsx` (refactor into components)

- [ ] App dashboard as landing page (card grid of kiosk apps)
- [ ] "New App" modal (name, slug, description, type selector)
- [ ] App card: name, description, type badge, [Edit Config] [Open Agent] buttons
- [ ] Config editor modal (app.json key-value editor)
- [ ] Env editor modal (per-app .env key-value editor)
- [ ] "Restart GUI" button in header/toolbar
- [ ] Screenshot viewer (preview after restart)

### Phase 5: Scoped Agent Sessions
**Files:** `server/index.ts`, `src/App.tsx`

- [ ] "Open Agent" flow: start Pi RPC at `FERALBOARD_PATH` CWD
- [ ] Pre-seed first message with app context (slug, file paths, what to focus on)
- [ ] Chat view reuses existing streaming UI
- [ ] Back button to return to dashboard
- [ ] Session list filtered to show only kiosk app sessions

### Phase 6: Polish & Integration

- [ ] Error handling for all API routes
- [ ] Loading states and feedback in UI
- [ ] Mobile-responsive layout (portal used from laptop or phone)
- [ ] Quick actions: "Restart GUI + Screenshot" combo button

## App Types

### Greeting App
```
kiosk_apps/hello-world/
├── app.json    {"name": "...", "description": "...", "greeting": "..."}
└── .env        (optional)
```

### Custom Page App
```
kiosk_apps/expedicao/
├── app.json    {"name": "...", "description": "...", "page": "expedicao", ...}
├── .env        READER_HOST=192.168.50.2
└── README.md   (optional)

gui/pages/expedicao.py  ← the actual page code (outside kiosk_apps/)
```

## Page Class Contract

```python
class <Name>Page(Gtk.Box):
    def __init__(self, on_unlock=None): ...
    def load_app(self, app_info): ...   # receives full app.json dict
    def cleanup(self): ...               # stop timers, threads, connections
    def update_from_rx(self, rx_buffer): ...  # optional: serial RX data
```
