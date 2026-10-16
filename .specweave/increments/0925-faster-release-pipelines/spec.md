# Faster release pipelines and release-timing regression scanning

## Problem

The four release tracks shipped on 2026-10-16 took far longer than their real work: specweave 13 min, vskill npm + Skill Studio desktop 30 min, verified-skill.com 79 min, SpecWithCode 1.0.36 98+ min. Profiling every CI job step and every command in the shipping transcripts (reports/find-*.md, each finding re-checked by an independent reviewer) shows where it went:

- verified-skill.com: vitest runs on one worker on the 2-vCPU private runner (14-15 min per PR, waited on 3 times); each local deploy builds Next twice; no post-deploy error gate, so a pg 8.23 regression served production for 12.5 minutes while the agent sat in a blind wait.
- vskill desktop: Rust caches never restore on tag builds (every release compiles cold), RPM bundling takes 321s on the critical Linux leg, a version-bump PR waited 9 minutes on a redundant Windows cargo job, assets upload twice, and the shipped DMG is not notarized because the only check uses `|| true`.
- SpecWithCode: no in-repo one-command release (12 min of rediscovery), the 22-minute server suite runs single-process and ran twice on identical source, fast suites ran after it so a contrast failure surfaced 24 minutes late and forced a second signed build, and the fleet rollout waited on the wrong condition and in the wrong order.
- Cross-cutting: no release manifest or entrypoint, CI waits blew the 600s tool cap, stale memory notes prescribed slow procedures, a truncated MEMORY.md hid the Studio release procedure, and nothing records step timings, so regressions such as permanent cache misses went unnoticed.

## Scope

In: CI workflow speedups (parallelism, sharding, caches, de-duplication, path filters, timeouts), one-command release scripts per repo, a post-deploy error gate with auto-rollback for verified-skill.com, macOS DMG notarization, flaky-test fixes found on the release path, an umbrella release manifest and entrypoint, a CI-wait helper, and a release-timing regression scanner with a CI workflow lint. Memory and runbook corrections.

Out: account or billing changes that only Anton can make (branch protection, npm Trusted Publisher for vskill, the VSKILL_PLATFORM_TOKEN secret, self-hosted or larger runners, re-enabling GitHub Actions on specwithcode-dev), dropping a user-facing installer format, and any change to the release that is in flight right now.

## Acceptance Criteria

- [ ] AC-01: vskill-platform unit tests use every runner core and are sharded with merged coverage that still enforces the 60% thresholds; PR wall time for the check drops well below today's 13-15 min.
- [ ] AC-02: vskill-platform has one release command that gates on green CI for the deployed tree, builds once, watches production logs after deploy and rolls back automatically on the Hyperdrive/pg error signatures.
- [ ] AC-03: vskill desktop tag builds restore warm Rust caches written on main, RPM bundling is off the critical leg, the release needs no bump PR, the DMG is notarized and stapled with gating checks, and the release script tags, watches and verifies end to end.
- [ ] AC-04: vskill CI and Sidecar Smoke drop redundant work (sharded unit suite, single cargo test, no unfiltered push trigger, concurrency, timeouts) and the Windows settings flake is fixed deterministically.
- [ ] AC-05: specweave release-path workflows skip work that cannot affect the result, have timeouts, and a one-command release script covers bump, merge, tag, publish and verification.
- [ ] AC-06: SpecWithCode has a resumable one-command local release: preflight, parallel stage-1 suites, sharded server suite run once on the final candidate, bundle verified before signing, drafts during waits, fleet rollout M4 first then M1/M3 on installedVersion, and a per-stage timing record compared with the previous release.
- [ ] AC-07: The umbrella has a release manifest, a release entrypoint with status and verify, a CI-wait helper that never trips the 600s cap, and a timing scanner that records step durations, flags regressions against a baseline and lints every workflow for missing caches, timeouts, concurrency and unfiltered triggers.
- [ ] AC-08: Memory notes and runbooks describe the current procedures, MEMORY.md fits its load limit, and no secret value remains in a memory note.

