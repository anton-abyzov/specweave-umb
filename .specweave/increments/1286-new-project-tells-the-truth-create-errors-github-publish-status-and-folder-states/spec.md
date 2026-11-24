# New project tells the truth: create errors, GitHub publish status and folder states

## Problem

From the New project review of November 10, 2026 (`.specweave/reviews/new-project-2026-11-10/report.html`), in the SpecWithCode app (`specwithcode-dev`). The dialog creates projects correctly, but what it tells the person is often wrong or empty:

1. Every create failure reads the same. `apps/server/src/project/ManagedProjectFolders.ts:87` and `:99` return "Failed to create the project folder." or "Failed to create the project." for a missing parent, no permission, missing git and a failed `git init`; `apps/web/src/hooks/useNewProject.ts:126` shows only that.
2. GitHub publish claims success it did not have. With no first commit the server returns `remote_added` and pushes nothing (`apps/server/src/sourceControl/SourceControlRepositoryService.ts:724`); the toast says "Published to GitHub" (`useNewProject.ts:82-88`). Real failures are flattened to "The source control operation could not be completed." (`SourceControlRepositoryService.ts:139`).
3. The GitHub option disappears with no reason when `gh` is missing or signed out on the chosen machine (`apps/web/src/components/CommandPalette.tsx:3687-3696`), and publishing is skipped silently for an existing folder (`useNewProject.ts:179`).
4. The picker misreports folders. An unreadable folder returns an empty listing (`apps/server/src/workspace/WorkspaceEntries.ts:296`), shown as "No folders inside." and accepted as the location. Symlinked folders never list (`:307`). Git is marked for the first 200 entries only (`:134`), and the "Creates / Uses" footer depends on that mark (`apps/web/src/components/studio/folderBrowser.logic.ts:145`), so it can disagree with what the server does.
5. Creating a project has no sensitive-path guard: New folder refuses `~/.ssh`, `createNamedProject` with that parent does not.
6. After create, nothing happens when the machine has no scratch folder: `apps/web/src/hooks/useHandleNewThread.ts:154-159` returns null, so the dialog closes with no navigation and no message.
7. Machines in the form look alike when they cannot be used: offline, read-only and too-old are all greyed with no reason (`apps/web/src/components/studio/ProjectCreation.tsx:53-59`, `CommandPalette.tsx:3666-3681`). Success toasts name the path but not the machine.

## Scope

In: specific create failure messages end to end; publish result handling and messages; a reason when the GitHub option is unavailable; unreadable and symlinked folders in the picker; the footer agreeing with the server; the sensitive-path guard on create; a message when navigation is skipped; per-machine reasons in the machine row; the machine in the success toast.

Out: the sidebar ordering of a new project (known issue, with 1272); SpecWeave on an existing folder (1275); a public repository option; the picker's layout and motion (1272); the small text fixes handed to the 1272 thread (README link, stale fixtures).

## Acceptance Criteria

