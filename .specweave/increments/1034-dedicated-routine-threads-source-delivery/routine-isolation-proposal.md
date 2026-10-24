---
title: Quiet routines with durable threads
status: proposal awaiting review
increment: 1034
date: October 24, 2026
scope: research and design only
---

# Quiet routines with durable threads

Run each background routine in its own durable thread. Render its progress as application state in the right panel. Send the coordinator only an actionable escalation or a result the user requested. A UI filter cannot undo provider ingestion.

## Evidence and delivery boundaries

Inspected retained source at `f89d09bc9117dd299d811c44eccc1258908cf65a`, clean checkout `/Users/antonabyzov/.specwithcode/m4/worktrees/routine-own-threads`. GitHub readback: PR https://github.com/anton-abyzov/specwithcode-dev/pull/649 is OPEN, not merged. Latest published release readback is `v1.0.75`. Its tagged scheduler still sends unbound routines without ownThread through the coordinator. Installed app/service version and actual schedule bindings were not queried; the supplied screenshot proves repeated coordinator turns in that captured session, not current installation identity.

- `/Users/antonabyzov/.specwithcode/m4/worktrees/routine-own-threads/apps/server/src/scheduledTasks/ScheduledTaskService.ts:874`: sends scheduled text as a queued thread message. Lines 903–962 launch/reuse dedicated threads under project admission. Lines 967–971 label successful dispatch succeeded, before provider completion. Dispatch exclusion is not a whole-turn overlap policy.
- `/Users/antonabyzov/.specwithcode/m4/worktrees/routine-own-threads/apps/server/src/scheduledTasks/ScheduledTaskOwnThread.ts:23`: unbound/coordinator-bound routines normalize to ownThread; explicit workers remain bound. Replacement and compare-and-set binding protect thread identity.
- `/Users/antonabyzov/.specwithcode/m4/worktrees/routine-own-threads/apps/server/src/scheduledTasks/ScheduledTaskAdmission.ts`: project ownership fences, paused/archive state and destination validation remain authoritative.
- `/Users/antonabyzov/.specwithcode/m4/worktrees/routine-own-threads/apps/server/src/orchestration-v2/ProviderTurnStartService.ts:1171`: message.text becomes provider userText; at line 1431 it is passed to startTurn alongside handoff context. Collapsing a scheduled card does not change this.
- `/Users/antonabyzov/.specwithcode/m4/worktrees/routine-own-threads/apps/server/src/orchestration-v2/ContextHandoffService.ts:104`: user/assistant messages are eligible for summaries; legacy import also retains them. `/Users/antonabyzov/.specwithcode/m4/worktrees/routine-own-threads/apps/server/src/orchestration-v2/ContextHandoffDelivery.ts:76` deduplicates historical items by ID, not routine semantics. Already-ingested native history is not removed by changing future dispatch.
- `/Users/antonabyzov/.specwithcode/m4/worktrees/routine-own-threads/apps/server/src/channels/TelegramChannel.ts:494`: dedicated routine results can still forward to Telegram. Coordinator silence alone is not a channel delivery policy.

No new product tests were run: this is a proposal, not implementation acceptance. Historical source tests are not installed proof. Installed CLI was 3.1.7; registry stable was 3.1.9; read-only task inspection used session-local 3.1.9. Existing increment 1034 has unfinished ledger tasks; this proposal does not close or overwrite them.

## Alternatives researched

| Choice | Context isolation | Trade-off |
|---|---|---|
| Collapse/hide scheduled cards | No | Same provider turns and history, less visible evidence |
| Coordinator forwards every tick | No | Extra model turn and two conversations per run |
| Fresh thread for every tick | Yes | Loses continuity and floods thread list |
| Durable routine thread plus status events | Yes | Requires explicit occurrence and notification state; recommended |

Kubernetes documents Allow/Forbid/Replace concurrency policies and warns that jobs must tolerate duplicate scheduling: https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/ . Adopt explicit concurrency semantics and idempotency, not cancellation/replacement of active work.

