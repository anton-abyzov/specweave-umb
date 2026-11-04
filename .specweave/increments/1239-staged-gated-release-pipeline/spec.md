# Staged, gated release pipeline with canary and fleet acks

## Problem

A SpecWithCode studio release is one sequential script (`specwithcode-dev/scripts/release/release.sh`) on the M4. It publishes GitHub Releases on both repos before any machine has installed the build. Nothing launches the built app, nothing rehearses migrations on real old state, and no free-disk check runs before an update stops the service. Every host updates straight from GitHub. On 2026-11-04 this produced three failures:

- (a) M4's 1.0.184 update ran out of scratch disk after the service had stopped. The cause was a full read for migration 072 (`additive_migrations.py` FULL_READ, `database_continuity.py:138-141`), and `release.sh:100-149` has no disk check.
- (b) Two updates failed on M4 after the stop: 1.0.180, where the new service wrote `project_plans` (`update_migration.py:250-251`), and 1.0.184, the 072 full read. Migrations 068, 070 and 072 have no tests, and every test fixture is a tiny synthetic database.
- (c) M1 and M3 were never sent 1.0.186. Worker rollout runs only inside `release.sh` after `fleet-m4` (`release.sh:1094-1101`). In 1.0.187 a slow restart was counted as a lost host (`fleet_rollout.py:111, 819-821`), and a skipped host still exits 0 (`fleet_rollout.py:934-939`).

The full analysis, with the reference project's `release.yml` comparison, is on the M4 at `~/.specwithcode/release-pipeline-proposal.md`, with a local copy in this increment's `reports/` (untracked evidence).

## Scope

In (`repositories/anton-abyzov/specwithcode-dev` unless noted):
- Phase 1, stop the bleeding: free-disk preflight on every host, `update.py room`, fleet rollout exit codes, acknowledgement, a time-window restart wait, a rollout lock, and a reconcile on M4 `installFinalized`.
- Phase 2, migration rehearsal: tests for migrations 068, 070 and 072; a coverage rule; a check that full reads complete; protected tables unchanged after a restart; `rehearse_update.py` on a temporary copy of M4's real `statev2.sqlite`.
- Phase 3, built-app verify: `verify-built-app.mjs` for fresh and upgraded installs, the acceptance proofs wired into `verify.*`, and a macOS desktop E2E leg.
- Phase 4, R2 candidate channel and canary: `r2_publish.py` (publish, rollback, retention), channel feeds in `update_agent.py` with GitHub as the fallback, a canary stage, and GitHub flips moved into `finalize`.
- Phase 5, visibility: a `release.yml` `needs:` graph with `--stage` entry points, an 8-shard server matrix, a run record, and an in-app Releases view.
- Umbrella: `.specweave/release/manifest.json` route and verify entries, and `scripts/release/release.sh` for the dispatch.

Out: npm CLI publishing (not shipped from this track), AUR, the marketing site deploy, Discord announcements, and changes to other products' release tracks.

## Acceptance Criteria

### US-01 Stop the bleeding (phase 1)
As the owner, I want a release to refuse to start when any host lacks disk, and to fail loudly when any required machine does not end verified, so that a release never half-applies or silently skips M1 and M3.
- [ ] AC-01: `update.py room --version <v> --json` reports needed and free bytes (fallback room for pending FULL_READ migrations + backup + staged release). Release preflight runs it on M4 and every fleet host, and stops with the host name, need and free space when any host is short.
- [ ] AC-02: `update.py apply` checks fallback room before draining the service. With too little room, the service is never stopped.
- [ ] AC-03: `fleet_rollout.py` exits non-zero with `result: partial` and a per-host `not-updated` row (with a reason) when any required host (M4, M1, M3) is unreachable, skipped or not verified. Optional hosts may end `not-updated` with exit 0.
- [ ] AC-04: A host that answers no status reads for up to 5 minutes after install, then reports the new version, ends `verified` (a time window replaces the 5-strike rule).
- [ ] AC-05: Worker install requests are acknowledged (request id written back) and retried in bounded windows.
- [ ] AC-06: An exclusive rollout lock stops two rollouts or reconciles from sending duplicate requests. A stale lock left by a dead PID is reclaimed.
- [ ] AC-07: An M4 `installFinalized` from any path (Update now, hourly agent) triggers a workers reconcile, so M1 and M3 on N-1 get a request and a run row.

