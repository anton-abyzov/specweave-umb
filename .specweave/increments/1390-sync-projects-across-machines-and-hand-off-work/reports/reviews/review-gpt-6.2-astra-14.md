FIX FIRST
Verdict: fix first

**Review:** anton-abyzov/specwithcode#684, increment 1390, T-21. **Head:** `11874f7a01e434b2f4ba9cc72704272613e4edab`. **Findings:** 0 critical, 11 high, 2 medium, 1 low. Locations below are relative to the [exact reviewed tree](https://github.com/anton-abyzov/specwithcode/tree/11874f7a01e434b2f4ba9cc72704272613e4edab), except where a release tag is explicit.

The same due slot can fire twice before a runner is settled, or nowhere after it is settled. Neither finding requires a change to the standby takeover algorithm. They concern which routine the scheduler admits **at dispatch**, the boundary AC-45 assigns to T-21.

## [high] T21-01 — Both coordinators can fire before they settle the runner

`apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:413-420` falls back to the legacy gate for an unsettled routine. With two active, unfenced coordinators and the same enabled replica due on both, the gate admits both; the conditional claim in `apps/server/src/scheduledTasks/ScheduledTaskService.ts:602-612` is in each machine's own database. The production poll runs due work **before** reconciliation (`:1587-1592`). A partition prevents reconciliation but not either local claim. The equal-coordinator test settles both *before* making them due (`apps/server/src/scheduledTasks/ScheduledTaskRunner.test.ts:69-87`).

**Fix:** Preserve the actual incumbent runner before a second copy can dispatch, and keep an ambiguous replica from firing without that ownership evidence. Test the first already-due poll on both machines, including with the link down; count dispatches without a preparatory settlement.

## [high] T21-02 — The old coordinator binding still vetoes the settled runner

`apps/server/src/scheduledTasks/ScheduledTaskService.ts:840-863` checks the runner and then independently calls `assertTaskAdmission`. For an own-thread routine, `apps/server/src/scheduledTasks/ScheduledTaskAdmission.ts:58-64` substitutes the coordinator thread; `packages/contracts/src/logicalProject.ts:170-176` fences that thread on a `transferred` source. The check is repeated at own-thread launch (`apps/server/src/scheduledTasks/ScheduledTaskService.ts:1283-1293`). After a real coordinator transfer, the original, settled runner is therefore refused and the disarmed peer rests: **zero fires**, the Proof 4 failure. The passing role-change test changes only `state.role`; its project row contains no transferred binding (`apps/server/src/scheduledTasks/ScheduledTaskRunner.testkit.ts:182-201`).

**Fix:** Use the durable routine owner, not its former coordinator, for this part of admission at both checks. Preserve pause, archive, grant and actual destination checks. Persist a real transferred binding in the test and require one dispatch on the original runner and none on the peer.

## [high] T21-03 — An acknowledged disarm is invisible after downgrade

`apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:1177-1188` acknowledges after writing only the new runner record; the legacy schedule can remain enabled. The owner treats the recorded peer ID as sufficient coverage (`:385-389`, `:413-418`, `:547-549`). If that peer restarts on `v1.0.379`, its `apps/server/src/scheduledTasks/ScheduledTaskCoordinatorGate.ts:83-94` uses coordinator role and wake fencing, not the new table. With both coordinators active and unfenced, a partitioned, downgraded peer can fire alongside the settled owner. This is different from a peer that was already old when probed: that peer does not acknowledge.

**Fix:** Make the disarm persist in a form the previous scheduler honors, including after replica refresh, or block the downgrade until a safe legacy owner is re-established. Run the previous scheduler against the post-disarm state and count the same slot on both machines.

## [high] T21-04 — A lost disarm reply can strand the only eligible runner

`apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:606-621` remembers only successful replies. A standby can persist `disarmed` at `:1177-1188` and lose its reply, leaving the source with no record of that disarm. If the legacy coordinator changes before the retry, the old source is held and rearms only recorded acknowledgements (`:489-503`, `:535-544`); the new coordinator rests because its local record is disarmed (`:398-401`) and skips reconciliation for that record (`:533-535`). Neither fires. The partition need not last: reconnecting does not reconstruct the missing acknowledgement once the old source no longer coordinates.

**Fix:** Persist disarm intent and its recipients before sending. Reconcile *uncertain* recipients as well as acknowledged ones on role change or restart. Drop the reply after the standby persists it, change roles, reconnect, and count the next due fire.

## [high] T21-05 — Handing off a worker through Away also moves its routine

