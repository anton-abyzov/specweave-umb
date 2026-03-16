# Tasks: Critical Sync Integration Bug Fixes

## Task Notation

- `[ ]`: Not started | `[x]`: Completed
- Priority tiers: Phase 1 = Critical (P0), Phase 2 = High (P1), Phase 3 = Medium (P2)

---

## Phase 1: Critical Fixes (P0)

### T-001: Remove stub code from sync-coordinator loadCompletionData()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed

**Description**: Replace mock task data generation with real tasks.md parsing. Currently line 838 says "Add mock data for demo" and generates generic "Task title" strings instead of parsing actual task IDs and titles from tasks.md.

**Implementation Details**:
- Parse `### T-XXX: Title` headings from tasks.md to get real task IDs and titles
- Parse `**Status**: [x] completed` or `**Status**: [x] completed` for completion status
- Remove the dummy loop that creates fake task entries

**Test Plan**:
- **File**: `tests/unit/sync/sync-coordinator.test.ts`
- **Tests**:
  - **TC-001**: Given a tasks.md with 3 tasks (2 completed, 1 pending) -> When loadCompletionData() is called -> Then tasks array contains 3 entries with real IDs, real titles, and correct completion flags
  - **TC-002**: Given a tasks.md with no tasks -> When loadCompletionData() is called -> Then tasks array is empty and progressPercentage is 0

**Dependencies**: None

---

### T-002: Remove TODO stubs from external-item-sync-service commentOnlySync()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed

**Description**: The commentOnlySync method at line 283 has a TODO comment saying "Integrate with external tool APIs" and just logs the comment. It needs to actually post the comment via the external client (GitHub, JIRA, ADO).

**Implementation Details**:
- Accept the external client as a parameter (like FormatPreservationSyncService does)
- Route to the correct API based on client type
- Post the formatted comment to the external tool

**Test Plan**:
- **File**: `tests/unit/sync/external-item-sync-service.test.ts`
- **Tests**:
  - **TC-003**: Given a GitHub client -> When commentOnlySync() is called -> Then it calls client.addComment() with the formatted comment
  - **TC-004**: Given dryRun=true -> When commentOnlySync() is called -> Then no API call is made

**Dependencies**: None

---

### T-003: Remove TODO stub from external-item-sync-service fullSync()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed

**Description**: The fullSync method at line 346 has a TODO saying "Implement full sync logic" and logs "not yet implemented". It needs to actually update the external item.

**Implementation Details**:
- Accept the external client as a parameter
- Update title, description, and acceptance criteria on the external item
- Respect format preservation validation results (allowedFields)

**Test Plan**:
- **File**: `tests/unit/sync/external-item-sync-service.test.ts`
- **Tests**:
  - **TC-005**: Given an internal US and a GitHub client -> When fullSync() is called with title change -> Then client.updateIssue() is called with new title
  - **TC-006**: Given validation blocks description update -> When fullSync() is called -> Then only allowed fields are updated

**Dependencies**: T-002

---

### T-004: Fix GitHub reconciler profile resolution bypass
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed

**Description**: `github-reconciler.ts` line 94 reads `config.sync?.github?.enabled ?? false` which bypasses profile-based detection. Should use `isProviderEnabled(config, 'github')` like the rest of the codebase.

**Implementation Details**:
- Import `isProviderEnabled` from `./status-mapper.js`
- Replace `config.sync?.github?.enabled ?? false` with `isProviderEnabled(config, 'github')`
- Verify JIRA and ADO reconcilers already use `isProviderEnabled` (they import resolvePermissions but check differently)

**Test Plan**:
- **File**: `tests/unit/sync/github-reconciler.test.ts`
- **Tests**:
  - **TC-007**: Given config with profile-based GitHub (no sync.github.enabled) -> When reconcile() is called -> Then it proceeds with reconciliation (not skipping)
  - **TC-008**: Given config with legacy sync.github.enabled=true -> When reconcile() is called -> Then it proceeds normally (backward compat)

**Dependencies**: None

---

### T-005: Fix JIRA idempotency check format mismatch
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01 | **Status**: [x] completed

**Description**: `sync-coordinator.ts` line 700 compares `lastComment.body` (which is an ADF object from JIRA API) with `completionComment` (which is a plain text string). The comparison always returns false, so every sync run posts a duplicate comment.

**Implementation Details**:
- Extract plain text from ADF body object for comparison
- Or use a stable comment marker (e.g., `<!-- specweave-sync:{incrementId}:{usId} -->`) embedded in comments for dedup
- The marker approach is more robust since JIRA may transform text

**Test Plan**:
- **File**: `tests/unit/sync/jira-sync-coordinator.test.ts`
- **Tests**:
  - **TC-009**: Given a JIRA issue with an existing SpecWeave comment -> When syncUserStory() runs again -> Then no duplicate comment is posted
  - **TC-010**: Given a JIRA issue with no existing comments -> When syncUserStory() runs -> Then a comment is posted

**Dependencies**: None

---

