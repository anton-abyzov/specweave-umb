# Skill Studio update fixes and release

## Problem

Skill Studio (vskill desktop) last shipped as desktop-v1.0.67 on 2026-10-21; main is 16 commits ahead (#199, #200, #204) because npm releases never trigger or flag desktop. `release.sh verify vskill-desktop` passes on a stale build. In the app, a failed update shows "Updated" (api-skill-updates.ts:200 returns res.ok on an SSE 200), "Update Selected" uses a GET EventSource against a POST-only route, pinned skills show a false success, the Updates view hides errors as "no updates", pin and install-version exist only in the CLI, and updates run whatever `vskill` is on PATH.

## Scope

In: the update-path fixes above; pin/unpin and "Install this version" in Studio; a "Push to all machines" action that calls `specweave-studio fleet skills` when that CLI exists (1125); `getOutdatedJson(root)`; CHANGELOG backfill; umbrella release pipeline: verify flags desktop drift, `ship vskill` runs desktop even if npm fails and is the documented default; release npm 1.2.16 and desktop 1.0.68. Out: auto-releasing desktop from CI without a person (needs a PAT), new Studio views, and a version-matched CLI inside the desktop sidecar (see Left undone).

## Acceptance Criteria

- [ ] AC-01: In Studio, a failed single or batch update shows the error, a pinned skill is reported as skipped (button shows the pin), and "Update Selected" shows per-row progress and a real result.
- [ ] AC-02: Studio can pin, unpin and install a chosen version of an installed skill from its detail and Versions views, and the Updates view shows an error with Retry when the check fails.
- [ ] AC-03: When `specweave-studio` is on PATH, a skill's detail view offers "Push to all machines" for the selected version and shows each machine's result; otherwise the action is hidden.
- [ ] AC-04: `bash scripts/release/release.sh verify vskill-desktop` fails or warns when main has desktop-relevant commits after the newest desktop-v tag; `ship vskill` runs desktop even when npm fails; README points at `ship vskill`.
- [ ] AC-05: vskill 1.2.16 is live on npm and Skill Studio 1.0.68 is served by latest.json with a verified signature.

## Approach

vskill worktree ~/.specwithcode/m4/worktrees/vskill/studio-fixes-1126, branch fix/studio-update-fixes from origin/main. Files: src/eval-ui/src/api-skill-updates.ts, UpdatesPanel/UpdateAction/UpdateDropdown/VersionHistoryPanel/SkillDetailPanel (find real paths with git ls-files), src/eval-server/api-routes.ts (or a new split routes file to respect 1500 lines), src/outdated.ts. Spawn the bundled CLI (process.execPath + package dist) async instead of execFileSync on PATH. Umbrella: scripts/release/release.sh, .specweave/release/manifest.json, .specweave/release/README.md. Release through `bash scripts/release/release.sh ship vskill` after merge; coordinate: SpecWithCode 1.0.110 is being cut in another thread, Skill Studio is a separate track.

## Left undone

- Desktop Skill Studio still runs `vskill` from PATH. The SEA sidecar ships no CLI entry (process.execPath is the sidecar, and esbuild maps import.meta.url to it), so the bundled-CLI fix covers only `vskill studio` from npm. Desktop update, batch update and install-version use the PATH CLI, or report "not found on PATH" with the install command. Closing it needs a CLI mode in scripts/desktop/sidecar-entry.mjs and a CLI bundle that does not read ../package.json at import time. Follow-up increment.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Auto desktop release from npm CI is out (unattended signed build; needs PAT). Verify-time drift detection plus `ship vskill` instead.
- D-02: Push to all machines goes through the SpecWithCode CLI, not a Studio-side fleet client.
### Open
- none

## Tasks

### T-01 Truthful update results and batch update
- AC: AC-01 | Files: repositories/anton-abyzov/vskill/src/eval-ui/src/api-skill-updates.ts, repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts, update UI components | Test: npx vitest run (vskill) for the update client and routes

### T-02 Pin, install version, error state, push to machines
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/vskill/src/eval-server/, repositories/anton-abyzov/vskill/src/eval-ui/src/, repositories/anton-abyzov/vskill/CHANGELOG.md | Test: npx vitest run (vskill) + headless Playwright screenshots of Studio

### T-03 Release pipeline drift check
- AC: AC-04 | Files: scripts/release/release.sh, scripts/release/release-self-test.sh, .specweave/release/manifest.json, .specweave/release/README.md | Test: bash scripts/release/release.sh verify vskill-desktop && bash scripts/release/release-self-test.sh

### T-04 Release npm 1.2.16 and desktop 1.0.68
- AC: AC-05 | Files: repositories/anton-abyzov/vskill/package.json, repositories/anton-abyzov/vskill/package-lock.json, repositories/anton-abyzov/vskill/CHANGELOG.md | Test: bash scripts/release/release.sh verify vskill

### T-06 Fleet CLI result integration
- AC: AC-03 | Files: repositories/anton-abyzov/vskill/src/eval-server/skill-pin-routes.ts, repositories/anton-abyzov/vskill/src/eval-server/__tests__/skill-pin-routes.test.ts | Test: npx vitest run src/eval-server/__tests__/skill-pin-routes.test.ts

### T-05 Verify and close 1126
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: .specweave/increments/1126-skill-studio-update-fixes-and-release/reports/ | Test: specweave verify 1126; fresh-context review; specweave complete 1126
