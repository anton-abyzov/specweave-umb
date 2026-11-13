# Each machine's project copies are visible: sidebar tag for projects not on this device, per-machine folders in settings, copy-first Add to another machine

## Problem

The sidebar lists every project from every linked machine the same way. On M4, projects that exist only on M5 (firstproject and others) look identical to ones with a folder on M4, so Anton cannot tell what this machine can run locally (screenshot, November 13, 2026). `sidebarProjectGrouping.ts` already computes `environmentPresence` ("remote-only") and the machine labels, but `SidebarProjectList.tsx` never shows them. Project settings show only the viewed copy's folder. In Add to another machine, "Copy files instead" hides under More options even for a project with no Git remote, where copying is the only way, and the dialog text is long.

## Scope

In: sidebar tag, muted name and tooltip for projects with no copy on this device, plus "Add to this machine…"; Add to another machine share view with both choices always visible, copy first where there is no remote or nested repositories, one short line per choice and details in hints; Browse beside the destination folder; Project settings > General lists each machine's folder with Change… for connected machines and a missing-folder state.
Out: OrchestratorSwitcher.tsx (owned by another thread), server changes, the Move flow (PR #327 owns it).

## Acceptance Criteria

- [ ] AC-01: A sidebar project with no copy on this device shows a machine tag with the machine nickname (chat-row style), its name is muted, and its tooltip says "Runs on {machine}. No copy on this device."; projects with a copy here show no tag.
- [ ] AC-02: That row's menu has "Add to this machine…", which opens the existing Add to another machine flow with this device as the destination (clone when the project has a Git remote, folder copy review when it has none).
- [ ] AC-03: The Add to another machine share view shows "Copy files instead" as a visible choice for every project, not under More options; with no Git remote or with nested repositories the copy choice is primary.
- [ ] AC-04: Share view text is one short line per choice; longer explanations sit in a hint reachable by hover, keyboard focus and touch; data-loss warnings (uncommitted files) stay visible.
- [ ] AC-05: Add to another machine's destination folder has a Browse button that browses the target machine.
- [ ] AC-06: Project settings > General titles the folder row "Project folder on {machine}" and lists the project's other copies as "{machine} {folder}", each with Change… enabled only while that machine is connected (reason shown otherwise).
- [ ] AC-07: A listed copy whose connected machine reports its folder missing shows "Folder missing" with Relink…; unknown or offline stays silent.
- [ ] AC-08: The released build shows AC-01..AC-04 and AC-06 in headless screenshots at desktop and 390 px widths.

## Approach

Web only, in `repositories/anton-abyzov/specwithcode-dev/apps/web/src` (the nested `specwithcode` checkout is held by PR #321's thread, so commits are built out of tree from `origin/main` with a temporary index and a scratch work tree; heavy checks run in the `specweave-studio checks copy`).

1. Sidebar: a pure helper `remoteOnlyMachines` beside `sidebarProjectGrouping.ts`; `ProjectRow` renders the tag with the `sws-row-machine` style and `data-elsewhere` mutes the label. "Add to this machine…" mounts the existing `AddToMachineDialog` (Git remote) or `DraftFolderCopy` (no remote) with `usePrimaryEnvironmentId()` as destination, so no project-page plumbing and no overlap with PR #327.
2. Share view (`HandoffShare.tsx`): the two choices become a visible pair; order by `addToMachineRoute` and nested repositories; long notes move into an `InfoHint` (Popover trigger button, works by keyboard and touch).
3. `AddToMachineDialog.tsx`: Browse button reusing `RemoteFolderBrowser`/`HandoffFolderPicker`.
4. `ProjectFolderChange.tsx` / `ProjectWorkspaceSettings.tsx`: other copies list reusing `ProjectMachinesSettings` row data and `useProjectFolderHealth` per environment.

Rejected: greying rows out completely and making them inert. The row still opens and runs on the other machine; muting plus the tag says it without losing that.

## Decisions

### Asked
- D-01 Grey out or tag? → Anton asked for "greyed out or some sign"; the approved brief said tag, not inert. Both: muted name plus tag, row still works.
### Defaulted (change any before sw-do)
- D-02 New strings in files that already use `tx` go through `tx` with all 8 phrase catalogs; `HandoffShare.tsx` keeps its existing plain-English convention.
- D-03 PR body carries no session or AI attribution (owner's git rule overrides the brief's attribution header).
### Open
- none

## Tasks

### T-01 Sidebar tag, muted name and Add to this machine
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/SidebarProjectList.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/shell.css, repositories/anton-abyzov/specwithcode-dev/apps/web/src/sidebarProjectGrouping.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/SidebarProjectList.test.tsx | Test: bash /Users/antonabyzov/.specwithcode/m4/scratch/2026-11-13-per-machine-folders/web-test.sh src/components/studio/shell/SidebarProjectList src/sidebarProjectGrouping

### T-02 Share view: both choices visible, copy first without a remote, short text with hints
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/HandoffShare.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/HandoffShare.test.tsx | Test: bash /Users/antonabyzov/.specwithcode/m4/scratch/2026-11-13-per-machine-folders/web-test.sh src/components/studio/HandoffShare

### T-03 Browse beside the destination folder
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/AddToMachineDialog.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/AddToMachineDialog.test.tsx | Test: bash /Users/antonabyzov/.specwithcode/m4/scratch/2026-11-13-per-machine-folders/web-test.sh src/components/chat/AddToMachineDialog

### T-04 Project folder on each machine in Project settings
- AC: AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/ProjectFolderChange.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/ProjectFolderChange.test.tsx | Test: bash /Users/antonabyzov/.specwithcode/m4/scratch/2026-11-13-per-machine-folders/web-test.sh src/components/studio/ProjectFolderChange

### T-05 Released build check
- AC: AC-08 | Files: .specweave/increments/1319-each-machines-project-copies-are-visible-sidebar-tag-for-projects-not-on-this-device-per-machine-folders-in-settings-copy-first-add-to-another-machine/reports/ | Test: ls .specweave/increments/1319-each-machines-project-copies-are-visible-sidebar-tag-for-projects-not-on-this-device-per-machine-folders-in-settings-copy-first-add-to-another-machine/reports/*.png

### T-06 Verify and close 1319
- AC: AC-08 | Files: .specweave/increments/1319-each-machines-project-copies-are-visible-sidebar-tag-for-projects-not-on-this-device-per-machine-folders-in-settings-copy-first-add-to-another-machine/spec.md | Test: specweave verify 1319
