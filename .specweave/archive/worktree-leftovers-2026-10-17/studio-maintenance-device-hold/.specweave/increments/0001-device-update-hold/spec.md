# Pause Device hub during guarded updates

## Problem

The installed SpecWithCode 1.0.35 service is waiting to install verified 1.0.37. Its guarded updater reaped two owned node descendants at 20:29 and 20:31 UTC on 2026-10-16. LocalDeviceHost immediately restarted Expo device hub after each exit. The replacement remains a quiescence blocker. The same lifecycle code is in both releases. Preserve all existing update guards, settings, native accounts and active work.

## Scope

A narrow Device hub lifecycle fix in this fresh owned source worktree, focused regression tests, production server build, independent review and private PR for the existing publisher. No version bump, direct process stop, persisted device disable, duplicate publisher, live provider turn, or installation bypass.

## Acceptance Criteria

- [ ] AC-01: A held or install-gated service cannot spawn or restart the local device hub or agent helper; legitimate restart resumes safely after the hold ends.
- [ ] AC-02: Stop and finalization cannot deadlock or resurrect a stopped host while a restart is paused; device settings remain unchanged.
- [ ] AC-03: Focused tests, relevant server production build and independent review pass; recoverable source and review evidence are retained for the agreed release owner.

## Approach

Owned checkout: /Users/antonabyzov/Projects/github/studio-maintenance-device-hold-20261016, branch codex/0889-device-update-hold, base 512fb42f9deb10ed8997f32a6cff36275443aa69. This local repair plan continues maintenance evidence 0889; canonical 0889 is absent and unrelated umbrella 0922 remains untouched. Respect ServiceUpdateHold and UpdateInstallGate at the device process boundary, using existing Effect services and typed errors. Never exclude the hub from quiescence or change its persisted enablement. The existing publisher retains release and installation ownership.

## Tasks

### T-01 Respect update hold across device helper lifecycle
- AC: AC-01, AC-02 | Files: apps/server/src/device/, apps/server/src/server.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/device/LocalDeviceHost.test.ts apps/server/src/device/DeviceService.test.ts apps/server/src/serviceUpdate/ServiceUpdateHold.test.ts

### T-02 Verify and hand repair to existing release owner
- AC: AC-03 | Files: .specweave/increments/0001-device-update-hold/ | Test: node apps/server/scripts/cli.ts build
