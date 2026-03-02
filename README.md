# FeralBoard Monorepo

This directory is a non-destructive monorepo scaffold built by copying the current standalone repositories into one workspace.

Current layout:

- `apps/pi-web` - browser-based control and agent UI
- `apps/website` - public website
- `apps/workbench` - Python GUI, kiosk apps, device tooling
- `hardware/firmware` - embedded firmware copied from workbench
- `packages/*` - reserved for code and config shared by Node apps
- `docs/*` - architecture and cross-project documentation

Notes:

- Original standalone Git repositories remain unchanged in `/home/pi/apps/*`.
- This workspace is a source snapshot, not a history-preserving migration.
- Build artifacts and nested `.git` directories are intentionally excluded.

Node bootstrap:

- `npm run install:node-apps`
- `npm run build:pi-web`
- `npm run build:website`
