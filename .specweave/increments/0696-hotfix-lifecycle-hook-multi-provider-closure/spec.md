---
increment: 0696-hotfix-lifecycle-hook-multi-provider-closure
title: 'Hotfix: LifecycleHookDispatcher multi-provider closure (JIRA + ADO)'
type: hotfix
priority: P1
status: completed
created: 2026-04-24T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Hotfix: LifecycleHookDispatcher multi-provider closure (JIRA + ADO)

**Increment ID**: 0696-hotfix-lifecycle-hook-multi-provider-closure
**Type**: hotfix
**Priority**: P1
**Project**: specweave
**Status**: planned
**Created**: 2026-04-24

---

## Problem Statement

When running `specweave complete <id> --yes` in the umbrella project with GitHub + JIRA + ADO sync enabled, the `LifecycleHookDispatcher.onIncrementDone()` hook does **not** reliably close JIRA epics. In the confirmed reproduction (closure of `0675-skill-creator-detection-hotfix` on 2026-04-24):

- Umbrella `.specweave/config.json` has `hooks.post_increment_done.close_github_issue: true`.
- ADO Feature `#1700` closure **worked** — but via the `sync-living-docs` pathway, NOT the `onIncrementDone` hook.
- JIRA epic `SWE2E-861` closure **DID NOT FIRE** — `sw-closer` had to close it manually via direct JIRA API (transition id `41`).

The code comment at `repositories/anton-abyzov/specweave/src/core/hooks/LifecycleHookDispatcher.ts:252-256` asserts:

> *"SyncCoordinator handles ALL providers despite the legacy flag name."*

The live run contradicts this claim for JIRA.

### Root-cause hypothesis (to verify in T-001)

Inspection of `SyncCoordinator.closeJiraIssuesForUserStories()` (`src/sync/sync-coordinator.ts:140-238`) shows the method only looks up JIRA keys in three places:

1. Per-user-story frontmatter: `usFile.external_tools?.jira?.key`
2. Per-user-story: `usFile.external_id`
3. Increment `metadata.json`: `metadata.jira?.issue`

It does **NOT** read `externalLinks.jira.epicKey` on increment metadata. When an increment has a JIRA epic linked only via `externalLinks.jira.epicKey` (no per-US JIRA refs and no `metadata.jira.issue`), the method iterates zero keys, returns `0`, and logs nothing user-visible — the epic stays open. `closeAdoWorkItemsForUserStories()` (line 249) has the same shape for ADO, which is why ADO happened to work only via the separate `sync-living-docs` pathway.

Secondary bugs to verify:

- Per-US JIRA errors (`src/sync/sync-coordinator.ts:229`) are `logger.error`-logged only — they do NOT populate `result.errors` / `result.syncErrors`, and they never reach `.specweave/logs/hooks.log`.
- The three flag names (`close_github_issue`, `close_external_issue`, `close_jira_issue`) OR together correctly at `LifecycleHookDispatcher.ts:255-257`, but the legacy name is misleading — documentation implies only `close_github_issue` is needed; we must validate that.

---

## Goal

Guarantee that `specweave complete <id> --yes` closes every configured external issue (JIRA epic, ADO work item, GitHub issue) for an increment, OR emits a loud, actionable error when it cannot. Silent "closed 0 issues" is unacceptable.

## Non-Goals (Out of Scope)

- Studio LeftPanel skill-builder primary-path banner — that is a follow-up on `0670-skill-builder-universal`.
- Refactoring `SyncCoordinator` into a per-provider strategy pattern — this is a targeted hotfix.
- Reworking the `close_github_issue` / `close_external_issue` flag naming — may add a clearer alias but keep backwards compatibility.
- Changing the dispatcher's error-isolation contract (each provider's failure must not abort the others).

---

## User Stories

### US-001: Automated JIRA epic closure on `specweave complete`
**Project**: specweave

**As a** SpecWeave user who has JIRA sync enabled
**I want** `specweave complete <id> --yes` to automatically close the linked JIRA epic
**So that** I do not have to manually transition JIRA issues after every increment

