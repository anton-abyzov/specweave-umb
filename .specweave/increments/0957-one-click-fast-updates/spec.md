# One-click fast updates

## Problem

Updating SpecWithCode takes two presses and minutes of downtime. On 2026-10-20, updating M4 from 1.0.59 to 1.0.60 ran from the first press at 04:06:56 UTC to done at 04:14:03:
- Press 1 swapped and relaunched the Mac app. The relaunched app requested the service install 19 s later (04:07:30).
- The agent snapshotted at 04:07:39. update.py's preflight then failed with "Guarded prestate changed: rows", because the relaunched app had rewritten its own auth_sessions row (client_app_version 1.0.59 to 1.0.60) between the snapshot and the apply.
- The toast then sat on "Preparing to install", showing "Cancel update" and "Update now", until the user pressed again at 04:08:54.
- That second attempt took 5m09s. About 4m14s of it was service downtime (restart at 04:08:58, new process at 04:13:12), during which a 4.1 GB database backup was written (receipts and backups in ~/.specwithcode/m4/updates/receipts and ~/.specwithcode/backups).

The first attempt failed the same way on 1.0.49, 1.0.50, 1.0.53, 1.0.54 and 1.0.60. Update options are split between Settings and the toast. The toast and the sidebar both offer "Update now", and either one re-runs prepare. agent.log has no timestamps and receipts have no per-phase timings, so nobody can see where install time goes.

## Scope

In: one Update now press that installs the service and then the app, a visible clock and state while it runs, reload-proof follow-up, never downgrading a forced request, one download clock for app and service, the service catching up to the app's release, release-pipeline follow-ups found while shipping 1.0.60 to 1.0.62 (M4 held before forcing, the rollout cancelling only its own request, a stage-wide retry cap, waiting for ShipIt, setting a half-installed app aside), a faster service install, and releasing 1.0.63. Out: the agent refusing an apply after the app relaunches (PR #466, its own thread), a main-process follow-up when every window is closed, and moving update options between Settings and the toast beyond routing both buttons through one flow.

## Acceptance Criteria

- [ ] AC-01: One Update now press installs the service and then the app, which restarts on its new version with no second press and no window reload in between.
- [ ] AC-02: While an update runs, the toast says what is happening with a running clock and offers only Cancel; a second press or a reloaded window follows the update already running instead of starting another, and the step that installs the app survives a reload.
- [ ] AC-03: A forced service request is never replaced by a normal one, and the service checks for a release as soon as the app finds one.
- [ ] AC-04: When the service runs an older release than the app, Update now brings the service to the app's release.
- [ ] AC-05: The release pipeline holds M4 before any forced request, cancels only its own request when it gives up, caps stage-1 retries across the whole stage, waits for the app's own ShipIt, and moves a half-installed app aside instead of keeping it.
- [ ] AC-06: The service install skips full database re-hash passes when nothing was committed since the last one and records per-phase timings in its receipt, with proof output byte-identical to today's on fixtures.
- [ ] AC-07: SpecWithCode 1.0.63 is released and a one-press update is checked on M4, M1 and M3.

## Approach

Renderer first: `serviceUpdateFlow.ts` drives one press as service then app; it asks for a forced, version-bound service install held 15 minutes, follows the agent's progress, and calls the registered app installer once the agent reports the target installed. The desktop exposes the agent's pending request (`pendingInstall`) so any window can adopt it; a sessionStorage flag (45-minute TTL) keeps "then install the app" across reloads. `SidebarRestartToUpdate.logic.ts` holds the pure view: target = newer of the agent's release and the app's, Cancel-only while the forced request is live, the clock, and the copy. The desktop never downgrades a forced request, kicks the agent once after a refresh, and asks it to check when the app finds a release. Install timeout 25 minutes, matching the agent's APPLY_TIMEOUT (1500 s).

Release follow-ups ride in their own PR (#474). The install speedup (T-05) waits for #466, which owns update.py, update_agent.py and quiescence.py today; it records PRAGMA data_version and table watermarks at the first read and skips later full passes when nothing was committed, caches release_verified per apply, and hashes appended tables from one scan. Golden-equality tests guard the proof format.

Rejected: installing the app first (the relaunched app rewrote its auth_sessions row mid-apply and failed the guarded prestate), a second confirmation press, and moving the follow-up into the main process now (needs a new IPC contract; deferred).

Risks: the update to 1.0.63 itself still runs the old two-press flow once, because the renderer doing it is 1.0.62's. #466 should land before 1.0.63 so the relaunch no longer refuses the apply.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Service first, then the app, in one press (the owner asked for one operation; app-first fails the guarded prestate).
- D-02: Forced request hold = 15 minutes; renderer timeout = 25 minutes (agent APPLY_TIMEOUT).
- D-03: The speedup lands after #466 merges, in its own PR, to avoid two branches editing update.py.
### Open
- none

## Tasks

### T-01 One press: service first, then the app, with a visible clock
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/serviceUpdateFlow.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/sidebar/SidebarRestartToUpdate.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/sidebar/restartToUpdateRequests.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/LegacySidebar.tsx | Test: cd repositories/anton-abyzov/specweave-studio && node node_modules/vite-plus/bin/vp test run apps/web/src/components/sidebar apps/web/src/components/settings

### T-02 Desktop: pending request, no downgrade, one download clock
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/desktop/src/updates/studioServiceUpdates.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/ipc/methods/serviceUpdates.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/managedUpdates.ts | Test: cd repositories/anton-abyzov/specweave-studio && node node_modules/vite-plus/bin/vp test run apps/desktop/src/updates/studioServiceUpdates.test.ts apps/desktop/src/ipc/methods/serviceUpdates.test.ts

### T-03 The service catches up to the app's release
- AC: AC-04 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.test.ts | Test: cd repositories/anton-abyzov/specweave-studio && node node_modules/vite-plus/bin/vp test run apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.test.ts

### T-04 Release follow-ups: M4 hold, own-request cancel, retry cap, ShipIt, partial app
- AC: AC-05 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/fleet_rollout.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update_request.py, repositories/anton-abyzov/specweave-studio/scripts/release/release.sh, repositories/anton-abyzov/specweave-studio/scripts/release/release-retry.sh, repositories/anton-abyzov/specweave-studio/docs/studio/releasing.md | Test: cd repositories/anton-abyzov/specweave-studio && bash scripts/release/release.sh --self-test && (cd scripts/studio-fleet && python3 -B test-fleet-rollout.py)

### T-05 Faster service install with per-phase timings
- AC: AC-06 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/database_continuity.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-update.py | Test: cd repositories/anton-abyzov/specweave-studio/scripts/studio-fleet && python3 -B test-update.py && python3 -B test-database-continuity.py

### T-06 Release 1.0.63 and check one press on the fleet
- AC: AC-07 | Files: .specweave/release/manifest.json | Test: bash scripts/release/release.sh verify studio --version 1.0.63
