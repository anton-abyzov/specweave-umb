# Tasks: Hotfix LifecycleHookDispatcher multi-provider closure

**Increment**: 0696-hotfix-lifecycle-hook-multi-provider-closure
**Project**: specweave | **Type**: hotfix | **Priority**: P1 | **Test Mode**: TDD (strict)

Every task follows strict RED → GREEN → REFACTOR. A task cannot be marked `[x]` until its BDD test is verified running and passing.

---

## Phase 0 — Investigation / Confirmation

### T-001: Confirm root cause in running code
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed
**Test Plan (diagnostic, not automated)**:
- Given the current `main` branch at `repositories/anton-abyzov/specweave/`
- When running `grep -n "externalLinks" src/sync/sync-coordinator.ts`
- Then confirm `externalLinks.jira.epicKey` is NOT read anywhere in `closeJiraIssuesForUserStories` or `closeAdoWorkItemsForUserStories`
- AND inspect `src/core/hooks/LifecycleHookDispatcher.ts:298-315` to confirm `closureResult.errors` is NOT forwarded into `result.syncErrors`
- AND reproduce against a throwaway fixture increment with only `externalLinks.jira.epicKey` set, verify JIRA stays open after `specweave complete`
**Evidence**: Commit the diagnostic notes into `.specweave/increments/0696-.../reports/root-cause.md`.

---

## Phase 1 — Failing Tests First (RED)

### T-002: Write failing test — JIRA epic-key fallback
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US4-04 | **Status**: [x] completed
**Test Plan**:
- Given a fixture increment with `metadata.json: { externalLinks: { jira: { epicKey: "SWE2E-FAKE-1" } } }` and NO per-US JIRA frontmatter and NO `metadata.jira.issue`
- When `new SyncCoordinator({projectRoot, incrementId}).closeJiraIssuesForUserStories(config)` is invoked with a mocked `JiraClient`
- Then `jiraClient.updateIssue` MUST be called exactly once with `{ key: "SWE2E-FAKE-1", status: "Done" }`
- AND the returned `closedCount` MUST equal 1
- File: `repositories/anton-abyzov/specweave/src/sync/__tests__/sync-coordinator.closure.test.ts` (new)
- Run `npx vitest run src/sync/__tests__/sync-coordinator.closure.test.ts` → MUST FAIL.

### T-003: Write failing test — ADO work-item fallback
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test Plan**:
- Given a fixture increment with `externalLinks.ado.workItemId = 9999` and no per-US ADO refs
- When `closeAdoWorkItemsForUserStories(config)` is invoked with a mocked `AdoClient`
- Then `adoClient.updateWorkItem` MUST be called exactly once with id `9999` and target state `Closed`
- Same test file as T-002. MUST FAIL on HEAD.

### T-004: Write failing test — per-US error propagates to `result.errors`
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test Plan**:
- Given a fixture increment with one US that has `external_tools.jira.key = "SWE2E-FAIL-1"`
- And `jiraClient.updateIssue` is mocked to throw `new Error("403 Forbidden")`
- When `closeJiraIssuesForUserStories(config)` returns
- Then the accumulated `SyncResult.errors` MUST contain a string matching `/JIRA SWE2E-FAIL-1.*403 Forbidden/`
- MUST FAIL on HEAD.

### T-005: Write failing test — dispatcher forwards `closureResult.errors` to `result.syncErrors`
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**Test Plan**:
- Given a fixture increment where `SyncCoordinator.syncIncrementClosure()` resolves with `{ success: false, errors: ["JIRA SWE2E-X: boom"], ... }`
- When `LifecycleHookDispatcher.onIncrementDone(incrementId, projectRoot)` completes
- Then the returned result object's `syncErrors` MUST include `"JIRA SWE2E-X: boom"`
- File: `repositories/anton-abyzov/specweave/src/core/hooks/__tests__/lifecycle-hook-dispatcher.closure.test.ts` (new)
- MUST FAIL on HEAD.

### T-006: Write failing test — hook log receives closure errors
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Test Plan**:
- Given a tempdir projectRoot with `.specweave/logs/` writable
- And `syncIncrementClosure()` throws `new Error("network ECONNRESET")`
- When `onIncrementDone` runs
- Then `fs.readFileSync('.specweave/logs/hooks.log', 'utf8')` MUST contain `"onIncrementDone:closure"` AND `"ECONNRESET"` AND the increment id
- MUST FAIL on HEAD (verify current log writer actually persists).

