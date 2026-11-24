# Working list shows only live work and wakes stranded threads

## Problem

The project's Working section lists threads that have no live turn, and nothing tells them apart from threads that are running. Anton has to open each one to learn whether anything is happening.

Evidence, read on November 11, 2026 at 04:24 UTC from project `1332065e-795b-4f98-91c4-f114917e53f6` (7 Working rows in his screenshot):

| Row | Thread status | Live work behind it | Verdict |
|---|---|---|---|
| 1267 fix, 1268 inline media, download click counts | `running` | a turn | correct |
| Minisforum list not clickable | `running`, `completed` at 04:23 | a turn at screenshot time | correct |
| Release all platforms in 3 hours | `completed` (run 280) | delegated child `lup-232-fix-r1` running | correct, but reads like a live turn |
| Fix umbrella verify gate | `completed` (run 1) | background `specweave verify` PID 52426, session `ready` | correct wait, hollow dot |
| Complete project work and disk audit | `completed` (run 61, November 3) | none | **stale since October 21** |

The stale row: the thread holds an `app_owned` subagent record `running` for the child "Finish 0734 0748 0752 0850 0854". That child's last run was `cancelled` on October 20 at 14:50 UTC. The child itself still holds two `provider_native` subagent records `running` since October 20 ("Review 0854 before close", "Review 0734 and 0850 before close"). The coordinator in turn holds a `running` record for the disk audit thread. Three levels are held open by two records nothing will ever report on.

Root causes, in the `anton-abyzov/specwithcode` source:

1. **Settlement is edge-triggered, its gate is level-based.** `finalizeAppOwnedSubagent` (`apps/server/src/orchestration-v2/Orchestrator.ts:11935`) is the only writer that ends a parent's delegated record. It runs on a terminal `run.updated`, at startup, and after a declined restart continuation. It returns early unless `delegatedTaskProgress` is `result_available` (`apps/server/src/orchestration-v2/SubagentProjection.ts:260-280`), which is `waiting_for_children` while the child has any open subagent record, a `pending` or `claimed` delivery, or a non-empty background roster. Those clear later through `subagent.updated`, `turn-item.updated` and `provider-thread.updated`, and nothing re-runs the finalize then. Startup recovery hits the same gate, so the record survives restarts.
2. **No sweep covers `app_owned` records.** `StrandedSubagents.ts` runs every minute but only for `provider_native` records, and restart recovery leaves delegated rows open on purpose ("the child settles them", `ProviderRuntimeRecoveryService.ts:175`). The two `provider_native` records above have also survived three weeks of that sweep, on a child whose provider is `acpRegistry_copilot`; why is not yet known.
3. **A background roster outlives its process.** The Claude session is pinned while a roster entry exists, for at most 4 hours (`ProviderSessionManager.ts:89`). Releasing the session writes no roster clear, so the row says "Background command running" until a Stop, a new turn or a restart.
4. **`reportedWait` is text.** A last paragraph that says "waiting for review" keeps a row in Working with nothing behind it (`ProjectionStore.ts:2004-2016`).
5. **The list cannot show the difference.** `buildThreadPaneGroups` (`apps/web/src/studio/shellModel.ts:466`) puts a row in Working when `root.working || root.waits.length`. A wait is a string with no owner, no start time and no proof of life.

Not the cause: usage limits and held queues. A limit-stopped thread shows "Usage limit reached" under Idle, a held queue shows under Needs you, and the project has no queued or waiting run. Opening a thread starts nothing: `subscribeThread` streams data and `thread.visit` writes a read receipt only (`Orchestrator.ts:3135-3149`). What appears to "start" on open is the open thread counting its subagents from the full projection instead of the list shell (`apps/web/src/studio/threadSubagents.ts:295-299`), or a wake that was already due.

## Scope

In: settling delegated and background waits that no live process backs, re-running delegated settlement when the gate opens, a Working row that says what it waits on and since when, and one-time repair of records already stranded.

Out: usage-limit auto-resume, held-queue rules, restarting any work automatically, changes to `thread.visit`, and the left Sidebar's own Waiting rule beyond reading the same predicate.

## Acceptance Criteria

