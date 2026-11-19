# Cancel live approvals when a selection switch detaches the session

## Problem

Found by the 1004 review (R27, `~/Projects/github/studio-research-notes/t3-v2-orchestrator-review/context-switch-audit.md` section "Confirmed manager defect"). When a thread waits on a live approval and the user switches its provider or model with the direct selection command, detach removes the thread from `attachedThreadIds` (`apps/server/src/orchestration-v2/ProviderSessionManager.ts:2428`) and then releases the now-unused exclusive session (line 2498). The release finalizer (line 789) only walks the released entry's remaining attachments, which are now empty, and the projection's `provider-session.detached` case (`ProjectionStore.ts:2353`) only deletes the binding. The approval stays `pending` with `responseCapability: "live"` although its callback is gone. Lines are at specwithcode-dev `ab96f4d1c`. Upstream T3 has the same shape (`ProviderSessionManager.ts:2410`, `:2457`, `:646` at `18e2742519`).

Repro (isolated, no provider or service): copy `~/Projects/github/studio-research-notes/t3-v2-orchestrator-review/probes/ProviderSessionManagerDetach.audit.test.ts` into `apps/server/src/orchestration-v2/` of a main checkout, then run `pnpm exec vp test run apps/server/src/orchestration-v2/ProviderSessionManagerDetach.audit.test.ts --testNamePattern 'audit probe:'` on Node 22. Observed: `{"status":"pending","responseCapability":"live","node":"waiting","item":"waiting"}`, assertion at line 3888 fails. Receipt: `~/Projects/github/studio-research-notes/t3-v2-orchestrator-review/context-switch-approval-probe.log`. The installed UI symptom is unverified.

## Scope

In: detach of an exclusive session cancels (marks non-live) runtime requests owned by the detached thread and the old session. Out: transferring approvals to the new provider; shared-session threads; the chronology gap (1065).

## Acceptance Criteria

- [x] AC-01: The audit probe, moved into the regular session-manager suite, passes: after detach the request is no longer `pending`/`live`.
- [x] AC-02: Requests of a replacement session and of other threads on a shared session are untouched (new tests).
- [x] AC-03: The thread shows no stale approval after a Claude-to-Codex selection switch in a headless or installed check.

## Results

Fixed in PR 669 (merge `cf3d8e99a`), released in 1.0.378. Still reproduced on `origin/main` before the fix: on the tests-only commit the probe test, the retry test and the race test fail (`expected 'pending' to equal 'cancelled'`, `expected 'live' to equal 'not_resumable'`) and the selection switch test fails (`expected 'pending' to not equal 'pending'`); all pass in PR 669 CI.

- AC-01, AC-02: `ProviderSessionManager.test.ts` (probe, other-session request, failed-write retry sparing a replacement, a release that wins the race with detach, shared session).
- AC-03: headless command-level check in `testkit/ProviderSwitch.integration.test.ts` through `thread.model-selection.set`. Proof limit: the approval is injected as events (the test adapter has no approval flow) and the installed UI was not checked. A message started at once on Codex does not detach the Claude session (`Orchestrator.ts` near line 8043), so its approval keeps a live callback; not a stale record.
- Review: Copilot Enterprise `gpt-6.1-sol`, four rounds, ship at `f01da938e`.

## Approach

Carry `detachedThreadId` into the runtime-request cleanup set in the release finalizer, scoped to the old `providerSessionId` and a cutoff, as the background-roster cleanup already does. Port with the existing release test as the template.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Cancel rather than transfer the obsolete approval; the old callback cannot be resumed on another provider.
### Open
- none

## Tasks

### T-01 Fix detach request cleanup with tests
- AC: AC-01, AC-02 | Files: apps/server/src/orchestration-v2/ProviderSessionManager.ts, apps/server/src/orchestration-v2/ProviderSessionManager.test.ts | Test: pnpm exec vp test run apps/server/src/orchestration-v2/ProviderSessionManager.test.ts

### T-02 Check the switch end to end
- AC: AC-03 | Files: apps/server/src/orchestration-v2/testkit | Test: headless or installed Claude-to-Codex switch with a pending approval

### T-03 Verify and close 1064
- AC: AC-01, AC-02, AC-03 | Files: .specweave/increments/1064-cancel-live-approvals-when-a-selection-switch-detaches-the-session | Test: specweave verify 1064 and fresh-context review
