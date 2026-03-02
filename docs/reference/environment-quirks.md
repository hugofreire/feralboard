# Environment Quirks

## Node

- Current machine Node version observed during bootstrap: `20.5.0`
- `apps/pi-web` toolchain wants Node `20.19+` or `22.12+`
- `apps/website` currently builds on `20.5.0`, but some packages emit engine warnings

## Puppeteer

- `apps/website` includes a prerender step using Puppeteer
- Browser download was previously blocked by low disk space
- Cached browser binaries on this Pi were not runnable, so prerender is allowed to skip without failing the build
- If prerender quality matters, run the website build on a machine with a compatible browser runtime

## Disk

- This Pi has limited free space
- Large package-manager caches can consume space quickly
- Root-level experimental `pnpm` artifacts were removed during bootstrap to recover space

## Monorepo vs Standalone Repos

- This monorepo was created by copy, not move
- The standalone repos remain intact and clean
- Migration work should be intentional; do not assume bidirectional sync
