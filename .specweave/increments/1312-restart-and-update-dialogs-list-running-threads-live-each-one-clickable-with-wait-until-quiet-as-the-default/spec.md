# Restart and update dialogs list running threads live, each one clickable, with Wait until quiet as the default

## Problem

Anton, November 12, 2026: "we used to have exact tasks and when I click to restart displayed ... with actual list of in progress, clickable threads!" Pressing Restart to update on the desktop now shows a plain text question ("3 tasks will be interrupted ... Stop and update now / Cancel") with no thread list and no way to wait.

Cause, from `anton-abyzov/specwithcode` history: the clickable list (`RestartRunningWorkList`, since 1.0.5) is rendered only by `confirmAppRestartForUpdate`, the app-only restart path. Since 1.0.67 a press whose local service also has an update goes through `startServiceUpdateNow` first (`SidebarRestartToUpdate.tsx` "A service update asks for itself"), and that path asks with `requestConfirmDialog(describeServiceUpdateStop(...))`: text only, two buttons. The app-only path stayed common while the service usually installed its update on its own ahead of the app. Since the "Update now" run (0988) and #175 (1304, November 11: updates pause running work only when the owner allows it, off by default) the service waits for quiet instead, so nearly every press now carries a service update and lands on the text dialog. `aef2615a9e` (November 7) also hid threads that only wait on a person, which is correct and is kept. The remote machine Update prompt (`ServerUpdateAction.tsx`) never listed threads.

## Scope

In: one live running-work panel used by every restart or update question (sidebar Restart to update, the update pill, the app menu and first-run notice that route through `requestRestartToUpdate`, Settings' update rows, and the remote machine Update in Settings > Machines and the sidebar). Three choices: Wait until quiet (default), Restart now, Later. Wait until quiet for the service path and for a remote machine.

Out: server changes to the blocker contract; the phone app; the force-install hold window setting (unchanged: Wait until quiet still ends after the configured minutes, as Restart when idle did).

## Acceptance Criteria

- [ ] AC-01: A restart or update question that would cut off work lists each interrupted thread as one row: a status icon, its title, what it is doing now (its current command or tool, else running, queued or a question), and the machine it runs on. Clicking a row closes the dialog and opens that thread.
- [ ] AC-02: The rows update live while the dialog is open: a thread that finishes leaves the list, a new one appears, and the count above the list follows; an empty list says all is quiet.
- [ ] AC-03: The dialog shows a clear count ("3 threads running") and three choices with icons: Wait until quiet (the default, primary button), Restart now, Later. Text stays to one short line under the title.
- [ ] AC-04: The same panel and choices appear on every entry point: an app-only restart, a restart that updates the local service first (sidebar button, update pill, menu, Settings, first-run notice), and a remote machine's Update. Wait until quiet on the service path and on a remote machine waits for quiet before it updates, without forcing.
- [ ] AC-05: Headless screenshots of the dialog before (the text-only question on `origin/main`) and after (the live list) are saved in this increment's `reports/`.

## Approach

- `apps/web/src/components/sidebar/RestartRunningWorkList.tsx`: rewritten as a flat, live list. `LiveRestartWork` holds the blockers, re-reads them every 3 s through a `poll` callback, and joins each blocker's thread with its shell (`useThreadShells`) for `activeWork.label` and the execution machine (`threadLocation` plus `useMachineNicknames`). Pure row building and the count text live in `restartRunningWork.logic.ts`.
- `confirmDialog.ts` and `ConfirmDialogHost.tsx`: optional button icons; the confirm button is the default focus.
- `serviceUpdateCalls.ts` (`confirmAppRestartForUpdate`) and `serviceUpdateFlow.ts` (`startServiceUpdateNow`): both ask through one `askRestartForWork` helper with the panel and the three choices. `startServiceUpdateNow` takes `confirmed` (skip the question once the wait came due) and `onWaitForQuiet`; without the latter (no sidebar mounted, for example the browser) it offers Restart now and Later only.
- `SidebarRestartToUpdate.tsx`: the existing wait-for-idle clock now also covers a service update, so Wait until quiet works for both.
- `ServerUpdateAction.tsx`: the remote Update asks with the panel, polled from that machine's `prepareServiceUpdate`; Wait until quiet re-checks every 15 s and updates once nothing there would be cut off, with a toast that says so and can be cancelled.
- Rejected: restoring the old project-grouped list unchanged. It had no machine and no current step, and grouping hid the thread rows behind project headers.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Wait until quiet keeps the existing "force install after N minutes" window on the desktop, because that is the setting that already governs Restart when idle; the remote machine wait never forces (decision_no_forced_updates).
- D-02 The list is flat, busiest first, five rows before "Show all", because Anton asked for rows with machine, title and current step; the project shows as a muted suffix.
### Open
- none

## Tasks

### T-01 Live running-work list with machine and current step
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/sidebar/RestartRunningWorkList.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/sidebar/restartRunningWork.logic.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/sidebar/RestartRunningWorkList.test.tsx | Test: cd ~/.specwithcode/m4/verify/specwithcode && specweave-studio checks run -- ~/.specwithcode/m4/scratch/2026-11-12-restart-list/run-gated.sh "cd apps/web && npx vp test run --project unit src/components/sidebar/RestartRunningWorkList.test.tsx"

### T-02 Three choices with icons on every restart and update entry point
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/confirmDialog.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/ConfirmDialogHost.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/serviceUpdateCalls.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/serviceUpdateFlow.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/sidebar/SidebarRestartToUpdate.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/ServerUpdateAction.tsx | Test: cd ~/.specwithcode/m4/verify/specwithcode && specweave-studio checks run -- ~/.specwithcode/m4/scratch/2026-11-12-restart-list/run-gated.sh "cd apps/web && npx vp test run --project unit src/components/sidebar src/components/serviceUpdate src/components/ServerUpdateAction.test.tsx src/confirmDialog.test.ts src/themeContrastClasses.test.ts"

### T-03 Headless before and after screenshots
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/tests/restart-work-list/main.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/restart-work-list/verify.mjs, .specweave/increments/1312-restart-and-update-dialogs-list-running-threads-live-each-one-clickable-with-wait-until-quiet-as-the-default/reports/after-dialog.png | Test: ls .specweave/increments/1312-restart-and-update-dialogs-list-running-threads-live-each-one-clickable-with-wait-until-quiet-as-the-default/reports/after-dialog.png

### T-04 Verify and close 1312
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: .specweave/increments/1312-restart-and-update-dialogs-list-running-threads-live-each-one-clickable-with-wait-until-quiet-as-the-default/spec.md | Test: specweave verify 1312
