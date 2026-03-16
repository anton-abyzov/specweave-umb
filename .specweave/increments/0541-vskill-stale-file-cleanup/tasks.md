---
increment: 0541-vskill-stale-file-cleanup
generated: 2026-03-15
---

# Tasks: Vskill Stale File Cleanup

## US-001: Legacy Lockfile Removal

### T-001: Define StaleFileCleanupOptions and StaleFileResult types
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed
**Test**: Given the `cleanup-stale-plugins.ts` module, when it is imported, then `StaleFileCleanupOptions` and `StaleFileResult` are exported TypeScript interfaces with fields `verbose`, `fs`, `mtimeThresholdMs`, `success`, `removedCount`, `skippedCount`, `removedPaths`, `skippedPaths`, and `errors`

---

### T-002: Implement cleanupLegacyLockfiles — happy path deletion
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01
**Status**: [x] completed
**Test**: Given a project tree with `skills-lock.json` at root and inside a nested subdirectory (both with mtime older than threshold), when `cleanupLegacyLockfiles(projectRoot, { fs: mockFs, mtimeThresholdMs: 0 })` runs, then both files are deleted and `result.removedCount === 2` with both paths in `result.removedPaths`

---

### T-003: Implement cleanupLegacyLockfiles — mtime guard skips recent files
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02
**Status**: [x] completed
**Test**: Given a `skills-lock.json` whose injected stat reports `mtimeMs = Date.now() - 100` (100 ms ago), when `cleanupLegacyLockfiles(projectRoot, { fs: mockFs, mtimeThresholdMs: 5000 })` runs, then the file is not deleted, `result.removedCount === 0`, `result.skippedCount === 1`, and the path appears in `result.skippedPaths`

---

### T-004: Implement cleanupLegacyLockfiles — no-op when no files exist
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03
**Status**: [x] completed
**Test**: Given a project tree with no `skills-lock.json` files anywhere, when `cleanupLegacyLockfiles(projectRoot, { fs: mockFs })` runs, then `result.success === true`, `result.removedCount === 0`, and `result.errors` is empty

---

### T-005: Implement cleanupLegacyLockfiles — per-file error capture continues processing
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01
**Status**: [x] completed
**Test**: Given two `skills-lock.json` files where `fs.unlinkSync` throws a permission error on the first but succeeds on the second, when `cleanupLegacyLockfiles` runs, then `result.errors` contains one entry for the failed file, `result.removedCount === 1`, and `result.success === true`

---

### T-006: Recursive walk skips node_modules, .git, and .specweave directories
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01
**Status**: [x] completed
**Test**: Given a project tree where `skills-lock.json` appears only inside `node_modules/` and `.git/`, when `cleanupLegacyLockfiles(projectRoot, { fs: mockFs })` runs, then `result.removedCount === 0` (excluded directories are not traversed)

---

## US-002: Orphaned Child-Repo Lockfile Cleanup

### T-007: Implement cleanupOrphanedChildLocks — non-umbrella project returns early
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03
**Status**: [x] completed
**Test**: Given a project root whose `.specweave/config.json` has neither `umbrella.enabled: true` nor `repository.umbrellaRepo`, when `cleanupOrphanedChildLocks(projectRoot, { fs: mockFs })` runs, then `result.removedCount === 0` and no `unlinkSync` calls are made

---

### T-008: Implement cleanupOrphanedChildLocks — removes child vskill.lock, preserves root
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Status**: [x] completed
**Test**: Given an umbrella project (`umbrella.enabled: true`) with `vskill.lock` at the project root and `repositories/org/child-repo/vskill.lock` (mtime older than threshold), when `cleanupOrphanedChildLocks(projectRoot, { fs: mockFs, mtimeThresholdMs: 0 })` runs, then the child lock is deleted, the root lock is untouched, and `result.removedCount === 1`

---

### T-009: Implement cleanupOrphanedChildLocks — mtime guard skips recently written child lock
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02
**Status**: [x] completed
**Test**: Given an umbrella project with a child-repo `vskill.lock` whose injected stat shows `mtimeMs = Date.now() - 500` (0.5 s ago), when `cleanupOrphanedChildLocks(projectRoot, { fs: mockFs, mtimeThresholdMs: 5000 })` runs, then the file is skipped, `result.skippedCount === 1`, and the path appears in `result.skippedPaths`

