# Restart to update recovers a service held after a failed install

## Problem

On m4 (November 18, 2026, 10:25 and 10:26 AM EST) Restart to update showed "Could not install update. SpecWithCode 1.0.356 installs after the SpecWithCode service on this machine updates to it." m4 has been on 1.0.338 since November 17, 4:54 PM, while releases moved to 1.0.356. Nothing on the machine will ever update the service, so the toast promises something that does not happen.

Evidence, all read on m4:

1. **The failed install.** At 03:47 to 03:52 UTC the 1.0.338 update agent ran an automatic (unheld) install of 1.0.344. The target helper refused in preflight with `AssertionError: Guarded prestate changed: rows`, every pointer unchanged (`updates/receipts/update-1.0.344-20261118T034729987466Z.json`). The "Disk space guard" routine runs every 5 minutes (`scheduled_tasks`, `everyMs` 300000, 7,369 runs), so it fired inside that 5 minute 19 second install and rewrote its row. PR #559 (in 1.0.345) makes the scheduler wait while an automatic install applies, but that is service code, and the running service is 1.0.338.
2. **The agent latch.** A failed automatic install holds every later automatic install until Install now (`update_agent_recovery.holds`, `automatic_retry`). The bounded retry for a pre-restart refusal (`record_refusal`) is bound to `installCancelledAt`; a non-interactive cancel at 03:54:44.488Z (`config.json`, and the service log's `service-update.prepare.requested releaseHold: true` at the same instant) voided it. A newer release gets one automatic attempt only after a clean rollback (`newer_release_after_rollback` needs `pointers == "previous-release"`), never after a preflight refusal (`pointers == "unchanged"`). So 1.0.345 to 1.0.356 were all held: `agent.log` has 70 passes since 04:02 UTC saying "SpecWithCode X did not install automatically; choose Install now to retry." The busy guard is not what blocks it: the hold is decided before the quiet wait.
3. **The UI dead end.** No surface offers Install now for that state. The sidebar's `isServiceErrorWithRelease` accepts only the deleted-log and lost-locks refusals and an expired request, so `service` is false; the Electron app had 1.0.356 downloaded, so the button became an app-only "Restart to update". Desktop main's activation gate refused it as `service-behind` (desktop trace: press, quick-look, "app install refused: service-behind" at 15:26:08Z and 15:26:26Z). Settings offers only "Check now" (`resolveServiceUpdateAction`). The same code is on main today.

What still works on 1.0.338: a held install. Its scheduler skips every tick while `updateHold.isHeld` (`Scheduler.ts:46` at `v1.0.338`), and its service holds for an agent in `error` with a newer release on disk (`updatePendingFor`). So Update now, or the rollout's hold plus forced request, installs without the race. No change in this increment reaches a machine already latched: its desktop, service and agent are all 1.0.338 (`updater/agent-release.json`), and only a verified update replaces them.

## Scope

In: the sidebar and Settings offer the service update for a held failed install; the service-behind toast says why and what happens next; the agent gives a newer release one automatic attempt after a pre-restart refusal that changed nothing; a documented recovery for machines already stuck on old builds, run from the newest helper tree already on disk; the exact step for m4.

Out: the helper's guarded-prestate check (unchanged); the activation gate's rule that the service updates first; restarting m4 or its service from a thread; `pauseWorkForUpdates` and the forced-update setting.

## Acceptance Criteria

- [ ] AC-01: With m4's state (agent `error`, "SpecWithCode 1.0.356 did not install automatically; choose Install now to retry.", installed 1.0.338, downloaded 1.0.356, app update 1.0.356 downloaded), the sidebar button reads "Update now", and pressing it starts the service update with the app's install after it (`installServiceUpdate`), never an app-only install.
- [ ] AC-02: In the same state Settings offers "Install now" for the service, and the text beside the sidebar button does not tell the person to choose a button that is not there.
- [ ] AC-03: The agent's first-failure message ("SpecWithCode X did not install; SpecWithCode stayed on Y. See the update receipt.") with a newer release on disk is offered the same way. Other `error` messages (failed check, rejected download, agent start failure) still offer only a check.
- [ ] AC-04: A test pins the web matchers to the agent's exact wording in `update_agent_recovery.py` and `update_agent.py`.
- [ ] AC-05: When an app install is still refused as `service-behind` while the service is in error, needs a manual step, waits for quiet, installs, downloads or has the update, the toast names what the service is doing or why it cannot update (from `swapGate.serviceStatus` and `serviceMessage`) instead of only "installs after the service updates".
- [ ] AC-06: After an automatic install refused in preflight with every pointer unchanged and a retryable refusal, a newer verified release gets one automatic attempt; if that fails too, the hold moves to it, and a retryable refusal of the newer release may use that release's own bounded retry budget (at most three applies). A receipt with any other key, phase, pointer state or error keeps the hold.
- [ ] AC-07: `docs/studio/updates.md` gives the recovery for a machine stuck on an old build whose agent holds a failed install: the command from the newest helper tree, with and without `--wait-for-idle`, what each interrupts, and why it must run outside SpecWithCode threads.
- [ ] AC-08: A test drives the agent shipped since 1.0.338 (unchanged on main) from m4's exact `state.json` and `config.json` shape and shows that a version-bound forced request is served (the failure hold does not apply), while an automatic pass stays held.

## Approach

1. `apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.ts`: `isHeldFailedInstall(message)` matches the two agent failure messages; `isServiceErrorWithRelease` accepts them (still requires a newer release on disk and no agent start failure); `serviceRefusalText` drops "; choose Install now to retry" beside a button that says Update now. `describeInstallOutcome("service-behind")` uses the gate's service status and message.
2. Settings (`UpdatePreferencesSection.logic.ts`) follows through `isServiceErrorWithRelease` unchanged; its test adds the m4 state.
3. `scripts/studio-fleet/update_agent_recovery.py`: `newer_release_after_rollback` also accepts a preflight refusal receipt as strict as `refusal_proof` (only the five keys, `pointers == "unchanged"`, `AssertionError: ` plus a `RETRYABLE_REFUSALS` phrase), started from this installation. `update_agent.py` is at the 1,500-line cap and is not touched.
4. Tests: logic, press-level run test, Settings, Python recovery tests, the wording pin.
5. `docs/studio/updates.md`: the recovery section.

Rejected: opening the activation gate for a latched service (the app would run ahead of its service, which the gate exists to stop, and a held service update is available); handing every refused app install to the service (for a rejected download or failed check the request fails after the work was stopped); a new recovery CLI (the rollout already holds and requests, and the newest helper tree carries it).

Risks: on a service older than 1.0.345 the newer-release attempt can race a routine again; it costs one quiet wait and two database reads per release, then holds. Offering Update now after a deterministic failure repeats it, which the agent's own message already invites.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Busy machine → the press asks Restart now, Wait for work to finish (the existing hold window, which says when it restarts) or Later; it never stops work without that question.
- D-02 m4 itself → not restarted from a thread; Anton runs the rollout command in Terminal at a quiet moment (see the report).
- D-03 AC-05 and AC-06 reworded to what shipped, after the closing review (Anton, November 19, 2026): the toast covers the statuses listed in AC-05, and a newer release's retryable refusal keeps its own bounded retry budget.
### Open
- none

## Follow-ups

Found by the closing review (GPT-6.1 Sol on Copilot Enterprise, November 19, 2026) on app `3ea7b49c8`; recorded, not fixed here:

- Gap in AC 06, retry budget (medium): `record_refusal` (`scripts/studio-fleet/update_agent_recovery.py:410-430`) starts a fresh `MAX_ATTEMPTS = 3` budget for the newer release, so it can get two more automatic applies after its one attempt. The test (`test-update-agent-recovery.py:849-859`) does not run a second agent pass.
- Gap in AC 05, disabled service (medium): `describeServiceBehind` (`apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.ts:405-428`) has no `disabled` branch, so with automatic checks off the toast omits the reason; it also calls `available` "downloading" when background download is off.
- Low: a newer release whose admission snapshot keeps failing never records `lastInstall`, so the attempt is not used up and the snapshot repeats each pass (`update_agent.py:1035-1058`).
- Unowned: the 1.0.361 install failure on m4 (November 18, 2026) began with a refused fast page proof (`pageFallback: "Refused:auth-heartbeat:Protected rows or counts changed"`), not with low disk alone; the full read then ran out of scratch space and the agent held 1.0.362 to 1.0.374. The receipt names no table or counts. Tracked in project memory `project_open_product_gaps.md` under Updates; outside this increment's scope (the helper's guarded-prestate check).