### US-02 Rehearse migrations before publish (phase 2)
As the owner, I want every release's migrations rehearsed on real old state before anything is published, so that a migration can never trip the post-update check on the fleet.
- [ ] AC-08: Migrations 068, 070 and 072 have `.test.ts` files: a rebuild on a populated table keeps every row, and the new constraints and indexes exist.
- [ ] AC-09: The coverage rule fails when a migration after 066 has no sibling test, or rebuilds a table without a `REBUILT` entry and a fixture.
- [ ] AC-10: Every FULL_READ and REBUILT migration reaches `phase: verified` on a populated fixture.
- [ ] AC-11: The candidate server started on a fixture with linked memory and a project plan (the synthetic CI fixture) runs 120 s idle. Every protected table keeps the same count and hash, and the test proves `LinkedMemorySync` actually ran.
- [ ] AC-12: `rehearse_update.py` runs `update.py apply` with the candidate helper and server on a temporary APFS clone of M4's latest real `statev2.sqlite` and `config.json`. The copy never leaves M4 and is deleted afterwards. It asserts verified, proof mode, time budget, unchanged protected hashes, and an upgraded `config.json` with no lost keys. `release.sh` runs it as a blocking background job before publish.

### US-03 Verify the built app (phase 3)
As the owner, I want the exact artifact we ship launched headless on a fresh install and on an upgraded install before publish, so that a build that cannot start or pass the post-update check never reaches users.
- [ ] AC-13: `scripts/release/verify-built-app.mjs` starts the unpacked, signed macOS app headless with an isolated home. The environment endpoint reports `<v>`, and a thread runs against the fake ACP agent, within 120 s.
- [ ] AC-14: The upgraded mode seeds the home from the previous release's state fixture, then passes the post-update check and `test-installed-startup.mjs --local`.
- [ ] AC-15: `release.sh` runs both modes after `sign` and before any draft or publish. The acceptance proofs excluded in `run-tests.sh:31-34` run in that stage, and a skipped verify counts as a failure.
- [ ] AC-16: Desktop E2E gains a macOS leg, and Windows and Linux release jobs run the equivalent verify.

### US-04 Candidate channel and canary (phase 4)
As the owner, I want builds to reach a candidate channel and one canary machine before the fleet and stable, so that a bad release never becomes public or reaches every machine.
- [ ] AC-17: `r2_publish.py` uploads verified assets to `candidate/<v>/`, re-downloads and matches digests, writes `candidate.json`, and prunes old candidate prefixes without touching the current candidate or stable targets.
- [ ] AC-18: `update_agent.py` reads a channel feed (`stable|candidate`) with GitHub as the fallback. An N-1 agent never crashes or downgrades, and a host not in the rollout never installs from `candidate.json`.
- [ ] AC-19: The `canary` stage installs the candidate on M4 and soaks 15 min (`fleet_health.py` clean, no new `stderr.log` errors) before `fleet` runs.
- [ ] AC-20: GitHub draft flips, the `stable.json` swap (keeping `stable.prev.json`) and the `release/<v>` merge happen only in `finalize`, after `fleet` reports M4, M1 and M3 verified. `r2_publish.py rollback` restores the previous stable pointer atomically.

### US-05 Show the graph (phase 5)
As the owner, I want to see the release as a stage graph with a row per machine, both in GitHub Actions and in SpecWithCode, so that I can tell at a glance what passed, what runs and which machine did not update.
- [ ] AC-21: Each release writes one run record (`updates/runs/release-<v>-<runId>.json`, `kind: "release"`) with stage ids, states, times and log paths, plus per-host rows (asked, acked, installed, verified or not-updated with a reason). Writes are atomic, and a resume keeps prior rows.
- [ ] AC-22: `.github/workflows/release.yml` expresses the stages as a `needs:` graph. Every job runs `release.sh <v> --stage <id> --resume`, and the server suite runs as an 8-shard matrix with a merge job.
- [ ] AC-23: The SpecWithCode web app has a Releases view: the stage graph with live states, plus a per-machine table for canary and fleet, read from the run record through a server endpoint.

## Approach

Follow the proposal's sections 5 to 7 (stage table, tests, graph). Stage ids are `resolve`, `preflight`, `test.unit`, `test.server`, `test.web`, `test.fleet`, `test.desktop-e2e`, `test.migration`, `build.<platform>`, `verify.<platform>`, `publish.candidate`, `canary`, `fleet`, `finalize` and `verify.release`. The same ids are used by `release.sh` markers, GitHub Actions jobs and the run record.

