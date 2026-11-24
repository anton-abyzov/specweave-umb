# One update record for app and service

## Problem

One Update now press coordinates six processes through JSON files, with five clocks that disagree: the renderer hold (15 min), FORCE_WINDOW (15 min), APPLY_TIMEOUT (1500 s), HOLD_MAX (45 min) and the 10 min request TTL. The "then install the app" step lives in renderer memory and sessionStorage. A relaunch, a reload without the sidebar, or expired adopt retries can lose it, and then "Restart to update" or "Update now" comes back. The toast shows one static "Installing" line for the whole install, even though the helper now writes live steps to updates/install-progress.json (0985). An open question card blocks even a forced install, and the toast doesn't say which thread is waiting. Research and the staged design are in 0985/reports.

## Scope

In:
- one durable update run record with one lease clock, owned by the desktop main process and the agent;
- the app follow-up persisted by the main process;
- a live step list from install-progress.json in the toast and sidebar;
- owner-only failure;
- naming the threads whose questions block an install;
- timestamps in agent.log;
- the activation gate from #551 (the app never activates ahead of the service), reworked onto main.

Out:
- the stable launcher and shipping the service inside the app bundle (later);
- closing questions on a forced press (waits on the owner's answer, D-03 in 0985).

## Acceptance Criteria

- [ ] AC-01: One Update now press creates exactly one run record (O_EXCL, keyed by runId). Every window, a reload and a relaunched app follow that run instead of starting another. No window shows Update now, Restart to update or Retry while the run is not terminal.
- [ ] AC-02: The "install the app next" step is persisted by the main process. After the service reports the target verified, the app installs and relaunches without any renderer being mounted. A relaunched app finishes or reports the run once, and a staged update named by the run is not wiped at startup.
- [ ] AC-03: One clock: a lease renewed by the run owner's heartbeat and one hard cap replace the five timers for runs that have a record. The renderer never declares failure on its own timer. A heartbeat older than 120 s shows an amber "no progress" line with no button.
- [ ] AC-04: While the helper runs, the toast shows its current step, step i of n, elapsed and expected time from install-progress.json, then "Service is back, finishing checks" after the restart.
- [ ] AC-05: When open questions block an install, the toast and sidebar name the threads, and the agent log lines carry timestamps.
- [ ] AC-06: The app never activates a release ahead of the local service. Older agents without run support keep today's path (capability handshake), and the vendored 1.0.65 agent contract still holds.

## Approach

Base: origin/main after #555 (one-press) and #564 (fast helper). Branch feat/update-run-record in ~/.specwithcode/m4/worktrees/update-run-record. The design is in ../0985-fast-observable-service-install/reports/design.md, sections 2 to 4 and the PR 2 and 3 rows. #551's desktop half is reworked here, and #551 is closed with a pointer once this merges.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Service first, then the app, only after the service is verified.
- D-02: The run record lives at updates/run.json. Desktop writes run-era requests only when state.json advertises runSupport.
### Open
- D-03 (from 0985): may a forced press close open questions? Until answered, they are named, not closed.

## Tasks

### T-01 Agent owns the run: claim, heartbeat lease, deadline, runSupport, stamped log
- AC: AC-01, AC-03, AC-05, AC-06 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update_agent_run.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update_agent.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update_request.py, repositories/anton-abyzov/specweave-studio/scripts/lib/studio-service-updater.ts, repositories/anton-abyzov/specweave-studio/scripts/lib/studio-service-updater.test.ts, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-update-agent-run.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-update-agent.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-update-agent-install.py | Test: cd ~/.specwithcode/m4/worktrees/update-run-record/scripts/studio-fleet && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && python3 -B test-update-agent-run.py && python3 -B test-update-agent.py && python3 -B test-update-agent-install.py && python3 -B test-update-agent-refresh.py && python3 -B test-update-agent-recovery.py && python3 -B test-update.py OldAgentContract && cd ~/.specwithcode/m4/worktrees/update-run-record && node node_modules/vite-plus/bin/vp test run scripts/lib/studio-service-updater.test.ts

### T-02 Desktop run record: O_EXCL create, config mirror, handshake, 2 s publish, re-kick
- AC: AC-01, AC-03, AC-06 | Files: repositories/anton-abyzov/specweave-studio/packages/contracts/src/serviceUpdateRun.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/managedUpdates.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/desktopUpdateActions.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/desktopUpdateBridge.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/ipc.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/index.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/updates/updateRun.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/updates/updateRun.test.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/updates/studioServiceUpdates.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/updates/studioServiceUpdates.test.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/ipc/methods/serviceUpdateRuns.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/ipc/methods/serviceUpdateRuns.test.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/ipc/methods/serviceUpdates.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/ipc/methods/serviceUpdates.test.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/ipc/channels.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/preload.ts | Test: cd ~/.specwithcode/m4/worktrees/update-run-record && node node_modules/vite-plus/bin/vp test run apps/desktop/src/updates/updateRun.test.ts apps/desktop/src/updates/studioServiceUpdates.test.ts apps/desktop/src/ipc/methods/serviceUpdates.test.ts apps/desktop/src/ipc/methods/serviceUpdateRuns.test.ts packages/contracts/src && node node_modules/vite-plus/bin/vp run @specweave-studio/contracts#typecheck && node node_modules/vite-plus/bin/vp run @specweave-studio/desktop#typecheck

### T-03 Activation gate from #551 reworked onto main
- AC: AC-06 | Files: repositories/anton-abyzov/specweave-studio/apps/desktop/src/updates/appActivationGate.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/updates/appActivationGate.test.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/updates/appActivationControl.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/updates/DesktopUpdates.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/updates/DesktopUpdates.activation.test.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/updates/updatesTestHarness.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/ipc/methods/serviceUpdates.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/desktopUpdateState.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/desktopUpdateActions.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/window/DesktopApplicationMenu.test.ts | Test: cd ~/.specwithcode/m4/worktrees/update-run-record && node node_modules/vite-plus/bin/vp test run apps/desktop/src/updates/appActivationGate.test.ts apps/desktop/src/updates/DesktopUpdates.activation.test.ts apps/desktop/src/updates/DesktopUpdates.test.ts apps/desktop/src/window/DesktopApplicationMenu.test.ts && node node_modules/vite-plus/bin/vp run @specweave-studio/desktop#typecheck

### T-04 Main-owned app follow-up: run-app.json, install after verified, relaunch reconcile, kept staged update
- AC: AC-02 | Files: repositories/anton-abyzov/specweave-studio/apps/desktop/src/updates/appFollowUp.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/updates/appFollowUp.test.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/updates/runFollowUp.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/updates/runFollowUp.test.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/ipc/methods/serviceUpdateRuns.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/ipc/methods/serviceUpdateRuns.test.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/electron/ElectronMacSwapUpdater.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/electron/ElectronMacSwapUpdater.test.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/updates/appActivationGate.ts, repositories/anton-abyzov/specweave-studio/apps/desktop/src/updates/appActivationGate.test.ts | Test: cd ~/.specwithcode/m4/worktrees/update-run-record && node node_modules/vite-plus/bin/vp test run apps/desktop/src/updates/appFollowUp.test.ts apps/desktop/src/updates/runFollowUp.test.ts apps/desktop/src/ipc/methods/serviceUpdateRuns.test.ts apps/desktop/src/electron/ElectronMacSwapUpdater.test.ts apps/desktop/src/updates/appActivationGate.test.ts && node node_modules/vite-plus/bin/vp run @specweave-studio/desktop#typecheck

### T-05 Renderer follows the run: no buttons, live steps, amber stall, named question threads
- AC: AC-01, AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/serviceUpdateRunView.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/serviceUpdateRunView.test.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/serviceUpdateRunFlow.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/serviceUpdateRunFlow.test.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/serviceUpdateFlow.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/serviceUpdateCalls.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/sidebar/SidebarRestartToUpdate.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/sidebar/SidebarRestartToUpdate.run.test.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/sidebar/useServiceQuestionBlockers.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/sidebar/SidebarUpdatePill.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/sidebar/SidebarUpdatePill.test.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/UpdatePreferencesSection.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/UpdatePreferencesSection.test.tsx | Test: cd ~/.specwithcode/m4/worktrees/update-run-record && node node_modules/vite-plus/bin/vp test run apps/web/src/components/serviceUpdateRunView.test.ts apps/web/src/components/serviceUpdateRunFlow.test.ts apps/web/src/components/sidebar apps/web/src/components/settings/UpdatePreferencesSection.test.tsx apps/web/src/components/serviceUpdateMemory.test.ts apps/web/src/components/serviceUpdateCalls.test.ts && node node_modules/vite-plus/bin/vp run @specweave-studio/web#typecheck

### T-06 Docs, old-service read check and full compatibility run
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specweave-studio/docs/studio/updates.md, repositories/anton-abyzov/specweave-studio/apps/server/src/serviceUpdate/ServiceUpdateHold.test.ts | Test: cd ~/.specwithcode/m4/worktrees/update-run-record && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && node node_modules/vite-plus/bin/vp test run apps/server/src/serviceUpdate/ServiceUpdateHold.test.ts apps/desktop/src apps/web/src/components packages/contracts/src scripts/lib && node node_modules/vite-plus/bin/vp run -r --concurrency-limit 2 typecheck && bash scripts/studio-fleet/run-tests.sh --out "$(mktemp -d)"