---

### T-010: Implement cleanupOrphanedChildLocks — symlink escape prevention
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Status**: [x] completed
**Test**: Given `repositories/org/symlinked-repo/` that resolves via `fs.realpathSync` to a path outside `projectRoot`, when `cleanupOrphanedChildLocks` runs, then the `vskill.lock` inside that symlinked repo is not deleted and a warning entry appears in `result.errors`

---

### T-011: Implement cleanupOrphanedChildLocks — umbrella root lock absent does not block child cleanup
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Status**: [x] completed
**Test**: Given an umbrella project where no `vskill.lock` exists at the project root but `repositories/org/child/vskill.lock` does (mtime older than threshold), when `cleanupOrphanedChildLocks` runs, then the child lock is still deleted and `result.removedCount === 1`

---

## US-003: Doctor Command Integration

### T-012: Add checkStaleLockfiles — detect mode warns with file paths
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] completed
**Test**: Given a project root with a `skills-lock.json` in a nested dir and an orphaned `repositories/org/child/vskill.lock` (umbrella enabled), when `checker.check(projectRoot, { fix: false })` runs, then the results include a `warn` check named "Legacy lockfiles" listing the `skills-lock.json` path, and a `warn` check named "Orphaned child lockfiles" listing the orphaned path

---

### T-013: checkStaleLockfiles — fix mode removes files and reports removed count
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03
**Status**: [x] completed
**Test**: Given a project root with one `skills-lock.json` and one orphaned child `vskill.lock`, when `checker.check(projectRoot, { fix: true })` runs, then both files are deleted on disk, both check results report the removed counts, and `check.status === 'pass'` for each

---

### T-014: checkStaleLockfiles — pass status when no stale lockfiles exist
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04
**Status**: [x] completed
**Test**: Given a clean project tree with no `skills-lock.json` and no orphaned child `vskill.lock`, when `checker.check(projectRoot, { fix: false })` runs, then both new check entries have `status === 'pass'` and `message === 'no stale lockfiles'`

---

### T-015: Wire checkStaleLockfiles into InstallationHealthChecker.check()
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [x] completed
**Test**: Given `InstallationHealthChecker.check()` is called with any project root, when the returned `CategoryResult` is inspected, then `checks` contains entries named "Legacy lockfiles" and "Orphaned child lockfiles" (confirming the wiring, independent of their status)

---

## US-004: Refresh-Plugins Cleanup Hook

### T-016: Wire cleanupLegacyLockfiles into refreshPluginsCommand before plugin install
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01
**Status**: [x] completed
**Test**: Given a project root with a `skills-lock.json` file (injected via mock), when `refreshPluginsCommand({ quiet: true })` runs with mocked plugin installers, then `cleanupLegacyLockfiles` is called before any `installPlugin` / `copyPluginSkillsToProject` call, and the `skills-lock.json` is deleted

---

### T-017: Wire cleanupOrphanedChildLocks into refreshPluginsCommand before plugin install
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02
**Status**: [x] completed
**Test**: Given an umbrella project root with an orphaned child-repo `vskill.lock` (injected via mock), when `refreshPluginsCommand({ quiet: true })` runs, then `cleanupOrphanedChildLocks` is called and the orphaned lock is deleted before plugin installation begins

---

### T-018: Verbose mode logs each removed file path during refresh
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03
**Status**: [x] completed
**Test**: Given `refreshPluginsCommand({ verbose: true })` runs and cleanup removes a `skills-lock.json` (via mock returning one removed path), when console output is captured via `vi.spyOn(console, 'log')`, then a log line containing the removed file path appears in stdout

---

### T-019: Cleanup errors during refresh are non-blocking
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed
**Test**: Given cleanup functions are mocked to throw an unexpected error, when `refreshPluginsCommand({ quiet: true })` runs, then no exception propagates out of the command, plugin installation still proceeds, and `process.exitCode` is not set to a non-zero value by the cleanup failure
