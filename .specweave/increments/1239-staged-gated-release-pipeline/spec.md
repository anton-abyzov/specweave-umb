# Staged, gated release pipeline

## Problem

Until November 4, 2026 SpecWithCode shipped from one sequential script, `scripts/release/release.sh` in `repositories/anton-abyzov/specwithcode-dev`, run on M4 by the umbrella's `release.sh ship studio` or on the M1 runner by `release-macos.yml`. It published to GitHub Releases before any machine had installed the release, never launched the built app, never rehearsed migrations on real state, and treated an unreachable worker as skipped. Three failures traced to those gaps: M4 ran out of scratch disk mid-update on 1.0.184, migrations tripped the post-update check on 1.0.180 and 1.0.184, and M1 and M3 were never sent 1.0.186 or 1.0.187. The design is in [reports/release-pipeline-proposal.md](reports/release-pipeline-proposal.md).

## Scope

In: disk preflight on every host, strict rollout semantics and a rollout lock, workers reached over SpecWithCode Connect, migration rehearsal, a headless launch of the built app before drafts, the R2 candidate channel with a canary soak and GitHub publish after the fleet, a run record per release, the staged `release.yml` graph and the Releases view, a dry run of that workflow, `verify.release` running the post-ship checks, and the umbrella manifest marking specwithcode-dev Actions enabled.

Out: switching the production release from `release-macos.yml` to `release.yml` (the owner does that after the staged workflow ships a release), the umbrella `ship studio` dispatching `release.yml`, R2 as the only update source, Windows and Linux builds inside the graph (they stay in `release-windows-linux.yml`).

## Acceptance Criteria

