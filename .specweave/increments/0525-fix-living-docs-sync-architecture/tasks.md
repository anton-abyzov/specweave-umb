# Tasks: Fix Living Docs Sync Architecture

---

## US-001: Fix specweave complete silent failures

### T-001: Convert external drift >168h from error to warning in completion-validator.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01
**Status**: [x] Completed
**Test**: Given `completion-validator.ts` lines 153-162 where `hoursSince > 168` pushes to `errors` → When `IncrementCompletionValidator.validateCompletion()` runs for an increment whose last sync was >168 hours ago → Then the drift appears in `result.warnings` (not `result.errors`) and `result.isValid` remains `true`

---

### T-002: Write unit tests for drift warning behavior (TDD Red → Green)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01
**Status**: [x] Completed
**Test**: Given a new test file `src/core/increment/__tests__/completion-validator.test.ts` with a mock `ExternalToolDriftDetector` that returns `{ externalToolsConfigured: true, hasDrift: true, hoursSinceSync: 200 }` → When `validateCompletion()` is called → Then `isValid === true` and `warnings` contains the drift message and `errors` is empty

---

### T-003: Ensure transition failures always write to stderr under --silent flag
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02
**Status**: [x] Completed
**Test**: Given `completeIncrement()` in `status-commands.ts` where `silent = true` and `MetadataManager.updateStatus()` throws during an intermediate transition → When the failure block at lines 273-276 executes → Then `process.stderr.write` is called with a diagnostic message containing the increment ID and error text, even though `log()` is suppressed

---

### T-004: Remove pre-completion sync block from completeIncrement()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03
**Status**: [x] Completed
**Test**: Given `completeIncrement()` in `status-commands.ts` with the pre-completion sync block (lines 306-319) removed → When `completeIncrement()` runs end-to-end with a spy on `LivingDocsSync.prototype.syncIncrement` → Then `syncIncrement` is called exactly once (from `LifecycleHookDispatcher.onIncrementDone`) and not from inside `completeIncrement()` directly

---

### T-005: Write integration test verifying single sync invocation per completion
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03
**Status**: [x] Completed
**Test**: Given a test that mocks both `LivingDocsSync` and `LifecycleHookDispatcher.onIncrementDone` with call counters → When `completeIncrement()` runs with `skipValidation: true` on a valid increment → Then `LivingDocsSync.syncIncrement` call count across both `completeIncrement` and `onIncrementDone` totals exactly 1

---

## US-002: Remove zombie-prone background sync from hook

### T-006: Add stale sync-*.lock cleanup at hook entry
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03
**Status**: [x] Completed
**Test**: Given `.claude/hooks/close-completed-issues.sh` with a new block before Section 1 that runs `find "$PROJECT_ROOT/.specweave/state/" -name "sync-*.lock" -mmin +60 -delete 2>/dev/null` → When the hook script is inspected with `grep` → Then the `find` command for stale lock cleanup appears before any `gh` issue-close commands in the file

---

### T-007: Add .env sourcing for GITHUB_TOKEN / GH_TOKEN in Section 1
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02
**Status**: [x] Completed
**Test**: Given `.claude/hooks/close-completed-issues.sh` with a block that sources `$PROJECT_ROOT/.env`, extracts `GITHUB_TOKEN`, and exports it as `GH_TOKEN` before the `gh issue close` call → When the hook runs with a `.env` file containing `GITHUB_TOKEN=abc123` → Then `GH_TOKEN` is set to `abc123` before any `gh` CLI call and missing `.env` is handled gracefully without aborting the script

---

### T-008: Remove Section 2 (background sync) entirely from hook
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Status**: [x] Completed
**Test**: Given the updated `.claude/hooks/close-completed-issues.sh` → When the file is inspected → Then it contains no `&` backgrounding operators and no `disown` calls and the Section 2 comment block (`=== Section 2: Living docs sync`) is absent

---

## US-003: Add living docs sync skip mechanism

### T-009: Add skipLivingDocsSync field to IncrementMetadataV2 interface
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03
**Status**: [x] Completed
**Test**: Given `src/core/types/increment-metadata.ts` with `skipLivingDocsSync?: boolean` added to `IncrementMetadataV2` → When the TypeScript compiler runs (`tsc --noEmit`) → Then it exits with code 0 and the field is accessible on objects typed as `IncrementMetadataV2`

---

### T-010: Wire autoSyncOnCompletion config flag into onIncrementDone()
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01
**Status**: [x] Completed
**Test**: Given `LifecycleHookDispatcher.onIncrementDone()` with a new early-return block that reads `config.sync?.settings?.autoSyncOnCompletion` and returns an empty result when it is `false` → When a unit test calls `onIncrementDone()` with `_bypassTestGuard: true` and a mock `ConfigManager` returning `{ sync: { settings: { autoSyncOnCompletion: false } } }` → Then `LivingDocsSync.syncIncrement` is never called and the returned `result.syncErrors` and `result.syncSuccess` are both empty arrays

---

### T-011: Wire per-increment skipLivingDocsSync flag into onIncrementDone()
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02
**Status**: [x] Completed
**Test**: Given `LifecycleHookDispatcher.onIncrementDone()` with a per-increment check added after the global `autoSyncOnCompletion` check that reads `metadata.skipLivingDocsSync` → When a unit test calls `onIncrementDone()` with `_bypassTestGuard: true`, global `autoSyncOnCompletion` is `true`, and a mock `MetadataManager.read()` returns `{ skipLivingDocsSync: true }` → Then `LivingDocsSync.syncIncrement` is never called and the returned result has empty sync arrays

---

### T-012: Write unit tests for both sync skip paths in onIncrementDone
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] Completed
**Test**: Given a test file `src/core/hooks/__tests__/LifecycleHookDispatcher.test.ts` with four test cases: (1) global skip, (2) per-increment skip, (3) both flags active, (4) neither flag set (normal path) → When each test runs with `_bypassTestGuard: true` and a spy on `LivingDocsSync.prototype.syncIncrement` → Then cases 1-3 confirm `syncIncrement` call count is 0 while case 4 confirms call count is 1