**Acceptance Criteria**:
- [x] **AC-US1-01**: When the umbrella or project `.specweave/config.json` has ANY of `hooks.post_increment_done.close_github_issue`, `close_external_issue`, or `close_jira_issue` set to `true`, AND `sync.settings.canUpdateExternalItems` is `true`, AND `sync.settings.autoSyncOnCompletion` is `true`, AND JIRA is enabled via `isProviderEnabled(config, 'jira')`, AND the increment has `externalLinks.jira.epicKey` (or `metadata.jira.issue`, or per-US `external_tools.jira.key`), then `SyncCoordinator.syncIncrementClosure()` MUST attempt to transition the resolved JIRA key to the target status (default `Done`, override via `sync.statusSync.mappings.jira.completed`).
- [x] **AC-US1-02**: When no per-user-story JIRA key is present AND no `metadata.jira.issue` is present BUT `externalLinks.jira.epicKey` is present on increment metadata, `closeJiraIssuesForUserStories()` MUST fall back to closing the epic itself. This is the direct fix for the `SWE2E-861` reproduction.
- [x] **AC-US1-03**: When the resolved JIRA issue is already in the target status, the hook MUST log `already Done` and treat it as success (idempotent), not as an error.
- [x] **AC-US1-04**: When `specweave complete` succeeds end-to-end, stdout MUST include a line of the form `✅ JIRA <KEY> transitioned to <Status>` for every closed issue, OR `⏭️  JIRA <KEY> already <Status>` for idempotent skips. Silent zero-closure runs when a JIRA link exists are forbidden.

### US-002: Automated ADO work-item closure on `specweave complete` (via the hook, not only `sync-living-docs`)
**Project**: specweave

**As a** SpecWeave user who has Azure DevOps sync enabled
**I want** `specweave complete <id> --yes` to close the linked ADO Feature/Story via the `onIncrementDone` hook
**So that** ADO closure has parity with JIRA closure and does not depend on the incidental `sync-living-docs` pathway

**Acceptance Criteria**:
- [x] **AC-US2-01**: When ADO is enabled via `isProviderEnabled(config, 'ado')` AND the increment has `externalLinks.ado.workItemId` (or per-US `external_tools.ado.id` or `metadata.ado.workItemId`), `SyncCoordinator.closeAdoWorkItemsForUserStories()` MUST transition the work item to the configured closed state (default `Closed`, override via `sync.statusSync.mappings.ado.completed`).
- [x] **AC-US2-02**: The epic / work-item fallback defined in AC-US1-02 applies symmetrically to ADO via `externalLinks.ado.workItemId`.
- [x] **AC-US2-03**: ADO closure via the `onIncrementDone` hook MUST produce the same stdout success line style as JIRA (`✅ ADO #<ID> transitioned to <Status>`), and MUST fire even when `sync_living_docs` is `false` — the two pathways are independent.

### US-003: Per-provider errors surface to `result.syncErrors` and `.specweave/logs/hooks.log`
**Project**: specweave

**As a** SpecWeave user debugging a failed closure
**I want** every JIRA / ADO / GitHub closure error to appear in the dispatcher result AND in the hook log file
**So that** I can diagnose silent failures without re-running with a debugger

**Acceptance Criteria**:
- [x] **AC-US3-01**: When `closeJiraIssuesForUserStories` catches a per-US `updateError` (currently at `sync-coordinator.ts:228-230`), the error message MUST be pushed into the returned `result.errors` array (not only `logger.error`-logged).
- [x] **AC-US3-02**: The `LifecycleHookDispatcher.onIncrementDone()` result object (`result.syncErrors`) MUST include every per-provider error string returned by `SyncCoordinator.syncIncrementClosure()` — not just the outer exception.
- [x] **AC-US3-03**: `LifecycleHookDispatcher.logError('onIncrementDone:closure', error)` MUST persist to `.specweave/logs/hooks.log` with the full error (provider, increment id, stack). The log writer MUST never throw even if the logs directory is unwritable (swallow-and-fallback to stderr).
- [x] **AC-US3-04**: When BOTH JIRA and ADO are configured and JIRA fails while ADO succeeds (or vice versa), the surviving provider MUST still close (error isolation is a dispatcher contract). Verified via unit test.

### US-004: Integration test against mocked SyncCoordinator
**Project**: specweave

**As a** maintainer
**I want** an automated integration test that runs `specweave complete <fixture-id> --yes` end-to-end with mocked provider clients
**So that** this regression cannot silently reoccur

