# Whiteboard quick access and post claims: hotkey, palette, subfolders, no list cap

## Problem

On November 27, 2026 the owner asked how to get into the whiteboard (Excalidraw) easily from the UI, by a mode or a hotkey, and noted that the only route, Artifacts › **+** › Whiteboard on the project page, is hard to find. They also want to post: "Why pay for Excalidraw when you could have as many files as you want with full navigation, organize it in folders or a better structure as you like, with artifacts, or store it on your computer?"

The app as of v1.0.454 (checked against a scratch server):

- No hotkey, no command palette entry and no slash command makes or opens a whiteboard.
- **Unlimited files:** boards on disk have no limit, but the Library listed only the 120 newest files in `.specweave/reports` and `.specweave/artifacts` combined. With 150 boards and 130 reports, older boards disappeared from the list.
- **Folders:** `.specweave/artifacts` was read one level deep. A board in `.specweave/artifacts/team/q4/` opened by path but was never listed.
- A board made with **+** was not listed until the page was reloaded.
- With focus on the whiteboard view's own toolbar (PNG/SVG buttons), Cmd+Z ran the app's thread undo and Cmd+A selected the page text instead of acting in the editor.

## Scope

In: the `whiteboard.new` hotkey; a palette entry; listing boards in subfolders and beyond the report limit; a subfolder tag on each row; a Library refresh after New; editor keys forwarded from the view's toolbar.

Out: a create-folder or move UI in the app (folders are made in Finder, Explorer or a file manager, or by the agent); a `/whiteboard` composer command; proof on an installed Windows or Linux app.

## Acceptance Criteria

- [x] AC-01: On a project page, Cmd+Option+W on a Mac and Ctrl+Alt+W on Windows and Linux make an empty `.excalidraw` file in `.specweave/artifacts/` and open it in the editor. The request leaves the URL, so reload and Back make no second board. The shortcut does nothing while a terminal has focus, and AltGr characters never trigger it.
- [x] AC-02: Outside a project page the hotkey opens the command palette on "New whiteboard". The palette lists "New whiteboard" for the project in context with its shortcut, and "New whiteboard in <project>" for every other project when the query asks for a whiteboard. The hotkey is listed and editable in Settings › Keybindings as "Whiteboard: New".
- [x] AC-03: Library › Artifacts lists boards and other office files in `.specweave/artifacts` and its subfolders up to 4 levels deep, hidden folders excluded, under their own limit of 2,000, apart from the 120 newest reports. Each row in a subfolder shows the subfolder (for example `team/q4`).
- [x] AC-04: A board made by the hotkey, the palette or **+** is listed in the Library at once.
- [x] AC-05: With focus on the whiteboard view's toolbar, Cmd/Ctrl+Z, Cmd/Ctrl+Shift+Z, Ctrl+Y and Cmd/Ctrl+A act in the editor and never reach the app's thread undo or select the page text. Typing in an input keeps its own keys.

## Approach

- `packages/contracts` and `packages/shared` keybindings: `whiteboard.new`, default `mod+alt+w` when `!terminalFocus`. Not `mod+shift+w`: browsers close the window on it before the page sees the key. Same pattern as `design.open` (⌥⌘D).
- New `apps/web/src/components/office/whiteboard/quickWhiteboard.tsx`: the global shortcut listener, the palette match, and the `?new=whiteboard` one-shot deep link on the project page. The deep link waits for this window's write access, makes the board with `useCreateWhiteboard`, opens it with `useArtifactOpener` and strips the param (same pattern as `?pane=`).
- `CommandPalette.tsx`: the entries; `ProjectWorkspaceSurface.tsx`: mounts the deep link; `ProjectArtifactShelf.tsx`: `onCreated` refreshes the Library.
- `apps/server/src/project/ProjectLibrary.ts`: office folders are collected separately at depth 4, and office files get their own 2,000 limit.
- `projectArtifacts.ts` `artifactSubfolder` + `ProjectArtifactsLibrary.tsx` tag.
- `bridge.ts` / `WhiteboardCanvas.tsx` / `WhiteboardView.tsx`: a `key` call on the frame api; the view claims editor keys in the capture phase when focus is in the view and not in an editable field, and dispatches them in the frame, where Excalidraw handles keys globally.

Rejected: a "whiteboard mode" toggle (a mode adds state without saving a step); `mod+shift+w` (closes the browser window).

## Decisions

### Asked
- none (the coordinator asked for a recommendation and implementation)
### Defaulted (change any before sw-do)
- D-01: The hotkey is ⌥⌘W / Ctrl+Alt+W, editable in Settings. Reversible.
- D-02: The office file limit is 2,000 newest; reports stay at 120. Reversible.
- D-03: Folder create and move stay outside the app for now. Reversible.
### Open
- none

## Tasks

### T-01 whiteboard.new hotkey and palette entry
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/keybindings.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/keybindings.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/whiteboard/quickWhiteboard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/whiteboard/quickWhiteboard.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/CommandPalette.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectPaneThreads.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/web/src/components/office/whiteboard/quickWhiteboard.test.ts

### T-02 Every board listed, subfolders tagged, refresh after New
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectLibrary.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectLibrary.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectArtifacts.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ProjectArtifactsLibrary.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ProjectArtifactShelf.tsx | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/project/ProjectLibrary.test.ts

### T-03 Editor keys from the view's toolbar
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/office/whiteboard/bridge.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/whiteboard/frame/WhiteboardCanvas.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/whiteboard/WhiteboardView.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/office-whiteboard/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/office-whiteboard/shoot.mjs | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/web/src/components/office/whiteboard/quickWhiteboard.test.ts
