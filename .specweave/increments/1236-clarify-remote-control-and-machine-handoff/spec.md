# 1236 Clarify remote control and machine handoff

## Problem
Connection setup, viewing another machine, granting workers access and moving execution appear in overlapping menus. Users cannot reliably predict which machine will execute their next action.

## Scope
In: read-only inventory of app and public documentation, vocabulary alternatives, proposed information architecture, responsive before/after concept mockups, approval decision. Implementation approved November 4, 2026: app, documentation and landing vocabulary and information architecture. Out: protocol/storage renames and permission changes. Existing implementation owners retain their files.

## Acceptance Criteria
- [ ] AC-01: Inventory maps machine, connection and handoff surfaces to current source paths and proposed terminology.
- [ ] AC-02: A designed HTML proposal distinguishes viewing/control, starting new work, moving an existing thread, coordinator transfer and file copy, with Mac/Windows/Linux width examples and failure states.
- [ ] AC-03: User explicitly chooses the concept before implementation; the selected scope and remaining delivery gates are recorded.

- [ ] AC-04: Independent app controls distinguish viewing, initial execution selection and moving execution without changing permissions or Stop holds.
- [ ] AC-05: Remote-control and portable-handoff guides explain execution location, readiness, credentials and account limits.
- [ ] AC-06: Reconciled Machines and Integrations navigation and landing use approved vocabulary, with focused tests, builds and headless evidence.
- [ ] AC-07: PRs receive exact-head SHIP and dispatcher-controlled merge/deployment evidence; proof limits remain explicit.

## Approach
Read app main and docs sources; preserve dirty shared checkout and active owners. Produce standalone artifacts under /Users/antonabyzov/.specwithcode/m4/scratch/1236-remote-control and an editable design document. Validate via hidden collaborative browser, saving captures. Implement only in the app-provisioned isolated checkout; coordinate overlapping PR paths and isolated landing binding before those edits. Manual worktree creation was refused by the app's Use worktrees guard; defer checkout creation to approved implementation. Use session-local specweave 3.1.21.

## Decisions
### Defaulted
- Recommend Machines as navigation, Remote control as an explicit action, Move thread as execution transfer; retain handoff in explanatory copy.
- Keep access direction and scopes explicit; a connected machine is not automatically allowed to run workers.
- Preserve SpecWithCode Connect as the transport brand. Connections for external services becomes Integrations within the approved implementation scope; this concept increment changes no product source.
- Width previews are web layout mockups, not native OS acceptance.
### Asked
- On November 4, 2026, Anton approved Machines + Remote control + Move thread, including implementation across app, docs and landing page.
### Open
- none for the concept scope; implementation requires ownership reconciliation.

## Tasks
### T-01 Inventory current surfaces
- AC: AC-01 | Files: /Users/antonabyzov/.specwithcode/m4/scratch/1236-remote-control/inventory.json, /Users/antonabyzov/.specwithcode/m4/scratch/1236-remote-control/source-matches.txt | Test: python3 -m json.tool /Users/antonabyzov/.specwithcode/m4/scratch/1236-remote-control/inventory.json

### T-02 Build and verify concept proposal
- AC: AC-02 | Files: /Users/antonabyzov/.specwithcode/m4/scratch/1236-remote-control/proposal.html, /Users/antonabyzov/.specwithcode/m4/scratch/1236-remote-control/verification.json | Test: python3 -m json.tool /Users/antonabyzov/.specwithcode/m4/scratch/1236-remote-control/verification.json

### T-03 Record concept decision
- AC: AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/scratch/1236-remote-control/decision.md | Test: test -s /Users/antonabyzov/.specwithcode/m4/scratch/1236-remote-control/decision.md

### T-04 Clarify independent remote control and handoff guides
- AC: AC-05 | Files: docs/user/remote-access.md, docs/user/portable-handoffs.md | Test: git diff --check