- [ ] AC-01: A failed create shows the cause and the folder: parent folder missing, no permission to write there, git not installed on that machine, `git init` failed (with git's message), name could not be claimed after 100 tries. Each names the machine when it is not this device.
- [ ] AC-02: After publish, the toast matches the result: "Published to GitHub" only when the push happened; a warning "Repository created, nothing pushed yet" with the reason when the status is `remote_added`.
- [ ] AC-03: A failed publish shows the provider's reason: name already taken, not signed in to GitHub on that machine, no permission to create in that account, network. No "could not be completed" text for these.
- [ ] AC-04: When the GitHub option cannot be offered, the row is shown disabled with the reason and the fix ("Sign in to GitHub on <machine>: gh auth login"), instead of being absent. For an existing folder the dialog says before create that publishing applies to new repositories only.
- [ ] AC-05: An unreadable folder shows "You do not have permission to read this folder on <machine>." and cannot be created into; the server returns a typed permission error instead of an empty listing.
- [ ] AC-06: Symlinks to folders list as folders, marked as links; a broken link is left out.
- [ ] AC-07: The footer's "Creates" or "Uses" matches the server's decision for a `.git` file (worktree or submodule), a child `.specweave`, and a child beyond the first 200 entries. The server answers the question for the selected folder instead of the client inferring it from marks.
- [ ] AC-08: Creating a project under a denied folder (`~/.ssh`, the app's state folder and the others `createDirectory` refuses) fails with the same refusal text as New folder.
- [ ] AC-09: When the project is created and the app cannot open it, a toast says the project exists, where, and how to open it; the dialog never closes silently.
- [ ] AC-10: Each machine in the Machine row that cannot be chosen shows why on hover and for assistive tech: offline, read-only access, needs a newer SpecWithCode.
- [ ] AC-11: Success toasts name the machine when the project is not on this device, and "Opened … in its existing folder" uses the existing project's title.

## Approach

1. Contracts: a typed create error with a `reason` union on `project.createNew` and a typed permission error on `filesystem.browse`; an optional `outcome` on a browse of one folder (`creates` or `uses`). All optional for mixed-version fleets.
2. Server: `ManagedProjectFolders.ts` maps each failure to its reason and applies the same denied-folder check as `WorkspaceEntries.ts`; `WorkspaceEntries.ts` stops swallowing EACCES/EPERM, follows directory symlinks with a realpath check, and reports the outcome for the browsed folder; `SourceControlRepositoryService.ts` passes the provider error through.
3. Web: `useNewProject.ts` reads the reason and the publish status; `CommandPalette.tsx` and `ProjectCreation.tsx` carry a per-machine reason and the disabled GitHub row; `FolderBrowser.tsx` shows the permission state; `useHandleNewThread.ts` returns a typed "not opened" result the caller reports.

Ordering: this touches files the 1272 branch owns. Start after 1272 and 1275 merge.

Rejected: parsing error message text on the client (the browse path already does this with `/does not exist/` at `FolderBrowser.tsx:137`; replace it with the typed error here).

Risks: an older server sends neither reasons nor outcomes, so every new message needs the old text as its fallback.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 The unavailable GitHub option is shown disabled with a reason, not hidden.
- D-02 Directory symlinks are listed; the denied-folder check runs on the resolved path.
- D-03 Repository visibility stays private only.
### Open
- none

## Review items with no AC yet

From the 2026-11-10 New project review (code read on the 1272 branch; the report file is no longer kept). Not checked in the app at HEAD. Whoever picks this increment up either adds an AC and a task for each, or drops it with a reason.

- Checkbox tick is low contrast in both themes (seen in the fixture; check once in the app).
- The name field carries a magnifier icon because the dialog reuses the command palette, so it reads as search.
- Create is an outline button while the hand-off dialog uses a filled primary; the main action is the quietest control.
- At 390 px the footer's "Navigate" and "Esc Close" hints mean nothing on touch and cover the Options heading until scrolled.
- Folder copy for a non-Git folder leaves out anything named like build output (`out`, `build`, `bin`, `dist`) by default and shows only a count (`apps/server/src/fleet/folderTransfer/classify.ts`). Belongs with 1285 if that increment owns folder copy.

## Review items with no AC yet (decided 2026-11-12)

- Name field magnifier: replaced with a folder icon in the New project form.
- Create as filled primary: dropped. `ProjectCreationAction.tsx` already renders a filled primary button; only the fixture's stand-in was outline.
- Footer "Navigate" and "Esc Close" hints: hidden below the small breakpoint in form mode.
- Checkbox tick contrast: fixed; the tick now uses the primary foreground color in both themes.
- Folder copy build-output names: handled in 1285 (the agent copy lists left-out rebuildable folders for non-Git folders).

## Tasks

### T-01 Contracts: create error reasons, browse permission error, folder outcome
- AC: AC-01, AC-05, AC-07 | Files: packages/contracts/src/project.ts, packages/contracts/src/filesystem.ts, packages/contracts/src/filesystem.test.ts | Test: bun run --cwd packages/contracts test filesystem project

### T-02 Server: specific create failures and the denied-folder guard
- AC: AC-01, AC-08 | Files: apps/server/src/project/ManagedProjectFolders.ts, apps/server/src/project/ManagedProjectFolders.test.ts | Test: bun run --cwd apps/server test ManagedProjectFolders

### T-03 Server: unreadable folders, symlinks, folder outcome
- AC: AC-05, AC-06, AC-07 | Files: apps/server/src/workspace/WorkspaceEntries.ts, apps/server/src/workspace/WorkspaceEntries.test.ts | Test: bun run --cwd apps/server test WorkspaceEntries

### T-04 Server: publish errors keep their reason
- AC: AC-03 | Files: apps/server/src/sourceControl/SourceControlRepositoryService.ts, apps/server/src/sourceControl/SourceControlRepositoryService.test.ts | Test: bun run --cwd apps/server test SourceControlRepositoryService

### T-05 Web: create, publish and open toasts
- AC: AC-01, AC-02, AC-03, AC-09, AC-11 | Files: apps/web/src/hooks/useNewProject.ts, apps/web/src/hooks/useNewProject.test.tsx, apps/web/src/hooks/useHandleNewThread.ts | Test: bun run --cwd apps/web test useNewProject

### T-06 Web: machine reasons, GitHub row, picker states
- AC: AC-04, AC-05, AC-06, AC-07, AC-10 | Files: apps/web/src/components/CommandPalette.tsx, apps/web/src/components/studio/ProjectCreation.tsx, apps/web/src/components/studio/ProjectCreation.test.tsx, apps/web/src/components/studio/FolderBrowser.tsx, apps/web/src/components/studio/folderBrowser.logic.ts, apps/web/src/components/studio/folderBrowser.logic.test.ts | Test: bun run --cwd apps/web test ProjectCreation folderBrowser.logic NewProjectFolderPicker

### T-07 Headless fixture: error and disabled states in both themes
- AC: AC-04, AC-05, AC-10 | Files: apps/web/tests/project-folder-choice/main.tsx, apps/web/tests/project-folder-choice/mocks.ts, apps/web/tests/project-folder-choice/verify.mjs | Test: PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never node apps/web/tests/project-folder-choice/verify.mjs
