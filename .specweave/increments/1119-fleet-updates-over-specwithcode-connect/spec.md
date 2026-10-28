# Fleet updates over SpecWithCode Connect

## Problem

On 2026-10-28 the 1.0.107 and 1.0.108 releases failed their fleet-workers stage: "m1 gave no answer (exit 255); m3 gave no answer (exit 255)". scripts/studio-fleet/fleet_rollout.py reaches workers only by SSH over Tailscale (ssh_command, line 131), and Tailscale is off on the M4. The owner treats Tailscale as a fallback only. The M4 service already reaches M1, M3 and ministorm over SpecWithCode Connect (`STUDIO_HOME=~/.specwithcode/m4 specweave-studio fleet list` shows "reachable via Connect"), yet ministorm sits on 1.0.105 while 1.0.109 is out, and nothing in the release can move it.

## Scope

In: a way for the primary machine to ask a fleet machine, over its Connect route (Tailscale only as fallback), to install a given version — the forced, held install Update now uses for macOS workers, and the server self-update for Linux workers ("boot-service"); fleet_rollout.py using it when SSH is unavailable; progress and result reported the same way the SSH path reports them. Out: the worker update agent internals and the hold logic (PR #939 owns those files), Tailscale setup, desktop UI changes.

## Acceptance Criteria

- [ ] AC-01: From the primary machine, one command asks a named fleet machine to install a given version over its Connect route, using only the management credential the primary already holds; a machine reached over Tailscale works the same way.
- [ ] AC-02: For a macOS worker the request is the same forced, held install Update now makes (questions closed and reopened, running work paused and resumed); for a Linux worker it is the server self-update; the command reports progress and ends with the installed version or the named reason it did not install.
- [ ] AC-03: fleet_rollout.py's worker stage uses this path when SSH gives no answer, so a release with Tailscale off still moves every Connect-reachable worker, and a machine reachable by neither is reported, not hung.
- [ ] AC-04: The management credential cannot be used through this path for anything beyond requesting an install of a published, signed release version and reading update status; a downgrade or an unknown version is refused by the worker.

## Approach

Studio repo, worktree ~/.specwithcode/m4/worktrees/fleet-connect-updates, branch feat/fleet-connect-updates from origin/main (rebase on #939 if it merges first; do not edit #939's files: desktop_app_update_remote.sh, update_agent*.py, ServiceUpdateHold.ts, docs/studio/releasing.md, docs/studio/updates.md). Reuse the fleet client that `fleet list` uses for Connect reachability (apps/server/src/studioFleet*.ts, cli/fleet.ts) and the existing update RPCs (managedUpdates/ManagedUpdatesRpc.ts, the serviceUpdate config the desktop's Update now writes). Add a narrow scope for the management token rather than granting orchestration:operate.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Connect first, Tailscale SSH as fallback (owner, 2026-10-28: "Tailscale is just a fallback method").
- D-02: A new narrow token scope for fleet update requests; no broader operate scope for the primary.
### Open
- none

## Tasks

### T-01 Request an install on a fleet machine over Connect
- AC: AC-01, AC-02, AC-04 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/cli/fleet.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/studioFleet.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/studioFleetHttp.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/fleet/fleetUpdate.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/fleet/fleetUpdate.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/auth/EnvironmentAuth.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/auth.ts | Test: cd ~/.specwithcode/m4/worktrees/fleet-connect-updates && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && node node_modules/vite-plus/bin/vp test run apps/server/src/fleet apps/server/src/studioFleetHttp.test.ts

### T-02 Release worker stage falls back to Connect
- AC: AC-03 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/fleet_rollout.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-fleet-rollout.py | Test: cd ~/.specwithcode/m4/worktrees/fleet-connect-updates && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && python3 scripts/studio-fleet/test-fleet-rollout.py

### T-03 Update ministorm over Connect and verify
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/fleet_rollout.py | Test: curl -s -m10 https://prod-901f0a2dbfb48b00.spec-weave.com/.well-known/studio/environment | python3 -c "import json,sys;v=json.load(sys.stdin)['serverVersion'];print(v);assert tuple(map(int,v.split('.')))>=(1,0,109)"

### T-04 Verify and close 1119
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/fleet/fleetUpdate.ts | Test: cd ~/.specwithcode/m4/worktrees/fleet-connect-updates && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && node node_modules/vite-plus/bin/vp test run apps/server/src/fleet apps/server/src/studioFleetHttp.test.ts && python3 scripts/studio-fleet/test-fleet-rollout.py
