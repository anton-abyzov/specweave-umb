# Recover runs closed by update drains and label interrupts by cause

## Problem

On October 23, 2026 the update-measure-1075 launchd job ran `prepare-update --stop-work --hold` six times with no update pending, so every hold was refused. In S3 (14:36:09-52 UTC) the stop round finished child tasks, their "Delegated task finished" wake-ups started parent turns at 14:36:22, and the drain's `clearLeftovers` then released busy sessions with `releaseIdle({ includeBusy: true })`. That release failed each event subscriber with `ProviderAdapterEventStreamError: Closed to install the SpecWithCode update.`, so 11 runs ended `failed` with "The provider event stream closed unexpectedly". Both recovery paths skip `failed` runs, so nothing continued them (the nine 1011 relays, `console-workspace-presets-resume`, two coordinators).

Separately, every `run_interrupt_result` said "Run interrupted by user", whatever stopped the run. The EasyChamp "Flyer Style Review" thread showed it on turns the service update stopped, which read as a user Stop.

Evidence: `~/.specwithcode/m4/evidence/update-measure-1075/recovery/receipt.md`, `~/.specwithcode/m4/stdout.log` at 10:36:35 EDT.

## Scope

In: the drain's busy-session release ends streams instead of failing them; the interrupted result records and shows its Stop request's cause; clients stop showing the old always-"by user" text. Out: resuming the affected threads (owners do that), a release, a drain that ends without a restart continuing its runs (still needs a restart).

## Acceptance Criteria

- [x] AC-01: A turn cut by the update drain's session release ends with its stream closed (not failed), is marked interrupted with cause `service_update` by `finalizeStuckRuns`, and is continued once after the restart.
- [x] AC-02: A run the user asked to stop, left running by its provider, stays interrupted with cause `user` through the same drain and is never continued.
- [x] AC-03: An interrupted run's result names its request's cause (update, user, agent, coordinator, none), and web, mobile and MCP show no attribution for the old "Run interrupted by user" text.

## Approach

`ProviderSessionManager.releaseIdle` gains `endStreams`, which releases with `gracefulSubscribers` (queues end, published events drain). `ServiceUpdatePreparation.clearLeftovers` passes it. The ingest fiber then returns with no terminal, and the run stays running until `finalizeStuckRuns` marks it interrupted for the update. The watchdog does not race this: a service update release sends no released-session signal and orphan settling needs 2 quiet minutes.

`makeInterruptResultTurnItem` takes the cause, from `runInterruptRequestCause` (latest request, no cause = user, no request = null): `ProviderTurnStartService` reads it for `RunExecutionService`, and `Orchestrator.settleInterruptedRun` uses its projection plus this command's pending items. Contracts gain `cause` on the result item, `runInterruptResultMessage` and `runInterruptResultDetail`.

Rejected: treating a failed run with an unpaired request as interrupted (a real provider failure would be continued); a projection migration for old items (projections can be replayed).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Old result items show no detail rather than a guessed cause (reversible).
### Open
- none

## Tasks

### T-01 Drain release ends streams instead of failing them
- AC: AC-01, AC-02 | Files: apps/server/src/orchestration-v2/ProviderSessionManager.ts, apps/server/src/serviceUpdate/ServiceUpdatePreparation.ts, apps/server/src/orchestration-v2/UpdateContinuation.integration.test.ts | Test: vp test run apps/server/src/orchestration-v2/ProviderSessionManager.test.ts apps/server/src/orchestration-v2/UpdateContinuation.integration.test.ts apps/server/src/serviceUpdate/ServiceUpdatePreparation.test.ts

### T-02 Label interrupt results by cause
- AC: AC-03 | Files: packages/contracts/src/orchestrationV2.ts, apps/server/src/orchestration-v2/RunExecutionService.ts, apps/server/src/orchestration-v2/Orchestrator.ts, apps/server/src/orchestration-v2/ProviderTurnStartService.ts, apps/web/src/components/chat/V2LifecycleRow.tsx, apps/web/src/components/chat/MessagesTimeline.tsx, apps/mobile/src/lib/threadActivity.ts, apps/server/src/mcp/OrchestratorMcpService.ts | Test: vp test run apps/server/src/orchestration-v2/RunExecutionService.test.ts packages/contracts/src/orchestrationV2.test.ts

### T-03 Ship: PR, review, green CI, merge
- AC: AC-01, AC-02, AC-03 | Files: none | Test: gh pr checks

Verify and close 1028.