`apps/server/src/away/AwayPlanner.ts:318-321` marks eligible routines for a move. For a bound routine, `apps/server/src/away/AwayRunner.ts:449-451` waits for the worker; `:494-516` then calls `transferRoutine` on a successful worker handoff. Its production dependencies build a transferable copy and call `moveOut` (`:377-383`, `:1115-1117`). No separate “Move the routine too” decision is required. In contrast, `apps/server/src/scheduledTasks/ScheduledTaskRunner.test.ts:555-573` populates a moved-thread lookup without running the Away caller.

**Fix:** After the worker moves, leave the schedule on its current runner with the handed-off note. Only a separate routine move should stage or enable it. Drive the Away flow and assert no target schedule or transfer request before that action.

## [high] T21-06 — Move recovery can undo a person's successful disable

`apps/server/src/scheduledTasks/ScheduledTaskTransfer.ts:455-476` reads enabled state and stages a snapshot over the network **before** recording `moving` (`:483-505`). Between those operations a user can successfully turn the routine off. If the process stops just after recording `moving`, recovery sees `wasEnabled: true` and a now-disabled row, assumes the mover disabled it, and enables it again (`:382-387`, `:286-293`). An uninterrupted move can likewise enable the old staged definition. The existing recovery test at `apps/server/src/scheduledTasks/ScheduledTaskRunner.test.ts:831-859` seeds an off row and assumes the mover wrote it.

**Fix:** Claim the source under an expected revision before staging its definition. Persist the mover's own disable and carried state together, so recovery cannot reverse a distinct, acknowledged user edit. Interleave a real user disable with the stage reply, reopen the source, and assert the routine stays off.

## [high] T21-07 — A failed forwarded delete removes the fence but not the schedule

`apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:1294-1305` deletes on the runner, excluding the requesting replica from the delete broadcast. On that replica `:824-830` ignores local row-deletion failure and still removes its disarm and revision records; `:851-853` reports completion. An enabled row left behind on an active coordinator becomes eligible under the legacy gate. This is the **reply to the requesting replica**, not the incoming broadcast path at `:1205-1214`, which checks deletion before dropping the fence.

**Fix:** Delete the schedule and its fence in one local transaction, or retain the fence with a durable pending delete until cleanup succeeds. Fail that row deletion, then run a due poll: the deleted routine must not dispatch.

## [high] T21-08 — Bring back treats a failed lookup as proof the target stopped

`apps/server/src/scheduledTasks/ScheduledTaskTransfer.ts:1120-1125` maps a task-list error to an empty list. `ownRoutine` consequently returns null (`:659-665`); `release` reports `enabled: false` without disabling anything (`:797-806`). The caller accepts this as a release and can turn the source on (`:546-574`). A transient list-read failure on a still-running target can therefore create two enabled owners.

**Fix:** Distinguish a read failure from a confirmed absence. Do not enable the source without positive, durable evidence that this operation released the target. Inject a target read failure before release and assert only the existing runner fires.

## [high] T21-09 — Bring back can report success without restoring the due slot, count or owner

`apps/server/src/scheduledTasks/ScheduledTaskTransfer.ts:568-580` returns `returned` regardless of whether local enable succeeded. The production adapters turn enable failure into `false`, suppress state-write errors, and ignore revision-write failure (`:1093-1096`, `:1104-1114`); restoring the prior ownership record also ignores failure (`:271-275`). Away persists this as a completed return (`apps/server/src/away/AwayRunner.ts:765-769`). After successful remote release, a failed local enable leaves neither copy running; a failed count or revision write is not retried. Losing the release reply is also material: the target has deleted the row, and its retry returns `runState: null` instead of the released count and slot (`apps/server/src/scheduledTasks/ScheduledTaskTransfer.ts:797-819`).

**Fix:** Save the release result, including run state, for replay. Commit the local owner, revision, enabled flag and carried state atomically before reporting `returned`; otherwise leave the return pending. Test loss of the reply and failure of the local state write independently across restart.

## [high] T21-10 — A replica presents an old definition as the current revision

`apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:560-566` sends revision numbers without their definitions; `:1177-1188` advances only the replica's runner record. The list attaches that revision to its existing local definition (`:1055-1066`). If the runner changes a prompt and this revision arrives before the definition, opening the replica's form and changing only the title sends the **old prompt with the current revision**. The runner accepts it and overwrites the new prompt (`:1284-1292`, `:1313-1347`). The test at `apps/server/src/scheduledTasks/ScheduledTaskRunner.test.ts:725-739` checks the revision and title, not preservation of other fields.

