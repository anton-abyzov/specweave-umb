# Provision a fleet machine from scratch with one command and one button

## Problem

Today a new machine joins the fleet with `install.sh --join` (macOS arm64; Linux x64/arm64, glibc, systemd user services). That script installs Tailscale, a pinned Node 22.20.0, the server and its service, and prints the invite. It never installs git, gh, Claude Code, Codex or the other tools workers need, so every new machine is finished by hand. Ministorm (Ubuntu, joined on October 20, 2026, running 1.0.62) took an agent session most of a day. On October 20, 2026 the user asked for a command that prepares such a machine from scratch, tested on a real one and part of the SpecWithCode installation, plus a button in Connections that provisions a connected machine with default settings.

Two version traps showed up on Ministorm. The npm registry's `latest` for `specwithcode` was 1.0.47 while the fleet ran 1.0.62, so `npm i -g specwithcode` would downgrade. The machine's service and the app's own instructions still use the legacy `specweave-studio` name, so removing that alias breaks them. Design inputs: ~/Projects/github/studio-research-notes/machine-provisioning-audit-2026-10-19.md, ~/Projects/github/studio-research-notes/minis-setup-2026-10-20/ (setup page and `scripts/worker-check.sh`).

## Scope

In: a deterministic, idempotent `provision` command that runs on the target machine; a Provision action in Settings > Connections > Your private machines for a machine that is already connected, with a preview of the defaults, progress, retry and a readback; the "just bought the hardware" path in the install docs; tests in an isolated supported Linux environment and on Ministorm.

Out:
- Installing an operating system. A machine with no OS cannot be reached; the docs say what must exist first.
- Disk formatting, repartitioning or reboots.
- Windows provisioning (the Windows and Linux apps lead owns Windows).
- Granting "Allow workers".
- Copying sign-ins.
- Paid plans or subscriptions, including Ubuntu Pro.
- Project folders, which belong to 0966's "Run on".

## Acceptance Criteria

- [ ] AC-01: Supported targets are written down and checked before anything is installed. Supported: Ubuntu 22.04/24.04 and Debian 12 on x64 and arm64 with glibc and systemd, and macOS 14+ on arm64. Prerequisites: an installed OS, network access, and a user account that can reach the machine. Anything else is refused with the reason and the nearest supported option.
- [ ] AC-02: `specwithcode provision` (legacy alias `specweave-studio provision`) installs or verifies a pinned set:
  - git, gh, Node 22 (the pinned build install.sh already uses), Claude Code, Codex, and Tailscale when it is not present;
  - the SpecWithCode server at the exact version of the release that ships the command (never npm `latest`), with its service.
  Each package has a pinned version and a checksum or signed source, and is verified after install. Running it again changes nothing and says so. It never downgrades a newer installed version.
