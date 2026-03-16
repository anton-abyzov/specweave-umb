# Tasks: 0549 — External Sync Reliability

**TDD Mode**: Active — RED→GREEN→REFACTOR for every task
**Coverage Targets**: Unit 95% | Integration 90% | E2E 100% of AC scenarios
**Code root**: `repositories/anton-abyzov/specweave/`

---

## Phase 1: Foundation (no external dependencies)

### US-002 / US-003 / US-008 — Shared Infrastructure

---

### T-001: Create SyncError type and sync-error module
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [ ] Not Started
**Test**: Given a provider name, HTTP status, and response body → When `new SyncError('jira', 422, '{"errorMessages":["Field required"]}', 'transition failed')` is constructed → Then `error.message` equals `"[JIRA] sync failed: 422 transition failed"`, `error.provider` equals `"jira"`, `error.httpStatus` equals `422`, `error.name` equals `"SyncError"`, and the instance is an `instanceof Error`

**Files**:
- `src/core/errors/sync-error.ts` (new, ~30 lines)

---

### T-002: Create retry-wrapper utility with exponential backoff
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03
**Status**: [ ] Not Started
**Test**: Given a function that throws a retryable 5xx error on the first 2 calls and succeeds on the 3rd → When `withRetry(fn, { maxRetries: 3, baseMs: 10, maxMs: 300 })` is called → Then the function is called exactly 3 times, the promise resolves with the success value, and the delays between calls follow exponential backoff (10ms, 20ms) with a tolerance of ±50ms

**Files**:
- `src/core/sync/retry-wrapper.ts` (new, ~40 lines)
- `tests/unit/sync/retry-wrapper.test.ts` (new)

---

### T-003: Create ADO token bucket rate limiter
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-04
**Status**: [ ] Not Started
**Test**: Given an `AdoRateLimiter` initialized with default 200-token capacity → When `consume()` is called 200 times → Then all 200 calls return `true`; when called a 201st time within the same 60-second window → Then `consume()` returns `false` (bucket exhausted); after advancing the clock by 60,001ms → Then `consume()` returns `true` again (bucket refilled)

**Files**:
- `plugins/specweave-ado/lib/ado-rate-limiter.ts` (new, ~70 lines)
- `tests/unit/plugins/ado/ado-rate-limiter.test.ts` (new)

---

### T-004: Extract and expose formatSuffixedId utility
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05
**Status**: [ ] Not Started
**Test**: Given the `formatSuffixedId` function exported from `src/sync/types.ts` → When called with `("FS-001", "github")` → Then it returns `"FS-001G"`; when called with `("FS-001", "jira")` → Then it returns `"FS-001J"`; when called with `("FS-001", "ado")` → Then it returns `"FS-001A"`; when called with `("FS-001", undefined)` → Then it returns `"FS-001"` (no suffix for local items)

**Files**:
- `src/sync/types.ts` (modify, ~10 lines added)
- `tests/unit/sync/types.test.ts` (new or extend)

---

## Phase 2: Core Wiring (depends on Phase 1)

### US-003 — Circuit Breaker and Retry Queue Integration

---

### T-005: Wire circuit breaker and retry queue into JIRA sync modules
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-05
**Status**: [ ] Not Started
**Test**: Given a `JiraStatusSync` instance with a circuit breaker that has recorded 2 prior failures → When the JIRA API returns HTTP 503 on the next call → Then the request is re-enqueued via `SyncRetryQueue`, `CircuitBreakerRegistry.get('jira').recordFailure()` is called (breaker now open), and `SyncError` is thrown; when the cooldown expires and the next call succeeds → Then `recordSuccess()` is called and `canSync()` returns `true`

**Files**:
- `plugins/specweave-jira/lib/jira-status-sync.ts` (modify, ~30 lines)
- `plugins/specweave-jira/lib/jira-spec-sync.ts` (modify, ~25 lines)
- `tests/unit/plugins/jira/jira-circuit-breaker.test.ts` (new)

---

