---
increment: 0395-init-location-guard-rails
generated: 2026-03-01T00:00:00.000Z
---

# Implementation Plan: Init Location Guard Rails

## Overview

Add two guard rail checks to the `specweave init` command to prevent `.specweave/` folder proliferation in wrong locations. Both checks run early in the init flow, before any file creation.

## Architecture

### Approach: Pure Functions in path-utils.ts + Integration in init.ts

All new detection logic lives in `src/cli/helpers/init/path-utils.ts` as pure, testable functions. The init command (`src/cli/commands/init.ts`) calls them at the right point in the flow.

### New Functions

#### 1. `detectUmbrellaParent(targetDir: string): UmbrellaParentResult | null`

**Location**: `src/cli/helpers/init/path-utils.ts`

Walks up from `targetDir` using the existing parent-walking pattern from `detectNestedSpecweave()`. For each parent with `.specweave/config.json`:
- Reads config and checks for `repository.umbrellaRepo`
- Checks for sibling `repositories/` directory
- Returns the umbrella root path and reason if found, null otherwise

```typescript
export interface UmbrellaParentResult {
  umbrellaRoot: string;
  reason: 'config-umbrella-repo' | 'repositories-dir';
}
```

#### 2. `detectSuspiciousPath(targetDir: string): SuspiciousPathResult | null`

**Location**: `src/cli/helpers/init/path-utils.ts`

Checks the resolved absolute path segments against a blocklist. Returns info about the suspicious segment if found, null otherwise.

```typescript
export const SUSPICIOUS_PATH_SEGMENTS: readonly string[] = [
  // Package managers
  'node_modules', 'vendor', '__pycache__', '.venv', 'venv',
  // Build output
  'dist', 'build', '.next', '.nuxt', '.output', 'out', 'coverage',
  // VCS internals
  '.git', '.svn', '.hg',
  // Temp
  'tmp', 'temp',
  // Test dirs
  '__tests__', 'stories', 'storybook',
  // Platform-specific
  '.cache',
];

export interface SuspiciousPathResult {
  segment: string;
  suggestedRoot: string; // Parent directory before the suspicious segment
}
```

Note: `src`, `lib`, `test`, `tests` are intentionally NOT in the default blocklist because they are common project root names. Only clearly non-root segments are blocked.

### Integration Point in init.ts

Both checks are inserted right after the target directory is resolved and BEFORE the nested `.specweave/` parent check (line ~458). The existing home directory guard (line ~326) already runs before this.

```
Language selection -> Target dir resolution -> Home dir guard ->
  NEW: Umbrella sub-repo guard ->
  NEW: Suspicious path guard ->
  Existing nested .specweave check -> ... rest of init
```

### --force Override

Both checks respect `options.force`:
- Without `--force`: Print error, exit with code 1
- With `--force`: Print warning, continue

### Types Update

Add `UmbrellaParentResult` and `SuspiciousPathResult` to `src/cli/helpers/init/types.ts`.

## File Changes

| File | Change |
|------|--------|
| `src/cli/helpers/init/path-utils.ts` | Add `detectUmbrellaParent()`, `detectSuspiciousPath()`, `SUSPICIOUS_PATH_SEGMENTS` |
| `src/cli/helpers/init/types.ts` | Add `UmbrellaParentResult`, `SuspiciousPathResult` interfaces |
| `src/cli/helpers/init/index.ts` | Re-export new functions |
| `src/cli/commands/init.ts` | Integrate both guards after target dir resolution |
| `tests/unit/cli/helpers/init/init-location-guards.test.ts` | Unit tests for both detection functions |

## Testing Strategy

- Unit tests for `detectUmbrellaParent()` with mocked filesystem
- Unit tests for `detectSuspiciousPath()` (pure path logic, no FS mocking needed)
- Integration test in init.test.ts flow if feasible
- TDD: Red-Green-Refactor cycle

## Risk Assessment

- **Low risk**: Both checks are pure additions with `--force` escape hatch
- **No breaking changes**: Existing init flows unaffected (normal project roots pass both checks)
- **False positive risk**: Mitigated by keeping the suspicious list conservative (no `src`, `lib`, `test`)
