---
increment: 0525-fix-living-docs-sync-architecture
title: Fix Living Docs Sync Architecture
type: bug
priority: P1
status: completed
created: 2026-03-14T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix Living Docs Sync Architecture

## Problem Statement

The PostToolUse hook (`close-completed-issues.sh`) spawns `specweave sync-living-docs` via `& disown` -- a fire-and-forget pattern that creates zombie processes consuming 5000 GitHub API calls/hour. This workaround exists because `specweave complete` silently exits with code 1 when external drift exceeds 168 hours. The fix must make the primary completion path reliable and remove the background sync workaround entirely.

Root causes:
1. `& disown` has no timeout, no PID management, and lock files leak on SIGKILL
2. Triple sync: `completeIncrement()` pre-sync + `onIncrementDone()` sync + PostToolUse hook background sync
3. External drift >7 days BLOCKS completion instead of warning
4. `autoSyncOnCompletion` config flag exists but is not wired into `onIncrementDone()`
5. Hook Section 1 uses `gh` CLI with broken keyring instead of GITHUB_TOKEN from .env

## Goals

- Eliminate zombie background processes from the sync architecture
- Make `specweave complete` succeed even when external sync state has drifted
- Reduce sync calls to exactly one per completion (via `onIncrementDone()` only)
- Provide opt-out mechanisms for living docs sync (global and per-increment)

## User Stories

### US-001: Fix specweave complete silent failures
**Project**: specweave

**As a** developer using SpecWeave
**I want** `specweave complete` to succeed even when external issues have drifted
**So that** completion is not blocked by stale external state

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given an increment with external drift >168 hours, when `specweave complete` runs, then it logs a warning to stderr and exits with code 0
- [x] **AC-US1-02**: Given a transition failure during completion with `--silent` flag, when the failure occurs, then diagnostic details are written to stderr (not suppressed)
- [x] **AC-US1-03**: Given a normal `specweave complete` invocation, when completion succeeds, then `LivingDocsSync.syncIncrement` is called exactly once (in `onIncrementDone`), not in `completeIncrement` pre-sync

---

### US-002: Remove zombie-prone background sync from hook
**Project**: specweave-umb

**As a** developer running SpecWeave in automated environments
**I want** the PostToolUse hook to not spawn background processes
**So that** zombie sync processes do not exhaust GitHub API rate limits

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the `close-completed-issues.sh` hook file, when inspected, then it contains no `&` backgrounding operators and no `disown` calls for sync operations
- [x] **AC-US2-02**: Given the hook runs in an environment with a `.env` file at PROJECT_ROOT containing GITHUB_TOKEN, when the hook executes gh CLI commands, then it sources GITHUB_TOKEN from `.env` and exports it as GH_TOKEN
- [x] **AC-US2-03**: Given stale `sync-*.lock` files (>60 minutes old) exist in `.specweave/state/`, when the hook starts execution, then those stale lock files are deleted before any other operations

---

### US-003: Add living docs sync skip mechanism
**Project**: specweave

**As a** developer working on increments that do not need external sync
**I want** to disable living docs sync globally or per-increment
**So that** unnecessary API calls and sync delays are avoided

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `autoSyncOnCompletion: false` in `.specweave/config.json`, when `onIncrementDone` fires, then living docs sync is skipped entirely
- [x] **AC-US3-02**: Given `skipLivingDocsSync: true` in an increment's `metadata.json` and `autoSyncOnCompletion` is not false globally, when `onIncrementDone` fires for that increment, then living docs sync is skipped for that increment only
- [x] **AC-US3-03**: Given the SpecWeave TypeScript codebase, when the `IncrementMetadata` interface is inspected, then it includes an optional `skipLivingDocsSync?: boolean` field

## Out of Scope

- Queue-based sync architecture (overengineering for this fix)
- Changes to `sw:increment` Step 5 sync trigger (planning-time sync, separate concern)
- JIRA/ADO sync changes (those work correctly)
- Concurrent completion mutex (auto-mode does not run concurrent completions)

## Technical Notes

### Dependencies
- `specweave` CLI (`repositories/anton-abyzov/specweave/`)
- PostToolUse hook (`close-completed-issues.sh` in umbrella root)

### Constraints
- Sync skip logic: sync runs ONLY when `autoSyncOnCompletion !== false` AND `skipLivingDocsSync !== true` (global disable always wins, per-increment is additive)
- Lock file cleanup targets only `sync-*.lock` pattern, not all lock files
- `.env` sourced from `$PROJECT_ROOT/.env` where PROJECT_ROOT is `${FILE_PATH%%/.specweave/*}`

### Architecture Decisions
- Single sync point: `onIncrementDone()` is the sole sync trigger during completion
- `completeIncrement()` pre-sync removed entirely (no lightweight check replacement)
- External drift is a warning, not a blocking error -- completion must always succeed

## Non-Functional Requirements

- **Performance**: Eliminates ~5000 wasted GitHub API calls/hour from zombie processes
- **Reliability**: `specweave complete` exits 0 for drift conditions that are non-fatal
- **Observability**: Transition failures log to stderr even under `--silent` flag
- **Compatibility**: No changes to planning-time sync (`sw:increment` Step 5) or JIRA/ADO paths

## Edge Cases

- **Stale lock files from killed processes**: Cleaned up on hook entry if >60 min old (`sync-*.lock` pattern only)
- **Missing .env file**: Hook gracefully handles missing `.env` (gh CLI falls back to its own auth)
- **Both skip flags set**: If global `autoSyncOnCompletion: false` AND per-increment `skipLivingDocsSync: true`, sync is skipped (global wins first, per-increment check is redundant but harmless)
- **External service unreachable during sync**: Existing error handling in `onIncrementDone` applies -- completion still succeeds

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Removing pre-sync reveals unhandled edge case in onIncrementDone | 0.2 | 5 | 1.0 | Existing test suite covers sync paths; add test for single-invocation guarantee |
| Hook .env sourcing breaks in non-standard project layouts | 0.1 | 3 | 0.3 | PROJECT_ROOT derivation already proven in hook; add fallback for missing .env |
| Users relying on background sync as safety net lose sync coverage | 0.3 | 4 | 1.2 | onIncrementDone is the reliable replacement; document in changelog |

## Success Metrics

- Zero zombie `specweave sync-living-docs` processes after hook execution
- `specweave complete` exits 0 for increments with external drift >168h
- GitHub API call rate drops to normal levels (no 5000/hr spikes)
- Living docs sync executes exactly once per completion cycle