Grafana separates alert evaluation from notification grouping and timing: https://grafana.com/docs/grafana/latest/alerting/fundamentals/notifications/ . Adopt transition-based attention episodes; routine polling is not itself a notification.

## Proposed behavior

### Destinations and migration

Separate schedule timing from purpose: background routine, command watch, or explicit follow-up/reminder. All background routines use a dedicated durable thread. Explicit worker follow-ups, including a one-shot release trigger, stay with their existing owner; do not manufacture a second release worker. An explicitly requested coordinator reminder may reach the coordinator once. Cadence alone cannot distinguish those cases.

For legacy coordinator bindings, first produce a migration preview with old destination, intended destination, active run and pending occurrences. Preserve schedule ID, cadence, disabled state, prompt, model policy, runtime permissions, worktree and delivery preferences. Do not enable anything. Already-dispatched occurrences drain at their existing destination; only undispatched occurrences can move atomically. If the coordinator previously forwarded to an existing routine worker, reconcile that worker using stored dispatch/relationship evidence before launching anything. A matching title or LLM guess is insufficient. Ambiguous cases stay held for a visible destination choice. PR649's automatic normalization is a foundation, not proof that this existing-worker reconciliation is solved.

A dedicated routine thread preserves its own history and bounded routine brief, without copying the coordinator transcript. Missing/archived routine threads can be replaced only under the existing project admission rules, with a link to prior history. Stopped threads retain Stop; a later tick must not release their held queue. An unavailable explicit worker does not silently become a new worker.

### Scheduling and overlap

Persist occurrence identity from schedule ID, generation and intended fire time, independently of transport retry. Keep current deterministic command/message identities and compare-and-set binding. Track checking, queued, running, waiting for approval, deferred, succeeded, failed, cancelled and coalesced separately. A successful enqueue is queued, never completed.

For recurring background work: one active occurrence per routine and at most one pending repeat. Further ticks update that pending repeat's last-due time and count; they neither steer the running turn nor append prompts to its provider queue. After terminal completion, execute one fresh repeat if still enabled and admissible. For cheap state watches, skip the overlapping check and evaluate fresh at the next tick. For one-shot release triggers and explicit follow-ups, retain the exact due occurrence and existing retry/deadline semantics; never discard it under a generic recurring coalescer. No cancellation/replacement of a running operation.

Manual Run now during active work offers Open running thread; a requested extra run must explicitly queue once. Recovery reconciles occurrence IDs with accepted messages and terminal runs before retrying. An uncertain send is reconciled, not blindly resent. Side-effecting external operations still need their own idempotency keys; exactly-once delivery is not promised.

### Right panel and attention

One row per routine: name, machine, current state, last outcome, next run, unread result marker, Open thread. A running row updates in place; it does not reorder the ordinary conversation list each hour. Example: “Disk space watch · M4 · Checking · next 2:55 PM”. Expanded history lists every occurrence, including skipped/coalesced runs. The panel is backed by application projections, not chat messages.

Quiet completion updates last-checked time without a toast, unread increment or coordinator turn. A new substantive report marks one unread result. Opening the report acknowledges that result only; opening the panel does not mark every thread read. An unresolved approval remains actionable after being read. Device read cursors and shared action resolution are distinct.

Example: “Disk space watch · Needs approval · Review 3 candidates”. Opening it navigates to the routine thread and the original approval request. It grants no cleanup authority. Example coordinator escalation, only when coordination is actually needed: “Release blocked by disk capacity on M4; owner needs a release-order decision. Open disk watch.” Do not send “Started the next run”, heartbeat confirmations or duplicate completion summaries.

### Escalation and channels

Default policy: quiet success; one actionable episode for approval, exhausted failure or a material change requiring intervention. Retryable failure shows Retrying in the panel without waking the coordinator. A critical safety condition may notify immediately; other errors follow explicit retry policy. Repeated identical errors update one episode. Recovery resolves it and withdraws stale actions. User approval goes directly to the user, not to a coordinator that cannot approve on the user's behalf.

