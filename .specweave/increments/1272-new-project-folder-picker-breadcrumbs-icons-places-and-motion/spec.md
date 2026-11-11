# New project folder picker: breadcrumbs, icons, places and motion

## Problem

Anton, November 10, 2026, on the New project dialog in the SpecWithCode app (`specwithcode-dev`):

1. "Up one folder, not nice animations." The location step is a plain text list: no icons, no motion, an "Up one folder" row, a path field plus a Browse button, and the same path printed three times.
2. "I should be able to create a folder here, right?" There is no way to make a new parent folder from the picker, on this device or a remote machine.
3. "Why does it always select M1 when I want to create a new project on this M4 machine?" PR #85 made this device the default only for the direct New project action. Two paths still pick another machine:
   - `apps/web/src/components/CommandPalette.tsx:1253-1263`: Add project defaults to `currentExecutionEnvironmentId` (the open thread's or project's machine), and New project inside that view inherits it (`CommandPalette.tsx:1893`).
   - `apps/web/src/studio/projectCreation.ts:78-82`: "this device" means the `PrimaryConnectionTarget` only (`apps/web/src/state/primaryEnvironment.ts:5`). When this device is a desktop-local target the primary is null or another machine, and the fallback is the open thread's machine.
   Nothing is stored: there is no saved default machine. Load balancing (`client-settings.json`, off on m4) is the only setting that can change it.
4. The default folder on every machine is app state: `apps/server/src/project/ManagedProjectFolders.ts:456` sets it to `<baseDir>/projects`, shown as `~/.specwithcode/m1/projects`.
5. Copy is unclear: "Use this folder" creates the project subfolder inside the chosen parent, but the dialog reads as if the folder itself becomes the project.

## Scope

In: the folder picker in the New project and clone-destination steps, the shared remote folder browser used by handoff, a create-folder RPC, repo and project marks in browse results, suggested places, the default machine rule and its visible reason, the default projects folder, copy.

Out: the Add existing project browse list in the palette, load balancing behaviour for new threads, mobile apps, moving existing projects out of `<baseDir>/projects`.

## Acceptance Criteria

- [ ] AC-01: The picker shows the current folder as a breadcrumb; each segment is a button that opens that folder; long paths collapse the middle behind a "…" button that expands them in place; there is no "Up one folder" row and the path is not repeated elsewhere in the panel.
- [ ] AC-02: Every row has an icon from lucide-react: folder, Git repository (`FolderGit2Icon`), and a mark plus the project's name when the folder is already a SpecWithCode project on that machine. No brain or lock icons.
- [ ] AC-03: A Places strip offers the projects folder, recent project parents on that machine (up to 3, from existing projects and remembered choices) and Home; one click opens the place.
- [ ] AC-04: Opening a folder animates the list (direction follows going deeper or back); rows and the new-folder row expand smoothly; with `prefers-reduced-motion: reduce` every transition is instant.
- [ ] AC-05: Keyboard: Up/Down move through rows, Right or Enter opens, Left or Backspace goes to the parent, typing letters jumps to a matching row, `/` or Cmd+L edits the path as text, Escape leaves path edit before it closes the dialog. Focus is visible and the list is a labelled listbox.
- [ ] AC-06: "New folder" adds an inline row with a name field in the current folder; Enter creates it on the selected machine and opens it; Escape cancels. Empty names, `.`/`..`, path separators, names over 255 bytes, Windows-reserved characters on Windows hosts and existing names are refused with a specific message before or after the call.
- [ ] AC-07: Create folder works on a remote machine (linux-mini, m1) through a new RPC; on a server that predates it the action is hidden, never an error.
- [ ] AC-08: The panel says where the project will be made in one line that updates live: "Creates `<parent>/<slug>`", or "Uses `<folder>` as the project" when the chosen folder is already one. The folder shown is the choice, so there is no "Use this folder" step; the dialog's own Create project button creates it. The old helper paragraph is gone.
- [ ] AC-09: New project preselects this device on every entry path, whatever thread, project or coordinator is open, unless load balancing is on. The person's pick in the dialog holds until it closes and is never remembered across opens.
- [ ] AC-10: The Machine section states why the selection is what it is: "This device", "Chosen by load balancing" (with a link to that setting), or "This device is not available: <reason>".
- [ ] AC-11: The default folder on each machine is its normal projects folder: the first that exists of `~/Projects`, `~/projects`, `~/Developer`, `~/dev`, `~/code`, `~/src`, `~/repos`; otherwise `~/Projects`, made on first use. Older servers keep their reported root; projects already in `<baseDir>/projects` stay where they are.
- [ ] AC-12: The same picker runs on m4, linux-mini and m1 with identical behaviour; loading shows row skeletons, a missing folder offers the nearest existing parent, a permission error names the folder and machine.
- [ ] AC-13: #85 holds: this device by default, the machine named in the picker, SpecWeave on by default, the dialog scrolls. Existing tests for those pass unchanged or with copy-only updates.
- [ ] AC-14: `RemoteFolderBrowser` (handoff) uses the same list, breadcrumb and icons, so the two do not drift.
- [ ] AC-15: A project made from New project is listed and selected in the sidebar on this device at once: it leads the "updated" sort from its creation time, and the project of the open draft or thread is listed even past the first 12 projects.
- [ ] AC-16: Binding an existing folder with "Use SpecWeave" on sets SpecWeave up when the folder has no `.specweave`, and says so; a failure is reported with the retry place. An empty, unregistered folder named like the project becomes a full new project (Git, README, icon, SpecWeave, first commit). This is the existing-folder piece of 1275, moved here.
- [ ] AC-17: A folder the machine's account may not list is named as unreadable with the machine, and is never the chosen folder.