**Fix:** Install a definition and its revision as one snapshot, or expose only the last revision whose definition was applied locally. Delay definition replication and verify a title-only edit cannot revert the runner's prompt.

## [high] T21-11 — Settings delete and toggle omit the displayed revision

`apps/web/src/components/settings/ScheduledTaskRow.tsx:130-135` sends toggle and delete without `expectedRevision`; bulk delete does the same at `apps/web/src/components/settings/RoutineList.tsx:200-204`. Neither the local guard nor the forwarded edit compares revisions when it is omitted (`apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:798-805`, `:923-929`, `:1284-1285`). A person can confirm deletion from an old screen after the runner has saved an intervening edit; the newer routine is deleted rather than the stale request refused.

**Fix:** Capture and send the revision of the snapshot the person acted on, including each bulk-selection item. Test a confirmation left open across a runner edit, using the real Settings command payload.

## [medium] T21-12 — A definition and its revision can commit separately

`apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:948-952` performs the change and then bumps the revision. The forwarded save has the same ordering at `:1343-1348`. If the second write fails, the caller sees an error but the changed definition remains at the old revision. A second editor with that revision can overwrite the change without a stale-edit refusal.

**Fix:** Compare the revision, write the definition and advance the revision in one transaction on the runner. Fail the bump after a save and assert that neither the definition nor the revision changed.

## [medium] T21-13 — The reverse compatibility test bypasses the route and changes the release's ordering

`apps/server/src/scheduledTasks/ScheduledTaskRunner.test.ts:480-489` turns off the old source **before** staging and calls `receive` with a cast, decoding only the reply. The released sender at `v1.0.379:apps/server/src/scheduledTasks/ScheduledTaskTransfer.ts:197-218,240-246` stages while the source is on, disables and reads it back only after success, then enables. The production receiving route validates the request at `apps/server/src/away/awayRoutinesRoute.ts:45-52`. A decoder that rejects a valid released request would fail in production but pass this test. The relevant released sender source is identical at `v1.0.377` and `v1.0.379`; the issue is the path exercised, not just the tag label.

**Fix:** Drive the pinned sender sequence through the new route's real decoder, retaining the source state at each boundary, including stage refusal. Keep the opposite-direction capability probe/no-move case. EC2-09 requires positive evidence in both directions.

## [low] T21-14 — The oversized scheduler gained policy logic despite the call-sites-only exception

`apps/server/src/scheduledTasks/ScheduledTaskService.ts:1981-1997` implements the decision between a role-service result, a project-row fallback and an unreadable project. This is more than a call to the runner. The file grew from 2,056 to 2,058 lines; T-21 explicitly allows call sites only above 1,500. The new runner module itself is 1,468 lines.

**Fix:** Extract the role-resolution adapter into a small module and pass it at this call site. There is no need to refactor the pre-existing scheduler wholesale.

### Evidence and limits

- **Worker exceptions:** The pre-settlement double fire (T21-01), the interrupted move reversing a disable (T21-06), the failed replica deletion (T21-07), and the failed bring-back count write (T21-09) block AC-45. The **absence of a failing-first lock test does not, by itself, block it**: forwarding is outside the sender's mutation lock at `apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:877-893`. The test at `apps/server/src/scheduledTasks/ScheduledTaskRunner.test.ts:762-785` runs both actions concurrently but does not force the original lock interleaving.
- **What works on the reviewed paths:** The outbound capability probe precedes staging; refusal from an old peer sends no move. The target's enable handler replays the operation receipt before touching state; the state, owner, revision and receipt commit together while the staged fence prevents a premature fire. The normal lost-enable-reply test counts launches/sends rather than handler calls. The scheduler tests use a test clock, and the subscription test waits for the first event and joins its worker. Webhook schedules are excluded from the copy builder; no URL disclosure was found. No personal path or real machine name was found in the added lines.
- **Upgrade and restart:** Migration 076's three table-creation statements were applied twice to a synthetic in-memory SQLite schema; the existing enabled row and due slot were unchanged. That verifies additive DDL, not downgrade behavior (T21-03). The fleet fixture creates fresh in-memory databases at `apps/server/src/scheduledTasks/ScheduledTaskRunner.testkit.ts:285-297`. The lost-enable-ack case retries on the same instances, and the interrupted-move case seeds records in place. Neither demonstrates a process reopening persisted state.
- **Method:** Exact-head source and test traces, comparison with released Git objects, existing green PR checks, and the isolated DDL check above. No local application build or test-suite run; the failure scenarios are source-verified interleavings, not claimed live reproductions. No source edits or live database access.
