# Routines wait while an automatic update installs

## Problem

On November 17, 2026 (22:52 EST) m4's first automatic install, 1.0.338 to 1.0.344, refused before the restart with `AssertionError: Guarded prestate changed: rows` (receipt `~/.specwithcode/m4/updates/receipts/update-1.0.344-20261118T034729987466Z.json`, phase `preflight`, pointers unchanged). The app showed "Could not install SpecWithCode 1.0.344".

An automatic install runs unheld. The agent takes an admission snapshot, then the helper does its own full before read (03:47:32 to 03:49:39 UTC) and a prestate re-read. The install gate goes up only after that. Two routines with pre-run checks fired in between: "Disk space guard" (every 5 minutes) at 03:48:15 and "New Relic repair watch" (every 30 minutes) at 03:49:11. Each fire rewrites its `scheduled_tasks` row (`last_run_at`, `next_run_at`, `updated_at`, `run_count`). That table is compared exactly, so the guard refused. That is correct behaviour for the guard. The bug is that the scheduler keeps firing while the agent reports `installing`. With a 5-minute routine, an automatic install on a large database fails most of the time, and after one refusal the agent waits for Install now.

Installs started with Update now are not affected, because `runTask` refuses while the service is held. Evidence: `~/.specwithcode/m4/evidence/update-1.0.344-prestate-refusal/`.

## Scope

In: while the update agent reports `installing` (fresh, within the apply timeout), the scheduler's tick does nothing. It starts no routine, follows or prunes no occurrence, and expires no finished routine. A due routine stays due and fires on the first tick after the install. Out: the update guard itself, which stays byte-exact; moving the install gate earlier; the agent's retry policy.

## Acceptance Criteria

- [ ] AC-01: While the agent state says `installing` and was written within `AGENT_APPLY_TIMEOUT_MS + AGENT_RETRY_MS`, a scheduler tick writes no `scheduled_tasks` or occurrence row, and a due routine is still due afterwards.
- [ ] AC-02: Once the status leaves `installing`, or an `installing` state is older than that bound (a dead agent), the next tick fires the due routine as before.
- [ ] AC-03: Services built without an update hold (tests, tools) and fakes of the hold shape behave as before.

## Approach

`apps/server/src/serviceUpdate/ServiceUpdateHold.ts` gains `automaticInstallApplying` (optional on the shape, so existing fakes compile; `false` in the view when absent). It reads the agent state: status `installing` and `updatedAtMs` within the apply bound. `ScheduledTaskService.runDueTasks` returns at once while it is true.

Version skew: the fix protects installs from the release that ships it onward. m4's next install still runs on the 1.0.338 service, so that install can race again unless it runs held (Update now).

Rejected alternatives:

- Exempting `scheduled_tasks` run-state columns from the guard: this weakens it.
- Writing the install gate before the before read: this refuses a person's messages for minutes.
- Deferring by rewriting `next_run_at`: that is itself a write the guard sees.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Gate on agent status `installing` only, not `waiting-for-quiet`, which can last hours. Reversible.
### Open
- none

## Tasks

### T-01 Scheduler waits while an automatic install applies
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/serviceUpdate/ServiceUpdateHold.ts, repositories/anton-abyzov/specwithcode/apps/server/src/scheduledTasks/ScheduledTaskService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/scheduledTasks/ScheduledTaskService.installWait.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/serviceUpdate/ServiceUpdateHold.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/scheduledTasks/ScheduledTaskService.installWait.test.ts apps/server/src/serviceUpdate/ServiceUpdateHold.test.ts