## Approach

1. Contracts (`packages/contracts/src/filesystem.ts`, `rpc.ts`, `server.ts`): optional `kind: "folder" | "git"` on `FilesystemBrowseEntry`; optional `places` on `FilesystemBrowseResult` (home, projects folder); new `filesystem.createDirectory` RPC with a typed error (`exists`, `invalid_name`, `permission_denied`, `parent_missing`); optional `suggestedProjectsRoot` on `ServerConfig`. All optional, so mixed-version fleets keep working.
2. Server (`apps/server/src/workspace/WorkspaceEntries.ts`): mark Git repos with a bounded `stat` of `<child>/.git` (cap 200 entries, parallel 16); `createDirectory` with name validation and the sensitive-path guard; resolve the suggested projects root. The `ws.ts` handler goes in without new imports there (TS2589 limit): route through the existing `WorkspaceEntries` service.
3. Web: new `apps/web/src/components/studio/FolderBrowser.tsx` (breadcrumb, places, list, new-folder row, keyboard) and `folderBrowser.logic.ts` (path segments, type-ahead, name validation; pure, unit-tested). `NewProjectFolderPicker.tsx` and `RemoteFolderBrowser.tsx` become thin wrappers. Existing projects are matched client-side from the project list by machine and workspace root.
4. Motion: CSS only, 140-180 ms, transform and opacity, `AnimatedHeight` for expand, all behind `motion-safe:`. No new dependency.
5. Machine default: a `thisDeviceEnvironmentId` derived with `isThisMachineTarget` replaces `primaryEnvironmentId` in `suggestProjectMachine` and in the Add project to New project path; `suggestProjectMachine` returns the reason with the id.
6. Custom glyphs: none planned; lucide has every icon needed. Kie.ai only if a mark turns out to be missing.

