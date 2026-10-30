# Safe fleet launcher repoint and Linux worker rollout

## Problem

Two recovered pull requests in `anton-abyzov/specwithcode-dev` received FIX verdicts from a fresh cross-model review on October 27, 2026 (`/Users/antonabyzov/.specwithcode/m4/evidence/openai-pr-review-20261027/pr-911.md` and `/Users/antonabyzov/.specwithcode/m4/evidence/openai-pr-review-20261027/pr-912.md`).

- PR #911 (`fix/update-shell-launchers`) repoints the shell launchers on `specwithcode update`. At `ff738427ff` it wrote through a predictable temporary name, which clobbered a file the name linked to. It did not recognise the fleet installer's `install/releases/<digest>` layout, and it matched raw text, so a quoted `=` inside a path took ownership and an `O'Brien` home was missed.
- PR #912 (`fix/linux-worker-rollout`) updates Linux workers after the macOS release. At `b4deae3a47` it had three problems:
  - An SSH session without the user bus read the service state as unknown and restarted a busy worker.
  - The idle preview did not protect the later restart.
  - It accepted a unit that named the target version while the worker was down or ran another version.

## Scope

In:

- #911: launcher parsing, ownership and safe replacement in `apps/server/src/cli`.
- #912:
  - the rollout script and its remote shell;
  - an `ifIdle` service-update hold (contracts, ServiceUpdatePreparation, `service prepare-update --if-idle`, `update --if-idle`);
  - a Linux CI job for the rollout's Linux-only cases;
  - docs.

Out: merging, releasing, any fleet rollout or service restart (release coordinator), and Windows launchers.

## Acceptance Criteria

- [ ] AC-01: The launcher repoint writes only through an exclusively created, no-follow temporary file in the same directory, removes only its own entry on failure, refuses a launcher changed since it was read, and never waits on a FIFO.
- [ ] AC-02: A launcher is repointed only when it is an exact install.sh or launcher.py rendering. Its decoded entry operand must be in this home's versions tree, or in the fleet release store with STUDIO_HOME equal to this home, both compared by real path. The replacement is rendered with the installers' quoting.
- [ ] AC-03: The rollout restores the user bus before asking systemd. It skips a worker on a failed query or an uncertain state. It treats only "inactive" and "failed" as stopped.
- [ ] AC-04: An active worker restarts only under an if-idle hold the running service takes right before the restart. A busy service, or one too old to hold itself, keeps running and the worker is reported as skipped.
- [ ] AC-05: A worker counts as updated only when its live server, in the unit's cgroup, runs the launcher's selected version with no trial pending. The same check runs before and after the update.
- [ ] AC-06: Each PR has a fresh exact-head review with no blocking findings, and its applicable CI passes.

## Approach

#911 adds `apps/server/src/cli/shellLauncher.ts`:

- shlex quoting and shell-word splitting;
- renderers for the three launcher.py formats, with a byte-for-byte re-render check;
- `readRegularFile` (O_NOFOLLOW|O_NONBLOCK) and `replaceRegularFile` (O_EXCL temporary file, descriptor chmod, dev/inode/bytes guard, inode-checked cleanup).

`repointShellLaunchers` in `update.ts` uses them. Test fixtures come from the real install.sh `render_cli_wrapper` and the Python `launcher.render_cli`.

#912 changes the following:

- The remote shell exports the user-bus variables, reads LoadState, ActiveState and ControlGroup through `systemctl --user show`, takes the live server's childVersion from `/proc/<pid>/environ` when the pid is in the unit's cgroup, and reads `service-state.json`.
- `ServerPrepareServiceUpdateInput.ifIdle` atomically takes an unowned conditional lease, closes command admission and waits for already admitted commands to finish persistence before looking for work. Busy/error cleanup releases only the matching token.
- `update --if-idle` requires idle/held/token acknowledgement, and confirms the still-owned, unexpired lease after runtime preparation immediately before stop. A refused restart does not stage a service selection change.

Rejected:

- A second preview, which still races.
- `--stop-work`, which interrupts the work the rollout promises to keep.
- Holding across the download: a hold without an install request ends after 60 s when no update agent runs.

Risk: Linux workers on 1.0.105 or earlier can't hold themselves, so they are skipped while active until updated by hand once. This is documented.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: The fleet release-store launcher is repointed to the CLI runtime only when its STUDIO_HOME is this home. It follows Sol's round-1 fix for #911.
- D-02: The optional `ifIdle`/`holdToken` contract remains decodable by older services, but the new CLI requires `idle: true`, `held: true` and a nonempty ownership token. Replies without that acknowledgement do not authorize restart or release of an existing hold.
### Open
- none

## Tasks

### T-01 Fix PR #911 review findings (rounds 1 and 2)
- AC: AC-01, AC-02 | Files: apps/server/src/cli/shellLauncher.ts, apps/server/src/cli/update.ts | Test: vp test run apps/server/src/cli/shellLauncher.test.ts apps/server/src/cli/update.test.ts

### T-02 Fix PR #912 review findings
- AC: AC-03, AC-04, AC-05 | Files: scripts/studio-fleet/linux_rollout.py, apps/server/src/serviceUpdate/ServiceUpdatePreparation.ts, apps/server/src/cli/update.ts, apps/server/src/cli/servicePrepareUpdate.ts | Test: python3 -B scripts/studio-fleet/test-linux-rollout.py

### T-05 Fence command and terminal admission and own if-idle restart leases
- AC: AC-04 | Files: packages/contracts/src/serviceUpdatePreparation.ts, apps/server/src/serviceUpdate/ServiceUpdateHold.ts, apps/server/src/serviceUpdate/ServiceUpdateHold.test.ts, apps/server/src/serviceUpdate/ServiceUpdatePreparation.ts, apps/server/src/serviceUpdate/ServiceUpdatePreparation.test.ts, apps/server/src/orchestration-v2/Orchestrator.ts, apps/server/src/terminal/Manager.ts, apps/server/src/terminal/Manager.updateHold.test.ts, apps/server/src/cloud/bootService.ts, apps/server/src/cloud/bootService.test.ts, apps/server/src/cli/update.ts, apps/server/src/cli/update.test.ts, docs/studio/releasing.md | Test: focused hold/preparation/orchestrator, terminal, CLI and boot-service tests; native server typecheck gate; fresh Sol regression probes

### T-03 Fresh exact-head reviews and CI for #911 and #912
- AC: AC-06 | Files: none | Test: Sol review SHIP at the pushed heads; gh pr checks green

### T-04 Verify and close 1104
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: none | Test: specweave verify 1104-safe-launcher-repoint-and-linux-rollout