### T-006: Wire circuit breaker and retry queue into ADO sync modules
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [ ] Not Started
**Test**: Given an `AdoStatusSync` instance with a circuit breaker registry → When the ADO API returns HTTP 500 on 3 consecutive calls → Then after the 3rd failure `CircuitBreakerRegistry.get('ado').canSync()` returns `false`; when a 4th call is attempted before cooldown expires → Then it throws `CircuitOpenError` without making an HTTP request; when `canSync()` returns `true` after cooldown and the next call succeeds → Then the breaker resets to closed state

**Files**:
- `plugins/specweave-ado/lib/ado-status-sync.ts` (modify, ~30 lines)
- `plugins/specweave-ado/lib/ado-spec-sync.ts` (modify, ~25 lines)
- `tests/unit/plugins/ado/ado-circuit-breaker.test.ts` (new)

---

### T-007: Add persistent circuit breaker state wrapper
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-04
**Status**: [ ] Not Started
**Test**: Given a `PersistentCircuitBreaker` wrapping an in-memory breaker and pointing to a temp state file → When `recordFailure()` is called 3 times → Then `.specweave/state/circuit-breakers.json` is written with `{ "jira": { "failures": 3, "state": "open", "openedAt": "<iso>" } }`; when a new `PersistentCircuitBreaker` instance is constructed pointing to the same file → Then `canSync()` returns `false` immediately (state restored from disk after simulated restart)

**Files**:
- `src/core/sync/persistent-circuit-breaker.ts` (new, ~40 lines)
- `tests/unit/sync/persistent-circuit-breaker.test.ts` (new)

---

### T-008: Integrate JIRA file locking via shared LockManager
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-03, AC-US9-04
**Status**: [ ] Not Started
**Test**: Given two concurrent JIRA sync operations starting simultaneously → When the first acquires the lock file at `.specweave/state/.jira-sync.lock` → Then the second waits up to 10 seconds for the lock; when the first operation completes (success or error) → Then the lock file is deleted and the second operation proceeds; given a lock file with mtime older than 5 minutes → When a new sync starts → Then it logs a stale-lock warning to stderr and forcibly acquires the lock

**Files**:
- `plugins/specweave-jira/lib/jira-spec-sync.ts` (modify, ~25 lines)
- `plugins/specweave-jira/lib/jira-status-sync.ts` (modify, ~10 lines)
- `tests/unit/plugins/jira/jira-file-locking.test.ts` (new)

---

### T-009: Surface GitHub push-sync errors instead of returning false
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Status**: [ ] Not Started
**Test**: Given `checkExistingGitHubIssue` is called and the GitHub API responds with HTTP 401 → When the function executes → Then it throws a `SyncError` with `provider="github"`, `httpStatus=401`, and a non-empty message; it does NOT return `false` or `undefined`

**Files**:
- `plugins/specweave-github/lib/github-push-sync.ts` (modify, ~15 lines)
- `tests/unit/plugins/github/github-push-sync.test.ts` (new or extend)

---

### T-010: Surface JIRA status-sync errors with response body
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02
**Status**: [ ] Not Started
**Test**: Given `JiraStatusSync.updateStatus()` is called and JIRA returns HTTP 400 with body `{"errorMessages":["Cannot transition to Done from current state"]}` → When the method executes → Then it throws a `SyncError` with `provider="jira"`, `httpStatus=400`, `responseBody` containing the JIRA error messages, and the error propagates to the caller without being swallowed

**Files**:
- `plugins/specweave-jira/lib/jira-status-sync.ts` (modify, already touched in T-005)
- `tests/unit/plugins/jira/jira-status-sync.test.ts` (new or extend)

---

### T-011: Surface ADO status-sync errors with structured stderr format
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04
**Status**: [ ] Not Started
**Test**: Given `AdoStatusSync.updateStatus()` is called and ADO returns HTTP 403 with message "Forbidden" → When the method executes → Then it throws a `SyncError` whose `.message` matches `"[ADO] sync failed: 403 Forbidden"`; given the closure dispatcher runs with both JIRA and ADO failing → When `dispatchClosure()` resolves → Then each failure is written to `stderr` as a separate line and the result object has `exitCode !== 0`

