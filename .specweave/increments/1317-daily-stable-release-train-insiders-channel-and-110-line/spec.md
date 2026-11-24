# Daily stable release train, insiders channel and 1.1.0 line

## Problem

SpecWithCode ships every merge to every user. On November 12 and 13, 2026, 1.0.262 to 1.0.276 were published in about 20 hours (15 releases); 1.0.276 holds a single fix. Every one of them became GitHub's Latest, so every user's desktop app and service update agent installed each one, and the download page served each one. Several dispatchers (m4, linux-mini, agent sessions) request releases independently. Nothing soaks before it reaches users, and 1.0, which was presented as the stable line, was not stable.

## Scope

In:
- Two tracks for every build: insiders (every request, published as a GitHub prerelease, never Latest) and stable (only the daily train, which promotes an insiders build that has soaked, or a labelled hotfix).
- A daily train workflow with a fixed cut time, a soak gate and a hold mark for bad builds.
- A guard in the release plan that refuses stable releases outside the train, except a merged pull request labelled `hotfix`.
- Updater channels: the service update agent's `stable` channel skips prereleases; the desktop app's second track (wire value `nightly`, shown as Insiders) reads the newest build including prereleases.
- The 1.1.0 line: the tracks apply from 1.1.0 on; 1.0.x is frozen at the last 1.0 release once 1.1.0 exists.
- Decision doc and runbook in the specwithcode repo.

