# Harden update installs against Finder races and rows changed during the hold

## Problem

M4's 1.0.112 install failed twice at preflight on 2026-10-28 (receipts update-1.0.112-20261028T21*):
1. "Guarded prestate changed: rows": rows changed between the agent's prestate and the helper's read while the service was held.
2. OSError Errno 66 "Directory not empty" from update.py's staging TemporaryDirectory cleanup, because Finder wrote .DS_Store into it.

3. "Owned service process identity changed" from quiescence.py _owned_tree while many threads were running.

4. "Preparing the update took too long to leave time for the restart" on a quiet retry: preflight took ~902 s (beforeRead 527, stage 101, prestateCheck 274) against a ~780 s pre-restart budget (agent APPLY_TIMEOUT 1500).

Each failure costs a full retry and blocks the update.

## Scope

In: update.py staging cleanup; the rows guard or the hold so benign writers no longer refuse an install. Out: backup and staging retention (the "Reclaim disk" thread owns it).

## Acceptance Criteria

- [ ] AC-01: A Finder file written into the staging folder during cleanup never fails an update; leftovers are pruned later.
- [ ] AC-02: The benign row change seen at 21:11Z no longer refuses an install, and a real user-data change during the hold still refuses.
- [ ] AC-03: A service that exits or restarts during the update read gives a retryable refusal (automatic and Install now), and a different or foreign service process still refuses.
- [ ] AC-04: A pre-restart phase as slow as M4's (~902 s) fits the install budget, and the update hold covers the whole apply.

## Approach

scripts/studio-fleet/update.py adds scratch_directory (mkdtemp plus a cleanup that retries and then leaves the folder for prune_update_leftovers). Rows: the 21:11Z refusal was an auth_pairing_links insert (POST /api/auth/pairing-token, label memory-cleanup, 21:16:47Z) during the hold. Pairing grants are bearer-equivalent, so the guard stays exact; instead the hold now refuses pairing-token mints with 503 update_in_progress (apps/server/src/auth/http.ts, admit), and a mint admitted before the hold is drained.

Process identity: the 21:26:57Z refusal was a `launchctl bootout` of the service by another Claude session at 21:28:59Z, mid-read. The refusal stays (the rows were read from the old process); it is now SERVICE_RESTARTED, a 'Guarded prestate changed' refusal the agent retries from a fresh snapshot.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Staging cleanup never raises; prune_update_leftovers removes owned-update-stage-* later.
### Open
- none

## Tasks

### T-01 Staging cleanup survives Finder files
- AC: AC-01 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-update.py | Test: cd ~/.specwithcode/m4/worktrees/update-hardening && python3 scripts/studio-fleet/test-update.py ScratchDirectory

### T-02 The hold stops pairing-token mints
- AC: AC-02 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/auth/http.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/environmentHttp.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/auth/http.test.ts, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-update-apply.py | Test: cd ~/.specwithcode/m4/worktrees/update-hardening && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && node node_modules/vite-plus/bin/vp test run apps/server/src/auth/http.test.ts && python3 scripts/studio-fleet/test-update-apply.py

### T-03 A service restart during the update read becomes a retry
- AC: AC-03 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/quiescence.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-update-quiescence.py | Test: cd ~/.specwithcode/m4/worktrees/update-hardening && python3 scripts/studio-fleet/test-update-quiescence.py && python3 scripts/studio-fleet/test-update-agent-recovery.py

### T-04 Install budget fits a slow preflight
- AC: AC-04 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update_agent.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update_request.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/fleet_rollout.py | Test: cd ~/.specwithcode/m4/worktrees/update-hardening && for t in scripts/studio-fleet/test-update*.py scripts/studio-fleet/test-fleet-rollout.py; do python3 $t || exit 1; done

### T-05 Verify and close 1134
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update.py | Test: cd ~/.specwithcode/m4/worktrees/update-hardening && python3 scripts/studio-fleet/test-update.py && python3 scripts/studio-fleet/test-update-apply.py