Reuse increment 1036's notification episode/action classifier, current-action revalidation, withdrawal, settings and environment-scoped deep links. Do not create another OS dispatcher or an independent unread/error classifier. The owner was contacted through the existing thread; agreement is pending. Preserve existing Telegram delivery settings until explicitly reviewed; propose applying the same episode policy across channels, with one receipt per episode/channel, without silently disabling an authorized report destination.

Only structured events explicitly classified as coordinator escalation, or a user-requested result, may produce a coordinator message. Provider input, portable handoff history, summaries and context assembly must exclude routine status events by construction. A coordinator explicitly asking for a report may retrieve that report; no routine status feed is injected on every coordinator turn.

### Existing polluted history

Prevent new pollution first. Do not delete messages or reset native provider sessions. Mark reliably attributed historical routine turns and forwarding receipts as operational history for future portable context assembly, while retaining audit access. Mixed user/decision content must remain. Removing prior native-provider context requires a deliberate fresh context/compaction operation with a reviewed summary preserving decisions and authorizations; it is not accomplished by the panel change and is not authorized here.

### Cross-machine and safety

Canonical identities include project/environment, schedule generation, occurrence and ownership epoch. Dispatch rechecks the current owner under project admission immediately before posting, including after slow command checks. Project transfer fences the previous machine. The current binding decides execution location; viewing another machine never migrates or duplicates work. Unreachable ownership is Unknown/deferred, not permission to run locally. Deep links include environmentId and threadId. Do not combine separately authorized schedules just because titles match.

Permissions, exact owner clearance for cleanup, model/provider selection, prepare-only restrictions, Stop/paused state and spending authorization are unchanged. Prefer read-only command checks for deterministic disk thresholds, but do not rewrite an existing cleanup routine into a threshold watch without reviewing the changed purpose. Physical APFS capacity reporting must retain the existing non-additive volume rule.

## Acceptance criteria for a follow-up implementation

- AC-P01: 24 quiet hourly ticks produce zero coordinator messages, zero coordinator provider starts and zero routine-status entries in coordinator handoff/summary payloads.
- AC-P02: Legacy migration reuses a proven existing worker; ambiguous ownership is held; in-flight delivery, schedule edits and retries cannot create duplicate workers or deliveries.
- AC-P03: A two-hour active routine receives no queued hourly prompts and has at most one coalesced pending repeat; a one-shot release trigger still reaches its exact owner once.
- AC-P04: Queued/running/terminal state reflects the provider lifecycle, including restart, failure, approval, provider deferral and cancellation; dispatch alone cannot show success.
- AC-P05: Repeated approval/failure observations yield one current episode per channel; resolution withdraws it; read acknowledgement never grants approval or releases Stop.
- AC-P06: Right-panel states and environment-scoped navigation pass headless desktop/mobile light/dark fixtures; every occurrence remains inspectable.
- AC-P07: Transfer during a slow check, stale owner, offline machine and retry-after-uncertain-send produce no duplicate dispatch; all existing authorization gates still refuse prohibited actions.
- AC-P08: Existing routine history remains readable; new portable coordinator context omits attributable operational noise without losing user decisions. Native history limitations are shown honestly.

## Proposed work sequence, not authorized implementation

1. Agree the event/action boundary with 1036 and the existing project-attention owner; finalize occurrence and destination-purpose contracts.
2. Extend scheduler lifecycle and migration reconciliation in the retained routine ownership lane, with fault-injected scheduler/provider-capture tests.
3. Build panel projection and history/unread behavior; reuse notification components owned by 1036.
4. Test zero coordinator ingestion at actual adapter boundaries, portable history, retries, coalescing and two-machine ownership faults. Run headless UI fixtures with headless:true, PWDEBUG=0 and PLAYWRIGHT_HTML_OPEN=never; save artifacts.
5. Fresh-context review, source/CI proof, then separately authorized release and installed acceptance. Do not claim those from mockups.
6. Verify and close 1034.

The existing 1034 spec and ledger remain unchanged. Before implementation, turn these proposed criteria into owned tasks, reconcile the unfinished source-delivery ledger and any follow-up increment split, and obtain review of this expanded scope. No live schedules, app source, release, service or provider sessions changed during this investigation.
