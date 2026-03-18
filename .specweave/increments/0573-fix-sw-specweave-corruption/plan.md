# Plan: Fix sw@specweave Silent Corruption

## Approach

Two-layer fix: fast bash recovery on every session + Node.js recovery during refresh-plugins.

### Layer 1: SessionStart Hook (bash)
Add a `jq`-based health check to `session-start.sh` that verifies `sw@specweave` is `true` and repairs it if not. Fast, no Node.js spawn, runs every session.

### Layer 2: refresh-plugins (Node.js)
Wire the existing but dead `migrateUserLevelPlugins()` function into `refresh-plugins.ts`. This activates the defensive `enablePlugin('sw', 'specweave')` calls that protect against `claude plugin uninstall` corruption.

## Files

1. `specweave/plugins/specweave/hooks/v2/dispatchers/session-start.sh` - add health check
2. `specweave/src/cli/commands/refresh-plugins.ts` - wire migration function
3. New test: `specweave/tests/unit/hooks/session-start-plugin-health.test.ts`