### T-05 Clarify independent machine controls
- AC: AC-04 | Files: apps/web/src/components/studio/OrchestratorSwitcher.tsx, apps/web/src/components/chat/DraftMachinePicker.tsx, apps/web/src/components/chat/threadMachine.ts, apps/web/src/components/handoff/HandOffMachineDialog.tsx, apps/web/src/components/studio/MachineHandoffDialog.tsx, apps/web/src/components/chat/AddToMachineDialog.tsx, apps/web/src/components/settings/ProjectHandoffModeSettings.tsx | Test: focused existing component tests and production web build

### T-09 Update independent machine control regression expectations
- AC: AC-04 | Files: apps/web/src/components/studio/OrchestratorSwitcher.test.tsx, apps/web/src/components/chat/DraftMachinePicker.test.tsx | Test: focused existing component tests

### T-06 Integrate reconciled Machines and Integrations surfaces
- AC: AC-06 | Files: apps/web/src/components/settings/ConnectionsSettings.tsx, apps/web/src/components/settings/IntegrationsSettings.tsx, apps/web/src/components/settings/ConnectionsLibrarySettings.tsx, apps/web/src/components/settings/settingsSearch.ts, apps/web/src/components/settings/settingsSearch.test.ts, apps/web/src/components/settings/SettingsSidebarNav.tsx, apps/web/src/components/settings/SettingsSidebarNav.active.test.ts | Test: focused navigation and permission tests, production web build, headless responsive evidence

### T-07 Align landing in supported isolated binding
- AC: AC-06 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave/feat-1236-remote-control/docs-site/src/pages/code.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave/feat-1236-remote-control/docs-site/src/components/code/Landing.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave/feat-1236-remote-control/docs-site/src/components/code/Landing.module.css | Test: landing production build and headless responsive evidence

### T-08 Deliver reviewed implementation through dispatcher
- AC: AC-07 | Files: reports/implementation-delivery.md | Test: exact-head review, CI and dispatcher deployment receipts

### T-10 Align project preparation regression
- AC: AC-04 | Files: apps/web/src/components/chat/AddToMachineDialog.test.tsx | Test: focused AddToMachineDialog component suite

### T-11 Fold reconciled machine readiness and access fixes
- AC: AC-04, AC-06 | Files: CHANGELOG.md, apps/web/src/components/handoff/HandOffThreadDialog.test.tsx, apps/web/src/components/handoff/HandOffThreadDialog.tsx, apps/web/src/components/handoff/HandoffResults.tsx, apps/web/src/components/settings/FleetInvite.test.tsx, apps/web/src/components/settings/FleetInvite.tsx, apps/web/src/components/settings/MachinesSettings.test.tsx, apps/web/src/components/settings/MachinesSettings.tsx, apps/web/src/components/settings/SettingHelp.tsx, apps/web/src/components/settings/StudioFleetConnections.test.tsx, apps/web/src/components/settings/StudioFleetConnections.tsx, apps/web/src/components/settings/machinesSettings.logic.test.ts, apps/web/src/components/settings/machinesSettings.logic.ts, apps/web/src/studio/fleetWorkers.test.ts, apps/web/src/studio/fleetWorkers.ts | Test: focused machine settings, fleet invite, worker and handoff suites

### T-12 Align move action labels and regression expectations
- AC: AC-04 | Files: apps/web/src/components/threadActionMenu.logic.ts, apps/web/src/components/threadActionMenu.logic.test.ts, apps/web/src/components/chat/threadMachine.test.ts, apps/web/src/components/studio/MachineHandoffDialog.test.tsx | Test: focused thread action, presentation and project move tests

### T-13 Repair consolidated setup routing and remote control
- AC: AC-04, AC-06 | Files: apps/web/src/routes/settings.machines.tsx, apps/web/src/routes/settings.connections.tsx, apps/web/src/components/settings/MachinesHub.tsx, apps/web/src/components/settings/MachineRemoteControl.tsx, apps/web/src/components/settings/MachineRemoteControl.test.tsx, apps/web/src/components/settings/MachinesHub.test.tsx | Test: focused hub and remote-control permission/routing tests, production build and headless composed hub

