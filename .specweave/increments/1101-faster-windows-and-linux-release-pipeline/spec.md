# Faster Windows and Linux release pipeline

## Problem

Windows and Linux builds reach a release hours after macOS, or not at all. Evidence, from GitHub job and step timings saved in `/Users/antonabyzov/.specwithcode/m4/evidence/wl-pipeline-speed-20261027/`:

- v1.0.94 (run 40369196670) took 12,195 s from publish to attached, of which about 9 minutes was build work. It waited 8,548 s on the workflow-wide concurrency group `release-windows-linux` behind the v1.0.93 run (40362524012). That run held the group while it polled a draft public release for an hour and then failed. A version that had nothing to do with v1.0.93 could not start.
- After that incident `RELEASE_WINDOWS_LINUX_ON_PUBLISH` was set to false (October 26, 21:37 UTC). Since then Windows/Linux reach a release only through the nightly run on whatever is Latest at 07:23 UTC, so v1.0.95-v1.0.101 and v1.0.103-v1.0.105 have no Windows/Linux installers.
- Every release build downloads every package: Windows 1,369 packages in 86 s, Linux 1,325 in 37 s, `reused 0` (run 40468631769). setup-vp's cache is off for both, and on Windows it cannot simply be turned on (it restores a Linux-shaped store, #7975).
- The published-release verification (desktop-windows-linux.yml with `release_tag`, run 40400283259) spends 297 s on Linux rebuilding the whole AppImage and .deb, then throws both away for the published files. It needs only the server and web bundles for the Linux CLI archive.

## Scope

In: release-windows-linux.yml locking and caching, desktop-windows-linux.yml caching and the release_tag Linux build, structure tests, before/after timings. Out: release.sh and scripts/studio-fleet (PR #912 owns them), the repository variable `RELEASE_WINDOWS_LINUX_ON_PUBLISH` (a release coordination decision), code signing, larger runners, independent per-platform publication (compared in the report, not built here).

## Acceptance Criteria

- [ ] AC-01: Release runs for different versions never wait on each other. Only uploads to the same version are serialized, and dry runs take no lock.
- [ ] AC-02: Dependency caching is kept only where it is measured to pay. Linux release builds restore setup-vp's store cache. A Windows store cache is measured on real runners and dropped if a hit is no faster than downloading.
- [ ] AC-03: Published-release verification on Linux no longer builds the desktop app. It builds only what the Linux CLI archive needs, and still downloads, checksums, installs, launches, end-to-end tests (thread and coordinator), runs the service and uninstalls the published AppImage and .deb.
- [ ] AC-04: Source, version and digest binding is unchanged: the tag commit is resolved once in Plan, the version check against the tag holds, `SHA256SUMS-windows-linux` and the post-upload digest checks are unchanged, signing settings are unchanged, and every real-OS gate step remains.
- [ ] AC-05: Before/after step timings, critical path and a comparison of independent platform publication are recorded with the exact runs used.

## Approach

1. release-windows-linux.yml: drop the workflow-level concurrency group. Add job-level concurrency to `publish`, keyed by `needs.plan.outputs.version` (or the run id for a dry run), with cancel-in-progress false. Builds for any version start as soon as runners are free. Two runs of one version still upload one at a time, and plan-upload already refuses a name that is on the release.
2. Linux build jobs: setup-vp `cache: true`, which is already used across ci.yml on Linux.
3. Windows: try a pinned pnpm store (`pnpm_config_store_dir`) cached under a Windows-only key in the PR runs. Result: on a hit it restored in 43 s and installed in 53 s (1,369 packages reused), no faster than the 91 s uncached install, and a miss cost 95 s to save 614 MB. Removed, with a comment in the workflow recording why.
4. desktop-windows-linux.yml Linux with release_tag: skip `build-desktop-artifact.ts` and the capture-helper cache, run `vp run --filter specweave-studio build` (server and web, the same task the desktop build depends on), and skip imagemagick, which only the desktop icon build uses.
5. Tests in scripts/release-windows-linux.test.ts and a new desktop workflow structure test.

Rejected: building the JS bundles once on Linux and handing them to Windows. Windows would wait about 200 s for the bundle job, which is no faster than its own 223 s build, and the handoff weakens per-platform source binding. Caching build outputs across runs: release builds bake secrets and the version, so cached outputs would break provenance.

Risks: release_tag mode and the release workflow cannot run on a pull request. Their after-measurement needs a dispatched dry run, which belongs to the release coordinator.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Independent per-platform publication is compared, not built. It needs per-platform checksum files, nightly skip logic and install.ps1 changes → follow-up.
- D-02: `RELEASE_WINDOWS_LINUX_ON_PUBLISH` stays as is; turning it back on is the coordinator's call once AC-01 ships.
### Open
- none

## Tasks

### T-01 Per-version publish lock
- AC: AC-01, AC-04 | Files: .github/workflows/release-windows-linux.yml, scripts/release-windows-linux.test.ts | Test: npx vitest run scripts/release-windows-linux.test.ts

### T-02 OS-specific dependency store caches
- AC: AC-02, AC-04 | Files: .github/workflows/release-windows-linux.yml, .github/workflows/desktop-windows-linux.yml, scripts/release-windows-linux.test.ts | Test: npx vitest run scripts/release-windows-linux.test.ts; PR run of desktop-windows-linux.yml

### T-03 Verification builds only the CLI inputs on Linux
- AC: AC-03, AC-04 | Files: .github/workflows/desktop-windows-linux.yml, scripts/desktop-windows-linux-workflow.test.ts | Test: npx vitest run scripts/desktop-windows-linux-workflow.test.ts

### T-04 Timings, comparison, PR, review
- AC: AC-05 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/wl-pipeline-speed-20261027/REPORT.md | Test: actionlint on both workflows; fresh-context review SHIP at the exact head

### T-06 Reject incomplete release integrity and optional OS gates; repair portable validation
- AC: AC-01, AC-03, AC-04 | Files: scripts/release-windows-linux.ts, scripts/release-windows-linux.test.ts, scripts/desktop-windows-linux-workflow.test.ts, scripts/studio-toolchain/reviewed-lock-changes.json, scripts/studio-toolchain/preservation-audit.mjs | Test: focused release/workflow tests with empty/missing checksum, draft/prerelease and skipped-dependency negative controls; lock preservation tests; actionlint; scripts native typecheck; applicable CI

### T-05 Verify and close 1101
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: none | Test: specweave verify 1101-faster-windows-and-linux-release-pipeline
