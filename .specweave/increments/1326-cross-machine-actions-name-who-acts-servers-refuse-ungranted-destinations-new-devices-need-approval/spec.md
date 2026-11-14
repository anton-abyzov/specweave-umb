# One "send to another machine" flow that syncs existing copies, clearer machine access, time-limited allow

## Problem

On November 13, 2026, sitting at m5, Anton could open m4's project and move it to linux-mini, while Settings > Machines said "m5 -> m4 Not set up". Analysis showed this is by design: SpecWithCode Connect signs in Anton's own machines with one account (authentication), and the per-direction grants only govern agents starting work on another machine (authorization of agents). Anton confirmed that model: the same Connect account on both machines means full control, no extra device approval (D-01).

What is wrong is the experience around it:

- The project menu has two items, "Add to another machine…" and "Move to another machine…", for what is one job: get this project onto another machine, and optionally continue there. When the destination already has a copy (moved before, or in the machine's default folder), the move should sync that copy, not redo a full copy.
- "Runs workers only" reads like a permission; it is only the status of a copy whose coordinator lives elsewhere.
- The Settings > Machines card is verbose ("This app can see it", "Limits", "Adding m4 from here needs the desktop app with full access to it…", "What m4 may use here: under Who can run work here.").
- "Allow m1" has no way to pick a time limit, and stopping it later is not obvious.

Analysis: `.specweave/reports/threads/2026-11-13-cross-machine-control-from-m5-security-analysis-b612da-999103.md`. Adversarial reviews: `reports/muse-security-review.md` (security model, max effort) and `reports/muse-design-review.md` (this design, high effort; A-01 to A-11 folded in below).

## Scope

In: one menu item and one dialog for add, move and sync; detection of an existing copy on the destination (linked project record, then Git remote plus the machine's default project folder); sync instead of full copy when one exists; renamed copy roles; a shorter machine card; Allow with a duration (1 hour, 1 day, 1 week, until I stop it) and a visible Stop. Out: changing Connect sign-in, changing what a grant permits, device approval (D-01).

## Acceptance Criteria

- [ ] AC-01: The project menu shows one "Send to another machine…" item replacing Add, Move and Sync everywhere; its dialog offers two named choices, "Copy to {m}. Keep working here." (default) and "Move to {m}. Work continues there, and this copy stops starting work."; when the destination already holds Main the choice is hidden and the dialog says so. "Start a coordinator on {m}" stays a separate action.
- [ ] AC-02: When the destination has exactly one copy of the project (linked record, or same repository and subpath), the dialog says "m1 already has a copy. It will be updated to this machine's commits." and the transfer brings every repository in it to the source heads (the existing `materialize` steps) and copies only changed local files; with two or more candidates the user picks one; a computed default folder is inspected first and an occupied one gets the `-2` suggestion.
- [ ] AC-06: If a Move cannot bring the copy to the source heads (local commits, dirty tree, detached HEAD, busy project), it stops before Main moves and shows the reason with "Move anyway on the old copy" or "Cancel"; a Copy that skips the update says why in its result.
- [ ] AC-03: One role derivation feeds the menu and Settings; badges read "Main" and "Copy · main on m4"; a non-main copy says once "Work starts on m4. This copy takes work from there." and the words "workers only" are gone.
- [ ] AC-04: A machine card shows the name, online state, one line per direction with a switch ("m4 can start work here", "This machine can start work on m4") and the projects list; the four verbose lines above are gone or behind an info icon.
- [ ] AC-05: Allowing a machine offers 1 hour, 1 day, 1 week (default) or "Until I stop it"; an allowed direction shows when it ends and a Stop button; at Stop or expiry new work is refused at once, running threads are interrupted after the current 2 minute grace, renewal is refused, and both machines show it stopped; Allow again starts a fresh period.

## Approach

Code map: `reports/code-map.md`. All project menu items already open one dialog (`ProjectMachineHandoff.tsx`); the job is to make it one decision and make "update an existing copy" real.

1. Menu: one "Send to another machine…" replaces "Add to another machine…", "Move to {m}…", "Sync to {m}…" and "Move to another machine…" (`OrchestratorSwitcher.tsx:262-305`, `DraftMachinePicker.tsx:840`, `AddProjectToMachine.tsx`, `SidebarProjectList.tsx:118`). "Start a coordinator on {m}" stays (A-06).
2. Dialog, one screen: machine list, each row "Has Main", "Has a copy" or "No copy"; two radio choices Copy (default) and Move (A-06); one plan sentence: "Update m1's copy to this machine's commits, then copy 3 changed local files" / "Clone into ~/Projects/specweave on m1, then copy 2 local files" / "Copy the folder to m1 (no Git remote)". Files and secrets review one click away, as today.
3. Detection, one shared function (A-05): linked member first; then repository key plus repository-relative subpath, exactly one candidate or let the user pick; default destination = destination `suggestedProjectsRoot` + folder name (`ManagedProjectFolders.ts:548-555`) run through the existing `destinationPlan` inspection (`studio/addToMachine.ts:88`) with its refuse-and-suggest. Replaces the two mirrored-home copies (`studio/addToMachine.ts:58-72`, `mcp/toolkits/project/addToMachine.ts:57-71`).
4. Update on receive (A-01, A-03, A-04, X-02): no upstream fast-forward. Run the git-sync path through `materialize` (`fleet/handoffGit.ts:727-830`): publish the source heads to the per-operation ref, fetch only that ref, validate every manifest repository (submodules, linked worktrees), re-check clean and in-use immediately before each `--ff-only` merge, under the destination project admission lock. Git runs with hooks, filters and fsmonitor off, and the existing copy's `.git/config` is checked against the 1328 allowlist first (unsafe entries named, not silently run). LFS pull and submodule update are explicit steps with their own failure text, or the copy falls back to the folder-copy review.
5. Skipped update (A-02): for Move, stop before the binding changes (`MachineHandoff.ts:1310`) and offer "Move anyway on the old copy" / "Cancel"; the receive result gains `updateSkipped: { reason }`, shown after the transfer.
6. Roles (A-07): one derivation shared by `machinesSettings.logic.ts:190-215` and `projectCoordinatorMachine.ts:203-220`; labels "Main", "Copy · main on {m}", "Moving main"; the copy's own line reuses `workersOnlyCopy.ts:20` reworded; internal state name unchanged.
7. Machine card (A-11, shared with 1327): header (name, online dot, ⋯); "Devices that can use this machine" (1327); "{there} can start work here · All projects · until November 20 · Stop" or "Allow…"; "This machine can start work on {there} · Not set up · Set up…"; projects collapsed past five. Help text behind ⓘ; "Limits", "Its app sees this machine" and the footer move into ⋯ "Connection details".
8. Allow duration (A-08, A-09, A-10): contract gets an optional `duration: "1h" | "1d" | "7d" | "until-stopped"` on allow and grant update (`packages/contracts/src/studioFleet.ts:137`, `:503`); the worker computes `expiresAt` from its own clock and stores it on the policy (`fleet/WorkGrants.ts:49`, both `effectiveGrant` branches at `:208-213`). The sweeper (`workGrantRevokeSweeper.ts:26`) materializes a passed `expiresAt` into the same stored state `revoke` writes (`WorkGrants.ts:544`: `revokedAt`, `interruptAt`, session revocation), once. Renewal (`auth/http.ts:638`, `SessionStore.ts:1113`) consults the policy and answers `grant_revoked` after expiry, so the coordinator marks it stopped (`FleetWorkerGrants.ts:361`). One state machine: Allow sets a fresh deadline (also after expiry), Stop = revoke now, Restore only for revoked-not-expired. Worker side ships first; clients send `duration` only to machines that report support.
9. Notice (X-03): expiry and Stop post one line in Settings activity on both machines: "m1 can no longer start work here (ended November 20)."

Risks: the update changes files on the destination, so it runs only clean, idle and strictly behind; version skew handled by the support flag.

## Decisions

### Asked
- D-01 Device approval for Connect-signed-in devices → none. Same Connect account on both machines means full control; grants stay about agents (Anton, November 13, 2026).
### Defaulted (change any before sw-do)
- D-02 Existing-copy detection: linked project record first, then repository key plus subpath with exactly one candidate; never guess by folder name alone and never write into an uninspected folder.
- D-03 Default choice in the dialog is Copy, not Move.
- D-04 Keep the workers-only state; rename only its words.
### Open
- none

## Tasks

### T-01 Map current add, move, role and grant code
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: .specweave/increments/1326-cross-machine-actions-name-who-acts-servers-refuse-ungranted-destinations-new-devices-need-approval/reports/code-map.md | Test: test -s .specweave/increments/1326-cross-machine-actions-name-who-acts-servers-refuse-ungranted-destinations-new-devices-need-approval/reports/code-map.md

### T-02 Timed Allow: duration, materialized expiry, renewal refusal
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/studioFleet.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/WorkGrants.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/workGrantRevokeSweeper.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/http.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/SessionStore.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/FleetWorkerGrants.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/fleet/WorkGrants src/fleet/workGrantRevokeSweeper src/fleet/FleetWorkerGrants

### T-03 Existing copy updated through materialize, skipped update reported
- AC: AC-02, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/MachineHandoff.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/handoffGit.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/safeGitConfig.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/fleet/handoffGit src/fleet/MachineHandoff

### T-04 One detection function and one role derivation
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/existingCopy.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectDomain.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/MachinesSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/addToMachine.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/addToMachine.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/machinesSettings.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectCoordinatorMachine.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/workersOnlyCopy.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/studio src/components/settings

### T-05 Send to another machine menu item and dialog
- AC: AC-01, AC-02, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectMachineHandoff.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffShare.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/MachineHandoffDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/sendToMachine.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/DraftMachinePicker.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AddProjectToMachine.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/SidebarProjectList.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/machines-page/sendScene.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/machines-page/shoot-send.mjs | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/studio src/components/chat src/components/settings src/studio/sendToMachine

### T-06 Shorter machine card with Allow duration and Stop
- AC: AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/MachinesSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/MachineCardDirections.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/machineDirections.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/MachineWorkGrants.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ConnectBothWays.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/DetailLine.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/machinesSettings.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/tests/machines-page/cardScene.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/machines-page/shoot-card.mjs | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/settings

### T-07 Verify and close 1326
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: .specweave/increments/1326-cross-machine-actions-name-who-acts-servers-refuse-ungranted-destinations-new-devices-need-approval/ | Test: specweave verify 1326