`release.sh ship studio` stays the only entry point, and no stage adds a manual approval. Waits longer than 540 s go through `ci-wait.sh`.

Order matters. Phase 1 ships first and is self-contained. Phases 2 and 3 can overlap. Phase 4 must ship channel support in `update_agent.py` as a stable release through the GitHub feed before any candidate-only rollout (schema skew). Phase 5 uses phase 4's stage ids.

Process: one PR per phase on its own branch, built outside the shared checkout's working tree. For each phase: review, fix findings, green CI, merge, then release. Before each release, check that no other release or rollout is running and that M4 has free disk.

## Decisions

### Asked
- none
### Defaulted (owner approved all five phases, relayed by the coordinator on 2026-11-04; owner can override)
- D-01 Candidate channel lives on R2, not as a GitHub prerelease.
- D-02 The migration rehearsal runs on a temporary copy of M4's real `statev2.sqlite` that never leaves the machine and is deleted afterwards. A synthetic fixture with linked memory and `project_plans` is kept for CI.
- D-03 A release counts as done only when M4, M1 and M3 are all `verified`. Any other state fails the run with a per-machine report. Ministorm and other machines are optional.
- D-04 Canary soak stays at 15 minutes.
- D-05 npm CLI publishing is dropped from `finalize` (this track does not ship a CLI).
### Open
- Which runner `ship studio` dispatches `release.yml` to (M1 `swc-release` plus an M4 `m4` label, or a local graph walk with Actions as the fallback). This is decided in phase 5.
- Whether activation should wait for the post-restart proof (the held-rollback case in failures a and b). This is decided in phase 2.

## Tasks

### T-01 Host room report and disk preflight
- AC: AC-01 | Files: scripts/studio-fleet/update.py, scripts/studio-fleet/update_apply.py, scripts/release/preflight_fleet.py, scripts/release/release.sh, scripts/studio-fleet/test-preflight-disk.py | Test: python3 scripts/studio-fleet/test-preflight-disk.py

### T-02 Room check before the service stops
- AC: AC-02 | Files: scripts/studio-fleet/update.py, scripts/studio-fleet/update_apply.py, scripts/studio-fleet/test-room-before-stop.py | Test: python3 scripts/studio-fleet/test-room-before-stop.py

### T-03 Skipped or unverified required host fails the rollout
- AC: AC-03 | Files: scripts/studio-fleet/fleet_rollout.py, scripts/studio-fleet/test-rollout-skipped-is-failure.py | Test: python3 scripts/studio-fleet/test-rollout-skipped-is-failure.py

### T-04 Restart time window and acknowledged requests
- AC: AC-04, AC-05 | Files: scripts/studio-fleet/fleet_rollout.py, scripts/studio-fleet/remote_update.py, scripts/studio-fleet/test-rollout-slow-restart.py | Test: python3 scripts/studio-fleet/test-rollout-slow-restart.py

### T-05 Rollout lock
- AC: AC-06 | Files: scripts/studio-fleet/fleet_rollout.py, scripts/studio-fleet/test-rollout-lock.py | Test: python3 scripts/studio-fleet/test-rollout-lock.py

### T-06 Reconcile workers on M4 installFinalized
- AC: AC-07 | Files: scripts/studio-fleet/update_agent.py, scripts/studio-fleet/fleet_rollout.py, scripts/studio-fleet/test-reconcile-on-finalize.py | Test: python3 scripts/studio-fleet/test-reconcile-on-finalize.py

### T-07 Release phase 1
- AC: AC-01, AC-03, AC-07 | Files: CHANGELOG.md | Test: bash scripts/studio-fleet/run-tests.sh --out /tmp/1239-p1-fleet

### T-08 Tests for migrations 068, 070 and 072
- AC: AC-08 | Files: apps/server/src/persistence/Migrations/068_ActiveTurnItemIndexes.test.ts, apps/server/src/persistence/Migrations/070_ThreadHistoryCompactions.test.ts, apps/server/src/persistence/Migrations/072_RetentionHorizon.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/persistence/Migrations

### T-09 Migration coverage rule
- AC: AC-09 | Files: scripts/studio-fleet/test-update-migration-coverage.py, scripts/studio-fleet/additive_migrations.py | Test: python3 scripts/studio-fleet/test-update-migration-coverage.py