- [ ] AC-03: The command has `--dry-run` (the plan only), `--json` (a machine-readable readback: OS, arch, each package's wanted and found version, service state, server version, providers found) and `--resume` after a failure. No step needs an AI model.
- [ ] AC-04: Root boundary. Steps that need root run through `sudo` only when the user can run it without a password, or with the user typing the password into the machine's own terminal. Otherwise the command prints the exact one-line `sudo` command to run and continues without that step. Root passwords never pass through the app, a thread, a log or chat. No remote script runs without a checksum, and SSH host-key checking is never turned off.
- [ ] AC-05: Default provisioning never grants "Allow workers", copies or creates sign-ins, enables billing, or attaches Ubuntu Pro or another account subscription. The readback lists these as the user's remaining steps, with exact commands: `claude`, `codex login`, `gh auth login`, and Allow workers in Settings > Connections.
- [ ] AC-06: Legacy compatibility: the `specweave-studio` binary name, the existing service unit or launch agent and their data directories keep working after provisioning, and the docs say which name is current.
- [ ] AC-07: Settings > Connections > Your private machines shows Provision on a connected machine's row. It opens a preview of the default set with each package's current and target version, then runs the command on that machine through its own server, with live progress, Retry for a failed step and the final readback. It needs only the permissions the machine row already uses. It never restarts a service while that machine runs threads; it waits, or asks.
- [ ] AC-08: The install docs and the "Add a machine" flow cover a machine you just bought: what must exist first, how to reach it (Tailscale, or SSH on the local network), the one install command, then Provision.
- [ ] AC-09: Tested on a clean supported Linux environment (a container or VM, Ubuntu 24.04 at least): the full provision, a second run that changes nothing, `--resume` after an injected failure, and the readback. Saved as artifacts. Headless browser checks of the Connections UI with screenshots saved to files.
- [ ] AC-10: Run on Ministorm with its current owner's agreement, without stopping running jobs. The readback (service health, server version, providers) is saved in the setup report. The report does not claim fresh-OS support beyond what was tested.

## Approach

Build on `scripts/install.sh` and the server's CLI (`apps/server/src/cli/`) instead of a second installer.
- **Package manifest:** a pinned list of packages, versions, sources and checksums, versioned with the release, under `apps/server/src/provision/`.
- **Execution:** a runner that plans, applies and verifies each step and writes a resumable state file under the SpecWithCode home.
- **Remote:** an RPC on the target's server that starts the runner and streams its progress. Its scope matches what Connections already uses for fleet machines.
- **Web:** a Provision sheet on the machine row in `StudioFleetConnections.tsx`. Check open PRs from 0966-0970 that touch that file before editing it.
- **Version source:** the running release's own version and its GitHub release assets, as install.sh does. Report the stale npm `latest` dist-tag to the release owner; do not change it here.

## Decisions

### Asked
- none (the user asked for the command, the button and a real test on October 20, 2026)
### Defaulted
- D-01: OS installation, reboots and disk changes are out of scope; the docs list the prerequisites.
- D-02: Sign-ins, Allow workers and subscriptions stay explicit user steps.
- D-03: The release that ships the command is its version source, never npm `latest`.
- D-04: Windows provisioning stays with the Windows and Linux apps lead.

## Tasks

### T-01 Supported-target check, manifest and the provision runner (CLI)
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: apps/server/src/provision/**, apps/server/src/cli/provision.ts, apps/server/src/bin.ts, scripts/install.sh, tests | Test: vp test run apps/server/src/provision

### T-02 Remote Provision from Connections
- AC: AC-07 | Files: packages/contracts/src/provision*.ts, apps/server/src/provision/rpc.ts, apps/web/src/components/settings/ProvisionMachineSheet.tsx, apps/web/src/components/settings/StudioFleetConnections.tsx, tests | Test: vp test run on touched tests; headless screenshots

### T-03 Clean Linux test environment and artifacts
- AC: AC-09 | Files: scripts/studio-provision/**, .github/workflows (only if a container job is needed) | Test: scripts/studio-provision/verify run log + readback JSON saved

### T-04 Docs: just-bought-hardware path and legacy names
- AC: AC-06, AC-08 | Files: docs/user/add-a-machine.md, docs/studio/fleet.md, scripts/install.sh usage text | Test: docs build or lint

### T-05 PR and merge; hand the release to the release owner
- AC: all | Files: none | Test: PR Gate and PR Gate (typecheck) green; merged

### T-06 Ministorm run on the installed release and setup report
- AC: AC-10 | Files: ~/Projects/github/studio-research-notes/minis-setup-2026-10-20/provision-report.md | Test: readback JSON from Ministorm saved; service healthy; version matches

### T-08 Reach the systemd user manager from the installer's `env -i` launcher
- AC: AC-02, AC-09 | Files: apps/server/src/systemdUserBus.ts, apps/server/src/provision/{host,probe,install,plan,format}.ts, apps/server/src/cloud/bootService.ts, packages/contracts/src/provision.ts, tests | Test: vp test run src/systemdUserBus.test.ts src/provision src/cloud/bootService.test.ts; fresh swc-prov-2404 installed by install.sh, `bash -lc "specwithcode provision"` exit 0 with Background service PASS, second run no change, `specwithcode service status` running
- Found at the lead's close check: every `systemctl --user` and `loginctl` call made under the launcher install.sh writes failed with "Failed to connect to bus: No medium found", and the probe called a running service stopped. One helper fills in XDG_RUNTIME_DIR and DBUS_SESSION_BUS_ADDRESS from /run/user/<uid> when unset; an unreachable manager is reported as the finding. The launcher format is unchanged.

### T-07 Verify and close 0979