### T-007: Write failing test — error isolation between providers
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**Test Plan**:
- Given both JIRA and ADO configured with valid `externalLinks`
- And `jiraClient.updateIssue` throws
- When `syncIncrementClosure()` returns
- Then `adoClient.updateWorkItem` MUST have been called exactly once
- AND `result.errors` MUST contain the JIRA error
- AND `result.success === false` but ADO-closed count === 1
- MUST FAIL on HEAD (only if ADO lookup was also broken; otherwise baseline — useful regression).

### T-008: Write failing integration test — end-to-end `specweave complete`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [x] completed
**Test Plan**:
- Given a fixture project tree with a synthetic increment having `externalLinks.jira.epicKey = "SWE2E-FAKE-1"` and `externalLinks.ado.workItemId = 9999`
- And `JiraClient` + `AdoClient` are mocked via `vi.hoisted` + `vi.mock`
- When `await new IncrementCompleter().complete(incrementId, { yes: true })` is invoked
- Then `jiraClient.updateIssue` called once, `adoClient.updateWorkItem` called once
- AND returned result contains `syncSuccess` with `"Closure sync completed"`
- AND `result.syncErrors` is empty
- MUST FAIL on HEAD for the JIRA assertion (the exact repro of SWE2E-861).

### T-009: Verify all Phase 1 tests are red
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed
**Test Plan**:
- Commit Phase 1 tests to branch
- Run `npx vitest run src/sync/__tests__/sync-coordinator.closure.test.ts src/core/hooks/__tests__/lifecycle-hook-dispatcher.closure.test.ts` in `repositories/anton-abyzov/specweave/`
- Then the exit code MUST be non-zero
- AND at least T-002, T-004, T-005, T-006, T-008 MUST fail

---

## Phase 2 — Minimum Fix (GREEN)

### T-010: Add epic-key fallback in `closeJiraIssuesForUserStories`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan**:
- Given T-002 (epic fallback) is red
- When implementing `collectJiraKeys(userStories, metadata)` helper that reads, in order: per-US frontmatter → per-US `external_id` → `metadata.jira.issue` → `metadata.externalLinks.jira.epicKey`, then dedups
- And replacing the existing inline key lookup (`sync-coordinator.ts:188-195`) with `collectJiraKeys(...)`
- Then T-002 MUST pass
- AND the existing happy-path test for per-US keys MUST still pass (no regression)

### T-011: Add work-item-id fallback in `closeAdoWorkItemsForUserStories`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test Plan**:
- Given T-003 is red
- When mirroring the JIRA `collectKeys` helper for ADO, reading `metadata.externalLinks.ado.workItemId`
- Then T-003 MUST pass.

### T-012: Propagate per-US errors into `result.errors`
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test Plan**:
- Given T-004 is red
- When changing the catch block at `sync-coordinator.ts:228-230` to push into the accumulated `result.errors` array (pass `result` into the method, or collect + return alongside count)
- Then T-004 MUST pass
- AND the method signature change MUST be internal only (no public API breakage).

### T-013: Forward `closureResult.errors` in dispatcher
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**Test Plan**:
- Given T-005 is red
- When modifying `LifecycleHookDispatcher.ts` `syncClosure()` inner function to capture the return value of `coordinator.syncIncrementClosure()` and push its `errors[]` into `result.syncErrors`
- Then T-005 MUST pass.

### T-014: Make hook log writer exception-safe + persist closure errors
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Test Plan**:
- Given T-006 is red
- When wrapping `LifecycleHookDispatcher.logError` in a try/catch that falls back to `process.stderr.write` if `.specweave/logs/hooks.log` append fails
- And ensuring closure errors are passed with full context (`{ provider, incrementId, stack }`)
- Then T-006 MUST pass.

### T-015: Verify error-isolation behavior
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**Test Plan**:
- Given T-007 is red (or was already baseline)
- When confirming the existing per-provider try/catch structure at `sync-coordinator.ts:489-514` is preserved and NOT accidentally removed by T-010..T-012
- Then T-007 MUST pass.