**Files**:
- `plugins/specweave-ado/lib/ado-status-sync.ts` (modify, already touched in T-006)
- `tests/unit/plugins/ado/ado-status-sync.test.ts` (new or extend)

---

## Phase 3: Feature Implementation (depends on Phase 2)

### US-001 — Post-Increment-Done Closure Hooks

---

### T-012: Create closure hook dispatcher module
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-05
**Status**: [ ] Not Started
**Test**: Given a config with all three `hooks.post_increment_done` flags set to `true` and an increment linked to a GitHub issue, JIRA issue, and ADO work item → When `dispatchClosure(incrementId, specPath, config)` is called → Then `closeGitHubIssues`, `closeJiraIssues`, and `closeAdoWorkItems` are each called exactly once; given the ADO closure function throws a `SyncError` → Then the promise still resolves (does not reject), the ADO error is included in the result's `failures` array, and `result.incrementClosed` is `true`

**Files**:
- `src/core/closure-dispatcher.ts` (new, ~150 lines)
- `tests/unit/core/closure-dispatcher.test.ts` (new)

---

### T-013: Wire closure dispatcher into SyncCoordinator
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [ ] Not Started
**Test**: Given `SyncCoordinator.syncIncrementCompletion()` is called with a config that enables all three provider closure hooks → When the method executes → Then `dispatchClosure()` is called after living docs sync completes; given `canUpdateExternalItems` is `false` in the config → When `syncIncrementCompletion()` runs → Then `dispatchClosure()` is NOT called and no external API calls are made

**Files**:
- `src/sync/sync-coordinator.ts` (modify, ~20 lines)
- `tests/unit/sync/sync-coordinator.test.ts` (new or extend)

---

### T-014: Add closure hook toggle config types and defaults
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [ ] Not Started
**Test**: Given a config file that does NOT include the `hooks.post_increment_done` key → When the config is loaded and parsed → Then the closure hook config resolves with all provider flags defaulting to `true` (backward-compatible opt-out); given a config with `hooks.post_increment_done.close_jira_issue: false` → When parsed → Then `dispatchClosure()` skips JIRA and does not instantiate any JIRA client

**Files**:
- `src/core/config/types.ts` (modify, ~15 lines)
- `src/core/types/sync-profile.ts` (modify, ~10 lines)
- `tests/unit/core/config-types.test.ts` (new or extend)

---

### US-004 — Import Creates Increments

---

### T-015: Wire ImportToIncrementConverter into import coordinator
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [ ] Not Started
**Test**: Given `import-coordinator.ts` processes a JIRA issue fetched by `ExternalImporter` → When `importBatch()` completes → Then a directory exists at `.specweave/increments/<id>-<slug>/` containing `metadata.json`, `spec.md`, and `tasks.md`; the `metadata.json` contains `externalLinks.jira` with the issue key and URL; no living-doc-only file (e.g., `FS-*J.md`) is created as the primary artifact

**Files**:
- `src/importers/import-coordinator.ts` (modify, ~40 lines)
- `tests/unit/importers/import-coordinator.test.ts` (new or extend)

---

### T-016: Add AC parser for external item descriptions
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04
**Status**: [ ] Not Started
**Test**: Given a JIRA issue description containing markdown checklist lines `"- [ ] User can log in\n- [x] Form validates email"` → When `parseExternalACs(description, 'jira')` is called → Then it returns an array of 2 `ACEntry` objects: the first with `completed: false` and text `"User can log in"`, the second with `completed: true` and text `"Form validates email"`; given a description with no checklist items → When parsed → Then it returns an empty array

**Files**:
- `src/importers/ac-parser.ts` (new, ~60 lines)
- `tests/unit/importers/ac-parser.test.ts` (new)

---

