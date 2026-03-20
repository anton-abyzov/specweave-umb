# Plan: Plugin Caching Hardening

## Architecture Decision

Add validation and logging layers to existing plugin pipeline without changing control flow. Empty catches get logging; critical boundaries get validation. No new exceptions — use result objects with error fields.

## Files Modified

1. `src/utils/plugin-copier.ts` — New `validatePluginCache()`, 9 logging fixes
2. `src/dashboard/server/data/plugin-scanner.ts` — Semver-sorted version selection
3. `src/utils/cleanup-stale-plugins.ts` — Phase 2.5 stale version pruning
4. `src/cli/commands/refresh-plugins.ts` — Error tracking, exit code, fallback warning
5. `src/cli/helpers/init/claude-plugin-enabler.ts` — Settings backup, error logging
6. `src/cli/helpers/init/plugin-installer.ts` — Core plugin failure detection
7. `src/core/plugins/plugin-loader.ts` — Optional strict mode
8. `src/core/doctor/checkers/plugins-checker.ts` — Stale version dir health check

## Design Principles

- Don't break graceful degradation — ADD logging, don't make everything throw
- Error propagation via result objects, not exceptions
- Quiet mode tracks errors internally but suppresses console
- Distinguish "expected empty" from "corrupt" (hooks-only plugins vs missing skills/)