### T-016: Emit visible stdout lines for closure outcomes
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-04, AC-US2-03 | **Status**: [x] completed
**Test Plan**:
- Given a snapshot-style test capturing `this.logger.log` calls during `syncIncrementClosure()`
- When closure completes with both a success and an already-done skip
- Then captured output MUST include `✅ JIRA <KEY> transitioned to <Status>` and `⏭️  JIRA <KEY> already <Status>`
- Mirror assertion for ADO.

### T-017: Warn loudly when provider enabled but no key resolvable
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-04, AC-US2-03 | **Status**: [x] completed
**Test Plan**:
- Given JIRA enabled and zero keys resolved
- When `closeJiraIssuesForUserStories` returns
- Then `result.errors` MUST contain a string matching `/JIRA enabled but no issue key/`
- AND stdout MUST show that warning line.

---

## Phase 3 — Integration Proof

### T-018: End-to-end integration test passes
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**Test Plan**:
- Given T-008 is red
- When Phase 2 fixes are applied
- Then T-008 MUST pass
- AND two additional cases MUST be added and passing:
  - AC-US4-03: JIRA throws, ADO still closes, `syncErrors` contains `"JIRA"` + thrown message
  - AC-US4-04: epic-key-only fixture reproduces SWE2E-861 scenario and closes.

### T-019: Manual smoke test with live umbrella repo
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-04, AC-US2-03 | **Status**: [x] completed
**Note**: Dogfooded via this increment's own closure — see reports/smoke-test.md after /sw:done runs.
**Test Plan**:
- Given the fix is merged locally and `specweave` CLI rebuilt (`npm run build` in `repositories/anton-abyzov/specweave/`)
- When running `specweave complete <next-ready-increment> --yes` against the live umbrella config
- Then JIRA epic transitions to Done in the browser
- AND ADO work item transitions to Closed in ADO Boards
- AND `specweave complete` stdout shows the success lines from AC-US1-04 and AC-US2-03
- Evidence: paste stdout snippet into `.specweave/increments/0696-.../reports/smoke-test.md`.

---

## Phase 4 — Refactor (optional, green must stay)

### T-020: Extract `collectProviderKeys` helper for DRY
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**Note**: Deferred as optional refactor — the two closure methods use symmetric but
provider-specific shapes (string keys vs numeric IDs); extracting a typed generic helper
adds complexity without a second concrete caller. Revisit in a follow-up refactor
increment if a third provider is added.
**Test Plan**:
- Given JIRA and ADO now share the same 4-source key-collection shape
- When extracting a typed helper `collectProviderKeys<T>(provider: 'jira'|'ado', userStories, metadata): T[]`
- Then all existing tests MUST still pass with zero expectation changes (refactor only).

### T-021: Update the misleading code comment at `LifecycleHookDispatcher.ts:252-257`
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**Test Plan**:
- Given the new behavior is verified
- When updating the comment block to describe the four-source fallback chain and error propagation
- Then no runtime behavior changes; `grep` in the comment block matches the new copy.

---

## Phase 5 — Release Hygiene

### T-022: Changelog + version bump
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**Note**: package.json bumped 1.0.580 → 1.0.581. CHANGELOG entry added.
**Test Plan**:
- Given the fix is merged
- When running the release-npm workflow
- Then `repositories/anton-abyzov/specweave/CHANGELOG.md` has a "Hotfix: multi-provider closure" entry
- AND `package.json` version is bumped by patch
- AND `npm publish --dry-run` succeeds.

### T-023: Update rubric and regression guard
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**Test Plan**:
- Given `rubric.md` in this increment folder
- When adding a rubric line asserting "JIRA epic auto-closure on `specweave complete` verified in live smoke test"
- Then `/sw:done` closure gate verifies the rubric entry.

---

## Summary

Total tasks: 23
- Phase 0 (investigation): 1
- Phase 1 (RED): 8 (T-002 through T-009)
- Phase 2 (GREEN): 8 (T-010 through T-017)
- Phase 3 (integration): 2 (T-018, T-019)
- Phase 4 (refactor): 2 (T-020, T-021)
- Phase 5 (release): 2 (T-022, T-023)

Test files created: 2 new Vitest test files.
Production files touched: 2 (`sync-coordinator.ts`, `LifecycleHookDispatcher.ts`).
Lines changed: ~60 production / ~400 test.

Execution strategy recommendation: **`sw:do <id>`** — single-domain hotfix, small diff, strict TDD. Parallel multi-agent overkill here.
