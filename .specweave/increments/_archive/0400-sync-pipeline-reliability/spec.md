---
project: specweave
status: completed
---
# FS-400: Sync Pipeline Reliability

## Problem Statement

The GitHub sync pipeline has multiple structural bugs causing increments to go unsynced, milestones to remain open after completion, and task-level progress to never reach external tools. Five specific failures were identified through audit of increments 0390-0399.

## Scope

**Target repo**: `repositories/anton-abyzov/specweave/` (core CLI)

## User Stories

### US-001: Task completion triggers external sync
**As a** developer using SpecWeave
**I want** task completions to automatically sync progress to GitHub
**So that** GitHub issues reflect real-time AC checkbox progress without manual `/sw:progress-sync`

**Acceptance Criteria**:
- [x] AC-US1-01: When a task is marked complete (via Edit to tasks.md), the shell hook or MetadataManager calls `LifecycleHookDispatcher.onTaskCompleted()` within 5 seconds
- [x] AC-US1-02: `onTaskCompleted()` triggers `LivingDocsSync.syncIncrement()` when `post_task_completion.sync_tasks_md: true`
- [x] AC-US1-03: GitHub issue AC checkboxes update automatically after each task completion (not just on `/sw:done`)
- [x] AC-US1-04: The `active → ready_for_review` status transition is added to `StatusChangeSyncTrigger.isSyncWorthy()` list

### US-002: Milestone lifecycle is fully automated
**As a** developer
**I want** GitHub milestones to be created on increment planning and closed on increment completion
**So that** milestones accurately reflect increment status without manual intervention

**Acceptance Criteria**:
- [x] AC-US2-01: `GitHubReconciler.closeCompletedIncrementIssues()` reads milestone numbers from BOTH `externalLinks.github.milestone` AND `github.milestone` fields
- [x] AC-US2-02: When `/sw:done` runs and `externalLinks` is empty but `github` field has data, the reconciler still finds and closes the milestone
- [x] AC-US2-03: When `/sw:done` runs and neither field has a milestone, a full sync is triggered BEFORE attempting closure (auto-recovery)
- [x] AC-US2-04: Duplicate milestone detection — before creating a new milestone, check if one with the same title already exists

### US-003: externalLinks and github fields stay consistent
**As a** developer
**I want** the sync pipeline to write to both `externalLinks` and `github` metadata fields
**So that** all consumers (reconciler, progress-sync, living docs) can find sync data regardless of which field they read

**Acceptance Criteria**:
- [x] AC-US3-01: `GitHubFeatureSync.syncFeatureToGitHub()` writes issue numbers and milestone to BOTH `externalLinks.github` AND `github` fields in metadata.json
- [x] AC-US3-02: `syncToGitHub()` in LivingDocsSync writes to both fields
- [x] AC-US3-03: A migration utility normalizes existing metadata — if `github` has data but `externalLinks` is empty, populate `externalLinks` from `github`

### US-004: Sync errors surface instead of being swallowed
**As a** developer
**I want** sync failures to be reported visibly
**So that** I know when GitHub sync failed and can take action

**Acceptance Criteria**:
- [x] AC-US4-01: `LifecycleHookDispatcher` logs sync failures as warnings (not just stderr) and includes them in the command output
- [x] AC-US4-02: `/sw:done` reports sync status in its summary output (e.g., "GitHub: 3 issues closed, milestone closed" or "GitHub sync failed: <reason>")
- [x] AC-US4-03: Sync failures do NOT block `/sw:done` from completing (non-fatal), but the failure is clearly communicated

### US-005: Metadata schema validation enforced globally
**As a** developer
**I want** increment metadata schema enforced at both creation and load time
**So that** malformed metadata never gets written and is caught immediately if introduced manually

**Acceptance Criteria**:
- [x] AC-US5-01: `MetadataManager.create()` enforces required fields: `id` (must be full slug), `status`, `type` (from standard vocab), `created` (not `createdAt`), `externalLinks` (initialized to `{}`)
- [x] AC-US5-02: `MetadataManager.load()` validates and auto-corrects: missing `externalLinks` → adds `{}`, `createdAt` → renamed to `created`, short `id` → expanded to full slug
- [x] AC-US5-03: Non-standard `type` values (e.g., "enhancement") are mapped to the closest standard value (e.g., "feature") with a warning
- [x] AC-US5-04: A shared `validateMetadataSchema()` function is used by both create and load paths — single source of truth for the schema contract

### US-006: Stale milestone cleanup command
**As a** developer
**I want** a command to reconcile stale GitHub milestones
**So that** milestones for completed increments are closed without manual `gh api` calls

**Acceptance Criteria**:
- [x] AC-US6-01: `specweave sync-reconcile` (or added to existing `sync-progress`) scans all completed increments and closes any open milestones whose issues are all closed
- [x] AC-US6-02: Duplicate milestones (same FS-XXX title, different milestone numbers) are detected — the empty one is closed
- [x] AC-US6-03: The command outputs a summary of actions taken (N milestones closed, N duplicates resolved)
