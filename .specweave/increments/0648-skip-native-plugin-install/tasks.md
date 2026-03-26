# Tasks: Skip native plugin install for Claude

## Phase 1: TDD Red — Failing Tests

### T-001: Write failing tests for isSwPluginInstalledNatively()
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-04, AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] Completed

**File**: `tests/unit/utils/is-sw-plugin-installed-natively.test.ts`

**Test Plan**:
- **TC-001**: Returns true when CLI shows sw@specweave enabled
  - Given `claude plugin list` output contains `sw@specweave` with `Status: ✔ enabled`
  - When `isSwPluginInstalledNatively()` is called
  - Then returns `true`
- **TC-002**: Returns false when sw@specweave is disabled
  - Given CLI output contains `sw@specweave` with `Status: ✘ disabled`
  - When called
  - Then returns `false`
- **TC-003**: Returns false when sw@specweave not in output
  - Given CLI output has other plugins but not sw@specweave
  - When called
  - Then returns `false`
- **TC-004**: Returns false when CLI fails
  - Given `execFileNoThrowSync` returns `success: false`
  - When called
  - Then returns `false`
- **TC-005**: Returns false when CLI throws
  - Given `execFileNoThrowSync` throws an error
  - When called
  - Then returns `false`

---

### T-002: Write failing tests for init.ts skip logic
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] Completed

**File**: `tests/unit/init/plugin-installer.test.ts`

**Test Plan**:
- **TC-006**: init.ts contains isSwPluginInstalledNatively check
  - Given init.ts source code
  - When read
  - Then contains `isSwPluginInstalledNatively`
- **TC-007**: forceRefresh bypasses native check
  - Given init.ts source code
  - When read
  - Then contains `!options.forceRefresh && isSwPluginInstalledNatively`

---

### T-003: Write export verification test
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Status**: [x] Completed

**File**: `tests/unit/utils/plugin-copier.test.ts`

**Test Plan**:
- **TC-008**: isSwPluginInstalledNatively is exported
  - Given plugin-copier module
  - When imported
  - Then `isSwPluginInstalledNatively` is a function

## Phase 2: TDD Green — Implementation

### T-004: Implement isSwPluginInstalledNatively() in plugin-copier.ts
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-04, AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] Completed

**File**: `src/utils/plugin-copier.ts`

**Implementation**:
- Add exported function after existing utility functions
- Run `claude plugin list` via `execFileNoThrowSync`
- Parse output for `sw@specweave` + enabled status
- Return boolean, catch all errors

---

### T-005: Add skip branch in init.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] Completed

**File**: `src/cli/commands/init.ts`

**Implementation**:
- Import `isSwPluginInstalledNatively` from plugin-copier
- Add `else if (!options.forceRefresh && isSwPluginInstalledNatively())` branch
- Print skip message, set `autoInstallSucceeded = true`

## Phase 3: TDD Refactor — Verify

### T-006: Run all tests and verify
**User Story**: US-001, US-002 | **Satisfies ACs**: All
**Status**: [x] Completed

- Run `npx vitest run` for all affected test files
- Verify no regressions
