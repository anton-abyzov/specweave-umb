# Release preflight and fleet rollout over SpecWithCode Connect

## Problem

On 2026-11-04 the 1.0.188 release stopped in its disk preflight because M3's Tailscale address in `~/.local/share/specweave/fleet/hosts.json` was stale. `scripts/release/preflight_fleet.py` reaches M1 and M3 only over pinned SSH, and `fleet_rollout.py` falls back to that SSH on its own whenever Connect does not answer. The workaround points M3 at a LAN IP. Every M4 service already reaches M1, M3 and ministorm over SpecWithCode Connect, so the release should ask workers there and use SSH only when the owner asks for it.

## Scope

In: a narrow Connect call on a worker that reports its disk room for a release version (`fleet room`), the preflight using it, `fleet_rollout.py` going Connect-only by default, one explicit SSH opt-in flag for both (`--ssh-fallback`, `RELEASE_FLEET_SSH=1` in release.sh), tests with a mocked Connect transport, docs. Out: `linux_rollout.py` (ministorm's SSH stage), a desktop-app update over Connect, hosts.json contents.

## Acceptance Criteria

- [ ] AC-01: From M4, `specweave-studio fleet room <machine> --version X --full-read N,... --connect-only --json` asks a worker over SpecWithCode Connect for the disk its update to X needs and prints one JSON line with the report and `"transport": "connect"`; a worker without the call, an unauthorized token or an unreachable machine ends with exit 1 and a named reason.
- [ ] AC-02: The worker answers only to its fleet primary's management token (`fleet:update` or legacy `environment:maintain`), runs only its own release's `disk_room.py` with the version and FULL_READ migration numbers M4 sends, and nothing in the request names a path, command or URL.
- [ ] AC-03: `preflight_fleet.py --version X` asks M1 and M3 by their Connect machine (from M4's studio-fleet.json), not by SSH address; each failure names the machine and the Connect error; SSH is used only with `--ssh-fallback`, and then only for a machine Connect could not ask.
- [ ] AC-04: `fleet_rollout.py` sends worker requests over Connect only by default; pinned SSH (service fallback and the desktop app step) runs only with `--ssh-fallback`; required-host, ack and lock semantics are unchanged.

## Approach

Studio repo `repositories/anton-abyzov/specwithcode-dev`, branch `fix/fleet-over-connect` from origin/main, built out of tree (manual worktrees are refused; commits via a temporary index).

- Worker: new `GET /api/studio/fleet/disk-room` (contracts `StudioFleetDiskRoomQuery`, capability `fleetDiskRoom`), handled through the same `requireFleetPrimary` check as fleet update; runs `/usr/bin/python3 -B -E -s <release>/studio-updater/disk_room.py --identity <own> --version X --full-read N,.. --json`. disk_room.py and the three modules it needs ship beside the agent files (new list, not the agent list, so installed agents stay valid).
- Primary: `runFleetDiskRoom` in a new `fleetDiskRoom.ts` (fleetUpdate.ts is near the 1500-line cap), CLI `fleet room`.
- `disk_room.py --full-read`: the target release's FULL_READ numbers, so an older installed copy computes the right fallback.
- Python: preflight builds `[cli, fleet, room, --base-dir, home, machine, ...]` from M4's service receipt, like fleet_rollout.connect_command; `--ssh-fallback` keeps the streamed SSH program per machine.
- Bootstrap: until M4 and a worker run a release with `fleet room`, the Connect check reports "unsupported"; that release needs `RELEASE_FLEET_SSH=1` once.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: One opt-in flag for both scripts, `--ssh-fallback`; release.sh passes it when `RELEASE_FLEET_SSH=1`.
- D-02: The desktop app step needs SSH, so by default it is skipped with a named reason (the app's own updater installs on quit); `--ssh-fallback` runs it.
- D-03: Preflight still asks only M1 and M3 (required hosts); ministorm stays out, as today.
- D-04: With --ssh-fallback, the preflight falls back to SSH only when Connect left the worker unasked (unreachable, timeout, unsupported, no route), never after a refusal it answered (code review).
### Open
- none

## Tasks

### T-01 Disk room over Connect: worker call, CLI, shipped helper
- AC: AC-01, AC-02 | Files: packages/contracts/src/studioFleet.ts, packages/contracts/src/environmentHttp.ts, packages/contracts/src/environment.ts, apps/server/src/environment/ServerEnvironment.ts, apps/server/src/fleet/fleetDiskRoom.ts, apps/server/src/fleet/fleetDiskRoom.test.ts, apps/server/src/studioFleetHttp.ts, apps/server/src/studioFleetHttp.test.ts, apps/server/src/cli/fleet.ts, apps/server/src/server.ts, scripts/lib/studio-disk-room.ts, scripts/studio-fleet/bundle.mjs, scripts/studio-fleet/runtime-package.test.mjs | Test: cd /private/tmp/claude-501/-Users-antonabyzov-Projects-github-specweave-umb/8f061025-32ca-4fe1-bcd9-9d70024c2c37/scratchpad/final && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/fleetDiskRoom.test.ts apps/server/src/studioFleetHttp.test.ts apps/server/src/cli/fleet.test.ts && node --test scripts/studio-fleet/runtime-package.test.mjs

### T-02 Preflight and rollout over Connect, SSH opt-in
- AC: AC-03, AC-04 | Files: scripts/studio-fleet/disk_room.py, scripts/studio-fleet/additive_migrations.py, scripts/studio-fleet/test-fleet-rollout-connect-only.py, scripts/release/preflight_fleet.py, scripts/studio-fleet/fleet_rollout.py, scripts/studio-fleet/test-preflight-disk.py, scripts/studio-fleet/test-fleet-rollout.py, scripts/studio-fleet/test-fleet-desktop-app.py, scripts/release/release.sh, scripts/release/release-self-test.sh, docs/studio/releasing.md, docs/studio/fleet.md | Test: cd /private/tmp/claude-501/-Users-antonabyzov-Projects-github-specweave-umb/8f061025-32ca-4fe1-bcd9-9d70024c2c37/scratchpad/final && export STUDIO_FLEET_HOSTS=/nonexistent/hosts.json STUDIO_FLEET_ROLLOUT_LOCK=$(mktemp -d)/lock && python3 -B scripts/studio-fleet/test-preflight-disk.py && python3 -B scripts/studio-fleet/test-fleet-rollout.py && python3 -B scripts/studio-fleet/test-fleet-rollout-connect-only.py && python3 -B scripts/studio-fleet/test-fleet-desktop-app.py && bash scripts/release/release-self-test.sh

### T-03 Verify and close 1240
- AC: AC-01, AC-02, AC-03, AC-04 | Files: scripts/release/preflight_fleet.py | Test: cd /private/tmp/claude-501/-Users-antonabyzov-Projects-github-specweave-umb/8f061025-32ca-4fe1-bcd9-9d70024c2c37/scratchpad/final2 && python3 -B scripts/release/preflight_fleet.py --version 1.0.191 --help | grep -q -- --ssh-fallback && gh pr view 1388 -R anton-abyzov/specwithcode-dev --json state -q .state | grep -qx MERGED
