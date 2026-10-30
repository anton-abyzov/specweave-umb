# Fix review state grouping

## Problem

The project Threads pane mislabels agent work as work for the person (Anton's report and screenshot, October 26, 2026).

Evidence, source `origin/main` `5f78002d81` of `anton-abyzov/specwithcode-dev`, live state read through `studio_thread_read`/`studio_thread_list`:

1. Red "Needs review" under Idle. `Muse approval check (Accept) - 0922` (`mcp:477cbdbf-da49-4ce1-9f94-91c266d59e05`), agent-created, run failed at 03:38:44 UTC October 27 with the provider-incapability error "This provider cannot use additional project folders under the current permissions…" (`ProviderFailure.ts:223`, `unsupported_provider`). Its owning sweep relaunched the check outside the project and resolved this thread at 03:40:50 UTC. `threadStatusWord` maps any failed run to "Needs review" (`apps/web/src/studio/shellModel.ts:584`, tone label `:595`), a phrase that asks the reader to act, while `projectThreadGroup` deliberately keeps failures out of attention (`packages/shared/src/projectAttention.ts:1`, "User action is independent of activity, failures…"), so the row lands in Idle. The label and the bucket disagree.
2. "Answer needed · <subagent>" under Waiting on you. `Close increment 1054`, `Fresh-context close review 1041` (October 25) and `Code check for DB recovery path` (October 21) are finished native Claude Code subagents (`relationshipToParent: "subagent"`, `pendingRequestCount: 0`). Each final result, returned to its parent agent, ends with a `**Blockers:**` paragraph. `observeProjectThread` turns any quiet thread's `reportedBlocker` into an `input` request (`packages/client-runtime/src/state/projectAttention.ts`), and `aggregateProjectAttention` folds subagent requests into the root, so the parent worker is listed under Waiting on you even while it runs. A subagent never receives a user message, so the notice never clears (October 21 still shown October 26).

## Scope

In: web/desktop row word and tone label for failed runs; subagent report blockers excluded from project attention; focused tests and a headless fixture screenshot. Out: iOS label parity (existing iOS owner), server-side `reportedBlocker` derivation, notifications, any change to real pending approvals, questions or sign-ins, thread lifecycle writes (no thread is woken, settled or stopped), merge, release or install.

## Acceptance Criteria

- [x] AC-01: A failed, unresolved thread reads "Run failed" (red tone) under Idle, never "Needs review"; a usage-limit failure still reads "Usage limit reached"; a resolved failed thread is under Resolved with no word.
- [x] AC-02: A real pending approval, question or sign-in on a root or on any of its subagents still puts the root under Waiting on you with the same words as today.
- [x] AC-03: A subagent whose final report carries a blocker adds no attention to its root: the root is grouped by its own state (Working while it runs, Idle when quiet), project counts exclude it, and no "Answer needed · <subagent>" word is shown.
- [x] AC-04: A root thread's own report blocker still puts it under Waiting on you as "Blocked" (receipt and #831 protections unchanged).
- [x] AC-05: Headless fixture screenshot of the Threads pane shows the failed row under Idle as "Run failed" and the parent of a blocked subagent outside Waiting on you.

## Approach

`apps/web/src/studio/shellModel.ts`: failed word and `THREAD_TONE_LABELS.failed` become "Run failed"; grouping unchanged (failures stay out of attention by design, no new bucket). The row's error snippet already names the provider limitation.

`packages/client-runtime/src/state/projectAttention.ts`: `observeProjectThread` adds the report-blocker request only when the thread is not a subagent (`lineage.relationshipToParent !== "subagent"`). The parent agent reads the subagent's report and decides; if the person is needed, the parent's own report carries the blocker. Native pending requests are untouched.

Rejected: moving failed runs to Waiting on you (contradicts the attention contract and would page Anton for agent-owned failures); a new "Needs review" bucket (the brief asks for consistent states, not another group).

Risk: a subagent whose parent ended without relaying a user decision. Mitigation: the parent's own final report is what the person reads; that path (AC-04) is kept.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Failed-run word → "Run failed" (reversible copy change).
- D-02 Subagent report blockers → parent agent only; real native requests still bubble.
### Open
- none

## Tasks

### T-01 Failed runs read "Run failed" under Idle
- AC: AC-01 | Files: apps/web/src/studio/shellModel.ts, apps/web/src/studio/shellModel.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1094-review-state-grouping/apps/web && ../../node_modules/.bin/vp test run --project unit src/studio/shellModel.test.ts

### T-02 Subagent report blockers stay with the parent agent
- AC: AC-02, AC-03, AC-04 | Files: packages/client-runtime/src/state/projectAttention.ts, packages/client-runtime/src/state/projectAttention.test.ts, apps/web/src/studio/shellModel.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1094-review-state-grouping/packages/client-runtime && ../../node_modules/.bin/vp test run src/state/projectAttention.test.ts

### T-03 Headless screenshot, typecheck, PR
- AC: AC-05 | Files: apps/web/tests | Test: headless Playwright fixture screenshot saved under /Users/antonabyzov/.specwithcode/m4/evidence/1094-review-state-grouping/

### T-04 Verify and close 1094
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: .specweave/increments/1094-fix-review-state-grouping/ | Test: specweave verify 1094