- [x] AC-01: Before anything is built, the preflight checks free disk on M4, M1 and M3 for the release's update (`preflight_fleet.py`, `fleet room` over SpecWithCode Connect, SSH only with `--ssh-fallback`); `fleet_rollout.py` fails on a skipped or unreachable required host, holds an exclusive rollout lock, tolerates a slow restart, and reconciles workers on finalize (PRs #1375, #1383, #1388).
- [x] AC-02: Migrations 068, 070 and 072 have rehearsal tests, and `rehearse_update.py` rehearses the update on a copy of real state beside the server suite (PR #1384).
- [x] AC-03: The signed app is launched headless, fresh and upgraded from the previous release's state, after sign and before drafts; drafts refuse a candidate without a passed verify (PR #1385).
- [x] AC-04: With the candidate channel, publish.candidate writes only to R2, the canary installs and soaks on M4, the fleet follows, and only finalize publishes to GitHub and promotes stable (PR #1394).
- [x] AC-05: Every release writes one run record; `release.yml` runs the release graph as one job per stage (`release.sh --stage ID --resume`, 8 server shards and a merge), gives release secrets only to stages that sign, push or publish, and the Releases view shows the run, its stages and each machine (PRs #1399, #1405, #1409).
- [x] AC-06: The umbrella manifest marks specwithcode-dev `actions_enabled: true`; `release.yml` has a `dry_run` input that runs every stage as `release.sh --stage ID --dry-run` with no release secret and its own concurrency group, and one dry run of `Release (staged)` passes while publishing, tagging and pushing nothing.
- [x] AC-07: The staged workflow owns the ship: `verify.release` runs the checks `release.sh ship studio` runs after a release (v<version> published on both repositories, the private one with `studio-update.json`, `SHA256SUMS` and the dmg, the tagged commit on main), records them in the run record and fails the run when one is missing; `release-macos.yml` keeps working unchanged as the fallback.
- [x] AC-08: The change is a PR to specwithcode-dev main with required Checks green and an exact-head SHIP review in a fresh context; the owner merges it and dispatches releases.

## Approach

All code is in `repositories/anton-abyzov/specwithcode-dev`; the increment's records stay in the umbrella. Phases 1 to 5 of the proposal merged on November 4, 2026. The finishing work, on branch `feat/1239-staged-release` (PR #1440):

- `release.yml` and `release-stage.yml` take `dry_run`. A dry run passes `--dry-run` instead of `--resume`, forces `RELEASE_SECRETS` false so the GitHub token is the run's read-only one, skips the Rust and Playwright installs, and uses the concurrency group `release-dry-run-<run id>` so it never queues behind or blocks a release in `release-macos`.
- `release-record.sh` gains `stage_verify_release`, reached from `stage_entry` for `--stage verify.release`: read-only `gh` checks, a run-record row with the missing items as a fact, and `record_finish 1` on failure. Stub answers for the self-test live in `release_common.sh`.
- `docs/studio/releasing.md` documents the staged workflow and its dry run; `release-macos.yml` is untouched.
- Umbrella `.specweave/release/manifest.json`: `actions_enabled: true` for specweave-studio (it only changes the status table; Actions already run there).

## Decisions

### Asked
- none
### Defaulted
- D-01: The owner's "move the `release.sh ship studio` step from release-macos.yml" was read as moving the post-ship verification into `release.yml`'s `verify.release`: neither workflow calls `release.sh ship studio`, which is the umbrella entry point that runs the release script and then `verify_track`. `release-macos.yml` keeps its Release step so the current production path keeps working.
- D-02: Windows and Linux files are counted in `verify.release`, not required; `release-windows-linux.yml` attaches them on its own schedule.
- D-03: The fleet endpoint and desktop-app checks of `verify_track` stay out of `verify.release`: under `--ci` the machines install on their next update check, so they would only report pending.
### Open
- none

## Tasks

### T-01 Fleet preflight, strict rollout, Connect transport
- AC: AC-01 | Files: scripts/release/preflight_fleet.py, scripts/studio-fleet/fleet_rollout.py | Test: gh pr view 1375 -R anton-abyzov/specwithcode-dev --json state -q .state | grep -qx MERGED && gh pr view 1383 -R anton-abyzov/specwithcode-dev --json state -q .state | grep -qx MERGED && gh pr view 1388 -R anton-abyzov/specwithcode-dev --json state -q .state | grep -qx MERGED

### T-02 Migration rehearsal and release-stability tests
- AC: AC-02 | Files: scripts/studio-fleet/rehearse_update.py, scripts/release/release_rehearsal.sh | Test: gh pr view 1384 -R anton-abyzov/specwithcode-dev --json state -q .state | grep -qx MERGED

### T-03 Verify the built app before drafts
- AC: AC-03 | Files: scripts/release/verify-built-app.mjs, scripts/release/release-verify.sh | Test: gh pr view 1385 -R anton-abyzov/specwithcode-dev --json state -q .state | grep -qx MERGED

### T-04 Candidate channel, canary soak, finalize after fleet
- AC: AC-04 | Files: scripts/release/r2_publish.py, scripts/release/canary_soak.py, scripts/release/release-canary.sh | Test: gh pr view 1394 -R anton-abyzov/specwithcode-dev --json state -q .state | grep -qx MERGED

### T-05 Run record, staged release.yml graph, Releases view
- AC: AC-05 | Files: .github/workflows/release.yml, .github/workflows/release-stage.yml, scripts/release/run_record.py, apps/web/src/components/releases/ReleasesView.tsx | Test: for n in 1399 1405 1409; do gh pr view $n -R anton-abyzov/specwithcode-dev --json state -q .state | grep -qx MERGED || exit 1; done

### T-06 Enable the staged workflow and dry-run it
- AC: AC-06 | Files: .specweave/release/manifest.json, .github/workflows/release.yml, .github/workflows/release-stage.yml, scripts/release-workflow.test.ts | Test: jq -e '.repos[] | select(.name == "specweave-studio") | .actions_enabled == true' .specweave/release/manifest.json && gh run view 42273682602 -R anton-abyzov/specwithcode-dev --json conclusion -q .conclusion | grep -qx success

### T-07 verify.release owns the ship checks; PR with Checks and SHIP review
- AC: AC-07, AC-08 | Files: scripts/release/release-record.sh, scripts/release/release_common.sh, scripts/release/release-self-test-record.sh, docs/studio/releasing.md | Test: gh pr view 1440 -R anton-abyzov/specwithcode-dev --json state -q .state | grep -qx MERGED

### T-08 Verify and close 1239
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: .specweave/increments/1239-staged-gated-release-pipeline/spec.md | Test: gh pr view 1440 -R anton-abyzov/specwithcode-dev --json state -q .state | grep -qx MERGED