## Approach

One branch per repo, each in its own worktree (relperf-*), so the release still running from the shared checkouts is never touched. Every change follows the reviewer-corrected implementation notes in reports/find-<track>.md; findings marked unsafe are implemented only in the reviewer's safe form or left out. Desktop-release changes are validated through a new workflow_dispatch dry-run path before merge. Savings are measured on the next real runs by the new timing scanner rather than claimed up front.

Rejected: a CI deploy for verified-skill.com (puts a Workers token in Actions on a repo with supply-chain history, and gating on main CI is slower today), gradual Workers version splits (Durable Objects and OpenNext caches), parallel fleet installs including M4, and caching signed artifacts.

## Open questions

- none

## Tasks

### T-01 Platform CI: workers, shards, merged coverage, timing summary
- AC: AC-01 | Files: repositories/anton-abyzov/vskill-platform/.github/workflows/unit-tests.yml, repositories/anton-abyzov/vskill-platform/vitest.config.ts, repositories/anton-abyzov/vskill-platform/src/test-setup.ts, repositories/anton-abyzov/vskill-platform/scripts/ci/vitest-timing-summary.mjs | Test: gh run view (unit tests on the PR) shows sharded jobs and a green merge job

### T-02 Platform release command with post-deploy error gate and rollback
- AC: AC-02 | Files: repositories/anton-abyzov/vskill-platform/scripts/release.sh, repositories/anton-abyzov/vskill-platform/scripts/verify-deploy-errors.mjs, repositories/anton-abyzov/vskill-platform/package.json | Test: node --test scripts/verify-deploy-errors.test.mjs (vskill-platform)

### T-03 vskill desktop release: caches, RPM leg, notarized DMG, no bump PR, script
- AC: AC-03 | Files: repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml, repositories/anton-abyzov/vskill/.github/workflows/notarize-dryrun.yml, repositories/anton-abyzov/vskill/scripts/release/release-desktop.sh, repositories/anton-abyzov/vskill/scripts/release/publish-manifest.sh | Test: desktop-release.yml dry-run dispatch on the branch is green

### T-04 vskill CI and Sidecar Smoke de-duplication and settings flake
- AC: AC-04 | Files: repositories/anton-abyzov/vskill/.github/workflows/ci.yml, repositories/anton-abyzov/vskill/.github/workflows/sidecar-smoke.yml, repositories/anton-abyzov/vskill/src-tauri/src/preferences/settings.rs | Test: cargo test --manifest-path src-tauri/Cargo.toml preferences (vskill)

### T-05 specweave release path
- AC: AC-05 | Files: repositories/anton-abyzov/specweave/.github/workflows/release.yml, repositories/anton-abyzov/specweave/.github/workflows/test.yml, repositories/anton-abyzov/specweave/scripts/release/release.sh | Test: npm run test:unit:fast (specweave)

### T-06 SpecWithCode one-command release
- AC: AC-06 | Files: repositories/anton-abyzov/specweave-studio/scripts/release/release.sh, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update_request.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/run-tests.sh, repositories/anton-abyzov/specweave-studio/docs/studio/releasing.md | Test: bash scripts/release/release.sh --self-test (specweave-studio)

### T-07 Umbrella manifest, entrypoint, CI-wait helper and timing scanner
- AC: AC-07 | Files: .specweave/release/manifest.json, scripts/release/release.sh, scripts/release/ci-wait.sh, scripts/release/timing.py, .specweave/metrics/release-timings.jsonl | Test: python3 scripts/release/timing.py --self-test

### T-08 Memory and runbook corrections
- AC: AC-08 | Files: AGENTS.md, .gitignore | Test: test $(wc -c < ~/.claude/projects/-Users-antonabyzov-Projects-github-specweave-umb/memory/MEMORY.md) -lt 24000
