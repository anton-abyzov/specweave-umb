# Implementation Plan: Vskill Stale File Cleanup

## Overview

Add cleanup logic for two categories of orphaned lockfiles in SpecWeave projects:

1. **`skills-lock.json`** -- a dead legacy format with zero code references. Remove at any depth.
2. **`vskill.lock` in child repos** -- orphaned files inside `repositories/` in umbrella setups. Only the umbrella root `vskill.lock` is authoritative.

The implementation extends three existing modules with new exported functions/methods (no new files). All functions receive their dependencies as arguments for TDD isolation.

## Architecture

### Component Map

```
cleanup-stale-plugins.ts          installation-health-checker.ts       refresh-plugins.ts
(src/utils/)                      (src/core/doctor/checkers/)          (src/cli/commands/)
─────────────────────────         ──────────────────────────────       ──────────────────
+ cleanupLegacyLockfiles()        + checkStaleLockfiles()              Wire cleanup at
+ cleanupOrphanedChildLocks()       (delegates to both cleanup fns)      Step 0.5 (after
                                                                         CLI detection,
  Both return StaleFileResult       Returns CheckResult[] for             before plugin
  { removedCount, skippedCount,     "Legacy lockfiles" and                install)
    removedPaths, skippedPaths,     "Orphaned child lockfiles"
    errors }
```

### Data Flow

```
refresh-plugins (entry)
  |
  +-- cleanupLegacyLockfiles(projectRoot, opts)
  |     Walk projectRoot recursively for skills-lock.json
  |     Skip files with mtime < 5s
  |     Delete all others
  |
  +-- cleanupOrphanedChildLocks(projectRoot, opts)
        Read .specweave/config.json -> umbrella.enabled / repository.umbrellaRepo
        If not umbrella -> return early (zero removals)
        Scan repositories/ for vskill.lock
        Skip files with mtime < 5s
        Delete orphaned files

doctor (entry)
  |
  +-- InstallationHealthChecker.checkStaleLockfiles(projectRoot, fix)
        Detect mode: list stale files and report CheckResult
        Fix mode:   call cleanup fns, report removed counts
```

### New Types

Added to `cleanup-stale-plugins.ts`:

```typescript
interface StaleFileCleanupOptions {
  verbose?: boolean;
  /** Override for testing: inject a custom fs module */
  fs?: typeof import('node:fs');
  /** Override mtime threshold in ms (default 5000) */
  mtimeThresholdMs?: number;
}

interface StaleFileResult {
  success: boolean;
  removedCount: number;
  skippedCount: number;
  removedPaths: string[];
  skippedPaths: string[];
  errors: Array<{ path: string; error: string }>;
}
```

### Key Design Decisions

**D1: Extend existing modules, no new files.**
The spec mandates adding to `cleanup-stale-plugins.ts` and `InstallationHealthChecker`. This keeps all stale-artifact cleanup co-located. Both existing modules already have the right imports (`fs`, `path`, `os`).

**D2: Injectable `fs` parameter for TDD.**
All new functions accept an optional `fs` override via the options object. This allows tests to use an in-memory filesystem (`memfs` or manual stubs) without touching disk. The existing `cleanupStalePlugins()` function uses `./fs-native.js`; the new functions follow the same pattern but accept the override for testability.

**D3: Mtime guard as a pure comparison, not side-effect.**
The 5-second mtime check is a simple `Date.now() - stat.mtimeMs < threshold` comparison. The threshold is configurable via options for deterministic testing (inject a known threshold + mock stat).

**D4: Recursive walk for `skills-lock.json`, shallow scan for `vskill.lock`.**
`skills-lock.json` is a dead format at any depth (spec: "aggressive, any depth"). `vskill.lock` orphans only exist at the root of child repos under `repositories/`, so we scan `repositories/*/*/vskill.lock` (org/repo structure per CLAUDE.md multi-repo rule) rather than a full recursive walk.

**D5: Umbrella detection reuses `findUmbrellaRoot()` logic inline.**
Rather than importing `findUmbrellaRoot()` (which walks up from cwd), the cleanup reads `config.json` directly at the known project root. This avoids cwd-dependent behavior and is simpler to test. The check mirrors the same two config flags used in `find-project-root.ts`: `umbrella.enabled` or `repository.umbrellaRepo`.

**D6: Doctor checker is a single new method returning two CheckResults.**
`checkStaleLockfiles()` returns a `CheckResult[]` array (one for legacy, one for orphaned child locks). The `check()` method spreads these into the existing checks array. This follows the pattern of the existing checker methods but groups the two related checks into one method to avoid duplication of the umbrella-detection logic.

**D7: Refresh-plugins cleanup runs before plugin install.**
The cleanup call is placed at Step 0.5 in `refreshPluginsCommand()` -- after CLI detection (Step 0) but before finding specweave root (Step 1). This ensures stale files are removed before any lockfile writes from the install process.

## Technology Stack

- **Language**: TypeScript (ESM, `.js` import extensions)
- **Runtime**: Node.js (fs, path, os from `node:` prefix in doctor checkers; `./fs-native.js` wrapper in cleanup module)
- **Testing**: Vitest with `vi.hoisted()` + `vi.mock()` for fs mocking

## Implementation Phases

