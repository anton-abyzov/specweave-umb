# Make handoff beautiful and simple

## Problem

Handoff in SpecWithCode works underneath but is hard to use. The word "handoff" names six different actions (thread move, bulk move, project move, same-machine model switch, a timeline event, a setting). The thread dialog has dead ends: a failed check hides "Check again", a thread with no model can never be submitted, and a destination update needs a manual re-check. The project dialog asks about 12 questions before it does anything, its method labels contradict each other, and "Move coordinator to X" opens in copy-only mode. On the receiving side the header hides "Continue here" when the source is offline, and "Continue here anyway" resumes the whole Mac without warning. Evidence: workflow map and critique (2026-10-28), before screenshots in ~/.specwithcode/m4/evidence/handoff-ux/before/. Proposal: https://claude.ai/artifact/TDrN6eY1qnn1STVxMu8EtV

## Scope

In: interface only. New plain wording ("Move"), a one-screen thread Move dialog, one "Move running threads" dialog, status chips and receiving-side banners, a confirm before resuming a paused Mac, a four-screen project move. Out: install and update mechanics (owned by the update thread), handoff protocol, server checks (except the one user-visible string HandoffTurnGate returns).

## Acceptance Criteria

- [ ] AC-01: Moving one thread is one screen: machine rows (this machine excluded, offline machines disabled with a reason), model as a summary under More options, Move disabled until checks pass, Try again available after any failed or errored check, automatic re-check after a destination update, no dead end when the thread has no model.
- [ ] AC-02: "Move running threads" replaces "Hand off this machine…" and "Migrate threads…" in one dialog with the same data path; never shows "Move 0 threads".
- [ ] AC-03: Thread rows and header show status as chips ("Ready to move", "Syncing", "Moved to X", "X is offline", "Paused after sleep"); the header offers Continue here when the source is offline; action buttons do not move on hover; "Resume this Mac…" asks for confirmation; the source banner reads "Moved to X".
- [ ] AC-04: Menus, palette, switcher, settings, limit banner and timeline use the new wording; same-machine model switch is its own "Switch model and continue…" item.
- [ ] AC-05: Project move is at most four short screens; Move vs Copy follows the entry point and requested machine; rare options live under More options; review appears only when files would be replaced, a choice is needed or secrets exist.
- [ ] AC-06: All handoff unit tests and headless harnesses pass with screenshots in light and dark; a real move between M4 and ministorm works on the released build.

## Approach

Keep pure *View components and every invariant (submit only after checks pass, no close while submitting, verbatim server failures with data-check, version regex, role=status/alert, personal-assistant exclusion, secrets consent, 14-day undo, publish lock). Add a shared machine option-row list used by thread, bulk and project dialogs. Rename strings and update tests. PR 1 ships AC-01..AC-04; PR 2 ships AC-05; AC-06 after release.

## Decisions

### Asked
- D-01 Rename "Hand off" to "Move" across the UI → proposed, awaiting user (recommended yes)
### Defaulted (change any before sw-do)
- D-02 Two PRs, threads first → default
- D-03 Keep the app's existing dialog primitives and accent; no new design tokens → default
### Open
- none

## Tasks

### T-01 One-screen thread Move dialog
- AC: AC-01 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/handoff/HandOffThreadDialog.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/handoff/HandoffResults.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/handoff/HandoffModelPicker.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/handoff/HandoffDestinationUpdate.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/handoff/MachineOptionRows.tsx | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/handoff-ux && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && node node_modules/vite-plus/bin/vp test run apps/web/src/components/handoff

### T-02 Move running threads dialog
- AC: AC-02 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/handoff/HandOffMachineDialog.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/handoff/HandOffMachineDialog.test.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/CommandPalette.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/OrchestratorSwitcher.tsx | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/handoff-ux && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && node node_modules/vite-plus/bin/vp test run apps/web/src/components/handoff apps/web/src/components/studio/OrchestratorSwitcher.test.tsx

### T-03 Status chips and receiving side
- AC: AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/handoff/HandoffBadge.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/studio/handoffMode.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/ChatView.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/shell/ThreadsPane.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/shell/ProjectThreadHeader.tsx | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/handoff-ux && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && node node_modules/vite-plus/bin/vp test run apps/web/src/components/handoff apps/web/src/studio

### T-04 New wording in menus, settings, banner and timeline
- AC: AC-04 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/threadActionMenu.logic.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/threadMachine.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/HandoffModeSettings.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/LimitHandoffCandidates.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/V2LifecycleRow.tsx | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/handoff-ux && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && cd apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/threadActionMenu.logic.test.ts src/hooks/useThreadActionMenu.test.ts src/components/chat src/components/settings/HandoffModeSettings.test.tsx

### T-05 Four-screen project move
- AC: AC-05 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/MachineHandoffDialog.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/ProjectMachineHandoff.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/HandoffFolderCopy.tsx | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/handoff-ux && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio

### T-06 Verify and close 1117
- AC: AC-06 | Files: none | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/handoff-ux && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && node node_modules/vite-plus/bin/vp test run apps/web/src && node node_modules/vite-plus/bin/vp run @specweave-studio/web#typecheck
