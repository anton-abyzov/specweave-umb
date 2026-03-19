---
increment: 0587-fix-github-sync-dedup
title: Fix GitHub Sync Duplication and Progress Comment Spam
status: completed
priority: P0
type: bugfix
created: 2026-03-19T00:00:00.000Z
---

# Fix GitHub Sync Duplication and Progress Comment Spam

## Problem Statement

The GitHub sync subsystem creates massive duplicate issues and spams identical progress comments with no actual state change. Evidence: increment FS-581 produced 40 GitHub issues in 38 seconds for only 6 user stories (34 excess duplicates). Issue #1613 received 19 identical comments all reporting "0/5 ACs, 9/10 tasks" with zero progress change. A previous fix attempt (0576-fix-duplicate-github-sync) was completed but insufficient -- the root causes were not fully addressed.

## Goals

- Eliminate duplicate GitHub issue creation during sync operations
- Prevent identical progress comments from being posted when no state has changed
- Reduce unnecessary GitHub API calls for no-op edits
- Coordinate the four independent sync trigger paths to prevent concurrent race conditions

## User Stories

### US-001: Progress Comment Deduplication
**Project**: specweave
**As a** developer using SpecWeave's GitHub sync
**I want** progress comments to only be posted when the tracked state actually changes
**So that** GitHub issues are not spammed with identical status updates

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a GitHub issue with an existing progress comment containing `<!-- sw-progress:3/5 -->`, when sync runs and progress is still 3/5 ACs complete, then no new comment is posted
- [x] **AC-US1-02**: Given a GitHub issue with an existing progress comment containing `<!-- sw-progress:3/5 -->`, when sync runs and progress has changed to 4/5 ACs complete, then a new comment is posted with `<!-- sw-progress:4/5 -->` fingerprint
- [x] **AC-US1-03**: Given a GitHub issue with no prior progress comments, when sync runs for the first time, then a progress comment is posted with the correct `<!-- sw-progress:N/M -->` fingerprint
- [x] **AC-US1-04**: Given the JIRA sync already uses `sw-progress:N/M` fingerprints in `jira-ac-comment-poster.ts`, when the GitHub equivalent is implemented, then the fingerprint format and detection logic is consistent between both providers

### US-002: Duplicate Issue Prevention
**Project**: specweave
**As a** developer running GitHub sync
**I want** the sync system to prevent duplicate issue creation across concurrent processes
**So that** each user story maps to exactly one GitHub issue

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given Phase 3 post-creation verification in `duplicate-detector.ts`, when sync creates an issue, then verification runs by default without requiring `SPECWEAVE_VERIFY_DUPLICATES=1` environment variable
- [x] **AC-US2-02**: Given users who explicitly want to skip verification, when `SPECWEAVE_SKIP_VERIFY_DUPLICATES=1` is set, then Phase 3 verification is skipped
- [x] **AC-US2-03**: Given two sync processes attempting to create an issue for the same user story concurrently, when both acquire the sync lock, then only one issue is created because the file-based lock serializes access
- [x] **AC-US2-04**: Given the existing `LockManager` used by JIRA sync, when GitHub sync acquires a lock, then it uses the same `LockManager` API with a GitHub-specific lock key
- [x] **AC-US2-05**: Given the in-memory `Map<string, number>` lock in `github-feature-sync.ts`, when replaced with file-based locking, then the old in-memory lock is removed

### US-003: Unnecessary API Call Prevention
**Project**: specweave
**As a** developer using SpecWeave
**I want** the sync system to skip no-op GitHub API calls and throttle concurrent triggers
**So that** API rate limits are preserved and sync operations are efficient

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `updateUserStoryIssue()` in `github-feature-sync.ts`, when the computed issue body is identical to the current body on GitHub, then `gh issue edit` is not called
- [x] **AC-US3-02**: Given four independent trigger paths (status-change-sync-trigger, sync-progress, auto-create-external-issue, living-docs-handler), when multiple triggers fire for the same increment within a configurable window, then only the first trigger executes and subsequent triggers are deduplicated
- [x] **AC-US3-03**: Given a new `sync-throttle.ts` utility, when any trigger path initiates sync, then it passes through the throttle which uses increment ID as the deduplication key
- [x] **AC-US3-04**: Given the throttle window, when the window expires, then the next trigger for the same increment is allowed to proceed

