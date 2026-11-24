# Rename sidebar chats by double click

## Problem

In the SpecWithCode sidebar, double-clicking a project renames it in place, but double-clicking a chat in the Chats section does nothing more than open it (screenshot October 20, 2026). The user expects chats to rename the same way. The legacy sidebar and the project thread header already rename threads through `thread.meta.update`; the default sidebar (`StudioSidebar`) had no rename at all.

## Scope

In: chat rows of the default sidebar's Chats list in `anton-abyzov/specwithcode-dev` (`apps/web/src/components/studio/shell/`), sharing the project row's in-place name editor, with unit, headless fixture and real-server checks. Out: renaming the "Chats" section heading, the legacy sidebar, project rename behaviour, server-side title rules.

## Acceptance Criteria

- [ ] AC-01: Double-clicking a person-started chat in the Chats list turns its title into a focused, selected text field in the row's place; a single click still only opens the chat.
- [ ] AC-02: Enter saves the trimmed new title through `thread.meta.update`; leaving the field saves a valid new title; Escape cancels and saves nothing; an unchanged title saves nothing; a blank title is refused in place ("Enter a name.") and Enter keeps the field open.
- [ ] AC-03: A refused save keeps the field open with the server's reason; focus returns to the row after Enter or Escape; live updates to other chats do not close the field.
- [ ] AC-04: The row menu offers Rename, which opens the same field with focus; chats a coordinator named (agent-created, subagents) and environments without operate scope offer no rename and a double click only opens them.
- [ ] AC-05: The new title persists: it survives a page reload and a restart of a real built server on a private home (headless).

## Approach

`ProjectNameEditor` becomes `SidebarNameEditor` (icon and field label passed in) and is reused by a new `SidebarChatRow`. `StudioSidebar` builds a `{check, commit}` rename for each chat unless `isCoordinatorNamedThread` or the operate scope says otherwise; `checkChatTitle` validates, `commit` dispatches `threadEnvironment.updateMetadata` and returns the failure message. The menu's Rename starts the edit once the menu has finished closing, because a closing menu returns focus to its item and would blur the field.

## Decisions

### Asked
- none
### Defaulted
- D-01: "Chats" in the request means each chat row, not the section heading (coordinator brief).
- D-02: No length cap beyond the server's; chat titles have none today, unlike project names.

## Tasks

### T-01 Chat rows rename in place
- AC: AC-01, AC-02, AC-03, AC-04 | Files: apps/web/src/components/studio/shell/SidebarChatRow.tsx, apps/web/src/components/studio/shell/SidebarChatRow.rename.test.tsx, apps/web/src/components/studio/shell/SidebarProjectList.tsx, apps/web/src/components/studio/shell/StudioSidebar.tsx, apps/web/src/components/studio/shell/shell.css, apps/web/src/studio/threadTitles.ts | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/shell/SidebarChatRow.rename.test.tsx apps/web/src/components/studio/shell/SidebarProjectList.rename.test.tsx apps/web/src/components/studio/shell/StudioSidebar.test.tsx

### T-02 Headless fixture, real-server persistence, PR and merge
- AC: AC-03, AC-04, AC-05 | Files: apps/web/tests/sidebar-stable-order/vite.config.ts, apps/web/tests/sidebar-stable-order/main.tsx, apps/web/tests/sidebar-stable-order/mocks.tsx, apps/web/tests/sidebar-stable-order/rename.mjs | Test: node apps/web/tests/sidebar-stable-order/rename.mjs

### T-03 Verify and close 0959
