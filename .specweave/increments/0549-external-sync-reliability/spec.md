---
increment: 0549-external-sync-reliability
title: "External Sync Reliability"
type: feature
priority: P0
status: active
created: 2026-03-16
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# External Sync Reliability

## Problem Statement

SpecWeave's synchronization with JIRA, GitHub Issues, and ADO has never worked reliably end-to-end. The sync lifecycle is broken at both ends: import creates living docs instead of increments, and increment closure does not propagate status to external tools. Between those endpoints, silent error handling masks failures, race conditions corrupt state, and platform parity is severely uneven -- GitHub is reasonably mature while JIRA lacks locking and ADO lacks rate limiting, bidirectional sync, and uses fragile regex for checkbox updates. Core infrastructure (circuit breaker, retry queue) exists but is only wired into GitHub, leaving JIRA and ADO without resilience.

## Goals

- Close the sync lifecycle: imports create proper increments, closure propagates to external tools
- Surface sync failures to users instead of silently swallowing them
- Bring JIRA and ADO plugin resilience to parity with GitHub (circuit breaker, file locking, rate limiting)
- Replace fragile ADO regex-based AC sync with a proper API approach
- Add bidirectional state sync for ADO
- Standardize the platform suffix convention (G/J/A) across all providers
- Achieve integration test coverage for the full sync lifecycle against real APIs

## User Stories

### US-001: Post-Increment-Done Closure Hooks (P0)
**Project**: specweave
**As a** SpecWeave user
**I want** external items (JIRA issues, GitHub issues, ADO work items) to be closed automatically when I close an increment
**So that** I do not have to manually update each external tracker after completing work

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given an increment linked to a GitHub issue, when `specweave complete <id>` succeeds, then the linked GitHub issue is closed via the GitHub API within the same command execution
- [ ] **AC-US1-02**: Given an increment linked to a JIRA issue, when `specweave complete <id>` succeeds, then the linked JIRA issue is transitioned to "Done" status via the JIRA API
- [ ] **AC-US1-03**: Given an increment linked to an ADO work item, when `specweave complete <id>` succeeds, then the linked ADO work item state is set to "Closed" via the ADO API
- [ ] **AC-US1-04**: Given `hooks.post_increment_done.close_github_issue` is false in config, when an increment is closed, then no external closure is attempted for that provider
- [ ] **AC-US1-05**: Given an external API call fails during closure, when the hook executes, then the increment is still marked closed locally and the failure is reported to stderr with the provider name and HTTP status

---

### US-002: Error Surfacing for Sync Failures (P0)
**Project**: specweave
**As a** SpecWeave user
**I want** sync failures to be reported clearly in the CLI output
**So that** I know when external tools are out of sync and can take corrective action

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Given `checkExistingGitHubIssue` encounters an HTTP error, when called during sync, then it throws an error with the HTTP status and message instead of returning false
- [ ] **AC-US2-02**: Given a JIRA transition fails with a non-2xx response, when status sync runs, then the error is propagated to the caller with the JIRA error response body
- [ ] **AC-US2-03**: Given an ADO status sync fails, when the sync command completes, then stderr contains a structured error line: `[ADO] sync failed: <status> <message>`
- [ ] **AC-US2-04**: Given multiple providers fail in the same sync run, when the command completes, then each failure is reported separately and the exit code is non-zero

---

### US-003: Circuit Breaker and Retry Queue Integration for JIRA and ADO (P0)
**Project**: specweave
**As a** SpecWeave user
**I want** JIRA and ADO sync operations to use the existing circuit breaker and retry queue
**So that** transient failures are retried automatically and persistent outages do not block my workflow

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Given the JIRA API returns a 5xx error, when a sync operation is attempted, then the request is enqueued in the retry queue with exponential backoff (base 1s, max 30s)
- [ ] **AC-US3-02**: Given 3 consecutive JIRA API failures, when the circuit breaker trips, then subsequent JIRA calls fail-fast for 60 seconds without hitting the API
- [ ] **AC-US3-03**: Given the ADO API returns a 5xx error, when a sync operation is attempted, then the request is enqueued in the retry queue with exponential backoff (base 1s, max 30s)
- [ ] **AC-US3-04**: Given 3 consecutive ADO API failures, when the circuit breaker trips, then subsequent ADO calls fail-fast for 60 seconds without hitting the API
- [ ] **AC-US3-05**: Given the circuit breaker is open for a provider, when the cooldown expires, then the next call is allowed through (half-open state) and success resets the breaker

