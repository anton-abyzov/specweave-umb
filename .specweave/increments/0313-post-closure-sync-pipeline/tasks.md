---
increment: 0313-post-closure-sync-pipeline
total_tasks: 7
completed_tasks: 0
---

# Tasks: Fix post-closure sync pipeline

## Phase 1: TDD RED - Write failing tests

### T-001: Write tests for sync_to_github_project handler in LifecycleHookDispatcher
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-04, AC-US3-05 | **Status**: [ ] not started
**Test**: Given hooks config with `sync_to_github_project: true` -> When `onIncrementDone()` is called -> Then the GitHub feature sync module is invoked with the correct feature ID

**Implementation Details**:
- Add mock for GitHub feature sync module (`../../sync/github-project-sync.js` or equivalent)
- Add mock for feature ID resolver
- TC-017: dispatches GitHub Project sync when `sync_to_github_project=true`
- TC-018: skips GitHub Project sync when `sync_to_github_project=false`
- TC-019: GitHub Project sync failure does not block other hooks (error-isolated)
- TC-020: feature ID is resolved from metadata and passed to sync

**File**: `tests/unit/core/hooks/lifecycle-hook-dispatcher.test.ts`
**Dependencies**: None

---

### T-002: Write tests for awaited hook dispatch in completeIncrement
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [ ] not started
**Test**: Given a valid increment -> When `completeIncrement()` is called -> Then `LifecycleHookDispatcher.onIncrementDone()` is awaited (not fire-and-forget) and errors are logged

**Implementation Details**:
- Verify hooks are awaited (not void IIFE)
- Verify hook errors are caught and logged but do not fail completion
- Verify completion returns true even when hooks error

**File**: `tests/unit/core/increment/status-commands-complete.test.ts` (or existing test file)
**Dependencies**: None

---

## Phase 2: TDD GREEN - Implement changes

### T-003: Add sync_to_github_project handler to LifecycleHookDispatcher.onIncrementDone()
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [ ] not started
**Test**: Given T-001 tests pass -> When handler is implemented -> Then all TC-017 through TC-020 go GREEN

**Implementation Details**:
- In `onIncrementDone()`, add a new block checking `doneConfig.sync_to_github_project`
- Implement `resolveFeatureId(projectRoot, incrementId)` private helper:
  1. Read metadata.json `feature_id` field
  2. Fallback: parse spec.md frontmatter for `feature_id`
  3. Fallback: derive from increment number `FS-{NNNN}`
- Use dynamic import for GitHub sync module (plugin may not be installed)
- Wrap in try/catch, log errors via `logError()`
- Add to the parallel/sequential execution flow alongside existing hooks

**File**: `src/core/hooks/LifecycleHookDispatcher.ts`
**Dependencies**: T-001

---

### T-004: Change fire-and-forget to awaited hook dispatch in completeIncrement()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [ ] not started
**Test**: Given T-002 tests exist -> When void IIFE is replaced with await -> Then T-002 tests go GREEN

**Implementation Details**:
- Replace the `void (async () => { ... })()` pattern with direct `try { await ... } catch { log warning }`
- Ensure hook errors do not change the return value (still returns true on completion success)
- Log hook errors as warnings with retry guidance

**File**: `src/core/increment/status-commands.ts`
**Dependencies**: T-002

---

### T-005: Update done skill Step 8 to use CLI completion path
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] not started
**Test**: Given done SKILL.md -> When Step 8 is read -> Then it instructs to run `specweave complete <id>` instead of direct metadata.json edit

**Implementation Details**:
- Replace Step 8 content:
  - Old: "Update metadata.json status to `completed`, set completion date"
  - New: "Run: `specweave complete <id> --skip-validation --silent`"
- Add explanation that validation was already done in Steps 6-7
- Update Step 9 to note that sync is now handled by the CLI completion path
- Keep marker file creation/removal around the CLI call

**File**: `plugins/specweave/skills/done/SKILL.md`
**Dependencies**: T-003, T-004

---

## Phase 3: Create missing skill + cleanup

### T-006: Create sw:sync-docs skill
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [ ] not started
**Test**: Given skill file exists at `plugins/specweave/skills/sync-docs/SKILL.md` -> When loaded by Claude Code -> Then it appears as `/sw:sync-docs` command

**Implementation Details**:
- Create `plugins/specweave/skills/sync-docs/SKILL.md`
- Frontmatter: description and argument-hint
- Skill body:
  1. Accept increment ID argument (required)
  2. Detect "review" mode from args
  3. Instruct LLM to use compiled `LivingDocsSync` from dist
  4. Report sync results (files created/updated count, feature ID)
  5. In review mode, run with `dryRun: true`
- Error handling: catch and report sync failures

**File**: `plugins/specweave/skills/sync-docs/SKILL.md` (new)
**Dependencies**: None

---

### T-007: Update done skill Step 9/10 to reflect unified pipeline
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [ ] not started
**Test**: Given done SKILL.md -> When Steps 9-10 are read -> Then they correctly describe sync as part of CLI completion and show result summary guidance

**Implementation Details**:
- Step 9: Update to note that sync operations fire automatically via `completeIncrement()` hooks
- Step 9: Add guidance to display sync result summary table
- Step 10: Update `sw:sync-docs` invocation to use the now-existing skill
- Add retry guidance: "If any sync failed, run `/sw:progress-sync` to retry"

**File**: `plugins/specweave/skills/done/SKILL.md`
**Dependencies**: T-005, T-006
