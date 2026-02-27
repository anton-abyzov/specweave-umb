# Tasks: Fix External Work Item Creation

**Increment**: 0304-fix-external-work-item-creation
**Status**: In Progress
**Created**: 2026-02-21

---

## User Story: US-001 - Guard external issue creation against template content

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, 2 completed

### T-001: Add template guard to ExternalIssueAutoCreator

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] completed
**Priority**: P0
**Estimated Effort**: 1 hour

**Description**: Import `isTemplateFile` from `template-creator.ts` and add a check in `createForIncrement()` before `loadIncrementInfo()`. If spec.md is still a template, return early with `skipped: true`.

**Implementation Steps**:
- [x] Add import for `isTemplateFile` from `../../core/increment/template-creator.js`
- [x] After `detectProvider()` check, add template guard: `isTemplateFile(specPath)` returns early
- [x] Log a clear message explaining the skip

**Test Plan** (BDD):
- **Given** an increment with a template spec.md containing `[Story Title]` placeholders
- **When** `createForIncrement()` is called
- **Then** it returns `{ skipped: true, skipReason: 'spec.md is still a template...' }` and makes no API calls

**Files Affected**:
- `repositories/anton-abyzov/specweave/src/sync/external-issue-auto-creator.ts` (modify)

**Dependencies**: None

---

### T-002: Add unit tests for template guard

**User Story**: US-001
**Satisfies ACs**: AC-US1-03, AC-US1-04
**Status**: [x] completed
**Priority**: P0
**Estimated Effort**: 1 hour

**Description**: Add unit tests to verify the template guard prevents external issue creation for template specs, and allows it for real specs.

**Implementation Steps**:
- [x] Create or update test file for `ExternalIssueAutoCreator`
- [x] Test: template spec.md -> skipped, no API calls
- [x] Test: real spec.md -> proceeds normally (mock API calls)

**Test Plan** (BDD):
- **Given** a spec.md with template markers like `[Story Title]`, `[user type]`, `{{RESOLVED_PROJECT}}`
- **When** `createForIncrement()` is called
- **Then** result has `skipped: true` and skipReason mentions "template"

- **Given** a spec.md with real user stories (no template markers)
- **When** `createForIncrement()` is called
- **Then** result proceeds to provider detection and issue creation

**Files Affected**:
- `repositories/anton-abyzov/specweave/tests/unit/core/universal-auto-create.test.ts` (modify)

**Dependencies**: T-001

---

## User Story: US-002 - Add living docs sync to post-increment-planning hook

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 3 total, 3 completed

### T-003: Extend HookConfiguration type and JSON schema

**User Story**: US-002
**Satisfies ACs**: AC-US2-01
**Status**: [x] completed
**Priority**: P1
**Estimated Effort**: 30 minutes

**Description**: Add `sync_living_docs?: boolean` to the `post_increment_planning` section of `HookConfiguration` type and update the JSON schema.

**Implementation Steps**:
- [x] Add `sync_living_docs?: boolean` to `HookConfiguration.post_increment_planning` in `src/core/config/types.ts`
- [x] Add `sync_living_docs` property to `post_increment_planning` in `src/core/schemas/specweave-config.schema.json`

**Test Plan** (BDD):
- **Given** the updated type definition
- **When** TypeScript compiles
- **Then** `hooks.post_increment_planning.sync_living_docs` is a valid optional boolean field

**Files Affected**:
- `repositories/anton-abyzov/specweave/src/core/config/types.ts` (modify)
- `repositories/anton-abyzov/specweave/src/core/schemas/specweave-config.schema.json` (modify)

**Dependencies**: None

---

### T-004: Wire living docs sync in LifecycleHookDispatcher.onIncrementPlanned

**User Story**: US-002
**Satisfies ACs**: AC-US2-02, AC-US2-03
**Status**: [x] completed
**Priority**: P1
**Estimated Effort**: 1 hour

**Description**: Update `onIncrementPlanned()` to:
1. Check `sync_living_docs` flag and call `LivingDocsSync.syncIncrement()` first
2. Then proceed with existing `auto_create_github_issue` logic

