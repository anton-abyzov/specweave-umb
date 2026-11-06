# 1206 Automatically update idle fleet machines

## Problem
SpecWithCode downloads desktop releases but its automatic install preference installs only on quit. Idle desktops therefore keep showing Restart. Service updates have a separate agent and policy; this machine explicitly disables automatic installation. Upstream T3 also requires explicit installation and does not solve fleet idle restart.

## Scope
In: a per-machine automatic idle restart policy, a window-independent desktop controller, service idle ownership fencing, clear settings, focused regression evidence, PR merge and coordinated release.
Out: changing saved user opt-outs, remote grants, forced rollout, provider updates, stopping busy work, bypassing service activation or update recovery.

## Acceptance Criteria
- [ ] AC-01: Settings explain automatic installation and permit disabling idle restart independently; existing install opt-outs remain effective.
- [ ] AC-02: A downloaded desktop update installs without a click after five minutes of OS inactivity and verified service idle, even without an open window.
- [ ] AC-03: Busy or unknown services, outstanding questions, folder copies, foreign holds, disabled automation and unsupported backend combinations never authorize automatic restart.
- [ ] AC-04: The installer confirms its own idle hold at the commit boundary after staging; refusal or failure releases only its own hold, and repeated failures back off.
- [ ] AC-05: Research records current local settings and exact upstream comparison; focused tests and build pass, a fresh-context review accepts the exact PR head, and the change merges and reaches a coordinated release.

## Approach
Add an optional restartWhenIdle preference to contracts and desktop settings. Default it on under existing check/install preferences, with a dedicated opt-out. Run one main-process controller using the existing OS idle monitor and authenticated local service RPC. Use stopWork:false with ifIdle and an owned holdToken; never call the forced-stop path. Keep the existing service-before-app gate, staging and recovery. Confirm idle and hold ownership after staging immediately before quit. Conservatively defer unsupported secondary backends. Existing fleet members apply their own policy on their own clocks, including after reconnect; no centralized forced restart or new permissions.

## Decisions
### Defaulted
- D-01: Five minutes of OS inactivity protects active reading and typing; running work and pending questions also defer the update.
- D-02: Restart when idle defaults on only beneath enabled automatic checks and installation. Existing explicit opt-outs are preserved.
- D-03: Automatic restart never escalates to stopping work; manual Restart retains its current behavior.
- D-04: Unknown or unsupported update capability defers this operation, without blocking normal cross-version use.
- D-05: Existing release dispatcher owns publication. This worker supplies a reviewed merged commit and verifies the published release.
### Open
- None.

## Tasks
### T-01 Implement and verify automatic idle desktop installation
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/managedUpdates.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/settings/DesktopAppSettings.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/settings/DesktopAppSettings.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/updates/idleAppUpdate.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/updates/idleAppUpdate.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/updates/idleAppUpdateRpc.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/updates/DesktopUpdates.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/updates/DesktopUpdates.staging.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/serviceUpdate/ServiceUpdatePreparation.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/serviceUpdate/ServiceUpdateHold.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/serviceUpdate/ServiceUpdatePreparation.interactive.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/app/DesktopApp.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/UpdatePreferencesSection.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/UpdatePreferencesSection.test.tsx | Test: focused desktop and settings tests plus production build

### T-02 Review, merge and verify coordinated release
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode-dev/reports/idle-fleet-auto-update.md | Test: exact-head fresh-context review, GitHub checks and published release ancestry

### T-03 Verify and close 1206
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: spec.md, ledger.jsonl | Test: specweave verify 1206
