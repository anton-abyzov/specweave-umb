FIX FIRST
Verdict: fix first

**anton-abyzov/specwithcode#684 · T-21 · round 3.** Reviewed `a6cbdad8737721e8260dc4ad757cac0622926d40` against `48a14393843a21fb74fce1013c0dac945edcef14`. **1 of 3 items fixed; 2 partially fixed. 3 high findings, 0 critical.** Rearm preserves the carried occurrence. One handover can still leave the same slot eligible on two machines, and two edit paths can still overwrite a newer prompt.

## Round-two disposition

| Item | Result at the reviewed head | Would the regression tests fail without the fix? |
|---|---|---|
| T21R2-01: downgraded copy and unreadable disarm | **Partial.** With unchanged membership, both the replica and the handover carry `enabled: false`. A failed row lookup gives no acknowledgement and is retried after repair (`apps/server/src/scheduledTasks/ScheduledTaskCopies.ts:234–251`; `apps/server/src/scheduledTasks/ScheduledTaskRunnerReceive.ts:172–178`). A newly linked member can invalidate the outgoing mask without invalidating the old acknowledgement. See T21R3-01. | **Yes, 3/3 red.** Both old-receiver tests selected `routine` on the resting machine; the unreadable-row test found the sender already settled. All three pass at head. |
| T21R2-02: rearm moves the due slot | **Fixed.** Disarm switches the row off before saving the unchanged schedule. Rearm changes `enabled` without a user enable, preserving a non-null `next_run_at` and the one-shot generation (`apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:552–569,850–898`; `apps/server/src/scheduledTasks/ScheduledTaskRunnerRecords.ts:245–258`). The tests set the slot before disarm, use the handover's run-state writer, and never repair it after rearm. | **Yes, 2/2 red.** The hourly routine fired zero times instead of once; the resting one-shot lost its slot. At head the hourly test counts exactly one dispatch on B and zero on A, and the one-shot retains both slot and generation (`apps/server/src/scheduledTasks/ScheduledTaskRunner.review2.test.ts:196–250`). |
| T21R2-03: old definition with current revision | **Partial.** The disarm sender now reads definitions and counts in one transaction. A late replica is marked unverified, and a save submitted *before* refresh is refused (`apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:464–493,527–542,952–965`). The revision shown to an open form and the revision recorded after move recovery are not always evidence of the definition the user saw. See T21R3-02 and T21R3-03. | **Yes, 2/2 red.** Both title-only saves restored the old prompt on the baseline. Both pass at head. Neither holds an unverified draft across a refresh or edits the destination between a lost enable reply and move recovery. |

## Blocking findings

### [high] T21R3-01: Adding a member can re-arm an already acknowledged, downgraded copy

**Location:** `apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:250–259,635–655,707–729`; `apps/server/src/scheduledTasks/ScheduledTaskCopies.ts:239–251`.

**Observed:** A settled with B off. B was then treated as v1.0.379, and C joined before the next reconciliation. A's outgoing handover snapshot for B changed from `enabled: false` to `true`: the mask requires *every current member* to have acknowledged, and C had not. B's released handover writer installed the enabled row and A's due slot. After the coordinator passed to B, A asked only C to disarm because B was still in `acked`. C confirmed. The released due selector on B returned `["routine"]`, and A's scheduler dispatched that same slot once. There was one active coordinator, no lost message and no partition. Two released peers would not both be eligible: the transferred A rests under `v1.0.379:apps/server/src/scheduledTasks/ScheduledTaskCoordinatorGate.ts:83–90`.

**Fix:** Never send an enabled copy to a recipient whose earlier disarm will still count. Make the wire mask recipient-aware, or invalidate the acknowledgement before an enabled snapshot can leave and require fresh proof before independent firing resumes. An unreadable runner set must not authorize an enabled snapshot either: `apps/server/src/scheduledTasks/ScheduledTaskRunnerRecords.ts:273–276` currently maps that read failure to an empty map. Extend the pinned handover test with C joining between settlement and snapshot; after C confirms, exactly one machine must be eligible.

