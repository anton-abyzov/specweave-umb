# Plan: Remove node_modules Specweave Dependency

## Overview

Straightforward search-and-replace refactor across 4 source files (5 change sites). Each site replaces a hardcoded `$PROJECT_ROOT/node_modules/specweave/...` path with a call to the existing `resolve-package.sh` utility or, for ES modules, removes the candidate entirely. A sixth change removes `specweave` from the umbrella `package.json`.

No new architecture, no new resolution mechanisms, no new files.

## Change Inventory

### File 1: `hooks/lib/scheduler-startup.sh` (AC-US1-01)

**Problem**: Line 100 uses `require('$PROJECT_ROOT/node_modules/specweave/dist/core/scheduler/session-sync-executor.js')` -- this path is hardcoded inside an inline `node -e` block. It also has a latent bug: missing `/src/` segment (should be `dist/src/core/...`).

**Fix**:
- Source `resolve-package.sh` near the top of the file (after PROJECT_ROOT is set).
- Before the `node -e` block, resolve the executor path via `find_specweave_script "dist/src/core/scheduler/session-sync-executor.js"`.
- Pass the resolved path into the inline JS via bash variable interpolation.
- Guard: if resolution fails, skip with a log message (consistent with other hooks).

**Source path for `resolve-package.sh`**: This file is at `hooks/lib/scheduler-startup.sh`, so `resolve-package.sh` is a sibling in the same `lib/` directory. Source as `"$(dirname "${BASH_SOURCE[0]}")/resolve-package.sh"`.

### File 2: `hooks/v2/handlers/ac-sync-dispatcher.sh` (AC-US1-03)

**Problem**: Lines 243-246 have a `node_modules/specweave` fallback candidate as step 2 in the resolution chain.

**Current state**: Already has SPECWEAVE_PKG (step 0) and PKG_ROOT (step 1) candidates.

**Fix**:
- Replace the `node_modules` candidate (step 2) with a `find_specweave_script` call.
- Source `resolve-package.sh` near the top. This file is at `hooks/v2/handlers/`, so relative path is `"$HANDLER_DIR/../../lib/resolve-package.sh"` (same pattern used by `github-sync-handler.sh` and others in the same directory).
- Note: the file already checks `$SPECWEAVE_PKG` at step 0, and sourcing `resolve-package.sh` auto-sets `$SPECWEAVE_PKG`. So after sourcing, step 0 always has a value when the package is findable, making the `node_modules` fallback redundant. The replacement `find_specweave_script` call is a defensive belt-and-suspenders approach.

### File 3: `hooks/v2/handlers/universal-auto-create-dispatcher.sh` (AC-US1-05)

**Problem**: Two `node_modules/specweave` candidates:
- Line 149-152: GitHub handler path (`plugins/specweave-github/hooks/github-auto-create-handler.sh`)
- Line 190-193: Auto-create module path (`dist/src/core/universal-auto-create.js`)

**Current state**: Already has SPECWEAVE_PKG (step 0) and PKG_ROOT (step 1) for the second site. The GitHub handler site has sibling-plugin and PROJECT_ROOT candidates but not SPECWEAVE_PKG.

**Fix**:
- Source `resolve-package.sh` near the top. Same relative path as ac-sync-dispatcher: `"$HANDLER_DIR/../../lib/resolve-package.sh"`.
- Replace line 151 candidate with `find_specweave_script "plugins/specweave-github/hooks/github-auto-create-handler.sh"`.
- Replace line 192 candidate with `find_specweave_script "dist/src/core/universal-auto-create.js"`.

### File 4: `hooks/universal/dispatcher.mjs` (AC-US1-04)

**Problem**: Lines 101-102 list `node_modules/specweave/dist/src/hooks` as the first candidate in `findHooksDir()`.

**Fix**: Remove lines 101-102 (the comment and the candidate path). The remaining candidates (project root `dist/src/hooks` and legacy `dist/hooks`) are sufficient. The `CLAUDE_PLUGIN_ROOT`-based resolution (via `shouldSkipDueToDevEnvironment` and the hook infrastructure itself) handles production routing.

### File 5: Umbrella `package.json` (AC-US2-01 through AC-US2-03)

**Fix**: Remove the `"specweave"` entry from `dependencies`. Run `npm install` to regenerate `package-lock.json`.

## Approach: AC-US1-02 (post-task-completion.sh)

The spec references `post-task-completion.sh` with `SYNC_CLI` and `DETECT_CLI` at lines 141 and 185. This file no longer exists in the current codebase -- it was refactored into the v2 handler architecture. The `sync-spec-content.sh` (which has `SYNC_CLI`) already uses `$SPECWEAVE_PKG` with no `node_modules` references. Grep confirms zero `node_modules/specweave` hits for any file matching `*post*task*` or containing `DETECT_CLI`. This AC is either already satisfied or refers to a removed file. The plan will note this as pre-satisfied and verify with grep.

## Implementation Order

1. **T-001**: Source `resolve-package.sh` in `scheduler-startup.sh`, fix the inline `node -e` path (fixes latent `/src/` bug too)
2. **T-002**: Source `resolve-package.sh` in `ac-sync-dispatcher.sh`, replace `node_modules` candidate with `find_specweave_script`
3. **T-003**: Source `resolve-package.sh` in `universal-auto-create-dispatcher.sh`, replace both `node_modules` candidates
4. **T-004**: Remove `node_modules/specweave` candidate from `dispatcher.mjs`
5. **T-005**: Verify AC-US1-02 is pre-satisfied (grep confirmation)
6. **T-006**: Remove `specweave` from umbrella `package.json`
7. **T-007**: Full grep verification -- zero `node_modules/specweave` refs in non-archive plugin source

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| `resolve-package.sh` source path wrong for `scheduler-startup.sh` | It's in the same `lib/` dir -- use `$(dirname "${BASH_SOURCE[0]}")/resolve-package.sh` |
| `resolve-package.sh` source path wrong for v2 handlers | Use `"$HANDLER_DIR/../../lib/resolve-package.sh"` -- proven pattern from 4 other handlers in same dir |
| `SPECWEAVE_PKG` empty after sourcing | All hooks already guard against this with `if [[ -n "${SPECWEAVE_PKG:-}" ]]` checks; `find_specweave_script` returns non-zero when not found |
| Removing `node_modules` candidate from dispatcher.mjs breaks production | Production hooks run from `CLAUDE_PLUGIN_ROOT`; the `node_modules` candidate was never the primary resolution path |

## No ADR Needed

This is a mechanical refactor using existing patterns (`resolve-package.sh`). No new architectural decisions, no new resolution mechanisms, no interface changes.

## No Domain Skills Needed

Pure bash/mjs refactor within the plugin hooks directory. No frontend, backend, or testing framework involvement beyond grep verification.
