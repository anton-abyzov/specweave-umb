# Tasks: Fix init guard order and temp path detection

## Phase 1: TDD Red — Write Failing Tests

### T-001: Write tests for isSystemTempDir
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test Plan**:
- Given a path under `os.tmpdir()` → When `isSystemTempDir` is called → Then returns true
- Given a path under `~/temp/` → When `isSystemTempDir` is called → Then returns false
- Given `os.homedir()` → When `isSystemTempDir` is called → Then returns false

### T-002: Write tests for temp/tmp segment removal
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] completed
**Test Plan**:
- Given `SUSPICIOUS_PATH_SEGMENTS` → When checked → Then does NOT contain "tmp" or "temp"
- Given path `~/temp/my-project` → When `detectSuspiciousPath` is called → Then returns null
- Given path `~/tmp/my-project` → When `detectSuspiciousPath` is called → Then returns null

### T-003: Write tests for suggestedRoot safety
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test Plan**:
- Given path `~/cache-dir/.cache/project` → When `detectSuspiciousPath` returns result → Then `suggestedRoot` is NOT `os.homedir()`
- Given suspicious segment at depth producing homedir → When computed → Then falls back to `path.dirname(targetDir)`

## Phase 2: TDD Green — Implement Fixes

### T-004: Implement isSystemTempDir and update detectSuspiciousPath
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Files**: `src/cli/helpers/init/path-utils.ts`, `src/cli/helpers/init/index.ts`

### T-005: Implement suggestedRoot home-dir guard
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Files**: `src/cli/helpers/init/path-utils.ts`

### T-006: Reorder guards before promptSmartReinit in init.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Files**: `src/cli/commands/init.ts`

## Phase 3: Verify

### T-007: Run full test suite
**Status**: [x] completed
**Test Plan**:
- Given all changes → When `npx vitest run` → Then all tests pass
