---
increment: 0557-fix-vskill-lock-global
generated: 2026-03-17
---

# Tasks: Separate Global Plugin Lock from Project-Scoped Skill Lock

## US-001: Global Lock for Bundled Plugins

### T-001: Add `GLOBAL_LOCKFILE_NAME` constant and `getGlobalLockDir()` to plugin-copier.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] Completed
**Test**: Given `~/.specweave/` does not exist → When `getGlobalLockDir()` is called → Then it creates the directory via `mkdirSync({ recursive: true })` and returns the absolute path; a second call succeeds without error (idempotent)

**TDD cycle**:
- RED: Write test asserting `getGlobalLockDir()` creates `<tmpHome>/.specweave/` and returns the path; test fails because function does not exist yet
- GREEN: Export `GLOBAL_LOCKFILE_NAME = 'plugins-lock.json'` and `getGlobalLockDir()` using `os.homedir()` + `mkdirSync({ recursive: true })`
- REFACTOR: Verify `homedir()` is mocked via `vi.mock('node:os')` so no real `~/.specweave/` is created during tests

---

### T-002: Add `readGlobalLockfile()`, `writeGlobalLockfile()`, and `ensureGlobalLockfile()` to plugin-copier.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] Completed
**Test**: Given `~/.specweave/plugins-lock.json` does not exist → When `ensureGlobalLockfile()` is called → Then it returns a new `VskillLock` with `version: 1` and `skills: {}` and writes `plugins-lock.json`; calling again returns the existing file unchanged

**TDD cycle**:
- RED: Write three failing tests: `readGlobalLockfile` returns null when absent, round-trip write+read preserves all fields, `ensureGlobalLockfile` creates on first call and returns existing on second
- GREEN: Implement the three functions in `plugin-copier.ts` using `getGlobalLockDir()` + `GLOBAL_LOCKFILE_NAME`; reuse the same `VskillLock` interface
- REFACTOR: Extract a shared "read JSON or return null" helper if it eliminates duplication with `readLockfile()`

---

### T-003: Update `installPlugin()` to use global lock instead of `getProjectRoot()`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] Completed
**Test**: Given `installPlugin()` is called with `execFileNoThrowSync` mocked to return success → When called from a temp directory with no `.specweave/config.json` → Then no `vskill.lock` appears in `process.cwd()` and `~/.specweave/plugins-lock.json` contains the plugin entry with `source: 'local:specweave'`

**TDD cycle**:
- RED: Write test asserting `vskill.lock` does NOT exist in `process.cwd()` and `plugins-lock.json` DOES exist in the mocked `homedir` after `installPlugin()` runs
- GREEN: Replace `const lockDir = getProjectRoot()` / `ensureLockfile(lockDir)` / `writeLockfile(lock, lockDir)` with `ensureGlobalLockfile()` / `writeGlobalLockfile(lock)` in `installPlugin()`
- REFACTOR: Remove `getProjectRoot` import from `plugin-copier.ts` if no longer referenced

---

### T-004: Verify skip logic works with global lock (force: false + hash match)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [x] Completed
**Test**: Given `~/.specweave/plugins-lock.json` already has an entry for plugin `sw` with a matching `sha` and the plugin appears in `installed_plugins.json` → When `installPlugin('sw', specweaveRoot, { force: false })` is called → Then `execFileNoThrowSync` is NOT called and the result has `skipped: true`

**TDD cycle**:
- RED: Write test writing a matching `sha` to `plugins-lock.json` (global) and a matching entry to `installed_plugins.json`; assert `execFileNoThrowSync` is never called
- GREEN: Confirm the skip guard in `installPlugin()` reads from `ensureGlobalLockfile()` (already the case after T-003); no additional code change if T-003 is correct
- REFACTOR: Remove any leftover reference to `lockDir` variable if it exists

---

## US-002: Refresh-Plugins Uses Global Lock

### T-005: Confirm native-CLI path in `refreshPluginsCommand()` uses global lock end-to-end
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Status**: [x] Completed
**Test**: Given `detectClaudeCli()` returns `{ available: true, pluginCommandsWork: true }` → When `refreshPluginsCommand()` runs → Then `installPlugin()` is called and no `vskill.lock` file appears at `projectRoot`