### [high] T21R3-02: A refresh makes an already-open stale draft appear current

**Location:** `apps/server/src/scheduledTasks/ScheduledTaskRunner.ts:956–965,1250–1268`; `apps/web/src/components/settings/scheduledTasksSettings.logic.ts:280`; `apps/web/src/components/settings/ScheduledTasksSettings.tsx:615–619`.

**Observed:** A had the new prompt at revision `1`. B had received a delayed, old replica and had `installedRevision: null`. B nevertheless displayed the old prompt at revision `1` because the list falls back to `record.revision`. A form opened then retained that prompt and base revision. A normal refresh installed the correct prompt at `1` on B. Submitting the original form with only the title changed now matched B's installed revision and A's current revision. The save returned `Success` and A's prompt reverted. The existing test submits before refresh, then constructs a *new* form from the refreshed row (`apps/server/src/scheduledTasks/ScheduledTaskRunner.review2.test.ts:293–302`). A v1.0.379 standby refuses that edit instead of forwarding it (`apps/server/src/scheduledTasks/ScheduledTaskService.ts:1984–2005` at the tag).

**Fix:** Do not give an unverified definition an editable base revision. Require refresh before opening an editable draft, or give such a draft a token that remains invalid even if the same numeric revision is later installed. Return the displayed definition and its verified edit token from one read, including for subscriptions (`apps/server/src/scheduledTasks/ScheduledTaskService.ts:2010–2013`). Add a test that saves the *original* draft after refresh; it must be refused and A must retain the newer prompt.

### [high] T21R3-03: A lost enable reply makes the source claim it installed a later destination edit

**Location:** `apps/server/src/scheduledTasks/ScheduledTaskTransfer.ts:314–332,341,402–417`; `apps/server/src/scheduledTasks/ScheduledTaskRunnerReceive.ts:509–529`.

**Observed:** A moved the routine to B. B enabled it; its answer was lost. While A still showed `moving`, B accepted a new prompt at revision `2`. A retried the move. Status confirmed the original operation but reported B's **current** revision. A stored `installedRevision: 2` against its **pre-move** prompt, without receiving a definition. A new form on A and the current row on B now showed different prompts at `2`. A title-only save from A returned `Success` and overwrote B's new prompt. This is separate from T21R3-02: no stale open form or late coordinator replica is needed. The v1.0.379 move leaves the source off on an uncertain enable and has no path that forwards its pre-move form into the target (`apps/server/src/scheduledTasks/ScheduledTaskTransfer.ts:255–265` at the tag).

**Fix:** An operation-status answer proves enablement, not which definition the source holds. Leave `installedRevision` unverified until the source installs a definition and revision returned together by B. If using the immutable enable receipt, use it only for the exact definition installed by that operation, not a later revision read from status. Extend the lost-answer retry test at `apps/server/src/scheduledTasks/ScheduledTaskRunner.test.ts:246–299` with a destination edit before retry and a source title edit afterward. The destination prompt must survive.

## Evidence

The [baseline log](/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t21/round2-red-on-48a14393.txt) contains seven assertion failures. The [exact-head CI run](https://github.com/anton-abyzov/specwithcode/actions/runs/44525834815) passed; its [server artifact](https://github.com/anton-abyzov/specwithcode/actions/runs/44525834815/artifacts/14532205886) records all seven tests passing.

The [three additional checks](/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t21/round3-boundary-check.mjs) ran against the reviewed Git objects and separate in-memory scheduler databases. They observed one new-runner dispatch plus one old-receiver due selection in T21R3-01, and successful writes of the old prompt in T21R3-02 and T21R3-03. The downgrade check used the tag-matched replica writer, handover run-state write and released eligibility query, not a second installed application. No build, install or edit in the reviewed repository.

## Follow-up (non-blocking)

No new non-blocking findings. T21-09 replay after a late copy, the run-state read mapping to `null`, and migration 076 on development installs remain tracked as before; none was reopened or counted.