Out: cutting 1.1.0 (waits for Anton's go), a cherry-pick release branch for hotfixes, the R2 candidate channel (local-only path, unchanged), percentage-based staged rollout, the iOS app's own version line.

## Acceptance Criteria

- [ ] AC-01: A release run for a version at or above 1.1.0 publishes it as a GitHub prerelease that is not Latest, unless the plan marked it a hotfix; 1.0.x versions keep today's flags.
- [ ] AC-02: The plan job refuses a `hotfix` dispatch unless the named pull request is merged into main and carries the `hotfix` label, and nothing but the train workflow promotes a prerelease to stable.
- [ ] AC-03: The train promotes the newest insiders build at or above 1.1.0 that is above the current stable, was published at least the soak time before the run, has the macOS, Windows and Linux update manifests and is not held; it does nothing when no build qualifies, and promotes at most once per 20 hours.
- [ ] AC-04: `release_train.py hold` and `unhold` mark and clear a build so the train skips it.
- [ ] AC-05: The service update agent on the `stable` channel ignores prerelease builds unless an install request names that exact version; on `preview` it takes them.
- [ ] AC-06: The desktop app on the Insiders track reads the newest release including prereleases that carries its platform's manifest; on Stable it is unchanged. Settings shows the track as Stable or Insiders.
- [ ] AC-07: `request-release.sh --hotfix <pr>` dispatches a hotfix run; the runbook and decision doc describe cadence, channels, hotfix rule, soak, ownership and the 1.1 plan.
- [ ] AC-08: 1.1.0 is cut only after Anton's go, as an insiders build that the train promotes as the first stable release.

## Approach

Promote, do not rebuild: the train flips an existing insiders release to stable (`gh release edit --prerelease=false --latest`), so stable users get the exact binaries the fleet ran. Version numbers stay plain 1.x.y because the installer, the update agent and release.sh accept only that shape; insiders and stable share one number series, so a stable release can skip numbers (1.1.0, then 1.1.6), and its notes list the insiders builds it includes.

Files (specwithcode repo):
1. `scripts/studio-projects/release-flags.mjs`: track from `RELEASE_TRACK`; default insiders for 1.1.0 and above.
2. `scripts/release/release_plan.py` + `.github/workflows/release-macos.yml`: `track` input (insiders, hotfix), hotfix PR check, `RELEASE_TRACK` to release.sh.
3. `scripts/release/release_train.py` + `.github/workflows/release-train.yml`: promote, hold, unhold, status; schedule at the cut time; shares the release concurrency group.
4. `scripts/studio-fleet/update_agent_recovery.py`: stable channel skips prereleases.
5. `apps/desktop/src/updates/platformFeed.ts`, `DesktopUpdates.ts`, `SettingsPanels.tsx`: Insiders feed and label.
6. `scripts/release/request-release.sh --hotfix`, `docs/studio/release-train.md`, `docs/studio/releasing.md`, `AGENTS.md`.

Rejected: building separate `-insiders.N` versions (the agent and installer refuse suffixed versions; rebuilding for stable would ship binaries nobody soaked); a minor bump per stable day (inflates versions); a repository variable switch (the 1.1.0 line itself is the switch, so nothing changes before Anton's go).

Risks: agents already installed (1.0.276 and older) ignore the prerelease flag and install insiders builds until they run an agent with this change; the first insiders build carries it. A hotfix ships main's head, unsoaked commits included; the runbook says to check main first.

## Decisions

### Asked
- D-01 When to cut 1.1.0 → Anton, November 13, 2026: yes. Cut Monday, November 16, 2026; the train promotes it Tuesday, November 17 at 15:00 UTC. 1.0.x keeps the current schedule (every merge, Latest) through the weekend for hotfixes; the train applies only from 1.1.0, so no guard change is needed.
### Defaulted (change any before sw-do)
- D-02 Cut time → 15:00 UTC daily (reversible: the cron line).
- D-03 Soak → 24 hours on insiders (VS Code recovery rule), all three platform manifests present, not held.
- D-04 Fleet machines (m4, linux-mini, m1) run the Insiders track; they are the canary ring.
- D-05 Hotfix approver → Anton; the `hotfix` label is applied only on his yes.
- D-06 Release owner → the train workflow for stable; any session may still request insiders builds through request-release.sh.
- D-07 1.0.x cadence until 1.1.0 → Anton, November 15, 2026, after 1.0.304 to 1.0.310 shipped within hours: "why are we releasing so often? I would wait for several features to be completed". Replaces D-01's "every merge" for the weekend. Merged features wait for one batched 1.0.x release; at most one more before the 1.1.0 cut, only after the in-flight PRs from both machines land (#437, #440, #441 from linux-mini, plus m4's open ones). Only real hotfixes ship at once: security, data loss, a broken update or install, or a crash in a core flow. Nobody dispatches Release macOS for a single merge. Cutoff 6 PM EST November 15, 2026: linux-mini dispatches the batch then, and anything unmerged rides in 1.1.0 (agreed with m4).
### Open
- none

## Tasks

### T-01 Release flags by track
- AC: AC-01 | Files: scripts/studio-projects/release-flags.mjs, scripts/studio-projects/release-flags.test.mjs, scripts/release/release.sh | Test: node --test scripts/studio-projects/release-flags.test.mjs

### T-02 Plan tracks and the hotfix guard
- AC: AC-02 | Files: scripts/release/release_plan.py, scripts/release/test-release-plan.py, .github/workflows/release-macos.yml | Test: python3 -B scripts/release/test-release-plan.py

### T-03 Daily train
- AC: AC-03, AC-04 | Files: scripts/release/release_train.py, scripts/release/test-release-train.py, .github/workflows/release-train.yml | Test: python3 -B scripts/release/test-release-train.py

### T-04 Update agent stable channel
- AC: AC-05 | Files: scripts/studio-fleet/update_agent_recovery.py, scripts/studio-fleet/test-update-agent.py | Test: python3 -B scripts/studio-fleet/test-update-agent.py

### T-05 Desktop Insiders track
- AC: AC-06 | Files: apps/desktop/src/updates/platformFeed.ts, apps/desktop/src/updates/platformFeed.test.ts, apps/desktop/src/updates/DesktopUpdates.ts, apps/web/src/components/settings/SettingsPanels.tsx | Test: vp test run apps/desktop/src/updates/platformFeed.test.ts

### T-06 Hotfix request and docs
- AC: AC-07 | Files: scripts/release/request-release.sh, docs/studio/release-train.md, docs/studio/releasing.md, AGENTS.md | Test: bash -n scripts/release/request-release.sh && bash scripts/release/request-release.sh --help

### T-07 Cut 1.1.0 after Anton's go
- AC: AC-08 | Files: none (dispatch) | Test: gh release view v1.1.0 -R anton-abyzov/specwithcode --json isPrerelease,isLatest