**TDD cycle**:
- RED: Write test mocking `installPlugin` and asserting it is called; assert `vskill.lock` is absent at the test project root
- GREEN: Confirm no code change to `refresh-plugins.ts` is needed after T-003 — `installPlugin()` now writes to the global lock by construction; test passes
- REFACTOR: Add inline comment in `refreshPluginsCommand()` documenting the two distinct `getProjectRoot()` usages: (1) orphaned child cleanup (legitimate) and (2) `copyPluginSkillsToProject` fallback (project-scoped by design)

---

### T-006: Confirm direct-copy fallback in `refreshPluginsCommand()` still uses project-local `vskill.lock`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03
**Status**: [x] Completed
**Test**: Given `detectClaudeCli()` returns `{ available: false }` → When `refreshPluginsCommand()` runs and `copyPluginSkillsToProject()` is called → Then it writes to `<projectRoot>/vskill.lock` (project-scoped) and does NOT touch `~/.specweave/plugins-lock.json`

**TDD cycle**:
- RED: Write test mocking `copyPluginSkillsToProject` and checking the `projectRoot` argument matches the known SpecWeave project directory; assert global lockfile path is untouched
- GREEN: No change to `copyPluginSkillsToProject()` or its callers — it already takes explicit `projectRoot`; test passes
- REFACTOR: Confirm `cleanupOrphanedChildLocks` call in Step 0.5 is the ONLY surviving `getProjectRoot()` call in `refreshPluginsCommand()` used for cleanup

---

## US-003: Migration from Project Lock to Global Lock

### T-007: Implement `migrateBundledToGlobalLock()` in plugin-copier.ts
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [ ] Not Started
**Test**: Given a project `vskill.lock` with one bundled entry (`source: 'local:specweave'`) and one user entry (`source: 'marketplace'`) → When `migrateBundledToGlobalLock(projectRoot)` is called → Then `plugins-lock.json` gains the bundled entry, `vskill.lock` retains only the user entry, and the return value is `{ migratedCount: 1, deletedProjectLock: false }`

**TDD cycle**:
- RED: Write four failing tests: (1) mixed-entry migration as above, (2) bundled-only lock deletes project file (`deletedProjectLock: true`), (3) second call is no-op (`migratedCount: 0`), (4) global entry is kept when global `installedAt` is newer than project entry
- GREEN: Implement `migrateBundledToGlobalLock(projectRoot: string): { migratedCount: number; deletedProjectLock: boolean }` — read project `vskill.lock`, filter `source === 'local:specweave'`, merge into global lock with timestamp precedence, delete project lock if empty
- REFACTOR: Extract timestamp comparison into a private `newerEntry(a, b)` helper if the logic is more than two lines

---

### T-008: Wire `migrateBundledToGlobalLock()` into `refreshPluginsCommand()` before plugin installation
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04
**Status**: [ ] Not Started
**Test**: Given a project `vskill.lock` containing only bundled entries → When `refreshPluginsCommand()` runs → Then after completion the project `vskill.lock` is deleted and `~/.specweave/plugins-lock.json` has those entries; running a second time does not attempt migration again

**TDD cycle**:
- RED: Write test mocking `migrateBundledToGlobalLock` and asserting it is called before the plugin installation loop
- GREEN: Import `migrateBundledToGlobalLock` and call it at the start of Step 1 in `refreshPluginsCommand()` after resolving `projectRoot`; wrap in try/catch to keep non-blocking
- REFACTOR: Confirm the call is placed inside a try/catch with silent error handling matching the existing cleanup pattern

---

### T-009: Update `checkLockfileIntegrity()` in `installation-health-checker.ts` to include global lock entries
**User Story**: US-003 | **Satisfies ACs**: AC-US1-04
**Status**: [ ] Not Started
**Test**: Given `~/.specweave/plugins-lock.json` contains a bundled `sw` entry and no `vskill.lock` exists at `projectRoot` → When `checkLockfileIntegrity(projectRoot, false)` is called → Then the result is `pass` or `warn` (not `skip`) and the `sw` entry's hash is verified against the plugin cache

**TDD cycle**:
- RED: Write test mocking `homedir` to temp dir; place `plugins-lock.json` there with a `sw` entry; assert `checkLockfileIntegrity` status is not `skip`
- GREEN: Update `checkLockfileIntegrity` to merge skills from `readGlobalLockfile()` with skills from project `vskill.lock` before iterating hash comparisons
- REFACTOR: Extract `readMergedSkills(projectRoot)` helper if the merge logic is also used by T-010

