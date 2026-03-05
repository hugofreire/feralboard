# FeralBoard Monorepo

This repository is a non-destructive monorepo created by copying the current standalone projects into one workspace.

## Layout

- `apps/pi-web` - browser UI and Node server for agent-driven FeralBoard control
- `apps/website` - public website built with Vite + React
- `apps/workbench` - Python GUI, kiosk apps, and device-side scripts
- `hardware/firmware` - embedded firmware copied out of workbench
- `packages/*` - reserved for shared TS code and config
- `docs/` - monorepo-level architecture and operational notes

## Important Rules

- The original standalone repositories in `/home/pi/apps/*` still exist and are the source of truth until migration is complete.
- Do not assume changes in this monorepo are mirrored back to the standalone repos.
- Keep app boundaries clear. Do not casually mix Python workbench logic into the Node apps or firmware tree.
- Prefer extracting only proven shared code into `packages/*`.

## Runtime Defaults

- `apps/pi-web/server/index.ts` defaults `FERALBOARD_PATH` to `apps/workbench` inside this monorepo.
- `apps/workbench/scripts/screenshot.sh` writes `screen.png` into the copied workbench root by default.
- `apps/website/scripts/prerender.mjs` is intentionally fail-open. If browser launch fails on this Pi, the build still succeeds and logs that prerender was skipped.

## Local Commands

- Install Node apps: `npm run install:node-apps`
- Build pi-web: `npm run build:pi-web`
- Build website: `npm run build:website`
- Run pi-web: `npm run dev:pi-web`
- Run website: `npm run dev:website`

## Current Environment Quirks

- This machine currently has Node `20.5.0`.
- `apps/pi-web` uses Vite 7 and warns that Node should be `20.19+` or `22.12+`.
- `apps/website` can build on this machine, but Puppeteer prerender is not reliable on this ARM setup.
- Disk space is limited. Avoid large transient downloads and clean caches when possible.

## Pi-Coding Agent (how to steer it)

The pi-web app embeds a coding agent that edits kiosk apps. Here's how its context is wired:

### Scope prefix (system-prompt-like injection)
- **File**: `apps/pi-web/src/App.tsx` → `buildScopePrefix()` (~line 542)
- This function builds the text prepended to the user's **first message** in each session.
- It tells the agent which app it's scoped to, which files to read, and any reference material.
- To add new context the agent should always see (e.g. a knowledgebase, new libraries), add a line here.

### Agent's CLAUDE.md files (auto-loaded by parent-dir walking)
- `apps/workbench/CLAUDE.md` — project-level context (serial protocol, GPIO, wayland, git, iterative workflow)
- `apps/workbench/kiosk_apps/CLAUDE.md` — kiosk app development guide (app types, page contract, GTK patterns, I/O reference, available libraries)
- The agent's CWD is `FERALBOARD_PATH` (defaults to `apps/workbench`), so both files are found automatically.

### Agent CWD and path resolution
- Set in `apps/pi-web/server/index.ts` → `FERALBOARD_PATH` (env var, defaults to `apps/workbench`)
- The agent sees files relative to this path. To reference pi-web files from the agent, use `../pi-web/...`.

### Knowledgebase
- `apps/pi-web/knowledgebase/` — Siemens PLC communication references extracted from 12 PDF manuals.
- PDFs are gitignored (archived locally as `siemens_plc_manuals.tar.gz`). Only the `.md` outputs and extraction scripts are tracked.
- `plc_reference_index.md` is the entry point with a protocol support matrix across all PLC families.
- The agent is told about this in the scope prefix so it can look up Modbus mappings, protocol details, etc.

## References

- Architecture plan: `docs/architecture/monorepo-plan.md`
- Environment notes: `docs/reference/environment-quirks.md`
