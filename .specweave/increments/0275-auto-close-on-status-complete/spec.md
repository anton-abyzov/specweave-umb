---
increment: 0275-auto-close-on-status-complete
title: "Auto-Close External Issues on status:complete Sync"
type: bug
priority: P1
status: planned
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Bug Fix: Auto-Close External Issues on status:complete Sync

## Overview

When `/sw:progress-sync` or the feature-sync pipeline pushes `status:complete` labels to GitHub issues, the issues remain Open. Example: GitHub issue #1198 has `status:complete` label but state is still OPEN.

**Root Cause Analysis**:

There are two independent sync paths that can mark a user story as complete:

1. **Feature Sync Path** (`github-feature-sync.ts` -> `updateUserStoryIssue()`): This path DOES close issues when `completion.overallComplete` is true AND adds `status:complete` label via `updateStatusLabels()`. However, `updateStatusLabels()` only manages labels -- it does not close the issue. The closing happens in `updateUserStoryIssue()` separately. **Bug**: If `updateStatusLabels()` runs but `updateUserStoryIssue()` fails or is not reached (e.g., US has no ACs/tasks but frontmatter says complete), the label is applied but the issue is not closed.

2. **Progress Sync Path** (`sync-progress.ts` -> `SyncCoordinator.syncACCheckboxesToGitHub()`): This path updates AC checkboxes in GitHub issue bodies but NEVER closes the issue. It only calls `closeGitHubIssuesForUserStories()` during increment closure via `syncIncrementClosure()`, which only fires when the increment itself transitions to `completed` status.

3. **Label-Only Path** (`user-story-issue-builder.ts` `computeLabels()`): When building issue content, labels include `status:complete` based on frontmatter status, but the issue create/update path does not check if the issue should also be closed at that point.

The fix: `updateStatusLabels()` in `github-feature-sync.ts` should also close the issue when the new label is `status:complete` and the issue is still open. Similarly, the JIRA and ADO progress sync should close/transition issues when all ACs are complete, not just on increment closure.

## User Stories

### US-001: GitHub Issues Auto-Close When status:complete Label Applied (P1)
**Project**: specweave

**As a** developer using SpecWeave with GitHub sync
**I want** GitHub issues to be automatically closed when progress-sync determines the user story is complete
**So that** issues with `status:complete` label are not left in OPEN state (like issue #1198)

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `updateStatusLabels()` in `github-feature-sync.ts` closes the issue via `gh issue close` when the new status label is `status:complete` and the issue is currently OPEN
- [ ] **AC-US1-02**: If the issue is already CLOSED, `updateStatusLabels()` does not attempt a redundant close operation
- [ ] **AC-US1-03**: A completion comment is posted before closing (consistent with existing closure flows)
- [ ] **AC-US1-04**: Unit tests verify that `updateStatusLabels()` with `overallComplete=true` triggers issue closure on an OPEN issue
- [ ] **AC-US1-05**: Unit tests verify that `updateStatusLabels()` with `overallComplete=true` skips closure on an already-CLOSED issue

---

### US-002: JIRA Issues Auto-Transition on AC Completion in Progress Sync (P2)
**Project**: specweave

**As a** developer using SpecWeave with JIRA sync
**I want** JIRA issues to be transitioned to Done when progress-sync determines all ACs are complete
**So that** I do not have to wait for increment closure to see JIRA issues resolved

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `syncJiraACProgress()` in `ac-progress-sync.ts` already transitions to Done when `isAllComplete()` returns true -- verify this works correctly with an integration-level test scenario
- [ ] **AC-US2-02**: The progress-sync CLI (`sync-progress.ts`) invokes the JIRA AC sync path (not just GitHub checkbox sync) when JIRA is configured

---

### US-003: ADO Work Items Auto-Close on AC Completion in Progress Sync (P2)
**Project**: specweave

**As a** developer using SpecWeave with Azure DevOps sync
**I want** ADO work items to be transitioned to Closed when progress-sync determines all ACs are complete
**So that** ADO work items reflect the actual completion state without waiting for increment closure

**Acceptance Criteria**:
- [ ] **AC-US3-01**: `syncAdoACProgress()` in `ac-progress-sync.ts` already transitions to Closed when `isAllComplete()` returns true -- verify this works correctly with an integration-level test scenario
- [ ] **AC-US3-02**: The progress-sync CLI (`sync-progress.ts`) invokes the ADO AC sync path when ADO is configured

---

### US-004: Existing Closed Issues Not Reopened by Label Sync (P1)
**Project**: specweave

**As a** developer
**I want** the auto-close fix to be idempotent and safe
**So that** already-closed issues are not reopened or double-closed

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Running progress-sync on an already-closed issue with `status:complete` label is a no-op (does not post duplicate comments or attempt re-close)
- [ ] **AC-US4-02**: The fix does not interfere with the existing `updateUserStoryIssue()` closure path in `github-feature-sync.ts` (no double-close race)
- [ ] **AC-US4-03**: Unit tests verify idempotency: calling `updateStatusLabels()` twice with `overallComplete=true` on a CLOSED issue produces no side effects

## Functional Requirements

### FR-001: Close Issue in updateStatusLabels When Complete
In `github-feature-sync.ts`, after applying `status:complete` label, check if the issue is OPEN. If so, post a completion comment and close it via `gh issue close`. This makes the label sync and issue closure atomic within the same method call.

### FR-002: Progress-Sync CLI Should Invoke Full AC Sync (Not Just GitHub Checkboxes)
The `sync-progress.ts` Step 5 currently only calls `syncCoordinator.syncACCheckboxesToGitHub()` which updates checkboxes but does not close issues. It should also invoke the AC-level progress sync via `syncACProgressToProviders()` from `ac-progress-sync.ts` which handles JIRA transitions and ADO state changes when all ACs are complete.

### FR-003: Idempotent Close Operations
All close operations must check current issue state before attempting closure. If already closed, skip silently. No duplicate comments on re-runs.

## Success Criteria

- GitHub issue #1198 (and similar) would be closed when progress-sync runs with status:complete
- No regressions: manual closure via `/sw:done` still works
- No duplicate close comments on repeated progress-sync runs
- JIRA and ADO transitions work during progress-sync (not just on increment closure)

## Out of Scope

- Changing the status label naming convention (status:complete vs status:completed)
- Adding new label types
- Modifying the increment closure flow (`syncIncrementClosure()` / `closeGitHubIssuesForUserStories()`)
- Adding new CLI flags to progress-sync

## Dependencies

- `plugins/specweave-github/lib/github-feature-sync.ts` (updateStatusLabels method)
- `src/core/ac-progress-sync.ts` (syncACProgressToProviders, JIRA/ADO providers)
- `src/cli/commands/sync-progress.ts` (progress-sync CLI orchestration)
- `src/sync/sync-coordinator.ts` (syncACCheckboxesToGitHub)
