<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=57332fff4e9d60172f848c872d92e43e32788028 at=2026-11-20T01:25:00.151Z -->
# Review: 1427 T-05 coordinator-message receiver, round 6
Verdict: fix first

Reviewer context: fresh cross-family review of `anton-abyzov/specwithcode#757`. The reviewed range is `db9e99cc5a216c62913e2b6ae5ffc57a2792c5c0` to `57332fff4e9d60172f848c872d92e43e32788028`. Source citations are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode` at that head.

Two of the three round-5 fixes hold. Session renewal cannot extend the presenting credential's signed expiry, and a busy provider with a live turn owner no longer puts a start-only run back in the queue. The deadline check moved past planning, but not past the waits inside the durable write. Three other paths can deliver without current authority.

| # | Severity | File | Lines | Vulnerability | Confidence |
|---|----------|------|-------|---------------|------------|
| 1 | 🟠 HIGH | `apps/server/src/orchestration-v2/EventSink.ts` | 255-283, 894-920 | The transaction can commit the peer message after the deadline checked by its caller. | 10/10 |
| 2 | 🟠 HIGH | `apps/server/src/orchestration-v2/RunExecutionService.ts` | 1710-1730, 1777-1809 | The checked session call can wait or resend before the actual provider offer, without carrying the deadline. | 10/10 |
| 3 | 🟠 HIGH | `apps/server/src/orchestration-v2/EffectOutbox.ts` | 380-425 | A pending start can outlast non-time revocation and deliver without a fresh authority check. | 10/10 |
| 4 | 🟠 HIGH | `apps/server/src/orchestration-v2/startOnlyDispatch.ts` | 125-141 | Recovery can check a newer queued run instead of the failed run whose message it resends. | 9/10 |

Below, `V` means `apps/server/src/orchestration-v2`, `O` means `V/Orchestrator.ts`, `X` means `V/RunExecutionService.ts`, and `R` means `apps/server/src/project/CoordinatorMessageReceiver.ts`.

## [high] `V/EventSink.ts:255-283` can wait inside the transaction after the deadline check

`O:13661-13684` checks the clock after planning, under the thread lock, then calls `commitCommand` without supplying the deadline. The sink reserves the receipt, appends events, applies projections, enqueues the start and writes the acceptance (`V/EventSink.ts:824-841,894-920`). It acquires a shared publication permit before the transaction commits (`:255-283`). If the deadline passes during that wait, the message can become durable on the coordinator thread without authority. Refusing the subsequent provider start cannot undo that delivery. Enforce the deadline inside the transaction after contended waits, so expiry rolls back the message, effect and receipt together.

## [high] `X:1777-1809` checks the deadline before the actual provider offer

Outer retries do recheck the clock. But `turnInput` does not carry the deadline (`X:1710-1730`), and the session wrapper can still prepare a handoff and write receipts before calling the adapter (`V/ProviderTurnStartService.ts:1681-1689,1735-1789`). In the Codex adapter, pending restores are awaited before `turn/start`; the adapter can also resume a thread and resubmit internally (`V/Adapters/CodexAdapterV2.ts:1982-1985,6417-6447,6533-6539,7001-7007`). A first effective offer after either wait can be past the signed deadline, even on an otherwise idle thread. Carry the deadline to outbound submission and recheck it on adapter-local resubmissions.

## [high] `V/EffectOutbox.ts:380-425` can defer first delivery without reauthorization

The outbox orders work behind earlier pending or running effects. Its claim checks availability and ordering, not time since the receiver last authorized the message (`V/EffectOutbox.ts:380-425,678-715`). The worker's execution timeout starts after claim (`V/EffectWorker.ts:53-58,280-303,889-897,942-947`). The receiver's five-minute timer does not run while the run remains `starting`, and its rows are excluded from due sends (`R:903-921,1003-1008`). When claimed, the start worker accepts that run state (`V/ProviderTurnStartService.ts:431-451`).

There is no maximum pending age independent of the original credential deadline. If the sender's grant is revoked during an outbox backlog while the original time bound is still ahead, the **original** effect can make the first offer. It does not need a duplicate send or a retry from the receiver. This is the deferred revocation window excluded by the brief. Invalidate deferred starts or reauthorize the exact sent revisions when claiming one.

## [high] `V/startOnlyDispatch.ts:125-141` checks the wrong source run for some recoveries

Explicit restart checks the named run. Other recognized recovery commands choose the thread's greatest run ordinal, including held queued runs. The recovery worker's projection excludes held queued runs when choosing its source (`V/ProjectionStore.ts:6296-6306`; queue allocation and hold at `O:6527-6529,6605-6615,2041-2063`). Those two selections need not name the same run.

A context handoff can fail before the provider start (`V/ContextHandoffDelivery.ts:205-226`; `V/ProviderTurnStartService.ts:1681-1684,1774-1789`). Context fallback retains the failed run's message text and builds a new dispatch without its start-only restriction or deadline (`V/contextOverflowFallback.ts:99-137`; `V/unopenableFallback.ts:319-356,365-376`; `V/ProviderFallbackWorker.ts:2309-2311`). A later held ordinary run can therefore satisfy the check at `O:5890-5895` while the content comes from the earlier, unoffered peer run. Bind the guard to the actual source run. Leave any new attempt for an unoffered peer message to the receiver.

## Round-5 fixes and lifecycle table

**Signed expiry: fixed.** Verification returns `claims.exp` (`apps/server/src/auth/SessionStore.ts:1070-1097,1117-1131`). Authentication and the route forward that value (`apps/server/src/auth/EnvironmentAuth.ts:1629-1641`; `apps/server/src/handoff/handoffRoute.ts:325-335`). The receiver keeps it with the admitted revision, including replacement on merge (`R:677-689,722-735,783`). `R:943-955,991-995` requires both the signed and current session expiry to be in the future, refuses missing evidence and takes the minimum with the grant end. The updated route-parity table reflects this change; no regression was identified in the prior device, reach, membership or revision checks.

| PR lifecycle row | Result at the reviewed head |
|---|---|
| Receiver send | `R:1070-1081,1093-1115` rechecks every selected row, takes the minimum finite deadline and sends `queue` with `startOnly: true`. `V/ThreadManagementService.ts:604-627` forwards both restrictions and does not steer. |
| Initial dispatch | `O:13735-13760` takes the thread lock. `O:6174-6182,6489-6506,13577-13590` refuses an expired or would-queue start without recording a rejection receipt. |
| Planning | Both immediate-run constructors keep the restriction and deadline (`O:7003-7025,7699-7725`). The start worker loads and spreads that run (`V/ProviderTurnStartService.ts:435-445,1253-1257`). |
| Commit | `O:13661-13684` fixes expiry **during planning**, but not inside the transaction. Finding 1. |
| Effect outbox wait | The run remains `starting`, not `queued`. That does not bound the wait before first offer. Finding 3. |
| Provider start and retries | `X:1695-1705,1777-1809` guards the outer session call and its retries. Adapter preparation and adapter-local resubmission are missing from the table. Finding 2. |
| Provider busy with a live owner | Fixed. Ownership is read at `V/ProviderTurnStartService.ts:332-348`; `X:1589-1593` fails a start-only run before the queue write at `X:1648-1664`. Unknown ownership also refuses (`X:1678`). That branch never feeds `startNextQueuedRun` (`O:1937-1962,13812-13828`). |
| Failure before offer, then recovery | The continuation classes are recognized, and provider-turn evidence is tied to attempts of the inspected run (`V/QueueFollowsThread.ts:20-34,53-68`; `V/startOnlyDispatch.ts:87-106,125-142`). The actual recovery source can differ from the inspected run. Finding 4. |
| Restart or update while starting | The table's replay claim is incorrect for process loss: `provider-turn.start` is process-bound and cancelled, not replayed (`V/EffectOutbox.ts:159-176,643-671`; `V/ProviderRuntimeRecoveryService.ts:619-625`). Restart checks for a live provider turn; update continuation skips an unoffered start-only run (`V/RestartContinuation.ts:52-66,96-106,152-179`). This discrepancy is fail-closed. |
| Stop while starting | Without a recorded provider turn, stop interrupts the run and cancels outstanding start/restart effects (`O:11234-11240,11317-11349`). |
| Receiver after send | `started` alone is not delivery. `R:1140-1151` saves thread, run and sent revision; `R:718-733,1003-1008` excludes those rows from merges and due sends. Settlement at both flush boundaries requires provider-turn evidence for a matching attempt (`R:892-921,1000-1002,1151`). |

**Receiver retry: no separate authority bypass found.** A terminal run with no recorded turn schedules a retry five minutes later and increments the attempt (`R:320-323,903-921`). When due, the receiver derives new command and message IDs and performs both per-row checks (`R:1022-1034,1070-1098`). A missing run or projection is not permission to resend. A duplicate if the original provider took the prompt without a recorded turn is an integrity follow-up, not a fifth blocker. The previously committed effect retaining stale authority is finding 3, not a failure of the new receiver attempt.

## Scope and evidence

This verdict covers T-05 receiver authority, not the sender outbox, reference reads, UI or release. Round 5's device, reach, membership and revision findings stand except where this delta changes their effect. A non-time revocation during immediate dispatch on an idle thread is accepted; a deferred start that can later use stale authority is not. Duplicate delivery alone is not a security blocker.

The delta consists of `9fc782003` (tests), `ca4d4ea11` (implementation) and `57332fff4` (format and restart-hook cleanup), across 15 files. `git diff --check` was clean. No checkout, install, build or local test run. There was no increment verification report. The live PR head matched the reviewed commit; CI was still running when inspected.

Four changed files were already over 1,500 lines: `apps/server/src/auth/EnvironmentAuth.ts` (1,904 to 1,907), `V/Orchestrator.ts` (14,334 to 14,359), `V/RunExecutionService.ts` (1,950 to 1,956), and `packages/contracts/src/orchestrationV2.ts` (4,527 to 4,531). No file crossed the threshold. No newly added real person's name, identifying hostname or private filesystem path was found in the patch.
