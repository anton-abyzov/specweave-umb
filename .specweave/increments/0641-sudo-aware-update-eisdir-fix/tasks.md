---
increment: 0641-sudo-aware-update-eisdir-fix
title: "Sudo-aware self-update and EISDIR fix"
status: planned
---

# Tasks

## US-001: Silent plugin hash computation

### T-001: Write failing test for EISDIR/ENOENT resilience in computePluginHash
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed

**Test Plan**:
- Given a plugin directory containing both files and subdirectories
- When `computePluginHash` is called
- Then it returns a valid 12-char hex hash without throwing or logging debug noise

- Given a plugin directory where an entry vanishes between readdir and stat (ENOENT race)
- When `computePluginHash` processes that entry
- Then it silently skips the entry and returns a valid hash for remaining files

- Given a non-existent plugin directory
- When `computePluginHash` is called
- Then it returns an empty string

**File**: `repositories/anton-abyzov/specweave/tests/unit/utils/plugin-copier.test.ts`

---

### T-002: Fix computePluginHash to use non-throwing statSync
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed

**Test Plan**:
- Given T-001 red tests exist
- When `statSync(fullPath).isFile()` at line 115 of `plugin-copier.ts` is replaced with `statSync(fullPath, { throwIfNoEntry: false })?.isFile()`
- Then all T-001 tests pass green and no EISDIR or ENOENT is thrown for directory or vanished entries

**File**: `repositories/anton-abyzov/specweave/src/utils/plugin-copier.ts` line 115

---

## US-002: Sudo-aware self-update with auto-elevation

### T-003: Write failing tests for isGlobalNpmWritable helper
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-05 | **Status**: [x] completed

**Test Plan**:
- Given `npm prefix -g` returns a path and `fs.accessSync(W_OK)` succeeds
- When `isGlobalNpmWritable()` is called
- Then it returns `true`

- Given `fs.accessSync` throws EACCES on the lib/node_modules path
- When `isGlobalNpmWritable()` is called
- Then it returns `false`

- Given `process.platform === 'win32'`
- When `isGlobalNpmWritable()` is called
- Then it returns `true` without invoking `npm prefix -g`

- Given `execSync('npm prefix -g')` throws (npm not found or timeout)
- When `isGlobalNpmWritable()` is called
- Then it returns `false`

**File**: `repositories/anton-abyzov/specweave/tests/unit/cli/commands/update.test.ts`

---

### T-004: Write failing tests for isSudoAvailable helper
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-05 | **Status**: [x] completed

**Test Plan**:
- Given `which sudo` exits 0 on a Unix platform
- When `isSudoAvailable()` is called
- Then it returns `true`

- Given `which sudo` throws (sudo not installed)
- When `isSudoAvailable()` is called
- Then it returns `false`

- Given `process.platform === 'win32'`
- When `isSudoAvailable()` is called
- Then it returns `false` without calling `which sudo`

**File**: `repositories/anton-abyzov/specweave/tests/unit/cli/commands/update.test.ts`

---

### T-005: Write failing tests for npmPublicInstall sudo retry behavior
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed

**Test Plan**:
- Given the npm global prefix is writable
- When `installWithFallback` runs
- Then npm install executes without sudo and succeeds

- Given the first install throws EACCES AND sudo is available
- When `npmPublicInstall` catches the error
- Then it retries with `sudo` prefix, `stdio: 'inherit'`, and the same `buildPublicRegistryEnv()` env

- Given the first install throws ETARGET (not a permission error)
- When `npmPublicInstall` catches the error
- Then it re-throws without a sudo retry

- Given the first install throws EACCES AND `isSudoAvailable()` returns false
- When `npmPublicInstall` catches the error
- Then it re-throws without a sudo retry

**File**: `repositories/anton-abyzov/specweave/tests/unit/cli/commands/update.test.ts`

---

### T-006: Implement isGlobalNpmWritable, isSudoAvailable, and npmPublicInstall in update.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed

**Test Plan**:
- Given T-003, T-004, T-005 red tests exist
- When the three helpers are added to `update.ts` and `installWithFallback` is wired to use `npmPublicInstall`
- Then all T-003, T-004, T-005 tests pass green

**Changes**:
- Add `isGlobalNpmWritable(): boolean` — `npm prefix -g` + `fs.accessSync(W_OK)` + win32 early-return `true`
- Add `isSudoAvailable(): boolean` — `which sudo` check + win32 early-return `false`
- Add `npmPublicInstall(packageSpec: string, timeout: number): string` — attempt without sudo, on EACCES+sudo available retry with `sudo` prefix + `stdio: 'inherit'` + `buildPublicRegistryEnv()`
- Line 759: replace `npmPublicExec('npm install -g specweave@${targetVersion}', 120000)` with `npmPublicInstall('specweave@${targetVersion}', 120000)`
- Line 793: replace `npmPublicExec('npm install -g specweave@${fallbackVersion}', 120000)` with `npmPublicInstall('specweave@${fallbackVersion}', 120000)`

**File**: `repositories/anton-abyzov/specweave/src/cli/commands/update.ts`

---

## US-003: Clear error messaging when permissions fail

### T-007: Write failing test for updated EACCES error message
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed

**Test Plan**:
- Given EACCES persists after sudo retry (or sudo unavailable) on Unix
- When `selfUpdateSpecWeave` catches the error
- Then the returned error string contains `sudo specweave update` and does NOT contain `sudo npm install -g specweave@latest`

- Given `process.platform === 'win32'` and an EACCES error
- When `selfUpdateSpecWeave` catches the error
- Then the returned error string suggests running the terminal as Administrator

- Given a sudo retry is triggered in `npmPublicInstall`
- When the elevated retry execSync is about to run
- Then the spinner text has been updated to "Retrying with sudo..."

**File**: `repositories/anton-abyzov/specweave/tests/unit/cli/commands/update.test.ts`

---

### T-008: Update EACCES error message and add spinner text in update.ts
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed

**Test Plan**:
- Given T-007 red tests exist
- When the EACCES catch block at line 953-957 is updated and spinner text is added before the sudo retry
- Then all T-007 tests pass green

**Changes**:
- Line 956: change `'Permission denied. Try: sudo npm install -g specweave@latest'` to platform-conditional message:
  - Unix: `'Permission denied. Try: sudo specweave update'`
  - Windows: `'Permission denied. Run your terminal as Administrator.'`
- In `npmPublicInstall`, add spinner/logger output "Retrying with sudo..." before the elevated `execSync` call

**File**: `repositories/anton-abyzov/specweave/src/cli/commands/update.ts`

---

## Verification

### T-009: Run full test suite and confirm zero regressions
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed

**Test Plan**:
- Given all implementation tasks T-002, T-006, T-008 are complete
- When `npx vitest run tests/unit/utils/plugin-copier.test.ts tests/unit/cli/commands/update.test.ts` is executed
- Then all tests pass with zero failures and coverage >= 90% for changed lines