### T-017: Implement import deduplication via external ref detector
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05
**Status**: [ ] Not Started
**Test**: Given an increment already exists at `.specweave/increments/0001-my-feature/` with `metadata.json` containing `externalLinks.github.issueNumber: 42` → When `importBatch()` is called again with a GitHub issue #42 → Then no new increment directory is created; instead the existing increment's `metadata.json` is updated with any changed fields from the re-import (e.g., updated title), and the return value indicates `{ action: "updated", incrementId: "0001-my-feature" }`

**Files**:
- `src/importers/import-coordinator.ts` (modify, same file as T-015)
- `tests/unit/importers/import-deduplication.test.ts` (new)

---

### US-005 — Standardized Platform Suffix Convention

---

### T-018: Audit and replace inline suffix concatenation across all plugins
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-05
**Status**: [ ] Not Started
**Test**: Given the codebase is audited for string patterns like `` `${id}G` ``, `` `${id}J` ``, `` `${id}A` `` in plugin source files → When a grep is run across `plugins/specweave-{github,jira,ado}/lib/` → Then zero matches are found for inline suffix concatenation; all suffix formatting routes through `formatSuffixedId()` from `src/sync/types.ts`

**Files**:
- `plugins/specweave-github/lib/*.ts` (audit, modify as needed)
- `plugins/specweave-jira/lib/*.ts` (audit, modify as needed)
- `plugins/specweave-ado/lib/*.ts` (audit, modify as needed)
- `tests/unit/sync/suffix-convention.test.ts` (new)

---

### US-006 — Bidirectional ADO State Sync

---

### T-019: Add pullWorkItemState method to AdoClient
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02
**Status**: [ ] Not Started
**Test**: Given an `AdoClient` instance → When `pullWorkItemState(workItemId)` is called and ADO returns `{ "fields": { "System.State": "Active", "System.ChangedDate": "2026-03-10T09:00:00Z" } }` → Then the method returns `{ state: "Active", modifiedAt: Date("2026-03-10T09:00:00Z") }`; given ADO returns state `"Closed"` → Then the method returns `{ state: "Closed", modifiedAt: ... }`

**Files**:
- `plugins/specweave-ado/lib/ado-client.ts` (modify, ~20 lines)
- `tests/unit/plugins/ado/ado-client.test.ts` (new or extend)

---

### T-020: Implement pullAdoChanges with last-write-wins logic
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04
**Status**: [ ] Not Started
**Test**: Given an increment with `metadata.json` having `status: "active"` and `updatedAt: "2026-03-01T00:00:00Z"`, linked to an ADO work item with state `"Closed"` and `ChangedDate: "2026-03-15T00:00:00Z"` → When `pullAdoChanges(incrementId, config)` is called → Then `metadata.json` is updated with `status: "completed"`; given the local `updatedAt` is `"2026-03-16T00:00:00Z"` (newer than ADO) → When `pullAdoChanges` runs → Then `metadata.json` is NOT modified and the result has `reason: "local-newer"`; given `config.canUpsertInternalItems` is `false` → When called → Then no metadata changes are made and result has `reason: "permission-denied"`

**Files**:
- `plugins/specweave-ado/lib/ado-pull-sync.ts` (new, ~80 lines)
- `tests/unit/plugins/ado/ado-pull-sync.test.ts` (new)

---

### US-007 — Replace ADO Regex-Based AC Checkbox Sync

---

### T-021: Create ADO description updater for HTML section manipulation
**User Story**: US-007 | **Satisfies ACs**: AC-US7-02, AC-US7-03, AC-US7-04
**Status**: [ ] Not Started
**Test**: Given an HTML description `"<p>Project overview</p><h3>Acceptance Criteria</h3><ul><li>[ ] Old AC 1</li></ul><p>Footer note</p>"` → When `updateAcSection(html, newAcHtml)` is called with `newAcHtml = "<ul><li>[x] AC 1</li><li>[ ] AC 2</li></ul>"` → Then the result contains the updated checkbox block between the "Acceptance Criteria" heading and the footer, and `"<p>Footer note</p>"` is preserved unchanged; given a description with no "Acceptance Criteria" section → When called → Then a new section is appended at the end of the HTML