### T-006: Fix GitHub issue search title format mismatch
**User Story**: US-011 | **Satisfies ACs**: AC-US11-01 | **Status**: [x] completed

**Description**: `external-issue-auto-creator.ts` line 497 searches for `[FS-XXX]` prefix but issues are now created with `US-XXX: Title` format (per types.ts formatIssueTitle). The Layer 3 API search will never find existing issues, causing duplicates.

**Implementation Details**:
- Update search to look for both formats: new `US-XXX:` and legacy `[FS-XXX]`
- Or search by label `specweave` + feature ID to be format-agnostic
- Also fix the user-story-level search (currently not done at all — only feature-level)

**Test Plan**:
- **File**: `tests/unit/sync/external-issue-auto-creator.test.ts`
- **Tests**:
  - **TC-011**: Given existing issue with title "US-001: Auth flow" -> When createGitHubIssues() runs -> Then it finds the existing issue and skips creation
  - **TC-012**: Given existing issue with legacy title "[FS-042][US-001] Auth flow" -> When createGitHubIssues() runs -> Then it finds the existing issue

**Dependencies**: None

---

## Phase 2: High Priority Fixes (P1)

### T-007: Replace hardcoded 'develop' branch with detection
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed

**Description**: `external-issue-auto-creator.ts` hardcodes `develop` in GitHub issue body links (lines 781, 811-812). Most repos use `main` as default branch.

**Implementation Details**:
- Add a helper method `detectDefaultBranch()` that tries:
  1. `config.repository.defaultBranch` from config.json
  2. `git symbolic-ref refs/remotes/origin/HEAD` (returns `refs/remotes/origin/main`)
  3. Fallback to `main`
- Replace `develop` in template strings with detected branch

**Test Plan**:
- **File**: `tests/unit/sync/external-issue-auto-creator.test.ts`
- **Tests**:
  - **TC-013**: Given config with repository.defaultBranch="main" -> When buildGitHubIssueBody() is called -> Then link contains `/tree/main/`
  - **TC-014**: Given no config and git HEAD pointing to "main" -> When buildGitHubIssueBody() is called -> Then link contains `/tree/main/`

**Dependencies**: None

---

### T-008: Add pagination to GitHub provider pullChanges()
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed

**Description**: GitHub provider only fetches first 50 issues. Need to follow `Link` header for pagination.

**Implementation Details**:
- Parse `Link` header for `rel="next"` URL
- Loop until no next page or max pages reached (default 5)
- Accumulate all issues across pages

**Test Plan**:
- **File**: `tests/unit/sync/providers/github-provider.test.ts`
- **Tests**:
  - **TC-015**: Given 120 issues -> When pullChanges() is called -> Then all 120 issues are returned (3 pages)
  - **TC-016**: Given max page limit of 2 -> When pullChanges() is called with 120 issues -> Then only first 100 are returned

**Dependencies**: None

---

### T-009: Add pagination to JIRA provider pullChanges()
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed

**Description**: JIRA provider only fetches `maxResults: 50`. Need to use `startAt` for pagination.

**Implementation Details**:
- Check `total` field in response
- Loop with incrementing `startAt` until all results fetched
- Cap at configurable max (default 250)

**Test Plan**:
- **File**: `tests/unit/sync/providers/jira-provider.test.ts`
- **Tests**:
  - **TC-017**: Given 80 JIRA issues -> When pullChanges() is called -> Then all 80 issues are returned (2 pages)

**Dependencies**: None

---

### T-010: Add pagination to ADO provider pullChanges()
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [x] completed

**Description**: ADO provider slices WIQL results to first 50 IDs. Need to batch the GET requests for all IDs.

**Implementation Details**:
- WIQL returns all matching IDs (no pagination needed there)
- Batch the `/wit/workitems?ids=` GET requests in groups of 200 (ADO max batch size)
- Remove the `.slice(0, 50)` limit

**Test Plan**:
- **File**: `tests/unit/sync/providers/ado-provider.test.ts`
- **Tests**:
  - **TC-018**: Given 300 ADO work items -> When pullChanges() is called -> Then all 300 are returned (2 batches of 200 and 100)

**Dependencies**: None

---

### T-011: Fix ADO work item type and state assumptions
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [x] completed

**Description**: ADO provider hardcodes `$Issue` for creation and `Done`/`Active` for state transitions. These vary by process template.

**Implementation Details**:
- Add optional `workItemType` and `closedState` and `activeState` to AdoAdapterConfig
- Default to `User Story` (most common for Agile) instead of `Issue`
- Default closeIssue to `Closed`, reopenIssue to `Active`
- Allow overrides via config

**Test Plan**:
- **File**: `tests/unit/sync/providers/ado-provider.test.ts`
- **Tests**:
  - **TC-019**: Given Agile config -> When createIssue() is called -> Then uses `$User%20Story` work item type
  - **TC-020**: Given custom workItemType="Epic" in config -> When createIssue() is called -> Then uses `$Epic`

**Dependencies**: None

---

### T-012: Add missing response.ok checks across providers
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05 | **Status**: [x] completed