---

### T-010: Update `detect-intent.ts` to include global `plugins-lock.json` in installed-plugins filter
**User Story**: US-003 | **Satisfies ACs**: AC-US1-04
**Status**: [ ] Not Started
**Test**: Given `~/.specweave/plugins-lock.json` has `sw` as a skill and no project `vskill.lock` exists → When `detectIntentCommand()` runs and `detectVskillPlugins()` returns `sw` as a recommendation → Then `sw` is absent from `result.vskillRecommendations`

**TDD cycle**:
- RED: Write test mocking `homedir` to temp dir; write `plugins-lock.json` with `sw`; mock `detectVskillPlugins` to return `sw`; assert `result.vskillRecommendations` is empty or undefined
- GREEN: Extend `installedVskillPlugins` Set construction in `detectIntentCommand()` to also call `readGlobalLockfile()` and add its `skills` keys to the set
- REFACTOR: Use the `readGlobalLockfile()` export from `plugin-copier.ts` directly — no duplicate JSON parsing

---

### T-011: Update `uninstall.ts` to remove `~/.specweave/plugins-lock.json` during full uninstall
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01
**Status**: [ ] Not Started
**Test**: Given `~/.specweave/plugins-lock.json` exists → When the full uninstall runs → Then `plugins-lock.json` is deleted; if the file does not exist the uninstall still succeeds without error

**TDD cycle**:
- RED: Write test mocking `homedir` to temp dir; write `plugins-lock.json`; run uninstall function; assert file is absent
- GREEN: Add `rmSync(join(homedir(), '.specweave', GLOBAL_LOCKFILE_NAME), { force: true })` to the cleanup sequence in `uninstall.ts`; import `GLOBAL_LOCKFILE_NAME` from `plugin-copier.ts`
- REFACTOR: Wrap in try/catch matching the non-fatal pattern used elsewhere in uninstall

---

### T-012: Update `shouldOfferMigration()` in `migrate-to-vskill.ts` to check global lock
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04
**Status**: [ ] Not Started
**Test**: Given `~/.specweave/plugins-lock.json` contains at least one skill entry and no project `vskill.lock` exists → When `shouldOfferMigration()` is called → Then it returns `false` (plugins already tracked globally)

**TDD cycle**:
- RED: Write test mocking `homedir` to temp dir; write `plugins-lock.json` with one entry; assert `shouldOfferMigration()` returns `false`
- GREEN: In `shouldOfferMigration()`, call `readGlobalLockfile()` and return `false` early if `Object.keys(lock.skills).length > 0`
- REFACTOR: Remove the `lockDir || process.cwd()` fallback once the global lock is the authoritative source for bundled plugins

---

## Cross-Cutting: Edge Cases

### T-013: Graceful fallback when `~/.specweave/` cannot be created (permission denied)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [ ] Not Started
**Test**: Given `mkdirSync` throws `{ code: 'EACCES' }` for the global dir path → When `installPlugin()` is called → Then it still returns `{ success: true }` after installation and does not throw; no `vskill.lock` is created in `process.cwd()`

**TDD cycle**:
- RED: Write test mocking `mkdirSync` to throw `EACCES`; assert `installPlugin()` returns `{ success: true }` rather than throwing
- GREEN: Wrap `getGlobalLockDir()` + `writeGlobalLockfile()` calls in a try/catch inside `installPlugin()`; on failure continue without writing (matching the existing non-fatal lock-write pattern)
- REFACTOR: Confirm warning is emitted via `logger.debug` rather than `console.warn` to respect quiet mode

---

### T-014: Graceful handling when `os.homedir()` returns empty string
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01
**Status**: [ ] Not Started
**Test**: Given `os.homedir()` returns `''` → When `writeGlobalLockfile()` is called → Then it does not write to the filesystem root and does not throw an unhandled exception

**TDD cycle**:
- RED: Write test mocking `homedir` to return `''`; call `writeGlobalLockfile()`; assert no file is written and no uncaught error escapes
- GREEN: Add guard in `getGlobalLockDir()`: if `homedir()` returns a falsy value, throw `new Error('No home directory')`; this is caught by the try/catch wrapper in `ensureGlobalLockfile()` and the lock write is skipped
- REFACTOR: Confirm the thrown error surfaces in `logger.debug` at the call site in `installPlugin()` for diagnosability