- [ ] AC-01: When a delegated child's last open subagent record, pending delivery or background roster entry clears and the child has no run in progress, the parent's `app_owned` record and turn item reach a terminal status within one sweep interval, without a server restart.
- [ ] AC-02: A sweep settles `app_owned` records whose child has no run in progress and no live provider session for two consecutive sweeps. A child whose latest run a person stopped settles as `cancelled` and its parent is not woken; any other ending settles as `interrupted` and the parent's next turn is told which task it lost.
- [ ] AC-03: The fixture of this incident (parent record `running`, child's latest run `cancelled`, child holding two `provider_native` records `running` on an ACP provider with no live session) ends with all three levels terminal and the parent out of Working.
- [ ] AC-04: Releasing a provider session clears that provider thread's `pendingBackgroundTasks` and records the lost work for the next turn, so "Background command running" never outlives its process.
- [ ] AC-05: A `reportedWait` with no open subagent record, roster entry or watched pull request behind it does not place a thread in Working.
- [ ] AC-06: A Working row with no live turn names what it waits on and for how long ("Waiting on Fix 1.0.232 Linux update proof hang · 12m", "Background command · 21m"), keeps the hollow dot, and the section header counts live turns separately ("Working 5 · 2 waiting").
- [ ] AC-07: No path in this increment starts a run on a thread whose latest run a person stopped or cancelled, and none starts a run on open.
- [ ] AC-08: On first start after the update, existing stranded records are settled by the same sweep; the three records named in Problem are terminal and "Complete project work and disk audit" leaves Working.

## Approach

1. `apps/server/src/orchestration-v2/StrandedSubagents.ts`: reproduce first. Find why the two `provider_native` records on the ACP child are skipped, fix it, then extend the sweep to `app_owned` records (child has no run in progress, no live session, two sweeps). Extend the `stranded-subagents` candidate query in `ProjectionStore.ts:685`.
2. `apps/server/src/orchestration-v2/Orchestrator.ts`: re-run `finalizeAppOwnedSubagent` for a subagent-lineage thread when a `subagent.updated`, `turn-item.updated` or `provider-thread.updated` event moves `delegatedTaskProgress` to `result_available`. Reuse the existing finalize; no second writer.
3. `apps/server/src/orchestration-v2/ProviderSessionManager.ts`: on `releaseEntry`, dispatch the existing `thread.background-work.settle` for the released provider thread. It already clears rosters that have no live session (`Orchestrator.ts:10105`).
4. `packages/client-runtime/src/state/projectAttention.ts`: `threadDependencyWait` returns a `reportedWait` only when the shell carries backing work; waits become `{ label, since, source }` instead of a string.
5. `apps/web/src/studio/shellModel.ts`, `apps/web/src/components/studio/shell/ThreadsPane.tsx`: render the wait's target and age, and the split header count.

Decisions: settle, never restart. A stranded wait means the work is gone, and restarting it is the owner's choice through the note its next turn receives. Rejected: reconciling on thread open, because it would make the list correct only for threads someone clicks, which is the bug.

Risks: a sweep that settles a child still starting. Mitigated by the existing two-sweep rule and the live-session check. Delegated completions arriving after a sweep settled the record must stay idempotent ("An earlier result is final", `ProjectionStore.ts:4212`).

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01 Stranded delegated work is settled and reported, not restarted → default (reversible).
- D-02 Waiting rows stay in Working with a hollow dot and an age, instead of moving to a new section → default (reversible).
- D-03 A background command row stays listed while its process lives, with no time limit → default (reversible).

### Open
- none

## Tasks

### T-01 Reproduce the incident and settle stranded delegated records
- AC: AC-02, AC-03 | Files: apps/server/src/orchestration-v2/StrandedSubagents.ts, apps/server/src/orchestration-v2/ProjectionStore.ts, apps/server/src/orchestration-v2/StrandedSubagents.test.ts | Test: bun run test apps/server/src/orchestration-v2/StrandedSubagents.test.ts

### T-02 Re-run delegated settlement when the gate opens
- AC: AC-01, AC-07 | Files: apps/server/src/orchestration-v2/Orchestrator.ts, apps/server/src/orchestration-v2/DelegatedCompletionDelivery.test.ts | Test: bun run test apps/server/src/orchestration-v2/DelegatedCompletionDelivery.test.ts

### T-03 Clear the background roster when a session is released
- AC: AC-04 | Files: apps/server/src/orchestration-v2/ProviderSessionManager.ts, apps/server/src/orchestration-v2/ProviderSessionManager.test.ts | Test: bun run test apps/server/src/orchestration-v2/ProviderSessionManager.test.ts

### T-04 Waits carry a source and a start time; text alone is not a wait
- AC: AC-05 | Files: packages/client-runtime/src/state/projectAttention.ts, packages/client-runtime/src/state/projectAttention.test.ts | Test: bun run test packages/client-runtime/src/state/projectAttention.test.ts

### T-05 Working rows say what they wait on and for how long
- AC: AC-06 | Files: apps/web/src/studio/shellModel.ts, apps/web/src/components/studio/shell/ThreadsPane.tsx, apps/web/tests/project-workspace/mocks.tsx | Test: headless screenshot of the project-workspace fixture with one running, one waiting-on-child and one background-command row

### T-06 Installed check on this project
- AC: AC-08 | Files: none | Test: specweave-studio db query "SELECT count(*) FROM orchestration_v2_projection_subagents WHERE status='running' AND updated_at < '2026-10-22'" returns 0 after the update, and the disk audit thread is out of Working