**Description**: Multiple provider methods parse JSON from response without checking response.ok first. This causes cryptic errors when APIs return 4xx/5xx.

**Implementation Details**:
- JIRA: Add response.ok check in transitionIssue() and detectHierarchy()
- ADO: Add response.ok check in pullChanges() WIQL and batch GET
- GitHub: Add response.ok check in applyLabels() PUT
- GitHub: Fix ensureLabelExists() to only catch 422 (conflict/already-exists), re-throw others

**Test Plan**:
- **File**: `tests/unit/sync/providers/*.test.ts`
- **Tests**:
  - **TC-021**: Given JIRA returns 500 on transition -> When transitionIssue() is called -> Then it throws with descriptive error (not JSON parse error)
  - **TC-022**: Given GitHub returns 403 on label creation -> When ensureLabelExists() is called -> Then it throws (not silently swallowed)
  - **TC-023**: Given ADO returns 401 on WIQL -> When pullChanges() is called -> Then it throws with descriptive error

**Dependencies**: None

---

### T-013: Fix ADO getAdoPat sync/async mismatch
**User Story**: US-012 | **Satisfies ACs**: AC-US12-01 | **Status**: [x] completed

**Description**: `sync-coordinator.ts` line 769 calls `getAdoPat()` without `await` but line 247 uses `await getAdoPat()`. Need to verify the function signature and use it consistently.

**Implementation Details**:
- Check if `getAdoPat()` returns `string` or `Promise<string>`
- If sync: remove `await` from line 247
- If async: add `await` to line 769
- Verify all other callsites are consistent

**Test Plan**:
- **File**: `tests/unit/sync/sync-coordinator.test.ts`
- **Tests**:
  - **TC-024**: Given ADO profile with valid PAT -> When ADO sync path runs -> Then PAT is correctly retrieved (no undefined)

**Dependencies**: None

---

## Phase 3: Medium Priority Fixes (P2)

### T-014: Fix JIRA epic description wiki markup in ADF context
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01 | **Status**: [x] completed

**Description**: `external-issue-auto-creator.ts` buildJiraEpicDescription() uses Confluence wiki markup (`h2.`, `h3.`, `*bold*`) but the JIRA API v3 createIssue wraps the description in an ADF paragraph — wiki markup renders as literal text.

**Implementation Details**:
- Replace wiki markup with plain text (headings as ALL CAPS or markdown-like)
- Or build proper ADF document structure for the description field

**Test Plan**:
- **File**: `tests/unit/sync/external-issue-auto-creator.test.ts`
- **Tests**:
  - **TC-025**: Given an increment -> When buildJiraEpicDescription() is called -> Then output contains no wiki markup (no `h2.`, no `*bold*`)

**Dependencies**: None

---

### T-015: Add 'paused' to reconciler open-state list
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02 | **Status**: [x] completed

**Description**: `github-reconciler.ts` line 153 lists `active`, `planning`, `backlog`, `ready_for_review` as open states but omits `paused`. Paused increments should keep their issues open.

**Implementation Details**:
- Add `paused` to the shouldBeOpen condition in all three reconcilers
- Add a warning log when status is unrecognized (not in either list)

**Test Plan**:
- **File**: `tests/unit/sync/github-reconciler.test.ts`
- **Tests**:
  - **TC-026**: Given increment with status="paused" and closed GitHub issue -> When reconcile() runs -> Then issue is reopened
  - **TC-027**: Given increment with unknown status -> When reconcile() runs -> Then a warning is logged

**Dependencies**: None

---

### T-016: Fix config schema inconsistencies
**User Story**: US-010 | **Satisfies ACs**: AC-US10-01, AC-US10-02, AC-US10-03 | **Status**: [x] completed

**Description**: Multiple config-related inconsistencies between the type definitions and runtime code.

**Implementation Details**:
- Add `profiles` field to `PartialSyncConfig` in config.ts
- Align StatusMapper.canUpdateExternal() default with SyncCoordinator behavior (use resolvePermissions)
- Add profile-based validation to validateSyncConfigConsistency()

**Test Plan**:
- **File**: `tests/unit/sync/config.test.ts`
- **Tests**:
  - **TC-028**: Given config with profiles but no legacy settings -> When validateSyncConfigConsistency() runs -> Then no false warnings about missing config
  - **TC-029**: Given bidirectional preset -> When StatusMapper.canUpdateExternal() is called -> Then returns true (matching coordinator behavior)

**Dependencies**: None

---

### T-017: Run full test suite and verify no regressions
**User Story**: All | **Satisfies ACs**: All | **Status**: [x] completed

**Description**: Run the complete test suite to verify all fixes work and no existing tests are broken.

**Implementation Details**:
- Run `npx vitest run` in `repositories/anton-abyzov/specweave/`
- Fix any test failures caused by the changes
- Verify all new tests pass

**Test Plan**:
- All existing tests pass
- All new tests (TC-001 through TC-029) pass
- No new TypeScript compilation errors

**Dependencies**: T-001 through T-016
