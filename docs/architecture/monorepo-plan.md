# Monorepo Plan

This workspace groups the current FeralBoard projects by runtime and release boundary:

- `apps/pi-web` and `apps/website` stay as independent Node applications.
- `apps/workbench` stays Python-first and keeps its own runtime dependencies.
- `hardware/firmware` is split out from workbench because firmware has a separate toolchain and deployment path.
- `packages/*` exists only for real shared code or config and should not be forced early.

Recommended next steps:

1. Add root scripts for bootstrap, lint, and CI orchestration.
2. Decide whether to convert `apps/workbench` from `requirements.txt` to `pyproject.toml`.
3. Extract only proven shared TypeScript code into `packages/ui` or `packages/shared-types`.
4. Introduce one CI pipeline that runs app-specific jobs without coupling their toolchains.

Current bootstrap:

- Root Node commands use `npm --prefix` for reliability on this machine.
- `pnpm-workspace.yaml` remains in place as a future option once package manager setup is standardized.
