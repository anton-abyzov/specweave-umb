# Implementation Plan: Fix init sync-setup command + brownfield repo onboarding

## Architecture

### Track A — Brownfield repo detection (independent)

**`scanMisplacedRepos(targetDir: string): string[]`** added to `path-utils.ts` after `scanUmbrellaRepos`.

- Reads `repositories/` at depth 1 only
- Returns names of dirs that have `.git` directly inside (1-level, non-standard)
- Called in `init.ts` only when `scanUmbrellaRepos()` returns null (mutually exclusive)
- Result threaded through `NextStepsContext.misplacedRepos` into `showNextSteps()`
- `next-steps.ts` renders a warning block with fix instructions

### Track B — `specweave sync-setup` CLI command

**`src/cli/commands/sync-setup.ts`** — new file.

Flow:
1. Guard: `.specweave/config.json` must exist
2. `--quick` / non-TTY → print hint, exit 0
3. Provider selection via `checkbox()` (or skip if `--provider` flag)
4. Per-provider credential collection via existing `setupIssueTracker()`
5. Permission preset via `select()` → maps to `SyncPermissions`
6. Umbrella per-repo targets (conditional on `config.umbrella.enabled`)
7. `writeSyncConfig()` per provider
8. Success summary + suggest `specweave sync-status`

Reuses: `writeSyncConfig`, `setupIssueTracker`, `getConfigManager`, `@inquirer/prompts`

Registered in `bin/specweave.js` before `docs` command block (near other sync-* commands).

## Files Changed

| File | Change |
|------|--------|
| `src/cli/commands/sync-setup.ts` | NEW — CLI wizard |
| `bin/specweave.js` | Register `sync-setup` command |
| `src/cli/helpers/init/path-utils.ts` | Add `scanMisplacedRepos()` |
| `src/cli/helpers/init/index.ts` | Export `scanMisplacedRepos` |
| `src/cli/helpers/init/types.ts` | Add `misplacedRepos?: string[]` to `NextStepsContext` |
| `src/cli/commands/init.ts` | Call `scanMisplacedRepos`, pass to `showNextSteps` |
| `src/cli/helpers/init/next-steps.ts` | Render misplaced-repos warning block |
| `tests/unit/scan-misplaced-repos.test.ts` | NEW — unit tests |
| `tests/unit/sync-setup-command.test.ts` | NEW — unit tests |

## Permission Preset Mapping

| Preset | canUpsertInternalItems | canUpdateExternalItems | canUpdateStatus |
|--------|----------------------|----------------------|----------------|
| read-only | false | false | false |
| push-only | true | false | false |
| bidirectional | true | true | true |
| full-control | true | true | true |
