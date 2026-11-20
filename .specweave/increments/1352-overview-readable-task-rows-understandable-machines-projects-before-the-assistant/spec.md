# Overview: readable task rows, understandable machines, projects before the assistant

## Problem

Anton, November 14, 2026, on the Overview page of m4: "We must improve the visual part of how we present the tasks and the machine. We don't fully understand the machine." His screenshot shows:

- "Needs you" stuck on "Reading your chats… Each connected machine reports its chats." while 14 chats are listed under Working.
- Task rows name the machine by the saved connection's host label ("Anton's MacBook M4MAX", "ministorm") with no color. The sidebar names the same machines "m4" and "linux-mini" in their colors.
- Status chips print the running step's label, which for a command is the first 60 characters of the shell line: "Waiting on cd /Users/anton…", "Waiting on W=/Users/anton…".
- The rail lists Percy above Projects. Machines rows say "Anton's MacBook Pro · Reconnecting · 0 projects" with no explanation, and a bare version number with no word on whether it is current.

Causes (app repo `repositories/anton-abyzov/specwithcode`, main 8f11ba707):

- `allEnvironmentShellsBootstrappedAtom` (`apps/web/src/state/shell.ts:27`) returns false while any enabled machine without a snapshot is in the supervisor's `connecting` phase. A machine that never answers alternates `connecting` and `backoff` forever, so every retry puts the page back to "Reading your chats…". The retry allowance (`attempt <= 2`) is only checked in `backoff`.
- `StudioOverview.tsx:265` builds `hostNames` from `environment.label`; `OverviewRows.tsx` prints it. Nicknames and colors (`useMachineIdentities`, `apps/web/src/studio/machineIdentity.ts`) are not used on this page, nor in `CapacityFleet` and the slow-request toast.
- `deriveSessions` (`apps/web/src/studio/overviewModel.ts:176-186`) writes `health.label` into the chip. The label is `activeWork.label`, a free string with no kind (`packages/shared/src/orchestrationV2PendingBackgroundWork.ts:357-406`).
- The rail order is hard-coded: assistant, projects, machines (`StudioOverview.tsx:973-1141`). `MachineRow` prints status only when not connected, the raw `serverVersion`, and a project count that reads 0 when the machine never reported.
- iPhone app (`apps/ios`): `MachineNicknameEntry` drops `color` and `short`, three banners print the raw host label, and a working thread's "Latest" line prints the raw command.

## Scope

In: the Overview page on web and desktop (task rows, status chips, rail order, assistant card, machine rows, the "Reading your chats…" gate), the other web places that still print a raw host label, the shared status phrase, and the iPhone app's machine color, names and status line.

Out: moving Percy in the sidebar and the iPhone drawer (D-02), a per-machine detail page, and any release.

## Acceptance Criteria

- [ ] AC-01: Overview settles when every enabled machine has either reported its chats or failed more than twice. A machine that keeps retrying no longer returns the page to "Reading your chats…"; the notice above the lists names it.
- [ ] AC-02: Every machine name on Overview (chat rows, Projects and assistant rows, Machines rows, scope chip, stale notice, "N more on", the new-chat chooser, the capacity cards) is the machine's nickname as the sidebar shows it, with its full host label on hover.
- [ ] AC-03: A chat row shows its title, then one meta line that starts with the machine's color mark and name, followed by project, model and increment progress.
- [ ] AC-04: A chip never contains a command line. A running step reads "Running a command · 3m", "Using a tool · 3m", "Waiting on a subagent · 3m", "Waiting on another thread · 3m" or "Waiting on a delegated task · 3m"; a stall reads "No activity for 35m". The step's own label is the chip's tooltip.
- [ ] AC-05: A row under Working shows no chip when its state is plain "Working".
- [ ] AC-06: The rail order is Projects, Personal assistant, Machines. The assistant section has its own heading and card style and each assistant row names its machine with the color mark.
- [ ] AC-07: A Machines row shows the machine's icon in its color, its name ("this machine" on the local one), its state in words, its version with "current" or "update available", how many chats are working there and how many projects it has.
- [ ] AC-08: A machine that has not reported shows "Can't reach it · retrying" (or "Offline", "Can't connect") and "Its chats and projects aren't counted", never "0 projects".
- [ ] AC-09: The server reports the kind of the active step (`command`, `tool`, `subagent`, `thread`, `task`) in `activeWork.kind`; a client talking to a server without it still shows a phrase from AC-04.
- [ ] AC-10: The slow-request toast names the machine by nickname.
- [ ] AC-11: The iPhone app decodes a machine's color, shows it beside the machine's name in thread and project rows, uses nicknames in the expiry, update and catching-up banners, and shows the AC-04 phrase where it showed the raw command.
- [ ] AC-12: The places checked are listed in `reports/places-checked.md` with what each shows and whether it changed.

## Approach

