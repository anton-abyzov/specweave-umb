# Routines follow the coordinator to the standby on takeover

## Problem

A routine lives only in the `scheduled_tasks` table of the machine that made it, and only that machine's scheduler fires it. Automatic coordinator takeover copies the goal, instructions and notes to the armed standby, but not routines. When the coordinator machine is off, its routines stop and nothing else runs them. After the old machine gives way, its coordinator-owned routines fail on every poll ("Routine coordinator has handed off ownership.") instead of resting. Daily and monthly runs missed while the host slept are skipped with only a log line, so the owner never learns a run was missed. Evidence: `ScheduledTaskService.ts` `runDueTasks`/`rescheduleMissedRun`, `ProjectLinkStandby.ts` `PeerReplicaContent` (goal, instructions, notes only), `ScheduledTaskAdmission.ts` fence.

## Scope

In:
- The coordinator's lease loop sends the project's coordinator-owned routines (definitions only) to the armed standby with the replica, plus a routines digest on every lease so edits travel.
- The standby keeps them as routines of its own copy, under the same ids, resting until it coordinates.
- A per-project firing gate for coordinator-owned routines, re-read before every fire from `CoordinatorRole.roleOf` and the coordinator wake fence.
- A visible note when a daily/monthly run is skipped because the host was off or asleep.

Out:
- Webhook routines: their URL tokens and signing secrets belong to one machine and are never copied.
- Routines bound to a worker thread (machine-local follow-ups).
- Run history and run state.
- The server-driven linked sync path (#1299) and person takeover by a member that is not the standby.
- Wiring the watch loop, `epochAdmits`, or the lease and fence rules (#1303 owns them).

## Acceptance Criteria

- [ ] AC-01: With a standby armed, the coordinator's coordinator-owned non-webhook routines reach the standby's copy of the project, with secrets, thread bindings and run state left out. An edit, a pause or a delete on the coordinator reaches the standby within a lease round. Older peers on either side keep leasing and replicating.
- [ ] AC-02: A machine fires a project's coordinator-owned routines only while `CoordinatorRole.roleOf` says its copy is active and its wake fence is down. A copy that is not active rests: due runs move to their next time, with one visible note and no run. After an automatic takeover the standby's copies fire and the old machine's rest once it gives way, so no run fires on both machines across epochs. Unlinked projects fire as before.
- [ ] AC-03: A daily or monthly run skipped because the host was off or asleep leaves a short note on the routine (`lastRunError`) that names the missed time. The next real run clears it.
- [ ] AC-04: docs/user/shared-projects.md (automatic takeover) and docs/studio/logical-projects.md describe what routines do on takeover.

## Approach

1. Contracts: `ProjectCoordinatorReplica.routinesDigest` (optional), `CoordinatorRoutineCopy` schema; `CoordinatorLeaseRequest.routinesDigest` and `CoordinatorReplicaRequest.routines`/`routinesDigest`, all optional. No protocol bump: an older peer ignores the new keys, so mixed versions keep working, and a newer standby asks for content only when the routines digest it is sent differs.
2. `ScheduledTaskService` gains `copiesFor(projectId)` (snapshot + digest) and `replaceCopies(...)` (upsert under the source ids, delete copies no longer sent). The copies are marked `copiedFrom` in `run_policy_json`, and the mark survives edits. A `RoutineCopies` bridge service decouples ProjectLink/CoordinatorLease from the scheduler layer, with no layer cycle.
3. CoordinatorLease sends `routinesDigest` with each lease and routines with each replica. `CoordinatorLeaseRoute` asks for content when the routines digest differs. `replicateFromPeer` checks the routines digest, applies the copies, then writes the replica with `routinesDigest`.
4. Gate in `runTask` (all triggers) and in the missed-run branch: resting runs advance like a suspended project's runs; a fenced or transferring copy waits.
5. `rescheduleMissedRun` writes the skip note.
6. Docs.

Rejected alternatives:
- Materializing at takeover: not crash-safe, and it misses whole-project handoffs. Copying on receipt plus a live gate covers both.
- Adding routines to `coordinatorContentDigest`: an older standby would then reject every replica as invalid.
- Bumping `COORDINATOR_LEASE_PROTOCOL_VERSION`: it would stop takeover between mixed versions.

Risks:
- A copy that was superseded while unreachable reads active until it hears. The wake fence covers that window.
- A once-routine that already ran on the coordinator is sent disabled.

## Decisions

### Asked
- none (coordinator brief; standing approval)
### Defaulted (change any before sw-do)
- D-01 Webhook routines are not copied. Reversible: they would need new tokens and secrets on the standby.
- D-02 Copies keep the source routine's id, so handing the coordinator back updates the original in place instead of making a duplicate.
- D-03 A copy deleted on the coordinator is deleted on the standby. The standby's own routines are never deleted by sync.
### Open
- none

## Tasks

### T-01 Routine copies in the standby replica
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/projectLink.ts, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/scheduledTask.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/handoff/handoffWire.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/CoordinatorLease.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/CoordinatorLeaseRoute.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ProjectLinkStandby.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ProjectLink.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/scheduledTasks/ScheduledTaskCopies.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/scheduledTasks/ScheduledTaskService.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/scheduledTasks/ScheduledTaskStorage.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/scheduledTasks/ScheduledTaskCopies.test.ts apps/server/src/project/coordinatorAutoTakeover.test.ts

### T-02 Fire only where this copy coordinates
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/scheduledTasks/ScheduledTaskCoordinatorGate.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/scheduledTasks/ScheduledTaskService.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/runtimeLayer.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/scheduledTasks/ScheduledTaskService.coordinatorGate.test.ts

### T-03 Visible note for a skipped run
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/scheduledTasks/ScheduledTaskService.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/scheduledTasks/Schedule.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/scheduledTasks/ScheduledTaskService.schedule.test.ts

### T-04 Docs for routines on takeover
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/docs/user/shared-projects.md, repositories/anton-abyzov/specwithcode-dev/docs/studio/logical-projects.md | Test: grep -n "routine" docs/user/shared-projects.md

### T-05 Verify and close 1215
- AC: AC-01, AC-02, AC-03, AC-04 | Files: none | Test: node node_modules/typescript/bin/tsc --noEmit --project apps/server/tsconfig.json