### T-10 Full reads and declared rebuilds complete
- AC: AC-10 | Files: scripts/studio-fleet/test-full-read-completes.py | Test: python3 scripts/studio-fleet/test-full-read-completes.py

### T-11 Protected tables unchanged after restart
- AC: AC-11 | Files: scripts/studio-fleet/test-protected-tables-after-restart.py, scripts/studio-fleet/fixtures/linked-memory-state/ | Test: python3 scripts/studio-fleet/test-protected-tables-after-restart.py

### T-12 Real-state rehearsal in the release
- AC: AC-12 | Files: scripts/studio-fleet/rehearse_update.py, scripts/studio-fleet/test-rehearse-update.py, scripts/release/release.sh | Test: python3 scripts/studio-fleet/test-rehearse-update.py

### T-13 Release phase 2
- AC: AC-08, AC-12 | Files: CHANGELOG.md | Test: bash scripts/studio-fleet/run-tests.sh --out /tmp/1239-p2-fleet

### T-14 Built-app verify, fresh and upgraded
- AC: AC-13, AC-14 | Files: scripts/release/verify-built-app.mjs, scripts/release/verify-built-app.test.mjs | Test: node --test scripts/release/verify-built-app.test.mjs

### T-15 Verify stage in release.sh and acceptance proofs
- AC: AC-15 | Files: scripts/release/release.sh, scripts/release/release-self-test.sh, scripts/studio-fleet/run-tests.sh | Test: bash scripts/release/release-self-test.sh

### T-16 macOS desktop E2E leg and Windows/Linux verify
- AC: AC-16 | Files: .github/workflows/desktop-windows-linux.yml, .github/workflows/release-windows-linux.yml, scripts/desktop-windows-linux-workflow.test.ts | Test: node node_modules/vite-plus/bin/vp test run scripts/desktop-windows-linux-workflow.test.ts

### T-17 Release phase 3
- AC: AC-13, AC-15 | Files: CHANGELOG.md | Test: bash scripts/release/release-self-test.sh

### T-18 R2 publish, rollback and retention
- AC: AC-17, AC-20 | Files: scripts/release/r2_publish.py, scripts/release/test-stable-rollback.py, scripts/release/test-candidate-retention.py | Test: python3 scripts/release/test-stable-rollback.py && python3 scripts/release/test-candidate-retention.py

### T-19 Channel feeds in the update agent
- AC: AC-18 | Files: scripts/studio-fleet/update_agent.py, scripts/studio-fleet/test-channel-feed-skew.py, scripts/studio-fleet/test-candidate-ignored-off-canary.py | Test: python3 scripts/studio-fleet/test-channel-feed-skew.py && python3 scripts/studio-fleet/test-candidate-ignored-off-canary.py

### T-20 Canary stage and finalize reorder
- AC: AC-19, AC-20 | Files: scripts/release/release.sh, scripts/studio-fleet/fleet_rollout.py, scripts/release/release-self-test.sh | Test: bash scripts/release/release-self-test.sh

### T-21 Release phase 4
- AC: AC-17, AC-18, AC-19, AC-20 | Files: CHANGELOG.md, ../../../.specweave/release/manifest.json | Test: bash scripts/release/release-self-test.sh

### T-22 Release run record
- AC: AC-21 | Files: scripts/release/run_record.py, scripts/release/test-run-record.py, scripts/release/release.sh, scripts/studio-fleet/fleet_rollout.py | Test: python3 scripts/release/test-run-record.py

### T-23 release.yml needs graph and 8-shard server matrix
- AC: AC-22 | Files: .github/workflows/release.yml, scripts/release/release.sh, scripts/release/release-self-test.sh, scripts/release/test-sharded.mjs | Test: bash scripts/release/release-self-test.sh

### T-24 Releases view in SpecWithCode
- AC: AC-23 | Files: apps/server/src/releases/ReleaseRunService.ts, apps/server/src/releases/ReleaseRunService.test.ts, apps/web/src/components/releases/ReleasesView.tsx, apps/web/src/components/releases/ReleasesView.test.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/releases apps/web/src/components/releases

### T-25 Verify and close 1239
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15, AC-16, AC-17, AC-18, AC-19, AC-20, AC-21, AC-22, AC-23 | Files: none | Test: bash scripts/release/release-self-test.sh