**Files**:
- `src/core/ado-description-updater.ts` (new, ~60 lines)
- `tests/unit/core/ado-description-updater.test.ts` (new)

---

### T-022: Rewrite ADO AC checkbox sync to use API-based section update
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04
**Status**: [ ] Not Started
**Test**: Given an increment with 3 ACs (2 complete, 1 pending) linked to an ADO work item → When `updateStoryCheckboxes(workItemId, acEntries, config)` is called → Then it issues `GET /wit/workitems/{id}?fields=System.Description` to fetch current HTML, calls `formatACCheckboxes(acEntries)` from core, calls `updateAcSection(currentHtml, formattedAcs)`, and issues `PATCH /wit/workitems/{id}` with JSON Patch `op:"replace"` on `System.Description`; the PATCH body contains 2 checked and 1 unchecked checkbox items; at no point does any regex pattern match against the description HTML

**Files**:
- `plugins/specweave-ado/lib/ado-ac-checkbox-sync.ts` (modify, rewrite `updateStoryCheckboxes`, ~80 lines)
- `tests/unit/plugins/ado/ado-ac-checkbox-sync.test.ts` (new or extend)

---

### US-008 — ADO Rate Limiting

---

### T-023: Integrate AdoRateLimiter into ADO client API calls
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03
**Status**: [ ] Not Started
**Test**: Given an `AdoClient` initialized with `AdoRateLimiter` that has 1 token remaining → When `makeRequest()` is called → Then the single token is consumed and the request executes; when `makeRequest()` is called again immediately (bucket empty) → Then the call waits until the window rolls forward before executing (not rejected); given the ADO API returns HTTP 429 with `Retry-After: 2` → When `withRetry` handles the response → Then the next attempt is delayed by ~2000ms (±200ms) and the `Retry-After` header value is used instead of the exponential backoff delay

**Files**:
- `plugins/specweave-ado/lib/ado-client.ts` (modify, already touched in T-019)
- `tests/unit/plugins/ado/ado-rate-limiter-integration.test.ts` (new)

---

## Phase 4: Testing — End-to-End Integration Tests (depends on Phase 3)

### US-010 — End-to-End Sync Lifecycle Tests

---

### T-024: GitHub full lifecycle integration test
**User Story**: US-010 | **Satisfies ACs**: AC-US10-01
**Status**: [ ] Not Started
**Test**: Given a test increment created in a temp `.specweave/` directory → When `specweave sync push` runs against the real `anton-abyzov/specweave` GitHub repo (using env `GITHUB_TEST_TOKEN`) → Then a GitHub issue is created (verified via `GET /repos/{owner}/{repo}/issues/{number}`), AC checkboxes appear in the issue body, and running `specweave complete <id>` closes the GitHub issue (verified via `GET` returning `state: "closed"`); after the test the issue is deleted via the API for cleanup

**Files**:
- `tests/integration/sync/github-lifecycle.test.ts` (new, @integration tag)

---

### T-025: JIRA full lifecycle integration test
**User Story**: US-010 | **Satisfies ACs**: AC-US10-02
**Status**: [ ] Not Started
**Test**: Given a test increment → When `specweave sync push` runs against the real `SWE2E` project on `antonabyzov.atlassian.net` (using env `JIRA_TEST_TOKEN`) → Then a JIRA issue is created in project SWE2E, AC checkboxes are synced in the issue description, and running `specweave complete <id>` transitions the JIRA issue to "Done" status (verified via `GET /rest/api/3/issue/{key}` returning `status.name: "Done"`); after the test the issue is deleted via the JIRA delete API

**Files**:
- `tests/integration/sync/jira-lifecycle.test.ts` (new, @integration tag)

---

