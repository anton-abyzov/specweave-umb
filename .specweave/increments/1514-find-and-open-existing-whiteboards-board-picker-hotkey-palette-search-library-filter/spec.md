# Find and open existing whiteboards: board picker hotkey, palette search, Library filter

## Problem

The owner asked on November 27, 2026: "How to find existing whiteboard items? Scrolling through the artifact is not an easy way. If I click a plus sign, it's a great new one, but what about existing ones?"

As of v1.0.457 (increment 1506):

- Cmd+Option+W / Ctrl+Alt+W always made a new, empty board, so every press of the hotkey wrote another file.
- Cmd+K offered "New whiteboard" only and could not find a board by name.
- To reach an existing board you scrolled the Artifacts row card by card, or opened Library › Artifacts, where boards were mixed in with documents under the "Documents" type.

## Scope

In: a Whiteboards picker on the existing hotkey; finding boards by name in Cmd+K; a one-shot `?open=<path>` page request; a Whiteboards type in the Library filter.

Out: boards in another project than the one in context (the picker lists the project in view; others stay one project switch away); boards only in a thread's worktree; renaming or moving boards.

## Acceptance Criteria

- [x] AC-01: Cmd+Option+W on a Mac and Ctrl+Alt+W on Windows and Linux open a Whiteboards picker in the palette. "New whiteboard" is the first row, so Enter makes a board as before. Below it are the project's boards, newest first, each with its folder and age. The command id stays `whiteboard.new`, so saved keybinding configs are unchanged.
- [x] AC-02: Typing in the picker filters boards by words of their name or folder. Picking a board opens it in the editor, and Previous/Next step through the project's boards only.
- [x] AC-03: Typing a board's name in Cmd+K lists it under "Whiteboards" (8 at most), and Cmd+K has a "Whiteboards…" entry, shown with the hotkey, that opens the picker.
- [x] AC-04: `?open=<path>` on a project page opens the board once, then leaves the URL. A reload or Back never opens it again. Only a project-relative `.excalidraw` path is accepted: absolute paths, drive letters, backslashes, `.`/`..` and control characters are refused. Names with spaces and `#` work.
- [x] AC-05: Library › Artifacts › Type has "Whiteboards", which lists boards only.

## Approach

- `quickWhiteboard.tsx`: `whiteboardsInLibrary` and `useProjectWhiteboards` read the same `projectWorkspace.library` snapshot the project page reads. Older servers send no `outputs`, so they list no boards and New still works. `openWhiteboardDestination` builds the `?open=` navigation. `useWhiteboardDeepLink` takes both `?new=` and `?open=`; `?open=` waits for the artifacts to load. The shortcut now opens the picker through the palette bus.
- New `whiteboardPalette.ts`: the board rows and the root search limit, so `CommandPalette.tsx` (already 4,567 lines) only gains call sites, the open intent and the picker view. The picker follows the existing open-intent and view pattern (`new-thread-in`, `change-theme`).
- `projectPaneThreads.ts`: `safeWhiteboardPath` and the `open` parse.
- `projectArtifacts.ts`: the `whiteboards` type filter.

Rejected: a second hotkey for the picker (two keys to learn, and the one-key path to a new board survives as ⌥⌘W then Enter); a new command id (it would clash with defaults the server already backfilled).

## Decisions

### Asked
- none (the coordinator's recommended default, taken)
### Defaulted (change any before sw-do)
- D-01: ⌥⌘W opens the picker instead of making a board; a new board is ⌥⌘W then Enter. Reversible.
- D-02: The picker lists the project in context only. Reversible.
### Open
- none

## Tasks

### T-01 Whiteboards picker, palette search and the open request
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/office/whiteboard/quickWhiteboard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/whiteboard/whiteboardPalette.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/whiteboard/quickWhiteboard.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/CommandPalette.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/CommandPalette.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/commandPaletteBus.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectPaneThreads.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/office/whiteboard/quickWhiteboard.test.ts src/components/CommandPalette.logic.test.ts

### T-02 Whiteboards type in the Library filter
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectArtifacts.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/studio/projectArtifacts.test.ts src/components/office/whiteboard/quickWhiteboard.test.ts