### T-14 Compose one machine inventory with existing fleet controls
- AC: AC-04, AC-06 | Files: apps/web/src/components/settings/MachinesSettings.tsx, apps/web/src/components/settings/StudioFleetConnections.tsx, apps/web/src/components/settings/MachinesSettings.test.tsx, apps/web/src/components/settings/StudioFleetConnections.test.tsx | Test: focused machine and fleet rendering suites

### T-15 Align guide setup routes with the consolidated hub
- AC: AC-05, AC-06 | Files: docs/user/remote-access.md, docs/user/portable-handoffs.md | Test: source route audit and git diff --check

### T-16 Repair reverse setup instructions found in composed-route proof
- AC: AC-04, AC-06 | Files: apps/web/src/components/settings/MachineWorkGrants.tsx, apps/web/src/components/settings/MachineWorkGrants.test.tsx, apps/web/src/components/settings/IncomingWorkerSetup.tsx, apps/web/src/components/settings/IncomingWorkerSetup.test.tsx, apps/web/src/components/settings/machinesSettings.logic.ts, apps/web/src/components/settings/machinesSettings.logic.test.ts, apps/web/src/components/settings/MachinesSettings.test.tsx, apps/web/src/components/settings/ConnectReachBanner.tsx, apps/web/src/components/settings/ConnectReachBanner.test.ts | Test: focused grant, incoming-worker, machine logic and reach-banner tests; production build and headless route proof

### T-17 Reconcile fleet-only empty copy with the unified inventory
- AC: AC-06 | Files: apps/web/src/components/settings/StudioFleetConnections.tsx, apps/web/src/components/settings/StudioFleetConnections.test.tsx | Test: focused fleet rendering suite and two-private-server headless check

### T-18 Keep machine identity readable beside Remote control
- AC: AC-06 | Files: apps/web/src/components/settings/MachinesSettings.tsx | Test: focused machine suite, production build and 390-pixel composed route capture

### T-19 Preserve the machine through project selection and creation
- AC: AC-04, AC-06 | Files: apps/web/src/components/settings/MachineRemoteControl.tsx, apps/web/src/components/settings/MachineRemoteControl.test.tsx, apps/web/src/commandPaletteBus.ts, apps/web/src/components/CommandPalette.tsx, apps/web/src/components/CommandPalette.logic.ts, apps/web/src/components/CommandPalette.logic.test.ts | Test: focused remote project routing and palette intent tests; production build; headless local-only, shared-primary and empty-remote project scenarios

### T-20 Correct the landing machine setup section name
- AC: AC-06 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave/feat-1236-remote-control/docs-site/src/pages/code.tsx | Test: landing source copy check and relevant build; owner 1236-landing

### T-21 Keep the machine-row test isolated from project registry state
- AC: AC-06 | Files: apps/web/src/components/settings/MachinesSettings.test.tsx | Test: focused MachinesSettings suite

### T-22 Rebase on main and preserve the merged narrow machine label
- AC: AC-04, AC-06 | Files: apps/web/src/components/settings/ConnectReachBanner.tsx, apps/web/src/components/chat/ThreadMachineComposerChip.tsx | Test: focused Connect routing and machine composer suites, production build, headless narrow composer verification and fresh exact-head review

### T-23 Align remaining integration tests with approved navigation vocabulary
- AC: AC-04, AC-06 | Files: apps/web/src/components/settings/settingsSearchModel.test.ts, apps/web/src/components/studio/ProjectWorkspace.threads.test.tsx | Test: reproduce the old web 2/2 CI failures on current head, preserve coordinator/draft assertions, run both focused suites and fresh exact-head review

### T-24 Preserve exact optional fleet renderer props
- AC: AC-06 | Files: apps/web/src/components/settings/ConnectionsSettings.tsx | Test: web typecheck and focused fleet composition tests

### T-25 Use the readable error foreground in Machines
- AC: AC-06 | Files: apps/web/src/components/settings/MachinesSettings.tsx | Test: theme contrast class guard and MachinesSettings suite

## Closure
Verify and close 1236 after implementation delivery, with specweave verify, a fresh-context review and specweave complete. Merge freeze remains until dispatcher explicitly lifts it.