### T-026: ADO full lifecycle integration test
**User Story**: US-010 | **Satisfies ACs**: AC-US10-03
**Status**: [ ] Not Started
**Test**: Given a test increment → When `specweave sync push` runs against the real `EasyChamp/SpecWeaveSync` ADO project (using env `ADO_TEST_TOKEN`) → Then an ADO work item is created, AC checkboxes appear in the work item description via API-based section update (no regex), and running `specweave complete <id>` sets the work item state to "Closed" (verified via `GET /wit/workitems/{id}?fields=System.State` returning `"Closed"`); after the test the work item is deleted

**Files**:
- `tests/integration/sync/ado-lifecycle.test.ts` (new, @integration tag)

---

### T-027: Multi-provider partial failure isolation test
**User Story**: US-010 | **Satisfies ACs**: AC-US10-04
**Status**: [ ] Not Started
**Test**: Given a test increment linked to GitHub and JIRA (real APIs) and ADO (mocked to return 503) → When `specweave sync push` runs → Then GitHub and JIRA sync operations complete successfully (verified via API read-back), ADO failure is reported to stderr as `"[ADO] sync failed: 503 Service Unavailable"`, the overall command exits with a non-zero code, and the increment itself is NOT rolled back (partial-sync warning is present in output)

**Files**:
- `tests/integration/sync/multi-provider-failure.test.ts` (new, @integration tag)

---

### T-028: Import-to-completion round-trip integration test
**User Story**: US-010 | **Satisfies ACs**: AC-US10-05
**Status**: [ ] Not Started
**Test**: Given a real JIRA issue exists in SWE2E project → When `specweave import --provider jira --project SWE2E` runs → Then a proper increment directory is created under `.specweave/increments/`; when that increment is worked on and `specweave complete <id>` is run → Then the original JIRA issue transitions to "Done" without any manual intervention; the entire round-trip (import -> local work -> close -> external closure) completes within a single test run with no human interaction required

**Files**:
- `tests/integration/sync/import-round-trip.test.ts` (new, @integration tag)

---

## Phase 4 (continued): Unit Test Coverage Sweep

---

### T-029: Unit tests for closure dispatcher — config gating and partial failures
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05
**Status**: [ ] Not Started
**Test**: Given a config with `close_github_issue: false` and the other two hooks enabled → When `dispatchClosure()` is called → Then the GitHub closure function is never called (verified via spy), JIRA and ADO closures execute; given both JIRA and ADO closures throw SyncErrors → When the dispatcher resolves → Then both errors appear in `result.failures`, `result.failures.length` equals 2, and `result.incrementClosed` is `true`

**Files**:
- `tests/unit/core/closure-dispatcher.test.ts` (extend from T-012)

---

### T-030: Unit tests for retry-wrapper — non-retryable errors and max retries
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03
**Status**: [ ] Not Started
**Test**: Given a function that always throws a 400 Bad Request error → When `withRetry(fn, { maxRetries: 3, baseMs: 10, maxMs: 300 })` is called → Then the function is called exactly once (non-retryable error, no retry) and the SyncError propagates immediately; given a function that throws 5xx errors on all 4 attempts (3 retries + initial) → When `withRetry` exhausts retries → Then the last error is thrown and the function was called exactly 4 times

**Files**:
- `tests/unit/sync/retry-wrapper.test.ts` (extend from T-002)

---

### T-031: Unit tests for ADO pull sync state mapping
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02
**Status**: [ ] Not Started
**Test**: Given the `mapAdoStateToSpecweave` mapping function → When called with `"New"` → Then it returns `"planned"`; with `"Active"` → `"active"`; with `"Resolved"` → `"active"`; with `"Closed"` → `"completed"`; with `"Removed"` → `"abandoned"`; with an unmapped string like `"Custom State"` → Then it returns `"active"` as the default fallback

**Files**:
- `tests/unit/plugins/ado/ado-pull-sync.test.ts` (extend from T-020)

---