---

### US-004: Import Creates Increments (P0)
**Project**: specweave
**As a** SpecWeave user
**I want** imported external items to create proper increment folders under `.specweave/increments/`
**So that** imported work follows the same lifecycle as locally-created increments

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Given a JIRA issue is imported, when the import worker completes, then a new directory `.specweave/increments/<id>-<slug>/` exists with `metadata.json`, `spec.md`, and `tasks.md`
- [ ] **AC-US4-02**: Given a GitHub issue is imported, when the import worker completes, then the created increment's `metadata.json` contains `externalLinks.github` with the issue number and URL
- [ ] **AC-US4-03**: Given an ADO work item is imported, when the import worker completes, then the created increment's `metadata.json` contains `externalLinks.ado` with the work item ID and URL
- [ ] **AC-US4-04**: Given an imported item has acceptance criteria in its description, when the import worker parses it, then those criteria appear as AC entries in the generated `spec.md`
- [ ] **AC-US4-05**: Given an external item was already imported (matching external link exists), when import runs again, then no duplicate increment is created and the existing increment is updated

---

### US-005: Standardized Platform Suffix Convention (P1)
**Project**: specweave
**As a** SpecWeave user
**I want** a consistent, documented suffix convention for external item references
**So that** I can identify which platform an item originated from at a glance

**Acceptance Criteria**:
- [ ] **AC-US5-01**: Given an item synced from GitHub, when it appears in living docs or metadata, then it uses the suffix "G" (e.g., `FS-001G`)
- [ ] **AC-US5-02**: Given an item synced from JIRA, when it appears in living docs or metadata, then it uses the suffix "J" (e.g., `FS-001J`)
- [ ] **AC-US5-03**: Given an item synced from ADO, when it appears in living docs or metadata, then it uses the suffix "A" (e.g., `FS-001A`)
- [ ] **AC-US5-04**: Given an item created locally (no external origin), when it appears in living docs, then it uses the suffix "E" (e.g., `FS-001E`) as currently documented
- [ ] **AC-US5-05**: Given the suffix convention, when `specweave sync` writes any living doc or metadata reference, then the suffix is applied consistently by a shared utility function (not inline string concatenation per plugin)

---

### US-006: Bidirectional ADO State Sync (P1)
**Project**: specweave
**As a** SpecWeave user
**I want** ADO work item state changes to be pulled back into SpecWeave
**So that** my local increment status reflects changes made by teammates in ADO

**Acceptance Criteria**:
- [ ] **AC-US6-01**: Given an ADO work item is moved to "Active", when `specweave sync pull` runs, then the linked increment's `metadata.json` status is updated to "active"
- [ ] **AC-US6-02**: Given an ADO work item is moved to "Closed", when `specweave sync pull` runs, then the linked increment's `metadata.json` status is updated to "completed"
- [ ] **AC-US6-03**: Given the local increment was modified more recently than the ADO item, when `specweave sync pull` runs, then the local state is preserved (last-write-wins by timestamp)
- [ ] **AC-US6-04**: Given `sync.settings.canUpsertInternalItems` is false in config, when `specweave sync pull` runs for ADO, then no local state changes are made

---

### US-007: Replace ADO Regex-Based AC Checkbox Sync (P1)
**Project**: specweave
**As a** SpecWeave user
**I want** ADO acceptance criteria checkbox sync to use the ADO API properly instead of regex on HTML
**So that** sync does not break when ADO changes its description format