### Phase 1: Core Cleanup Functions (US-001, US-002)

Add two exported functions to `cleanup-stale-plugins.ts`:

1. `cleanupLegacyLockfiles(projectRoot, options?)` -- recursive walk for `skills-lock.json`
2. `cleanupOrphanedChildLocks(projectRoot, options?)` -- `repositories/*/*/vskill.lock` scan

Both return `StaleFileResult`. Both respect the mtime < 5s guard. Both catch per-file errors and continue.

Implementation details:
- `cleanupLegacyLockfiles`: Use a recursive directory walk (Node `fs.readdirSync` with `recursive: true` on Node 18.17+, or manual walk for compatibility). Filter for files named exactly `skills-lock.json`.
- `cleanupOrphanedChildLocks`: Read `${projectRoot}/.specweave/config.json`. Check `umbrella.enabled` or `repository.umbrellaRepo`. If not umbrella, return early. Glob `${projectRoot}/repositories/*/*/vskill.lock`. Also resolve symlinks via `fs.realpathSync` and verify the resolved path is still under `projectRoot` to prevent symlink escapes.

### Phase 2: Doctor Integration (US-003)

Add `checkStaleLockfiles(projectRoot, fix)` method to `InstallationHealthChecker`:
- Detect mode: scan for files, report as `warn` with paths in `details[]`
- Fix mode: call the cleanup functions, report removed count
- Wire into `check()` method alongside existing calls

### Phase 3: Refresh-Plugins Hook (US-004)

Add a cleanup step to `refreshPluginsCommand()`:
- Import both cleanup functions
- Call them sequentially after CLI detection, before plugin install
- Log removed files when verbose mode is enabled
- Non-blocking: cleanup errors do not abort plugin refresh

## Testing Strategy

TDD mode is active. All tests follow Given/When/Then structure.

### Unit Tests for Phase 1

File: `src/utils/cleanup-stale-plugins.test.ts` (extend existing test file or create if absent)

**cleanupLegacyLockfiles:**
- Given a tree with `skills-lock.json` at root and nested dirs, when cleanup runs, then all are deleted
- Given a `skills-lock.json` with mtime < 5s ago, when cleanup runs, then it is skipped
- Given no `skills-lock.json` exists, when cleanup runs, then result has `removedCount: 0`
- Given a read-only `skills-lock.json`, when cleanup runs, then error is captured and other files still processed

**cleanupOrphanedChildLocks:**
- Given an umbrella repo with child `vskill.lock`, when cleanup runs, then child lock is deleted and root lock is preserved
- Given a child `vskill.lock` with mtime < 5s, when cleanup runs, then it is skipped
- Given a non-umbrella project, when cleanup runs, then no files are touched
- Given a symlinked child repo, when cleanup runs, then symlink is resolved and validated

### Unit Tests for Phase 2

File: `src/core/doctor/checkers/installation-health-checker.test.ts`

**checkStaleLockfiles:**
- Given stale lockfiles exist, when doctor runs (no fix), then warns with file paths
- Given stale lockfiles exist, when doctor runs with fix, then files are removed and result reports count
- Given no stale lockfiles, when doctor runs, then check returns `pass`
- Given umbrella not enabled, when doctor runs, then orphaned child check is skipped

### Integration Test for Phase 3

File: `src/cli/commands/refresh-plugins.test.ts` (if absent, add targeted test)

- Given `skills-lock.json` exists at project root, when refresh-plugins runs, then file is removed before install

## Technical Challenges

### Challenge 1: Recursive Walk Performance
**Problem**: Deep project trees could make recursive scan slow.
**Solution**: `skills-lock.json` scan uses `fs.readdirSync(dir, { recursive: true })` (Node 18.17+) which is implemented natively in libuv and fast for typical project sizes. The spec's 500ms budget is generous -- most umbrella repos have < 20 child repos.
**Fallback**: If the project has `node_modules/` or other deep trees, skip directories named `node_modules`, `.git`, and `.specweave` during the walk to avoid unnecessary traversal.

### Challenge 2: Symlink Escape Prevention
**Problem**: A symlinked child repo under `repositories/` could point outside the project tree, and deleting `vskill.lock` through it would affect an unrelated project.
**Solution**: Resolve the real path of each `vskill.lock` candidate via `fs.realpathSync()` and verify it starts with the resolved project root. Skip (and warn) if it resolves outside.

### Challenge 3: Concurrent Write Safety
**Problem**: Another `specweave refresh-plugins` instance might be writing to `vskill.lock` or `skills-lock.json` at the same time.
**Solution**: The 5-second mtime guard (configurable via `mtimeThresholdMs`) prevents deleting files that were recently modified. This is the same pattern used in the existing `cleanupStalePlugins()` function's Phase 2 (atomic rename + delete for cache dirs), adapted for lockfiles where rename is not needed because deletion is the entire operation.

### Challenge 4: Import Path Consistency
**Problem**: `cleanup-stale-plugins.ts` uses `./fs-native.js` while `installation-health-checker.ts` uses `node:fs` directly.
**Solution**: New functions in `cleanup-stale-plugins.ts` continue using `./fs-native.js` as the default, but accept an `fs` override in the options for testing. The doctor checker calls the cleanup functions (which handle their own fs), so no fs import conflict arises.