## Out of Scope

- Refactoring the four trigger paths into a single unified sync pipeline
- JIRA sync changes (already has fingerprint dedup working correctly)
- Azure DevOps sync changes
- Retry logic for failed GitHub API calls
- Historical cleanup of already-created duplicate issues or comments

## Technical Notes

### Dependencies
- `LockManager` (existing, used by JIRA sync) for cross-process file locking
- `jira-ac-comment-poster.ts` as reference implementation for fingerprint pattern
- `gh` CLI for GitHub API operations

### Constraints
- Must not break existing JIRA sync behavior
- File locks must be compatible with the existing `.specweave/state/` lock directory
- Throttle window must be configurable but have a sensible default (e.g., 5 seconds)

### Architecture Decisions
- Port JIRA's proven `sw-progress:N/M` HTML comment fingerprint pattern rather than inventing a new dedup mechanism
- Invert the environment variable semantics: opt-out (`SPECWEAVE_SKIP_VERIFY_DUPLICATES`) instead of opt-in (`SPECWEAVE_VERIFY_DUPLICATES`)
- Centralize throttling in a shared utility rather than adding dedup logic to each trigger independently

### Key Source Files
- `github-ac-comment-poster.ts` (lines 49-123): Comment posting without dedup
- `duplicate-detector.ts` (line 489): Phase 3 verification disabled by default
- `github-feature-sync.ts` (lines 60-63): In-memory lock
- `github-feature-sync.ts` (lines 1021-1031): Unconditional `gh issue edit`
- `status-change-sync-trigger.ts`, `sync-progress.ts`, `auto-create-external-issue.ts`, `living-docs-handler.sh`: Four uncoordinated trigger paths

## Non-Functional Requirements

- **Performance**: Sync operations for unchanged state must complete without any GitHub API calls (zero network round-trips for no-op syncs)
- **Reliability**: No duplicate issues created even under concurrent execution from multiple terminal sessions
- **Compatibility**: Existing `SPECWEAVE_VERIFY_DUPLICATES=1` users are unaffected (verification now on by default, their env var becomes a no-op)

## Edge Cases

- First sync for a new increment (no prior fingerprint): Posts comment and sets initial fingerprint
- Sync runs while a previous sync is still in-flight: File lock serializes access, second process waits
- Lock file left behind after process crash: LockManager's existing stale lock detection handles cleanup
- GitHub API returns 404 for deleted issue during body diff check: Sync treats as "issue needs recreation" rather than crashing
- Multiple ACs complete simultaneously between syncs: Single comment posted with latest state, not one per AC change

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| File lock contention under high concurrency degrades sync throughput | 0.3 | 4 | 1.2 | Lock timeout with fallback to skip-and-retry on next cycle |
| Inverting env var breaks CI pipelines that set SPECWEAVE_VERIFY_DUPLICATES=1 | 0.2 | 3 | 0.6 | Old env var treated as no-op (already default), documented in changelog |
| Throttle window too aggressive causes missed legitimate sync updates | 0.2 | 5 | 1.0 | Configurable window with conservative default; throttle only deduplicates identical increment+trigger pairs |
| GitHub API body comparison fails on whitespace/formatting differences | 0.4 | 3 | 1.2 | Normalize body content before comparison (trim, collapse whitespace) |

## Success Metrics

- Zero duplicate GitHub issues created per sync operation (down from 5-6x duplication)
- Zero identical consecutive progress comments on any GitHub issue (down from 19 identical comments)
- GitHub API call count reduced by at least 80% for no-change sync cycles
- No regressions in JIRA sync behavior
