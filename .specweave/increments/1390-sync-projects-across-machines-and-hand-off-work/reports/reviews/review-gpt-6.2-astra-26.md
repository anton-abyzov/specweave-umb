SHIP
Verdict: ship

`anton-abyzov/specwithcode#684` · Increment 1390, T-21 · Round 4 · Reviewed `378d6d75da65793aabc8c4743ce2cf9f49ee015b` in a fresh session. All three prior findings are fixed. Four server regressions failed on the round 3 head and passed on this head.

## Round 3 disposition

Source citations are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode` at the reviewed commit.

| Finding | Disposition and evidence at head | Does the test fail without the fix? |
|---|---|---|
| T21R3-01: an acknowledged peer is rearmed when another joins | **Fixed.** `apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:256–270` checks the recipient's acknowledgement, not unanimous membership. `apps/server/src/scheduledTasks/ScheduledTaskCopies.ts:245–265` reads that set before consulting the recipient-specific cache, refuses the snapshot on persistent read failure, and sends acknowledged copies off. | **Yes, both cases.** On round 3, the downgraded recipient selected `routine` and an unreadable runner set produced an enabled snapshot. At head the test observes one dispatch on A, no eligible slot on B, zero dispatches on C, and explicit snapshot failure until the table is readable (`apps/server/src/scheduledTasks/ScheduledTaskRunner.review2.test.ts:365–410`). |
| T21R3-02: refresh makes an open stale draft look current | **Fixed.** The form freezes the displayed hash and submits that value (`apps/web/src/components/settings/scheduledTasksSettings.logic.ts:283–303`; `apps/web/src/components/settings/ScheduledTasksSettings.tsx:615–618`). The copy refuses a stale or unnamed save; the runner independently compares the forwarded hash to its own definition before mutation (`apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:963–981`; `apps/server/src/scheduledTasks/ScheduledTaskRunnerReceive.ts:395–407`). | **Yes.** On round 3 the original draft reverted the prompt. At head the same-revision refresh does not rescue that draft: both it and a revision-only save fail. A freshly opened draft succeeds without reverting the prompt (`apps/server/src/scheduledTasks/ScheduledTaskRunner.review2.test.ts:448–468`). |
| T21R3-03: recovery treats a status reply as proof of the installed definition | **Fixed.** Status `enabled` completes the move without a new enable receipt. That branch explicitly persists `installedRevision: null`; only a direct enable reply takes the verified branch (`apps/server/src/scheduledTasks/ScheduledTaskTransfer.ts:330–344,359–360,416–420`). | **Yes for the reported overwrite.** On round 3 the source's title-only save reverted the destination prompt. At head that save fails, refreshes the source, and the next save preserves the destination edit (`apps/server/src/scheduledTasks/ScheduledTaskRunner.review2.test.ts:488–507`). This test does not isolate the marker assignment from the hash guard. |

## Blocking findings

None. No new changed path met the AC-45 or EC2-06 blocking rule.

## Follow-up (non-blocking)

**Test the recovery marker directly.** At `apps/server/src/scheduledTasks/ScheduledTaskRunner.review2.test.ts:496–499`, assert that the source record has `installedRevision === null` immediately after recovery, before the stale save refreshes it. Reverting just the marker assignment could otherwise leave this test green because the runner also checks the hash. The production assignment is correct at the reviewed head.

## What I verified

- Resolved the exact head with `gh pr view 684 --json headRefOid`. Compared the T-21 files against `a6cbdad8737721e8260dc4ad757cac0622926d40`, excluding unrelated mainline changes. Used AC-45 and the accepted EC2-06 amendment at lines 36 and 806 of the increment spec on umbrella `origin/main`.
- Traced both production snapshot senders: `apps/server/src/project/CoordinatorLease.ts:409–412,631–637,934–946` supplies the standby ID; `apps/server/src/project/CoordinatorPlannedHandover.ts:279,648–654` supplies the takeover target. On snapshot error these paths omit routine data rather than sending an enabled fallback.
- Read the [round 3 baseline failures](/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t21/round3-red-on-a6cbdad8.txt) and the [earlier baseline log](/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t21/round3-red-on-11874f7a.txt). The red claims in the table use the round 3 baseline. The [exact-head CI artifact](https://github.com/anton-abyzov/specwithcode/actions/runs/44533892642/artifacts/14535193675) records all four named T21R3 server tests as passed. `gh pr checks 684` subsequently showed `PR Gate (server 3/3)` succeeded on retry; no failing or pending check remained.
- Used existing test evidence. No local build, install, source edit, commit, PR comment, or live database access.
