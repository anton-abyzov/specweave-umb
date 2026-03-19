---
increment: 0631-fix-umbrella-root-resolution
title: "Fix Umbrella Root Resolution and Prevent Stale .specweave in Child Repos"
status: active
created: 2026-03-19
---

# Architecture Plan: Fix Umbrella Root Resolution

## Overview

14 modules construct `.specweave/` paths using `process.cwd()` instead of umbrella-aware resolution. The fix introduces a single `getSpecweavePath()` utility that wraps `resolveEffectiveRoot()`, then replaces all 14 bypass patterns with it. Dashboard gets dedicated resolution fixes. Config flag detection is unified. Tests are added using real temp directories.

## Architecture Decisions

### AD-1: New `getSpecweavePath()` in `find-project-root.ts`

**Decision**: Add `getSpecweavePath()` as a new export in `src/utils/find-project-root.ts`.

**Rationale**: All root resolution utilities already live in this module (`findProjectRoot`, `getProjectRoot`, `resolveEffectiveRoot`, `findUmbrellaRoot`, `getSpecWeaveDir`). Adding here maintains the single-module convention and avoids a new import path.

**Implementation**:
```typescript
export function getSpecweavePath(startDir?: string): string {
  return path.join(resolveEffectiveRoot(startDir), '.specweave');
}
```

**Key difference from existing `getSpecWeaveDir()`**: `getSpecWeaveDir()` uses `findProjectRoot()` (nearest root, returns null if not found). `getSpecweavePath()` uses `resolveEffectiveRoot()` (umbrella-aware, never returns null). The new function always returns a path and is the safe default for code that writes to `.specweave/`.

### AD-2: Direct Import Change for 14 Bypass Files

**Decision**: Each bypass file imports `getSpecweavePath` and replaces its `process.cwd() + '.specweave'` pattern.

**Alternatives rejected**:
- **Lower-level fix** (make `getProjectRoot()` umbrella-aware): Would break callers like `config-manager.ts` that specifically need the nearest project root for config reading.
- **Middleware/wrapper**: Over-engineering for a mechanical one-line swap.

**Files and fix patterns**:

| Pattern | Files | Change |
|---|---|---|
| **A: `?? path.join(process.cwd(), '.specweave')`** | command-integration.ts:84, notification-manager.ts:81, schedule-persistence.ts:71, log-aggregator.ts:109, sync-audit-logger.ts:169, permission-enforcer.ts:132, sync-scheduled.ts:48 | Replace default fallback with `?? getSpecweavePath()` |
| **B: Direct `path.join(process.cwd(), '.specweave', ...)`** | qa-runner.ts:49, autonomous-executor.ts:244, revert-wip-limit.ts:18, logs.ts:26, cross-linker.ts:56, content-distributor.ts:85 | Replace with `path.join(getSpecweavePath(), ...)` |
| **C: Function param default** | permission-enforcer.ts:364 | Change default param to `getSpecweavePath()` |

### AD-3: Dashboard Resolution — Silent Resolve to Umbrella Root

**Decision**: Dashboard resolves to umbrella root silently; no error for child repo paths.

**`dashboard.ts` fix** (line 24):
```typescript
// Before:
const projectRoot = process.cwd();
// After:
const projectRoot = resolveEffectiveRoot();
```

**`dashboard-server.ts` POST /api/projects handler** (lines 349-367):
After path validation, resolve umbrella before registering:
```typescript
const effectiveRoot = findUmbrellaRoot(resolvedPath) || resolvedPath;
const info = this.addProject(effectiveRoot);
```

**Rationale**: The user's intent is to view their project. When running from a child repo, they expect umbrella data. Returning an error would be unhelpful.

### AD-4: `detectUmbrellaParent()` Updated In-Place

**Decision**: Add `config?.umbrella?.enabled` check to `detectUmbrellaParent()` in `path-utils.ts` to match `findUmbrellaRoot()` behavior.

**Do not deprecate**: `detectUmbrellaParent()` serves a different purpose (init-time guard) from `findUmbrellaRoot()` (runtime resolution). Both needed.

**Change** (path-utils.ts, line 210):
```typescript
// Before:
if (config?.repository?.umbrellaRepo) {
// After:
if (config?.umbrella?.enabled || config?.repository?.umbrellaRepo) {
```

### AD-5: Test Structure — Real Temp Directories

**Decision**: Extend existing `tests/unit/utils/find-project-root.test.ts` with new `describe` blocks. Use real temp directories matching existing patterns.

**New test helper**:
```typescript
async function createUmbrellaTree(): Promise<{
  tmpBase: string;
  umbrellaRoot: string;
  childRepo: string;
  childRepoNested: string;
}> {
  const tmpBase = await fsPromises.mkdtemp(path.join(os.tmpdir(), 'sw-umb-'));
  const umbrellaRoot = path.join(tmpBase, 'umbrella');
  const specweaveDir = path.join(umbrellaRoot, '.specweave');
  const reposDir = path.join(umbrellaRoot, 'repositories', 'org');
  const childRepo = path.join(reposDir, 'child-repo');

  await fsPromises.mkdir(specweaveDir, { recursive: true });
  await fsPromises.writeFile(
    path.join(specweaveDir, 'config.json'),
    JSON.stringify({ umbrella: { enabled: true }, repository: { umbrellaRepo: true } })
  );
  await fsPromises.mkdir(path.join(childRepo, '.git'), { recursive: true });
  await fsPromises.mkdir(path.join(childRepo, 'src', 'deep'), { recursive: true });

  return { tmpBase, umbrellaRoot, childRepo, childRepoNested: path.join(childRepo, 'src', 'deep') };
}
```

