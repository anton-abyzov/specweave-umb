# Updates survive database restarts and finish fast

## Problem

On 2026-10-28 an Update now to 1.0.106 ran 592 s and never applied, after about 2 h of refusals (report: /mnt/project-files/update-report.md). The helper saw lost SQLite locks and restarted the held service (database-restart receipt 20261028T060501Z). The hold lives only in memory (ServiceUpdateHold.ts), the restart marker carries only servicePid and restartedAt (update.py:353), and startup gates only on an in-memory hold or install-gate.json (serverRuntimeStartup.ts:567). So the new service resumed the interrupted turn and started 3 Codex clients, and every reap refused at update_service.py assert_held because hold.json was gone and launched <= began <= requested cannot hold after a restart. The same pattern hit 1.0.95 (10 failed reaps). Finder .DS_Store files also still break two strict release listers (activate-providers.py verify, update_agent.py verify_helpers) that #925 did not cover. A clean install takes a median 171 s, 62% of it one full 21 GB database read; when the delta read misses (pages-outside-auth) a second full read adds 109-300 s. Orphaned owned-updates and verification folders are never pruned.

## Scope

In: carrying a forced request's hold across a held database restart (helper marker, service startup, reap check); Finder-proof provider and helper verification and the pre-* backup filter; avoiding the full re-read after a delta-read miss where the proof allows; age-pruning orphaned owned-updates, held receipts, reap records and install/verification. Out: deleting or compacting database rows, VACUUM, one-time disk cleanup (each needs Anton's approval), worktree and home cleanup (owned by the Reclaim disk thread), automatic-install behaviour.

## Acceptance Criteria

- [ ] AC-01: When the helper restarts a service that holds itself for a forced request, the restarted service starts held for that same request (no thread resumes, no agent starts) until the install releases or the hold expires, and reap and the held gate settle accept that carried hold; a restart with no open forced request, a mismatched request or an expired hold starts normally.
- [ ] AC-02: A regular Finder .DS_Store file in a release, helper folder, provider release or backup folder no longer fails provider activation, helper verification or backup pruning; any other unlisted file or a symlink named .DS_Store still fails.
- [ ] AC-03: A forced install whose delta read misses does not repeat a full database read before the stop when the earlier full read still proves the rows; every refusal still names its cause.
- [ ] AC-04: Orphaned owned-updates folders, held receipts and reap records older than 7 days, and install/verification entries older than 7 days, are pruned after an update; the current run's files and the last verified install's files are never removed.

## Approach

Studio repo, worktree ~/.specwithcode/m4/worktrees/update-restart-hold, branch fix/update-restart-hold from origin/main. Helper: update.py restart marker gains request, installRunId, until; update_service.assert_held accepts a carried hold (hold.request == request, began within launched..ends). Service: ServiceUpdateHold re-takes a hold at startup from a matching marker plus open forced request; serverRuntimeStartup gates on isHeld || installRequestOpen. Python listers reuse release_check.FINDER_FILES. Rejected: removing the database restart (it fixes lost locks), persisting every hold to disk (a crash would leave threads paused forever; the marker is bounded by until).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Code-only fixes ship now; row compaction, VACUUM and the 8.5 GB one-time cleanup wait for Anton's yes.
- D-02: A carried hold ends at the original hold's expiresAt, never later.
### Open
- none

## Tasks

### T-01 Carry the hold across a held database restart
- AC: AC-01 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update_service.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/database_restart.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-database-restart.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-reap.py, repositories/anton-abyzov/specweave-studio/apps/server/src/serviceUpdate/ServiceUpdateHold.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/serviceUpdate/ServiceUpdateHold.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/serverRuntimeStartup.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/serverRuntimeStartup.test.ts | Test: cd ~/.specwithcode/m4/worktrees/update-restart-hold && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && python3 scripts/studio-fleet/test-database-restart.py && python3 scripts/studio-fleet/test-reap.py && node node_modules/vite-plus/bin/vp test run apps/server/src/serviceUpdate/ServiceUpdateHold.test.ts apps/server/src/serverRuntimeStartup.test.ts && node node_modules/vite-plus/bin/vp run @specweave-studio/server#typecheck

### T-02 Ignore Finder files in every strict release check
- AC: AC-02 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/activate-providers.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-activate-providers.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update_agent.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-update-agent-install.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/state_backup_prune.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-state-backup-prune.py | Test: cd ~/.specwithcode/m4/worktrees/update-restart-hold && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && python3 scripts/studio-fleet/test-activate-providers.py && python3 scripts/studio-fleet/test-update-agent-install.py && python3 scripts/studio-fleet/test-state-backup-prune.py

### T-03 Skip the repeated full read after a delta-read miss
- AC: AC-03 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/read_delta.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/read_watermark.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-read-watermark.py | Test: cd ~/.specwithcode/m4/worktrees/update-restart-hold && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && python3 scripts/studio-fleet/test-read-watermark.py && python3 scripts/studio-fleet/test-release-helpers.py

### T-04 Prune orphaned update records and old verification
- AC: AC-04 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/release_retention.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-release-retention.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update.py | Test: cd ~/.specwithcode/m4/worktrees/update-restart-hold && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && python3 scripts/studio-fleet/test-release-retention.py

### T-05 Verify and close 1116
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update.py | Test: cd ~/.specwithcode/m4/worktrees/update-restart-hold && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && bash scripts/studio-fleet/run-tests.sh && node node_modules/vite-plus/bin/vp test run apps/server/src/serviceUpdate apps/server/src/serverRuntimeStartup.test.ts && node node_modules/vite-plus/bin/vp run @specweave-studio/server#typecheck