### T-032: Unit tests for AC parser — edge cases
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04
**Status**: [ ] Not Started
**Test**: Given a GitHub issue body containing a mix of markdown checkboxes and regular list items → When `parseExternalACs(body, 'github')` is called → Then only lines matching `"- [ ]"` or `"- [x]"` are parsed as ACs (regular `"-"` list items are ignored); given a description containing HTML-encoded checkboxes (ADO format `"&#9744;"`) → When parsed with platform `"ado"` → Then the unchecked HTML entity maps to `completed: false`; given an empty string → Then an empty array is returned

**Files**:
- `tests/unit/importers/ac-parser.test.ts` (extend from T-016)

---

### T-033: Unit tests for ADO description updater — backward compatibility
**User Story**: US-007 | **Satisfies ACs**: AC-US7-04
**Status**: [ ] Not Started
**Test**: Given an existing ADO work item description that uses the legacy regex-based checkbox format (unicode `&#9745;` checked, `&#9744;` unchecked inline) → When `updateAcSection(legacyHtml, newFormattedAcHtml)` is called → Then the AC section is identified by the "Acceptance Criteria" heading, the legacy checkboxes inside that section are replaced with the new format, and all content outside the AC section is byte-for-byte identical to the original

**Files**:
- `tests/unit/core/ado-description-updater.test.ts` (extend from T-021)

---

### T-034: Unit tests for persistent circuit breaker — restart recovery
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-04
**Status**: [ ] Not Started
**Test**: Given a `PersistentCircuitBreaker` for `"ado"` that is in open state (3 failures recorded) serialized to a temp file → When a new `PersistentCircuitBreaker` instance is constructed with the same file path → Then `canSync()` immediately returns `false` without any API calls; when the mocked clock advances past the 60-second cooldown → Then `canSync()` returns `true` (half-open), a success is recorded, and `canSync()` continues returning `true` (closed state); the state file is updated to reflect the reset

**Files**:
- `tests/unit/sync/persistent-circuit-breaker.test.ts` (extend from T-007)

---

### T-035: Unit tests for JIRA file locking — stale lock recovery
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-03, AC-US9-04
**Status**: [ ] Not Started
**Test**: Given a `.jira-sync.lock` directory exists with mtime set to 6 minutes ago → When a JIRA sync operation calls `lock.acquire()` → Then a warning is written to stderr containing "stale lock", the lock is forcibly acquired (returns `true`), and the sync proceeds; given a normal lock acquisition followed by a sync error → When the operation exits → Then the lock directory does not exist (released in finally block); given the GitHub plugin's `LockManager` is imported and used for JIRA → When the module path is checked → Then it is the same `src/utils/lock-manager.ts` import (no reimplementation)

**Files**:
- `tests/unit/plugins/jira/jira-file-locking.test.ts` (extend from T-008)

---

## Coverage Summary

| User Story | Tasks | ACs Covered |
|-----------|-------|-------------|
| US-001: Closure Hooks | T-012, T-013, T-014, T-029 | AC-US1-01 through AC-US1-05 |
| US-002: Error Surfacing | T-001, T-009, T-010, T-011 | AC-US2-01 through AC-US2-04 |
| US-003: Circuit Breaker + Retry | T-002, T-005, T-006, T-007, T-030, T-034 | AC-US3-01 through AC-US3-05 |
| US-004: Import Creates Increments | T-015, T-016, T-017, T-032 | AC-US4-01 through AC-US4-05 |
| US-005: Platform Suffix Convention | T-004, T-018 | AC-US5-01 through AC-US5-05 |
| US-006: Bidirectional ADO Sync | T-019, T-020, T-031 | AC-US6-01 through AC-US6-04 |
| US-007: ADO AC Checkbox API Sync | T-021, T-022, T-033 | AC-US7-01 through AC-US7-04 |
| US-008: ADO Rate Limiting | T-003, T-023 | AC-US8-01 through AC-US8-04 |
| US-009: JIRA File Locking | T-008, T-035 | AC-US9-01 through AC-US9-04 |
| US-010: E2E Integration Tests | T-024, T-025, T-026, T-027, T-028 | AC-US10-01 through AC-US10-05 |

**Total tasks**: 35
**Total ACs covered**: 44 across 10 user stories
