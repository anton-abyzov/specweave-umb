FIX FIRST
Verdict: fix first

Independent review of `anton-abyzov/specwithcode#706`, round 1. Reviewed `8edc9181e40b03a0c81943e326bdda3a194aaac5` against merge base `cb2963143699269aaed155cf8279dd1cfe90c2f0`. Citations are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode`.

| AC-45 check | Result |
|---|---|
| An unnamed edit cannot change the remote routine | Pass on the updated copy. The runner also rejects a missing hash. |
| The edit names the definition shown | Fail: a list can pair old fields with a new hash; a promoted copy ignores a supplied hash. |
| A capped copy can change the runner without changing unrelated settings | Toggle passes; a title-only save can replace the runner's execution settings. |
| One machine runs a due routine after a mid-settlement handover | Fixed for the frozen 1.0.379 receiver; not for a recipient that understands runner records. |
| Migration 077 preserves existing data and old reads | Pass: one new table and its primary-key index; no existing table is altered. |

### Blocking findings

1. **High: a stale form can receive a current hash.** `apps/server/src/scheduledTasks/ScheduledTaskService.ts:2012-2013` reads task rows before `runner.decorate` reads runner records. If a refresh commits between those reads, the list can return prompt A from the first read with revision B and hash B from the second (`apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:181,1325,1337-1351`). A title edit then sends the unseen B token with prompt A. Both checks pass, and the runner overwrites prompt B. Read the displayed row and its token in one snapshot, including for subscriptions.

2. **High: a title edit from a capped copy changes how the routine runs.** `apps/server/src/mcp/OrchestratorMcpService.ts:3254-3265` fills a title-only update with the copy's runtime mode and model. The new stored hash at `apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:950-951` authenticates the runner's *uncapped* definition, but the save at `apps/server/src/scheduledTasks/ScheduledTaskRunnerReceive.ts:450-461` writes the copy's fields. A runner set to `full-access` becomes `auto-accept-edits` after a rename. The mobile form also sends the projected fields. Preserve unchanged runner fields; test a rename, not just two toggles.

3. **High: a stale delete succeeds after the copy becomes the runner.** `apps/server/src/mcp/OrchestratorMcpService.ts:3298-3306` sends the caller's hash but no revision. List on B while A runs prompt P, change P on A, move the routine to B, then submit the old delete on B. `apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:1126-1138` selects the local guard because B is no longer disarmed. That guard checks only `expectedRevision` at lines 1170-1175 and 1199-1207. It deletes the changed routine despite the supplied stale hash. Check any supplied hash under the local write guard too.

4. **High: handover can leave a due routine off until the departing machine returns.** `apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:291-296` removes the recipient's acknowledgement on the source, not its `disarmed` record on the recipient. With B already disarmed and C unanswered, A can hand over successfully to B and go offline before its next reconciliation. B skips the incoming enabled row (`apps/server/src/scheduledTasks/ScheduledTaskCopies.ts:302`; 1.0.386: line 292), and its `disarmed` gate still refuses to fire (`apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:317-318`; 1.0.386: lines 279-280). A is still a linked member, so B does not release itself. Make recipient rearming part of confirmed handover, or refuse to report success until it is safe for A to leave. Test with A offline immediately after acknowledgement.

### Verification and follow-ups

- Read T-21, AC-45, the four commits, and the 1.0.386 tag. New copy → 1.0.386 runner: named edits use the existing wire and hash check. 1.0.386 copy → new runner: the old copy still invents the hash for unnamed toggles/deletes; the new runner cannot distinguish it from a caller-supplied hash. An old capped copy can still receive a stale refusal on its first edit.
- Applied the exact 076 and 077 DDL in memory with a populated runner row, then ran 077 again. The old query returned the same row and the runner schema was unchanged; the new join returned a null hash for that row. No live database was opened.
- CI run `44546792926` tested `529792cc`, patch-identical to `6aace2e4`, not the later tests-only commit `954da079`. Its logs confirm five runner regressions, three MCP regressions and three mobile helper failures. The missing-hash test on the runner pins behavior already present, so it is not red-first. The later migration test needs 077 and was not in that run. Mobile helper tests would still pass if a screen stopped calling the helper; the handover test invokes the snapshot directly and uses only the frozen 1.0.379 receiver.
- No checkout, install, build or local application suite. Head CI was still running when inspected. The four findings above are from tracing the reviewed code, not claimed runtime reproductions.
