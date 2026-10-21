# Fast observable service install

## Problem

The 1.0.65 update on M4 (2026-10-21) succeeded but took 15m15s from the Update now press to the relaunched app, while the service was down for about 4 s. update.py spent about 730 of its 810 s on roughly six full proof reads of the 8.05 GB statev2.sqlite (about 90 s each), and the accepted post-restart read finished about 17 s past READINESS_DEADLINE_SECONDS=300. The receipt landed 26 s before the 15-minute service hold expired. The toast showed one static "Installing" line for 13.5 min because the helper reports no phases. Evidence: receipts/update-1.0.65-20261021T120652771099Z.json, design and research notes in reports/ (Codex, ChatGPT, T3 Code, Skill Studio, our flow, timeline).

## Scope

In: the release helper (scripts/studio-fleet) only, so the 1.0.65 to 1.0.66 install itself benefits: watermark-guarded skip of the pre-restart re-reads, readiness split from the full post-restart proof, an APFS clone backup taken after the service stops, live install-progress.json with phases, heartbeat and timings, and the #551 helper half (a deleted-log service is stopped with SIGTERM, never killed). Out: desktop and web UI (fix/update-now-one-press owns them for 1.0.66), the single run record and main-owned app follow-up (next increment), the launcher (later), database growth.

## Acceptance Criteria

- [ ] AC-01: When the database did not change (same data_version on one read-only connection, same inode, size and WAL salt, no reconnect), update.py reuses its last full read instead of re-reading before the restart; any change or doubt triggers a full read, and the proof format stays byte-identical on fixtures.
- [ ] AC-02: After the restart, a cheap readiness check (new pid, target version answering) is bounded by READINESS_DEADLINE_SECONDS and one full post-restart read always runs; a mismatch still rolls back.
- [ ] AC-03: The state backup is taken after the old service stops, as a clonefile copy of the db, -wal and -shm with a headroom check and an sqlite3 backup fallback; restore and pruning work unchanged.
- [ ] AC-04: During an apply, updates/install-progress.json names the current phase, step i of n, elapsed and expected time, and a heartbeat at least every 5 s, and ends with the result on success, refusal or rollback.
- [ ] AC-05: The 1.0.65 update agent accepts the new helper's snapshot, preflight and verified receipt unchanged.
- [ ] AC-06: A deleted-log service is stopped with SIGTERM and a wait, never kickstart -k or SIGKILL.

## Approach

Base: perf/update-install-speed-v2 (data_version idle gate, one capture scan, per-phase timings), rebased onto main, plus PR #551's helper commit. New logic lives in new modules (read_watermark.py, install_progress.py) because update.py is over the size cap. Branch perf/update-install-fast-proofs in ~/.specwithcode/m4/worktrees/fast-proofs. Full staged design (run record, main-owned app follow-up, launcher) in reports/design.md.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Service first, app only after the service is verified (unchanged from 0957).
- D-02: Re-reads are skipped only on a provably unchanged watermark; the post-restart full read is never skipped.
### Open
- D-03: May a forced Update now close open questions so they cannot block it (recorded, reopened after)? Recommended yes; not in this increment.

## Tasks

### T-01 Watermark-guarded re-reads
- AC: AC-01, AC-05 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/read_watermark.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-read-watermark.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-update.py | Test: cd ~/.specwithcode/m4/worktrees/fast-proofs/scripts/studio-fleet && python3 -B test-read-watermark.py && python3 -B test-update.py

### T-02 Readiness split and clone backup after stop
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-update.py | Test: cd ~/.specwithcode/m4/worktrees/fast-proofs/scripts/studio-fleet && python3 -B test-update.py && python3 -B test-update-timings.py

### T-03 Live install progress
- AC: AC-04 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/install_progress.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-install-progress.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/make_helpers.py, repositories/anton-abyzov/specweave-studio/docs/studio/updates.md | Test: cd ~/.specwithcode/m4/worktrees/fast-proofs/scripts/studio-fleet && python3 -B test-install-progress.py && python3 -B test-update.py

### T-04 Deleted-log service stop
- AC: AC-06 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/database_restart.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-database-restart.py | Test: cd ~/.specwithcode/m4/worktrees/fast-proofs/scripts/studio-fleet && python3 -B test-database-restart.py

### T-05 Measured run on a clone of M4's database
- AC: AC-01, AC-02, AC-03, AC-05 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/run-tests.sh | Test: cd ~/.specwithcode/m4/worktrees/fast-proofs/scripts/studio-fleet && bash run-tests.sh
