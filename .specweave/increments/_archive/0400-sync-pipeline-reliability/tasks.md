---
increment: 0400-sync-pipeline-reliability
total_tasks: 15
completed_tasks: 15
---

# Tasks: FS-400 Sync Pipeline Reliability

## US-001: Task completion triggers external sync

### T-001: Wire onTaskCompleted into production code path
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given a task is marked `[x]` in tasks.md → When the shell hook fires → Then `LifecycleHookDispatcher.onTaskCompleted()` is called within 5 seconds AND `LivingDocsSync.syncIncrement()` runs if `sync_tasks_md: true`

### T-002: Add active→ready_for_review to sync-worthy transitions
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test**: Given an increment transitions from `active` to `ready_for_review` → When `StatusChangeSyncTrigger.triggerIfNeeded()` evaluates → Then it returns true and triggers living docs + external sync

### T-003: Verify GitHub AC checkboxes update on task completion
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given increment with 3 ACs synced to GitHub issue → When task completing AC-1 is marked done → Then GitHub issue body shows AC-1 checked within 60 seconds

## US-002: Milestone lifecycle is fully automated

### T-004: Fix GitHubReconciler to read both metadata fields
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given increment with milestone in `github.milestone` but empty `externalLinks` → When `/sw:done` runs `closeCompletedIncrementIssues()` → Then milestone is found and closed

### T-005: Auto-recovery sync before closure when no sync data exists
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test**: Given increment with empty `externalLinks` AND empty `github` → When `/sw:done` runs → Then full sync fires first (creating milestone + issues) → Then closure proceeds normally

### T-006: Duplicate milestone detection on creation
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test**: Given GitHub already has milestone "FS-400: Sync Pipeline Reliability" → When sync creates milestone for FS-400 → Then existing milestone is reused (not duplicated)

## US-003: externalLinks and github fields stay consistent

### T-007: GitHubFeatureSync writes both metadata fields
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test**: Given increment syncs to GitHub → When `syncFeatureToGitHub()` completes → Then both `externalLinks.github.issues` AND `github.issues[]` contain matching data

### T-008: LivingDocsSync syncToGitHub writes both fields
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**Test**: Given living docs sync runs → When `syncToGitHub()` completes → Then both metadata fields are populated with matching milestone and issue data

### T-009: Migration utility normalizes existing metadata
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Test**: Given metadata with `github.issues[{US-001, #100}]` but `externalLinks: {}` → When `normalizeMetadata()` runs → Then `externalLinks.github.issues.US-001.issueNumber` = 100

## US-004: Sync errors surface instead of being swallowed

### T-010: LifecycleHookDispatcher reports sync failures visibly
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Test**: Given GitHub API returns 403 during sync → When `onIncrementDone()` runs → Then failure message appears in command output (not just stderr)

### T-011: /sw:done includes sync status summary
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03 | **Status**: [x] completed
**Test**: Given increment with 2 issues and 1 milestone → When `/sw:done` completes → Then output includes "GitHub: 2 issues closed, 1 milestone closed" AND sync failure does NOT block completion

## US-005: Metadata schema validation on load

### T-012: Create shared validateMetadataSchema() and enforce on create + load
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-04 | **Status**: [x] completed
**Test**: Given `MetadataManager.create()` called with `id: "0399"` (no slug) → Then it auto-expands to full slug AND initializes `externalLinks: {}`. Given `MetadataManager.load()` reads metadata with `createdAt` field → Then it renames to `created` and writes corrected file back.

### T-013: Map non-standard type values with warning
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**Test**: Given metadata with `type: "enhancement"` → When created or loaded → Then type is mapped to "feature" with warning "non-standard type 'enhancement' mapped to 'feature'"

## US-006: Stale milestone cleanup command

### T-014: Implement sync-reconcile for stale milestones
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01 | **Status**: [x] completed
**Test**: Given 5 completed increments with open milestones (all issues closed) → When `specweave sync-progress --reconcile` runs → Then all 5 milestones are closed

### T-015: Detect and resolve duplicate milestones
**User Story**: US-006 | **Satisfies ACs**: AC-US6-02, AC-US6-03 | **Status**: [x] completed
**Test**: Given FS-391 has milestones #187 (empty) and #189 (with issues) → When reconcile runs → Then #187 is closed, #189 is kept → Output: "1 duplicate milestone closed, 5 stale milestones closed"