## Tasks

### T-01 Offer the service update for a held failed install
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/sidebar/SidebarRestartToUpdate.heldFailure.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/sidebar/SidebarRestartToUpdate.heldFailure.test.tsx | Test: `cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/sidebar/SidebarRestartToUpdate.heldFailure`

### T-02 Say why an app install waits for the service
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/sidebar/SidebarRestartToUpdate.heldFailure.logic.test.ts | Test: `cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/sidebar/SidebarRestartToUpdate.heldFailure.logic.test.ts`

### T-03 A newer release gets one attempt after a refusal that changed nothing
- AC: AC-04, AC-06, AC-08 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-fleet/update_agent_recovery.py, repositories/anton-abyzov/specwithcode/scripts/studio-fleet/test-update-agent-recovery.py | Test: `cd repositories/anton-abyzov/specwithcode/scripts/studio-fleet && python3 test-update-agent-recovery.py HeldRefusalRecovery AutomaticRecovery NewerReleaseRecovery`

### T-04 Recovery for machines stuck on old builds
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/docs/studio/updates.md | Test: read the section against `fleet_rollout.py --dry-run` output

### T-05 Review, merge, release
- AC: AC-01, AC-06 | Files: none | Test: Muse Wonderful review at xhigh, green CI, `request-release.sh`
