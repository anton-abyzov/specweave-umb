# Implementation Plan: Fix init guard order and temp path detection

## Overview

Reorder init command flow so guards run before destructive actions, replace segment-based temp detection with `os.tmpdir()` check, and add home-dir safety to `suggestedRoot`.

## Changes

### 1. Reorder guards — `src/cli/commands/init.ts`

Split the path-resolution if/else block (lines 117-186) into two phases:
- **Phase A**: Path resolution only (set `targetDir`, `finalProjectName`, `usedDotNotation`)
- **Guard clauses**: `detectUmbrellaParent`, `detectSuspiciousPath`, `detectNestedSpecweave`
- **Phase B**: Reinit prompt and existence checks using `usedDotNotation` to branch

### 2. Fix temp detection — `src/cli/helpers/init/path-utils.ts`

- Remove `'tmp'` and `'temp'` from `SUSPICIOUS_PATH_SEGMENTS`
- Add `isSystemTempDir(resolvedPath)` using `os.tmpdir()`
- Call it in `detectSuspiciousPath()` before segment loop

### 3. Fix suggestedRoot — `src/cli/helpers/init/path-utils.ts`

After computing `suggestedRoot`, check if it equals `os.homedir()` or is an ancestor. If so, fall back to `path.dirname(targetDir)`.

## Testing Strategy

- Unit tests for `isSystemTempDir`, `detectSuspiciousPath` changes, `suggestedRoot` safety
- Existing test suite must pass unchanged (except removed temp/tmp segment expectations if any)
