# Fast update install on busy machines

## Problem

M4's update went from 26-40 s (1.0.131 to 1.0.140, October 30-31, 2026) to 165-499 s (1.0.145 to 1.0.147). Receipts show 462 of the 499 s on 1.0.147 in three full reads of the 18.8 GB database; the backup clone took 2.2 s.

Cause: on October 31 a Connect client minted about 47,000 `auth_sessions` and 49,000 `auth_pairing_links`. `PageMode.authority` refuses over 20,000 rows, and `PageMode.prepare` swallows the refusal, so every held install since has silently taken the full-read path. Connect mints are also outside the update hold, so a mint during a read refuses the install ("Guarded prestate changed: rows"): seven refusals and two failed runs on November 1 for 1.0.145, each ending at Try again.

The UI shows "Step 11 of 17" and a static estimate from the previous install, which elapsed time passes.

## Scope

In: authority budget, a recorded page-mode refusal reason, Connect mints under the hold, one live estimate and progress bar, plain wording for waits on running threads. Out: pruning expired auth rows, page proof across schema changes.

## Acceptance Criteria

- [ ] AC-01: A held install with 48,000 auth sessions and 55,000 pairing links takes the page path, and the receipt says why whenever page mode is refused.
- [ ] AC-02: A Connect mint during a held update waits for the restart and creates no `auth_pairing_links` row.
- [ ] AC-03: The helper publishes per-phase expected times, chosen from the newest verified install on the same proof path, and revises them when the proof falls back to a full read.
- [ ] AC-04: While installing, the UI shows no step counter, one progress bar and a time left that updates; the bar never moves back and the estimate is never below elapsed.
- [ ] AC-05: A wait on running threads says how many, and names them.
- [ ] AC-06: A timed real update on M4 with threads running, compared with the 499 s 1.0.147 receipt.

## Approach

`scripts/studio-fleet/update_apply.py`, `update.py`, `install_progress.py`; `apps/server/src/cloud/CloudLink.ts`; `packages/contracts/src/serviceUpdateRun.ts`; `apps/desktop/src/updates/updateRun.ts`; `apps/web/src/components/serviceUpdateRunView.ts`, `serviceUpdateRunFlow.ts`, `sidebar/SidebarRestartToUpdate.tsx`, `ui/toast.tsx`.

The proofs are unchanged: page mode is the design reviewed under 0957, and it falls back to the full proof whenever it cannot decide. Rejected: moving the proof after activation, because a failed proof could not restore over post-activation writes.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Expired auth rows stay; the 500,000-row budget covers them and pruning credentials is a separate change.
- D-02 A release with a schema change keeps the full proof, about 5 minutes on M4, and the estimate says so.
### Open
- none

## Tasks

### T-01 Page mode survives large auth tables and records refusals
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/update_apply.py, repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/update.py, repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/test-update-page-mode.py | Test: python3 scripts/studio-fleet/test-update-page-mode.py

### T-02 Connect mints wait for the restart
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/cloud/CloudLink.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/cloud/CloudLink.lifecycle.test.ts | Test: bun run --cwd apps/server test src/cloud/CloudLink.lifecycle.test.ts

### T-03 Helper publishes live phase estimates
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/install_progress.py, repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/update.py, repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/test-install-progress.py | Test: python3 scripts/studio-fleet/test-install-progress.py

### T-04 One progress bar and live estimate
- AC: AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/serviceUpdateRun.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/updates/updateRun.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/serviceUpdateRunView.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/serviceUpdateRunFlow.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/sidebar/SidebarRestartToUpdate.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/ui/toast.tsx | Test: bun run --cwd apps/web test src/components/serviceUpdateRunView.test.ts

### T-05 Merge, release and timed M4 update
- AC: AC-06 | Files: none | Test: receipt timings on M4

### T-06 Verify and close 1160
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: none | Test: specweave verify 1160