1. `packages/contracts/src/orchestrationV2.ts`: optional `activeWork.kind`. `packages/shared/src/orchestrationV2PendingBackgroundWork.ts`: `deriveActiveRunWork` returns the kind; new `activeWorkPhrase(label, kind)` gives the words for a wait and for a stall, guessing the kind from the fixed labels when an older server sends none. `RunHealth` carries the kind.
2. `apps/web/src/state/shell.ts`: move the per-machine test into a pure `environmentHoldsBootstrap` and count attempts in `connecting` as in `backoff`.
3. `apps/web/src/studio/overviewModel.ts`: `SessionView.state` uses the phrase; `stateDetail` keeps the label for the tooltip.
4. `apps/web/src/components/studio/OverviewRows.tsx`, `StudioOverview.tsx`, `overview.css`: identity-based names, `MachineMark`, the new row layout, rail order, assistant card, machine rows. `apps/web/src/studio/overviewMachines.ts` holds the pure machine-row model (state words, version state, counts).
5. `CapacityFleet.tsx`, `SlowRpcRequestToastCoordinator.tsx`: nickname.
6. iPhone: `SWCWire/Settings.swift`, `SWCSync/MachineNickname.swift`, `SWCSync/ShellSummaries.swift`, the row views and banners. Built and tested on a Mac.

Rejected: a client-only guess at the step kind (a command and a tool title look alike); a timer in the bootstrap gate (the attempt count already says the machine had its chance); hiding the unreachable machine (it is a saved connection the person may want to fix or remove).

Risk: `allEnvironmentShellsBootstrappedAtom` is shared by the first-run gate, the project workspace, thread links and remote worker cards. The change only makes it settle sooner for a machine that failed more than twice, which is the case those callers already accept in `backoff`.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01 Mock shown in the thread before the build; the build proceeds without waiting (the request says mock first, then build).
- D-02 The sidebar and the iPhone drawer keep the assistant pinned above the project list. There it is a navigation shortcut already separate from Projects, and below ten or more projects it would be buried. Reversible in one place each (`StudioSidebar.tsx`, `DrawerView.swift`, `SidebarView.swift`).
- D-03 "Current" means not behind the newest version this app knows: its own version, the newest release it has heard of, and the highest version any connected machine reports.
- D-04 The command stays readable in the chip's tooltip and inside the open thread's timeline; only summary rows drop it.

### Open
- none

## Tasks

### T-01 Bootstrap gate settles past a machine that keeps retrying
- AC: AC-01 | Files: [repositories/anton-abyzov/specwithcode/apps/web/src/state/shell.ts, repositories/anton-abyzov/specwithcode/apps/web/src/state/shellBootstrap.ts, repositories/anton-abyzov/specwithcode/apps/web/src/state/shellBootstrap.test.ts] | Test: pnpm --dir apps/web exec vp test run src/state/shellBootstrap.test.ts

### T-02 Active step kind and plain status phrase
- AC: AC-04, AC-09 | Files: [repositories/anton-abyzov/specwithcode/packages/contracts/src/orchestrationV2.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/orchestrationV2PendingBackgroundWork.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/orchestrationV2PendingBackgroundWork.test.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/models.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/overviewModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/overviewModel.test.ts] | Test: pnpm --dir packages/shared exec vp test run src/orchestrationV2PendingBackgroundWork.test.ts && pnpm --dir apps/web exec vp test run src/studio/overviewModel.test.ts

### T-03 Overview rows, rail order, assistant card and machine rows
- AC: AC-02, AC-03, AC-05, AC-06, AC-07, AC-08 | Files: [repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/StudioOverview.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OverviewRows.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/overview.css, repositories/anton-abyzov/specwithcode/apps/web/src/studio/overviewMachines.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/overviewMachines.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/StudioOverview.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CapacityFleet.tsx] | Test: pnpm --dir apps/web exec vp test run src/components/studio/StudioOverview.test.tsx src/studio/overviewMachines.test.ts

### T-04 Slow-request toast and other raw host labels
- AC: AC-10, AC-12 | Files: [repositories/anton-abyzov/specwithcode/apps/web/src/components/SlowRpcRequestToastCoordinator.tsx, .specweave/increments/1352-overview-readable-task-rows-understandable-machines-projects-before-the-assistant/reports/places-checked.md] | Test: pnpm --dir apps/web exec vp test run src/components/SlowRpcRequestToastCoordinator

### T-05 Screenshots of the built page, checks, PR, merge, SHA to the release owner
- AC: AC-02, AC-03, AC-06, AC-07 | Files: [repositories/anton-abyzov/specwithcode/apps/web/tests/overview-rows/] | Test: specweave-studio checks run -- pnpm verify:pr

### T-06 iPhone: machine color, nicknames in banners, plain status line
- AC: AC-11 | Files: [repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCWire/Settings.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/MachineNickname.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/ShellSummaries.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/] | Test: swift test --package-path apps/ios/SWCKit