**Acceptance Criteria**:
- [ ] **AC-US7-01**: Given an increment with 3 ACs where 2 are complete, when sync pushes to ADO, then the ADO work item description contains 2 checked and 1 unchecked checkbox without using regex-based HTML string manipulation
- [ ] **AC-US7-02**: Given an ADO work item description was edited manually by a user (custom HTML), when sync pushes AC updates, then the non-AC portions of the description are preserved unchanged
- [ ] **AC-US7-03**: Given the ADO description contains no existing checkboxes, when sync pushes ACs for the first time, then checkboxes are appended to the description in a dedicated "Acceptance Criteria" section
- [ ] **AC-US7-04**: Given the previous regex-based implementation, when the new implementation is deployed, then existing ADO work items with checkbox markup continue to sync correctly (backward compatible)

---

### US-008: ADO Rate Limiting (P1)
**Project**: specweave
**As a** SpecWeave user
**I want** ADO API calls to be rate-limited
**So that** bulk sync operations do not exceed the 200 requests/minute PAT limit and trigger throttling

**Acceptance Criteria**:
- [ ] **AC-US8-01**: Given 50 increments need syncing to ADO, when sync runs, then no more than 200 API requests are made within any 60-second window
- [ ] **AC-US8-02**: Given the rate limiter is at capacity (200 req in the current window), when a new request is enqueued, then it waits until the window rolls forward before executing
- [ ] **AC-US8-03**: Given ADO returns HTTP 429, when the response is received, then the retry-after header is respected and the request is retried after the specified delay
- [ ] **AC-US8-04**: Given the rate limiter implementation, when initialized, then it uses a token bucket algorithm consistent with the approach described in the existing config schema

---

### US-009: JIRA File Locking (P1)
**Project**: specweave
**As a** SpecWeave user
**I want** JIRA sync operations to use file-based locking
**So that** concurrent sync operations (hook trigger + manual push) do not corrupt JIRA sync state

**Acceptance Criteria**:
- [ ] **AC-US9-01**: Given a JIRA sync operation is in progress (lock file exists), when a second sync operation starts, then it waits up to 10 seconds for the lock before failing with a "sync in progress" error
- [ ] **AC-US9-02**: Given a JIRA sync operation completes (success or failure), when the operation exits, then the lock file is released (deleted)
- [ ] **AC-US9-03**: Given a lock file older than 5 minutes exists (stale lock from crash), when a new sync operation starts, then the stale lock is forcibly acquired with a warning logged to stderr
- [ ] **AC-US9-04**: Given the locking implementation, when compared to the GitHub plugin's existing locking, then it uses the same mutex utility (shared code, not a reimplementation)

---

### US-010: End-to-End Sync Lifecycle Tests (P0)
**Project**: specweave
**As a** SpecWeave developer
**I want** integration tests covering the full sync lifecycle for all 3 providers
**So that** regressions in the sync pipeline are caught before release

**Acceptance Criteria**:
- [ ] **AC-US10-01**: Given a test increment, when `specweave sync push` runs against the real GitHub API, then a GitHub issue is created, AC checkboxes are synced, and closure propagates -- verified by reading back via the API
- [ ] **AC-US10-02**: Given a test increment, when `specweave sync push` runs against the real JIRA API, then a JIRA issue is created, AC checkboxes are synced, and status transition works -- verified by reading back via the API
- [ ] **AC-US10-03**: Given a test increment, when `specweave sync push` runs against the real ADO API, then an ADO work item is created, AC checkboxes are synced, and closure propagates -- verified by reading back via the API
- [ ] **AC-US10-04**: Given a multi-provider sync failure scenario, when one provider is down (mocked 503) and two are healthy, then healthy providers complete successfully and the failing provider's error is reported without blocking others
- [ ] **AC-US10-05**: Given the import flow, when an external item is imported and then the resulting increment is closed, then the round-trip (import -> work -> close -> external closure) completes without manual intervention

## Out of Scope

