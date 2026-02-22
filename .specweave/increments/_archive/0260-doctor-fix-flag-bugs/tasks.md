# Tasks: Doctor --fix flag not working for PluginsChecker and lockfile integrity

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed

## Phase 1: Fix PluginsChecker (US-001)

### T-001: Add fix support to PluginsChecker
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04

**Description**: Update `plugins-checker.ts` to accept and act on the `fix` option.

**Implementation Details**:
- Rename `_options` to `options` in `check()` method
- Extract `const fix = options.fix ?? false`
- Pass `fix` to all 4 private methods
- `checkLocalPluginState(projectRoot, fix)`: when fix=true and invalid state file, `unlinkSync` the corrupt file
- `checkGlobalPluginCache(fix)`: when fix=true and stale (>24h), `unlinkSync` the stale cache file
- `checkMarketplaceDirectory(fix)`: when fix=true and empty/not-installed, `execSync('specweave refresh-plugins', { stdio: 'pipe' })`
- `checkCorePlugin(fix)`: when fix=true and missing/incomplete, `execSync('specweave refresh-plugins', { stdio: 'pipe' })`
- Import `execSync` from `child_process`

**File**: `repositories/anton-abyzov/specweave/src/core/doctor/checkers/plugins-checker.ts`

**Test Plan**:
- **File**: `repositories/anton-abyzov/specweave/tests/unit/core/doctor/checkers/plugins-checker.test.ts`
- **Tests**:
  - **TC-PC-01**: fix=true with invalid state file deletes the file
    - Given a corrupt plugins-loaded.json state file
    - When check() called with fix=true
    - Then the state file is deleted and status is warn with "removed" message
  - **TC-PC-02**: fix=true with stale global cache deletes the file
    - Given a global cache file older than 24h
    - When check() called with fix=true
    - Then the cache file is deleted and status is warn with "removed" message
  - **TC-PC-03**: fix=true with empty marketplace runs refresh-plugins
    - Given marketplace dir exists but plugins/ is empty
    - When check() called with fix=true
    - Then execSync is called with 'specweave refresh-plugins'
  - **TC-PC-04**: fix=true with missing core plugin runs refresh-plugins
    - Given core plugin dir does not exist
    - When check() called with fix=true
    - Then execSync is called with 'specweave refresh-plugins'
  - **TC-PC-05**: fix=false preserves existing behavior (suggestion text only)
    - Given any fixable issue
    - When check() called with fix=false
    - Then fixSuggestion is set but no side effects occur

**Dependencies**: None

---

## Phase 2: Fix lockfile integrity (US-002)

### T-002: Add auto-fix to lockfile integrity check
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04

**Description**: Update `checkLockfileIntegrity()` in `installation-health-checker.ts` to execute `specweave refresh-plugins` when fix=true and issues detected.

**Implementation Details**:
- When fix=true and mismatches detected (lines 262-276): wrap in try/catch, call `execSync('specweave refresh-plugins', { stdio: 'pipe' })`, return warn with "refreshed plugins" message on success, fail on error
- When fix=true and missing skills detected (lines 252-259): same pattern -- call execSync to refresh, return appropriate status
- Import `execSync` from `child_process` (add to existing imports)

**File**: `repositories/anton-abyzov/specweave/src/core/doctor/checkers/installation-health-checker.ts`

**Test Plan**:
- **File**: `repositories/anton-abyzov/specweave/tests/unit/core/doctor/checkers/installation-health-checker.test.ts`
- **Tests**:
  - **TC-LF-01**: fix=true with hash mismatches runs refresh-plugins
    - Given lockfile with wrong hash for installed skill
    - When check() called with fix=true
    - Then execSync is called with 'specweave refresh-plugins' and status is warn
  - **TC-LF-02**: fix=true with missing skills runs refresh-plugins
    - Given lockfile references skill not in commands dir
    - When check() called with fix=true
    - Then execSync is called with 'specweave refresh-plugins' and status changes from fail to warn
  - **TC-LF-03**: fix=true but refresh-plugins fails returns fail status
    - Given execSync throws an error
    - When check() called with fix=true
    - Then status is fail with error message
  - **TC-LF-04**: fix=false preserves existing behavior (no execSync call)
    - Given lockfile with wrong hash
    - When check() called with fix=false
    - Then fixSuggestion text is set but execSync is not called

**Dependencies**: None (parallelizable with T-001)

---

## Phase 3: Verification

### T-003: Run full test suite and verify
**User Story**: US-001, US-002 | **Status**: [x] completed

**Description**: Run all existing doctor tests plus new tests. Verify no regressions.

**Test**: Given all changes applied -> When `npx vitest run tests/unit/core/doctor/` -> Then all tests pass

**Dependencies**: T-001, T-002