**Implementation Steps**:
- [x] Refactor `onIncrementPlanned()` to read the full `post_increment_planning` config
- [x] Add living docs sync before external issue creation
- [x] Ensure errors in living docs sync don't prevent external issue creation

**Test Plan** (BDD):
- **Given** config with `post_increment_planning.sync_living_docs: true`
- **When** `onIncrementPlanned()` is called
- **Then** `LivingDocsSync.syncIncrement()` is called before `autoCreateExternalIssue()`

**Files Affected**:
- `repositories/anton-abyzov/specweave/src/core/hooks/LifecycleHookDispatcher.ts` (modify)

**Dependencies**: T-003

---

### T-005: Update config templates and defaults

**User Story**: US-002
**Satisfies ACs**: AC-US2-04
**Status**: [x] completed
**Priority**: P1
**Estimated Effort**: 30 minutes

**Description**: Add `sync_living_docs: true` to all config template locations so new projects get the correct defaults.

**Implementation Steps**:
- [x] Update `src/templates/config.json.template`
- [x] Update `src/cli/helpers/init/directory-structure.ts`
- [x] Update `src/cli/helpers/issue-tracker/sync-config-writer.ts`
- [x] Update `src/cli/helpers/init/smart-defaults.ts`

**Test Plan** (BDD):
- **Given** a new project initialized with `specweave init`
- **When** config.json is generated
- **Then** `hooks.post_increment_planning.sync_living_docs` is `true`

**Files Affected**:
- `repositories/anton-abyzov/specweave/src/templates/config.json.template` (modify)
- `repositories/anton-abyzov/specweave/src/cli/helpers/init/directory-structure.ts` (modify)
- `repositories/anton-abyzov/specweave/src/cli/helpers/issue-tracker/sync-config-writer.ts` (modify)
- `repositories/anton-abyzov/specweave/src/cli/helpers/init/smart-defaults.ts` (modify)

**Dependencies**: T-003

---

## User Story: US-003 - Update test coverage

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 2 total, 2 completed

### T-006: Add unit tests for LifecycleHookDispatcher living docs sync

**User Story**: US-003
**Satisfies ACs**: AC-US3-02, AC-US3-03
**Status**: [x] completed
**Priority**: P1
**Estimated Effort**: 1 hour

**Description**: Add tests to the existing `lifecycle-hook-dispatcher.test.ts` to verify living docs sync integration.

**Implementation Steps**:
- [x] Add test: `onIncrementPlanned` calls `LivingDocsSync.syncIncrement` when `sync_living_docs: true`
- [x] Add test: `onIncrementPlanned` calls living docs sync BEFORE external issue creation
- [x] Add test: `onIncrementPlanned` still works when `sync_living_docs: false` (backward compat)

**Test Plan** (BDD):
- **Given** config with `sync_living_docs: true` and `auto_create_github_issue: true`
- **When** `onIncrementPlanned()` is called
- **Then** `LivingDocsSync.syncIncrement()` is called first, then `autoCreateExternalIssue()` second

**Files Affected**:
- `repositories/anton-abyzov/specweave/tests/unit/core/hooks/lifecycle-hook-dispatcher.test.ts` (modify)

**Dependencies**: T-004

---

### T-007: Run full test suite and verify no regressions

**User Story**: US-003
**Satisfies ACs**: AC-US3-04
**Status**: [x] completed
**Priority**: P1
**Estimated Effort**: 30 minutes

**Description**: Run the complete test suite to verify all existing tests pass alongside the new changes.

**Implementation Steps**:
- [x] Run `npm test` in the specweave repository
- [x] Fix any failures
- [x] Verify all new tests pass

**Test Plan** (BDD):
- **Given** all changes from T-001 through T-006 are applied
- **When** `npm test` is run
- **Then** all tests pass with no regressions

**Files Affected**: None (verification only)

**Dependencies**: T-001, T-002, T-004, T-005, T-006

---

## Progress Tracking

**By User Story**:
- US-001: 2/2 tasks completed (100%)
- US-002: 3/3 tasks completed (100%)
- US-003: 2/2 tasks completed (100%)

**Overall**: 7/7 tasks completed (100%)
