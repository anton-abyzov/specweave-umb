# New project dialog: this device by default, target machine folders, scroll and SpecWeave on

## Problem

On the M4, New project preselected m1, because `suggestProjectMachine` (apps/web/src/studio/projectCreation.ts) put the machine of the open thread or project first. The folder picker then listed m1's folders without naming m1, so the user took them for the M4's.

m1's default folder `/Users/antonabyzov/.specwithcode/m1/projects` is correct: M1's account is `anton`, but its home is `/Users/antonabyzov`. The folder did not exist yet, because the server advertises `<baseDir>/projects` as `newProjectsRoot` and creates it only on the first create without a parent. Browse got ENOENT and showed the generic "Failed to browse filesystem path" error. Creating with that folder as an explicit parent also failed the `stat` check. Any machine that has never created a name-only project has this problem.

The dialog body could not scroll to its last option on macOS. A nested ScrollArea inside the scrolling form panel clipped the list, with `overscroll-contain` and overlay scrollbars on top. "Use SpecWeave" was off by default, and its description was a file list.

## Scope

In: default machine, a machine row at the top of the form, the picker naming its machine, the missing default folder, specific browse errors, one scroller, SpecWeave on by default with plain copy and a disclosure, and the step order name, machine, location, options, create. Out: a general "create folder" RPC for arbitrary paths, and the clone flow's layout beyond naming its machine.

## Acceptance Criteria

- [x] AC-01: New project starts on this device even while a thread or project on another machine is open. Load balancing, when on, still decides.
- [x] AC-02: The machine is chosen in a row at the top of the form. The picker header and listed folder name that machine ("Project location on m1", "<folder> on m1"). Switching machines resets the path and listing to that machine.
- [x] AC-03: The server creates `<baseDir>/projects` at start. A create whose parent is that folder succeeds even when it is missing. The client sends the default folder as no parent, so older servers make it too.
- [x] AC-04: Browse errors say what went wrong (does not exist on m1, is a file, errno code), and a missing default folder is offered as "does not exist yet, made on create" with Use this folder.
- [x] AC-05: The form body scrolls to its last element at 1280x560 with Create pinned. Checked headless on the real built server.
- [x] AC-06: Use SpecWeave is checked by default. Its one-sentence description and a "What Use SpecWeave adds" disclosure state the files and what turning it off loses.

## Approach

`projectCreation.ts` changes the default machine. `ProjectCreation.tsx` adds ProjectMachineChoice, SpecweaveSetupDetails and AddExistingProjectLink, and drops the machine and existing-project groups from the list. `CommandPalette.tsx` handles the wiring, the SpecWeave default and the submit parent. `NewProjectFolderPicker.tsx` and `useProjectFolderChoice.tsx` name the machine and handle the missing default. `autocomplete.tsx`, `CommandPaletteResults.tsx` and `CommandPaletteContent.tsx` make the form a single scroller.

On the server, `ManagedProjectFolders.ts` creates the root at start and treats the root as the implicit parent. `WorkspaceEntries.ts` and `ws.ts` produce the errno messages. In `contracts/filesystem.ts` an optional `message` stays compatible with older clients.

## Decisions

### Asked
- D-01: Default machine → this device; a remembered machine is not kept (user).
- D-02: Use SpecWeave → on by default (user).
### Defaulted (change any before sw-do)
- D-03: With load balancing on, its weights still pick the machine.
- D-04: "Add existing project" moves from the last list row to a link below the options.
### Open
- none

## Tasks

### T-01 Default machine, machine row, picker naming
- AC: AC-01, AC-02 | Files: apps/web/src/studio/projectCreation.ts, apps/web/src/components/studio/ProjectCreation.tsx, apps/web/src/components/studio/NewProjectFolderPicker.tsx, apps/web/src/components/CommandPalette.tsx | Test: npx vp test run apps/web/src/studio/projectCreation.test.ts apps/web/src/components/studio

### T-02 Default folder exists, specific browse errors
- AC: AC-03, AC-04 | Files: apps/server/src/project/ManagedProjectFolders.ts, apps/server/src/workspace/WorkspaceEntries.ts, apps/server/src/ws.ts, packages/contracts/src/filesystem.ts | Test: npx vp test run apps/server/src/project/ManagedProjectFolders.test.ts apps/server/src/workspace/WorkspaceEntries.test.ts packages/contracts/src/filesystem.test.ts

### T-03 Scroll, SpecWeave default and copy, order
- AC: AC-05, AC-06 | Files: apps/web/src/components/ui/autocomplete.tsx, apps/web/src/components/CommandPaletteResults.tsx, apps/web/src/components/CommandPaletteContent.tsx, apps/web/tests/project-folder-choice/integration.mjs | Test: node apps/web/tests/project-folder-choice/integration.mjs (headless, real built server)
