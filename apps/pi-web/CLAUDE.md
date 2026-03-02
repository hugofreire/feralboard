# CLAUDE.md

## Project Overview

FeralBoard Developer Portal — a web-based tool for managing kiosk apps on the FeralBoard system. Built on the Pi Coding Agent's RPC protocol. Runs on a Raspberry Pi, accessible via local network.

## Key Files

- `server/index.ts` — Express API server. Manages kiosk app CRUD, Pi RPC instances, system actions (restart GUI, screenshot).
- `src/App.tsx` — React app with views: Dashboard (app grid), Agent (scoped chat), Config Editor, Env Editor, Create App.
- `src/style.css` — Dark theme (GitHub-inspired).
- `vite.config.ts` — Proxies `/api` to the Express server during dev.
- `PLAN.md` — Full implementation plan with phases.

## Architecture

- **App CRUD**: `/api/apps/*` routes read/write `kiosk_apps/` in the feralboard-workbench repo.
- **Scoped Agent**: When opening an agent session, CWD is set to `FERALBOARD_PATH` (feralboard-workbench root). A scoping message tells the agent which app files to focus on.
- **Agent Context**: Pi automatically loads `feralboard-workbench/CLAUDE.md` + `kiosk_apps/CLAUDE.md` via parent-dir walking.
- **System Actions**: Restart GUI kills/restarts the GTK app, screenshot captures via grim.

## Configuration (env vars)

- `FERALBOARD_PATH` — path to workbench (default: `/home/pi/apps/feralboard/apps/workbench`)
- `OPENAI_API_KEY` — API key for the Pi agent
- `PI_PROVIDER` — LLM provider (default: `openai`)
- `PI_MODEL` — model ID (default: `o3-mini`)

## Development

```bash
npm run dev          # starts server + vite concurrently
npm run dev:server   # server only (tsx watch)
npm run dev:client   # vite only
```

## Things to Watch Out For

- Pi binary path is hardcoded to nvm's node v22 — update `PI_BIN` in `server/index.ts` if your setup differs.
- The agent CWD defaults to `FERALBOARD_PATH`, not `process.cwd()`.
- Custom page apps generate both `kiosk_apps/<slug>/app.json` AND `gui/pages/<slug>.py`.
- Deleting a custom app also removes its page file from `gui/pages/`.