- Webhook-based real-time sync (push model from external tools to SpecWeave)
- Conflict resolution beyond last-write-wins for ADO bidirectional sync
- UI dashboard for sync status monitoring
- Support for additional external tools beyond JIRA, GitHub Issues, and ADO
- Migrating existing living docs (FS-*E suffix) to the new suffix convention retroactively

## Non-Functional Requirements

- **Performance**: Rate-limited ADO sync must not add more than 500ms latency per individual request. Circuit breaker fail-fast must return within 5ms.
- **Reliability**: Retry queue must persist across process restarts (file-based queue). Circuit breaker state must survive process restarts.
- **Security**: No new credential storage mechanisms -- use existing config.json PAT/token fields. Lock files must not contain sensitive data.
- **Compatibility**: All changes backward-compatible with existing sync config schema. No breaking changes to CLI commands.

## Edge Cases

- **Stale lock recovery**: Lock file from a crashed process must be auto-recovered after 5-minute timeout
- **Partial closure**: If 2 of 3 providers close successfully but 1 fails, the increment is still closed locally with a partial-sync warning
- **Import deduplication**: Re-importing the same external item must update (not duplicate) the existing increment
- **Empty AC list**: Syncing an increment with zero acceptance criteria must not produce empty checkbox sections in external tools
- **Config changes mid-sync**: If a provider is disabled in config during an active sync, the in-flight operation completes but no new operations start for that provider
- **ADO HTML edge cases**: Manual edits to ADO descriptions (adding custom HTML) must not be destroyed by AC checkbox sync

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| ADO API format changes break new AC sync approach | 0.3 | 7 | 2.1 | Use ADO's documented field update API, not HTML manipulation. Add format versioning. |
| Real API tests are flaky due to network/rate limits | 0.6 | 5 | 3.0 | Use dedicated test projects, implement retry in test harness, tag as integration tests for separate CI stage. |
| JIRA transition IDs vary between projects | 0.4 | 6 | 2.4 | Query available transitions dynamically before attempting state change, never hardcode IDs. |
| Circuit breaker false positives during DNS issues | 0.3 | 4 | 1.2 | Use separate circuit breakers per provider. Add health-check endpoint verification before tripping. |
| Import increment ID collisions with manually created increments | 0.2 | 8 | 1.6 | Use the existing `find .specweave/increments` max-ID logic to allocate import IDs. |

## Technical Notes

### Key Source Files (repositories/anton-abyzov/specweave/)
- Core sync types: `src/core/types/sync-profile.ts`, `sync-config.ts`, `sync-config-validator.ts`
- Circuit breaker + retry: Already in core, needs wiring to JIRA/ADO plugins
- JIRA plugin: `plugins/specweave-jira/lib/jira-*.ts`
- GitHub plugin: `plugins/specweave-github/lib/github-*.ts` (reference implementation)
- ADO plugin: `plugins/specweave-ado/lib/ado-*.ts`
- Hook registration: Each plugin's `hooks/` directory
- Existing tests: `tests/unit/cli/commands/sync-*.test.ts`

### Test Infrastructure
- Real JIRA: SWE2E project on `antonabyzov.atlassian.net`
- Real GitHub: `anton-abyzov/specweave` repo
- Real ADO: `EasyChamp/SpecWeaveSync` project

### Architecture Decisions
- GitHub plugin is the reference implementation for resilience patterns (circuit breaker, file locking, rate limiting pre-check)
- JIRA and ADO plugins must be brought to parity by reusing shared utilities, not reimplementing
- The shared mutex utility from GitHub plugin should be extracted to core if not already there
- ADO AC sync must move from regex HTML manipulation to using the ADO REST API's field update operations

## Success Metrics

- All 3 providers pass end-to-end lifecycle tests (create -> sync -> close) against real APIs
- Zero silent sync failures: every API error is surfaced to the user
- ADO AC sync works reliably without regex: manual ADO description edits survive sync
- Closure propagation works for all 3 providers within the `specweave complete` command
- Import creates proper increments that can be managed through the full SpecWeave lifecycle