**Test scenarios**:
- `findUmbrellaRoot()`: umbrella-enabled config, standalone config, missing config, repositories/ dir fallback
- `resolveEffectiveRoot()`: returns umbrella root when inside umbrella, returns project root in standalone
- `getSpecweavePath()`: correct `.specweave/` path for both modes
- `detectUmbrellaParent()`: `umbrella.enabled`, `repository.umbrellaRepo`, both, neither

## Component Breakdown

### C1: `getSpecweavePath()` utility
- **File**: `src/utils/find-project-root.ts`
- **Satisfies**: AC-US2-03
- **Risk**: Low — additive export, no existing API modified

### C2: Dashboard root resolution
- **Files**: `src/cli/commands/dashboard.ts`, `src/dashboard/server/dashboard-server.ts`
- **Satisfies**: AC-US1-01, AC-US1-02, AC-US1-03
- **Risk**: Medium — user-facing, must verify standalone mode

### C3: 13 bypass module fixes
- **Files**: See AD-2 table
- **Satisfies**: AC-US2-01, AC-US2-02
- **Risk**: Low — mechanical import swap; existing optional params preserved

### C4: Config flag consistency
- **File**: `src/cli/helpers/init/path-utils.ts`
- **Satisfies**: AC-US3-01, AC-US3-02, AC-US3-03
- **Risk**: Low — one condition added

### C5: Test coverage
- **File**: `tests/unit/utils/find-project-root.test.ts`
- **Satisfies**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
- **Risk**: None — test-only

### C6: Stale cleanup
- **Dirs**: `repositories/anton-abyzov/vskill/.specweave/increments/`, `repositories/anton-abyzov/specweave/.specweave/increments/`
- **Satisfies**: AC-US5-01, AC-US5-02, AC-US5-03
- **Risk**: Medium — must verify each orphan in umbrella archive before deletion

## Implementation Order

1. **Tests first (TDD Red)** — Write failing tests for `findUmbrellaRoot`, `resolveEffectiveRoot`, `getSpecweavePath`, `detectUmbrellaParent` in umbrella scenarios
2. **`getSpecweavePath()` utility** — Add export, make tests green
3. **`detectUmbrellaParent()` config flag fix** — One-line change + tests
4. **Dashboard fix** — `dashboard.ts` + `dashboard-server.ts addProject()`
5. **13 bypass module fixes** — Bulk import swaps
6. **Verification grep** — Confirm zero remaining `process.cwd()` + `.specweave` bypass patterns
7. **Stale cleanup** — Verify orphan presence in umbrella, then delete

## Data Flow

```
CLI from child repo (CWD = /umbrella/repositories/org/child-repo)
    │
    ▼
getSpecweavePath()
    │
    ▼
resolveEffectiveRoot()
    ├─► findUmbrellaRoot()
    │     ├─► findProjectRoot() → nearest .specweave/config.json
    │     ├─► Check umbrella.enabled || repository.umbrellaRepo
    │     └─► Fallback: check for repositories/ directory
    └─► Returns: /umbrella (umbrella root)
    │
    ▼
path.join("/umbrella", ".specweave") → /umbrella/.specweave ✅
```

## Files Changed

| File | Change | Lines |
|---|---|---|
| `src/utils/find-project-root.ts` | Add `getSpecweavePath()` export | ~15 |
| `src/cli/commands/dashboard.ts` | Import + replace `process.cwd()` | ~3 |
| `src/dashboard/server/dashboard-server.ts` | Import + resolve umbrella in POST handler | ~5 |
| `src/cli/helpers/init/path-utils.ts` | Add `umbrella.enabled` check | ~1 |
| `src/core/qa/qa-runner.ts` | Import + replace path | ~2 |
| `src/core/workflow/autonomous-executor.ts` | Import + replace path | ~2 |
| `src/cli/commands/revert-wip-limit.ts` | Import + replace path | ~2 |
| `src/cli/commands/logs.ts` | Import + replace path | ~2 |
| `src/core/living-docs/cross-linker.ts` | Import + replace default | ~2 |
| `src/core/living-docs/content-distributor.ts` | Import + replace default | ~2 |
| `src/core/notifications/command-integration.ts` | Import + replace default | ~2 |
| `src/core/notifications/notification-manager.ts` | Import + replace default | ~2 |
| `src/core/scheduler/schedule-persistence.ts` | Import + replace default | ~2 |
| `src/core/logs/log-aggregator.ts` | Import + replace default | ~2 |
| `src/core/sync/sync-audit-logger.ts` | Import + replace default | ~2 |
| `src/core/sync/permission-enforcer.ts` | Import + replace (2 locations) | ~3 |
| `src/cli/commands/sync-scheduled.ts` | Import + replace default | ~2 |
| `tests/unit/utils/find-project-root.test.ts` | Add umbrella test suites | ~120 |

**Total**: 18 files, ~170 lines changed

## Technical Challenges

### Challenge 1: Standalone mode regression
**Risk**: `getSpecweavePath()` could return wrong path in non-umbrella projects.
**Mitigation**: `resolveEffectiveRoot()` already falls back to `findProjectRoot() || process.cwd()` — behavior is identical when no umbrella exists. Tested in AC-US1-03.

### Challenge 2: Config flag fragmentation
**Risk**: Existing configs may have various combinations of flags.
**Mitigation**: `findUmbrellaRoot()` checks `umbrella.enabled` OR `repository.umbrellaRepo` OR `repositories/` dir — three independent signals, any one sufficient. `detectUmbrellaParent()` will match this logic.

### Challenge 3: Stale cleanup destroying active work
**Risk**: An orphaned increment might contain unsaved work not yet moved to umbrella.
**Mitigation**: AC-US5-03 requires verifying each orphan exists in umbrella archive before deletion. Implementation checks `find .specweave/increments/ -name "XXXX-*"` at umbrella root.
