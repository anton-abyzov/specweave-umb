---
increment: 0395-init-location-guard-rails
total_tasks: 5
completed_tasks: 5
---

# Tasks: Init Location Guard Rails

## User Story: US-001 - Prevent Init Inside Umbrella Sub-Repos

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, 2 completed

---

### T-001: Add detectUmbrellaParent() to path-utils.ts

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-04
**Status**: [x] completed
**Priority**: P0 (Critical)
**Estimated Effort**: 1 hour

**Description**:
Add `UmbrellaParentResult` interface to `types.ts`. Add `detectUmbrellaParent(targetDir: string)` function to `path-utils.ts` that walks up the directory tree looking for parent `.specweave/config.json` files with umbrella indicators (`repository.umbrellaRepo` set or sibling `repositories/` dir). Re-export from `index.ts`.

**Implementation Steps**:
1. Add `UmbrellaParentResult` interface to `src/cli/helpers/init/types.ts`
2. Add `detectUmbrellaParent()` to `src/cli/helpers/init/path-utils.ts`
3. Re-export from `src/cli/helpers/init/index.ts`

**Test Plan**:
- **File**: `tests/unit/cli/helpers/init/init-location-guards.test.ts`
- **Tests**:
  - **TC-001**: Given a target dir inside an umbrella (parent has config with umbrellaRepo) -> When detectUmbrellaParent is called -> Then returns UmbrellaParentResult with reason 'config-umbrella-repo'
  - **TC-002**: Given a target dir inside an umbrella (parent has repositories/ sibling) -> When detectUmbrellaParent is called -> Then returns UmbrellaParentResult with reason 'repositories-dir'
  - **TC-003**: Given a target dir that is NOT inside an umbrella -> When detectUmbrellaParent is called -> Then returns null
  - **TC-004**: Given a target dir with parent .specweave but no config.json -> When detectUmbrellaParent is called -> Then returns null (skip stale folders)

**Dependencies**: None

---

### T-002: Integrate umbrella guard into init.ts

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed
**Priority**: P0 (Critical)
**Estimated Effort**: 30 minutes

**Description**:
Call `detectUmbrellaParent(targetDir)` in `initCommand()` after target dir resolution and before the existing `detectNestedSpecweave()` check. If result is non-null and `--force` is not set, print error and exit. If `--force` is set, print warning and continue.

**Implementation Steps**:
1. Import `detectUmbrellaParent` in `init.ts`
2. Add guard check after targetDir is resolved (~line 457, before the nested .specweave check)
3. Handle `--force` override with warning message

**Test Plan**:
- **File**: `tests/unit/cli/helpers/init/init-location-guards.test.ts`
- **Tests**:
  - **TC-005**: Given umbrella detected and no --force -> When init runs -> Then process.exit(1) is called
  - **TC-006**: Given umbrella detected and --force -> When init runs -> Then warning printed but init continues

**Dependencies**: T-001

---

## User Story: US-002 - Prevent Init in Suspicious Paths

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 2 total, 2 completed

---

### T-003: Add detectSuspiciousPath() to path-utils.ts

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-05
**Status**: [x] completed
**Priority**: P0 (Critical)
**Estimated Effort**: 1 hour

**Description**:
Add `SuspiciousPathResult` interface to `types.ts`. Add exported `SUSPICIOUS_PATH_SEGMENTS` constant and `detectSuspiciousPath(targetDir: string)` function to `path-utils.ts`. The function checks if any path segment matches the blocklist and returns the first match with a suggested root directory. Re-export from `index.ts`.

**Implementation Steps**:
1. Add `SuspiciousPathResult` interface to `src/cli/helpers/init/types.ts`
2. Add `SUSPICIOUS_PATH_SEGMENTS` constant to `src/cli/helpers/init/path-utils.ts`
3. Add `detectSuspiciousPath()` function to `src/cli/helpers/init/path-utils.ts`
4. Re-export from `src/cli/helpers/init/index.ts`

**Test Plan**:
- **File**: `tests/unit/cli/helpers/init/init-location-guards.test.ts`
- **Tests**:
  - **TC-007**: Given path `/home/user/project/node_modules/some-pkg` -> When detectSuspiciousPath is called -> Then returns segment='node_modules', suggestedRoot='/home/user/project'
  - **TC-008**: Given path `/home/user/project/src/stories` -> When detectSuspiciousPath is called -> Then returns segment='stories', suggestedRoot='/home/user/project/src'
  - **TC-009**: Given path `/home/user/project/dist/output` -> When detectSuspiciousPath is called -> Then returns segment='dist', suggestedRoot='/home/user/project'
  - **TC-010**: Given path `/home/user/my-project` (clean root) -> When detectSuspiciousPath is called -> Then returns null
  - **TC-011**: Given path `/home/user/.git/hooks` -> When detectSuspiciousPath is called -> Then returns segment='.git'
  - **TC-012**: SUSPICIOUS_PATH_SEGMENTS is an exported readonly array

**Dependencies**: None

---

### T-004: Integrate suspicious path guard into init.ts

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] completed
**Priority**: P0 (Critical)
**Estimated Effort**: 30 minutes

**Description**:
Call `detectSuspiciousPath(targetDir)` in `initCommand()` right after the umbrella guard (T-002). If result is non-null and `--force` is not set, print warning with suspicious segment and suggested root, then exit. If `--force` is set, print warning and continue. In CI/quick mode, still block unless `--force` is also passed.

**Implementation Steps**:
1. Import `detectSuspiciousPath` in `init.ts`
2. Add guard check after umbrella guard, before nested .specweave check
3. Handle `--force` override with warning message
4. Ensure CI/quick mode does NOT auto-skip this check

**Test Plan**:
- **File**: `tests/unit/cli/helpers/init/init-location-guards.test.ts`
- **Tests**:
  - **TC-013**: Given suspicious path detected and no --force -> When init runs -> Then process.exit(1) is called
  - **TC-014**: Given suspicious path detected and --force -> When init runs -> Then warning printed but init continues
  - **TC-015**: Given suspicious path detected in CI mode without --force -> When init runs -> Then still blocks (process.exit(1))

**Dependencies**: T-003

---

## Cross-Cutting

### T-005: Build, test, verify

**User Story**: US-001, US-002
**Satisfies ACs**: All
**Status**: [x] completed
**Priority**: P0 (Critical)
**Estimated Effort**: 30 minutes

**Description**:
Run full test suite, verify TypeScript build passes, ensure no regressions in existing init tests.

**Implementation Steps**:
1. Run `npx tsc --noEmit` to verify TypeScript compilation
2. Run `npx vitest run tests/unit/cli/helpers/init/init-location-guards.test.ts` for new tests
3. Run `npx vitest run tests/unit/cli/commands/init.test.ts` for existing init tests
4. Run `npm run build` to verify dist output

**Test Plan**:
- All new tests pass
- All existing init tests pass
- TypeScript compiles without errors
- Build succeeds

**Dependencies**: T-001, T-002, T-003, T-004