Rejected: a native dialog for remote machines (cannot see their disks); a tree view (deeper nesting than the dialog's width holds); changing `namedProjectsRoot` itself (existing projects live there).

Risks: `.git` stats on slow network mounts (bounded and time-boxed at 300 ms, falling back to plain folders); copy changes touch `themeContrastClasses.test.ts` and the two fixture harnesses.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Breadcrumb plus single list, not a tree or columns.
- D-02 Default projects folder is detected per machine (AC-11), not a new setting.
- D-03 The machine pick is never remembered; load balancing stays the only override.
- D-04 No second button in the location panel: the folder shown is the choice and the dialog's Create project button acts on it.
- D-05 create-folder uses the same permission as creating a project (`orchestration:operate`).
### Open
- none

## Tasks

### T-01 Contracts: entry kind, places, createDirectory, suggested root
- AC: AC-02, AC-07, AC-11 | Files: packages/contracts/src/filesystem.ts, packages/contracts/src/rpc.ts, packages/contracts/src/server.ts, packages/contracts/src/filesystem.test.ts | Test: bun run --cwd packages/contracts test filesystem

### T-02 Server: Git marks, create folder, suggested projects root
- AC: AC-02, AC-06, AC-07, AC-11 | Files: apps/server/src/workspace/WorkspaceEntries.ts, apps/server/src/workspace/WorkspaceEntries.test.ts, apps/server/src/ws.ts, apps/server/src/project/ManagedProjectFolders.ts | Test: bun run --cwd apps/server test WorkspaceEntries ManagedProjectFolders

### T-03 Folder browser logic: segments, type-ahead, name validation
- AC: AC-01, AC-05, AC-06 | Files: apps/web/src/components/studio/folderBrowser.logic.ts, apps/web/src/components/studio/folderBrowser.logic.test.ts | Test: bun run --cwd apps/web test folderBrowser.logic

### T-04 FolderBrowser component: breadcrumb, places, icons, list, new folder, motion
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-12 | Files: apps/web/src/components/studio/FolderBrowser.tsx, apps/web/src/components/studio/NewProjectFolderPicker.test.tsx | Test: bun run --cwd apps/web test NewProjectFolderPicker

### T-05 Wire the picker and handoff browser, new copy
- AC: AC-08, AC-13, AC-14 | Files: apps/web/src/components/studio/NewProjectFolderPicker.tsx, apps/web/src/components/studio/NewProjectFolderPicker.test.tsx, apps/web/src/components/studio/RemoteFolderBrowser.tsx, apps/web/src/components/studio/HandoffFolderPicker.test.tsx, apps/web/src/hooks/useProjectFolderChoice.tsx, apps/web/src/components/studio/ProjectCreation.tsx, apps/web/src/themeContrastClasses.test.ts | Test: bun run --cwd apps/web test NewProjectFolderPicker HandoffFolderPicker ProjectCreationAction themeContrastClasses

### T-06 Default machine is this device, with the reason shown
- AC: AC-09, AC-10, AC-13 | Files: apps/web/src/studio/projectCreation.ts, apps/web/src/studio/projectCreation.test.ts, apps/web/src/components/CommandPalette.tsx, apps/web/src/components/studio/ProjectCreation.tsx | Test: bun run --cwd apps/web test projectCreation

### T-07 Headless end-to-end check, local and remote, with screenshots
- AC: AC-04, AC-12, AC-13 | Files: apps/web/tests/project-folder-choice/verify.mjs, apps/web/tests/project-folder-choice/mocks.ts, apps/web/tests/machine-folders/verify.mjs | Test: node apps/web/tests/project-folder-choice/verify.mjs && node apps/web/tests/machine-folders/verify.mjs

### T-08 New project shows and is selected in the sidebar
- AC: AC-15 | Files: apps/web/src/components/sidebar/SidebarProjectTree.logic.ts, apps/web/src/components/sidebar/SidebarProjectTree.tsx, apps/web/src/components/sidebar/SidebarProjectTree.logic.test.ts, apps/web/src/components/Sidebar.tsx | Test: bun run --cwd apps/web test SidebarProjectTree

### T-09 SpecWeave on an existing folder, empty folder becomes a full project
- AC: AC-16 | Files: apps/server/src/project/ManagedProjectFolders.ts, apps/server/src/project/ManagedProjectFolders.test.ts, packages/contracts/src/project.ts, apps/web/src/hooks/useNewProject.ts, apps/web/src/components/studio/folderBrowser.logic.ts | Test: bun run --cwd apps/server test ManagedProjectFolders

### T-10 Review fixes: unreadable folders, write guard, listbox, reason link, remembered place
- AC: AC-03, AC-05, AC-06, AC-08, AC-10, AC-17 | Files: apps/server/src/workspace/WorkspaceEntries.ts, apps/server/src/workspace/WorkspaceEntries.test.ts, packages/contracts/src/filesystem.ts, packages/contracts/src/filesystem.test.ts, apps/web/src/components/studio/FolderBrowser.tsx, apps/web/src/hooks/useProjectFolderChoice.tsx, apps/web/src/hooks/useProjectFolderChoice.test.ts, apps/web/src/studio/projectCreation.ts, apps/web/src/components/studio/ProjectCreation.tsx | Test: bun run --cwd apps/server test WorkspaceEntries
