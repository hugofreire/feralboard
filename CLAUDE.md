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

## References

- Architecture plan: `docs/architecture/monorepo-plan.md`
- Environment notes: `docs/reference/environment-quirks.md`