**Acceptance Criteria**:
- [x] **AC-US4-01**: A Vitest integration test MUST spin up a fixture increment with `externalLinks.jira.epicKey = "SWE2E-FAKE-1"` and `externalLinks.ado.workItemId = 9999`, invoke the `onIncrementDone` hook via the real `LifecycleHookDispatcher`, and assert `jiraClient.updateIssue({key, status})` AND `adoClient.updateWorkItem(...)` are each called exactly once with the expected args.
- [x] **AC-US4-02**: The test MUST also assert the hook returns `result.syncSuccess` containing both `"Closure sync completed"` and a per-provider summary, AND `result.syncErrors` is empty.
- [x] **AC-US4-03**: A sibling test MUST assert: when `jiraClient.updateIssue` throws, the ADO call still fires, and `result.syncErrors` contains a string with `"JIRA"` and the thrown message.
- [x] **AC-US4-04**: A third test MUST assert: when no per-US JIRA ref and no `metadata.jira.issue` exist but `externalLinks.jira.epicKey` is set, the epic fallback fires — guarding the exact `SWE2E-861` repro.

### US-005: Strict TDD — failing tests first
**Project**: specweave

**As a** maintainer
**I want** each fix to start with a red test that reproduces the bug
**So that** we prove the fix actually changes behavior, not just code shape

**Acceptance Criteria**:
- [x] **AC-US5-01**: The first commit in the implementation branch MUST add failing tests for AC-US1-02, AC-US2-01 (hook-only pathway), AC-US3-01, AC-US3-02, AC-US3-03, AC-US4-04 — and MUST be verified red before any production code is changed.
- [x] **AC-US5-02**: The second commit MUST turn those tests green with the minimum diff to `SyncCoordinator` and `LifecycleHookDispatcher`.
- [x] **AC-US5-03**: A refactor commit MAY follow but MUST NOT change test expectations.

---

## Confirmed Evidence

### Files and line ranges (verified 2026-04-24)
- `repositories/anton-abyzov/specweave/src/core/hooks/LifecycleHookDispatcher.ts` lines `230-318` — the `onIncrementDone` orchestration.
- `repositories/anton-abyzov/specweave/src/sync/sync-coordinator.ts` lines `140-238` — `closeJiraIssuesForUserStories` (missing `externalLinks.jira.epicKey` lookup).
- `repositories/anton-abyzov/specweave/src/sync/sync-coordinator.ts` lines `249-359` — `closeAdoWorkItemsForUserStories` (same shape).
- `repositories/anton-abyzov/specweave/src/sync/sync-coordinator.ts` lines `394-540` — `syncIncrementClosure` orchestrator.

### Live config at time of repro
- `.specweave/config.json` has `sync.preset: "bidirectional"`, `issueTracker.provider: "jira"`, `issueTracker.domain: "antonabyzov.atlassian.net"`, `sync.profiles.jira-swe2e.config.projectKey: "SWE2E"`, GitHub + ADO both enabled in workspace config.
- `hooks.post_increment_done.close_github_issue: true` (the only closure flag set).

### Manual workaround actually used
`sw-closer` had to run a direct JIRA REST `POST /rest/api/3/issue/SWE2E-861/transitions` with `transitions.id=41` to close the epic.

---

## Rollout & Rollback

- Ship behind a feature flag? **No** — this is a hotfix. The change is strictly additive (new fallback path + extra error propagation). Deploy with a patch release.
- Rollback plan: revert the patch commit. Nothing persisted in user config or files changes.

## Dependencies / Prior Art

- Closure of `0675-skill-creator-detection-hotfix` on 2026-04-24 — the live repro.
- `v1.0.357` release notes (code comment at `LifecycleHookDispatcher.ts:252`) claim multi-provider closure — must update after fix lands.
- ADR `sync-architecture.md` in `.specweave/docs/internal/architecture/adr/` (reference only).

## Questions Deferred to Implementation

- Should the "missing link but provider enabled" case be a warning (stderr) or a hard error (non-zero exit)? Current proposal: warning, but pushed into `result.syncErrors` so CI can assert on it.
- Should we add a new `externalLinks.jira.issueKey` (distinct from `epicKey`) for non-epic JIRA types? Deferred — current fix covers the Epic case; Story / Task linking is follow-up.
