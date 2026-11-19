# Chats without a project: no project settings, chat settings instead

## Problem

Anton, November 19, 2026, on M5: a chat started without a project opens a "Project settings" dialog titled "No project". It offers Name and icon, Project folder `~/.specwithcode/scratch` with Choose and Check, Use worktrees ("This folder holds no Git repository"), Goal and Coordinator model. None of these mean anything for a chat, and some can break things (moving the folder every chat lives in).

What a project-less chat is today (app repo `anton-abyzov/specwithcode`, main `3eafbca0c`):

- Each machine has one hidden Scratch project titled "No project" (`apps/server/src/project/ManagedProjectFolders.ts:466-513`). It is an ordinary `kind: "code"` project; it is told apart only by its folder, `<baseDir>/scratch` (`isScratchWorkspace`, `:185`; client `isScratchProject`, `packages/client-runtime/src/state/projects.ts:139`).
- Every chat gets a folder of its own under it, `<baseDir>/scratch/<date>-<words>-<id>` (`folderForThread`, `:530-559`; `ThreadLaunchService.ts:1240-1258`), pruned after 14 days idle (`scratchPrune.ts`). On linux-mini the scratch folder is a symlink into `/srv`.
- Goal, instructions, project memory, knowledge, coordinator and routines are keyed by project id, so all chats on a machine share one set. Every turn of every chat is sent that project's goal, instructions, memory inventory, `MEMORY.md` and knowledge (`ProjectWorkspaceService.ts:570-668`), and `studio_project_memory_write` from any chat writes into that one shared store (`mcp/toolkits/projectMemory/handlers.ts:18-27`). So two unrelated chats can read each other's notes: a privacy leak waiting for its first memory write.
- Web shows the full code-project dialog for it: the thread menu always lists "Project settings" (`apps/web/src/components/threadActionMenu.logic.ts:383`), and so do the draft menu, the header right-click, the command palette and the shortcut.
- iOS already shows no project settings for a chat (`apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift:591-596,753-764`). The React Native app has no project settings screen.
- Percy is a separate `kind: "personal"` project with its own memory, which is about the person and is shared between that person's machines by design (1269).
- "Move to project…" already adopts a chat into a project in place: same conversation, same folder (`ThreadMoveService.ts:148-175`).

Live data checked on minisforum (November 19, 2026): the Scratch project holds 0 memory files and 0 routines, so hiding them deletes nothing.

## Options

| | A: no project settings, chat settings | B: one shared "Chats" space | C: hybrid |
|---|---|---|---|
| Privacy between unrelated chats | Kept: nothing is shared | Lost: every chat reads every other chat's notes | Kept by default |
| What an agent needs (folder, permissions) | Own folder per chat, machine default access | Shared folder: agents collide in one cwd | Own folder |
| Per-machine scratch, `/srv` on linux-mini | Unchanged | A shared space per machine still differs per machine | Unchanged |
| Overlap with Percy | None: Percy is where things about you live, across machines | Duplicates Percy's memory, but per machine only | None |
| Web, desktop, iOS | Matches iOS, which already shows none | iOS needs a new space screen | Matches iOS |
| Moving into a project later | Existing Move to project, keeps folder | Must untangle what came from the shared memory | Existing Move to project |
| Settings the person sees | Model, folder, machine | Goal, memory, model for a "Chats" space | Same as A plus a link to projects |

B's one real benefit, chats that can see each other's context, is already covered twice: Percy for what is about the person (shared across their machines), and a project for a body of work (Move to project keeps the chat's conversation and folder). B would add a third, weaker memory that is per machine and leaks between topics.

**Recommendation: A**, with the hybrid's pointers: the chat settings view says how to get shared context (move to a project; Percy for things about you). The server stops treating the Scratch project as a context source, so the privacy guarantee does not depend on the UI.

## Scope

In: web (desktop renders the same web UI) and server, in `anton-abyzov/specwithcode`.

Out: iOS (already right), React Native (no such screen), deleting or moving any existing chat folder or data, the scratch folder location, a per-machine "data folder" setting.

## Acceptance Criteria

- [ ] AC-01: A chat's thread menu (sidebar row and chat header) lists "Chat settings" instead of "Project settings" and does not list "Open project in new window"; a project thread's menu is unchanged.
- [ ] AC-02: An unsent chat draft's menus (sidebar draft row, header right-click) offer "Chat settings", never "Project settings".
- [ ] AC-03: The Project settings shortcut and the command palette, used in a chat, open Chat settings ("Chat settings" in the palette); the Project settings dialog never opens for the Scratch project, even from a URL or saved request.
- [ ] AC-04: Chat settings shows the chat's machine, its own folder (with Copy) and its model, says that a chat shares nothing with other chats, and offers Move to project… and Switch model… where the thread supports them.
- [ ] AC-05: The server sends a chat no project goal, instructions, memory or knowledge; it sends one short section saying the chat has no project and shares nothing.
- [ ] AC-06: The server refuses project memory reads, writes and deletes for the Scratch project with a message that names Move to project, lists no memory for it and offers no knowledge search; a goal or instructions saved for it are never sent; existing rows are left in place.
- [ ] AC-07: Before and after headless screenshots of a chat's settings on a seeded server, and an adversarial review by another model family.

## Approach

Server first, then web.

1. `apps/server/src/project/scratchProject.ts` (new): pure `isScratchWorkspaceRoot(baseDir, workspaceRoot)` with the same canonical path rule as `isScratchWorkspace`, so `ProjectWorkspaceService` can use it without the `ManagedProjectFolders` service.
2. `ProjectWorkspaceService.ts`: `contextSnapshot` returns only a `role` section for a Scratch project thread; `readMemory`/`writeMemory`/`deleteMemory` refuse, the memory list is empty, knowledge search and read are unavailable. Goal and instructions are not refused at the command layer (the decider has no scratch root); they are simply never sent.
3. Web: `threadActionMenu.logic.ts` gains `chat-settings` (thread and draft menus); `ChatSettingsDialog.tsx` (new) mounted in `__root.tsx`, opened through a light zustand request in `studio/chatSettingsRequest.ts` so menus do not import the dialog; `useThreadActionMenu.ts`, `Sidebar.tsx` and `StudioSidebar.tsx` draft and row menus, `ChatHeader.tsx`, `ChatView.tsx`, `CommandPalette.tsx`, `ProjectSettingsShortcut.tsx` route chats there; `InPlaceProjectSettings.tsx` and the project page refuse a Scratch project.

Rejected: B (see Options); hiding the menu item without a replacement (the person still needs the chat's folder, model and machine); deleting the Scratch project's memory table rows (data deletion, and there is none today).

Risk: an agent in a chat that relied on scratch memory loses it. There is none on minisforum; other machines keep their rows, unread.

## Decisions

### Asked
- none: A changes no earlier decision of Anton's and deletes or moves no chat data.
### Defaulted (change any before sw-do)
- D-01 Recommendation A over B and C → A, with pointers to Move to project and Percy (reversible: the shared rows are kept).
- D-02 Existing Scratch memory rows → kept in place, not shown to chats (reversible).
- D-03 Chat settings is read-only plus actions (Copy folder, Switch model…, Move to project…); no new per-chat setting is stored.
### Open
- none

## Tasks

### T-01 Server: chats get no shared project context
- AC: AC-05, AC-06 | Files: apps/server/src/project/scratchProject.ts, apps/server/src/project/ProjectWorkspaceService.ts, apps/server/src/project/ProjectWorkspaceService.chat.test.ts | Test: cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/project/ProjectWorkspaceService.chat.test.ts

### T-02 Web: Chat settings replaces Project settings for chats
- AC: AC-01, AC-02, AC-03, AC-04 | Files: apps/web/src/components/threadActionMenu.logic.ts, apps/web/src/components/chat/ChatSettingsDialog.tsx, apps/web/src/hooks/useThreadActionMenu.ts, apps/web/src/components/CommandPalette.tsx, apps/web/src/components/ProjectSettingsShortcut.tsx | Test: cd apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/threadActionMenu.logic.test.ts src/components/chat/ChatSettingsDialog.test.tsx

### T-03 Screenshots, review, PR
- AC: AC-07 | Files: apps/web/tests/chat-settings/verify.mjs | Test: node apps/web/tests/chat-settings/verify.mjs <report dir>

## Delivery

- App PR: https://github.com/anton-abyzov/specwithcode/pull/723 (branch `feat/1424-chats-without-a-project`).
- Screenshots (minisforum): before `~/.specwithcode/minisforum/evidence/1424/before/2-shortcut.png` (Project settings "No project"), after `~/.specwithcode/minisforum/evidence/1424/after/2-shortcut.png` (Chat settings) and `after/3-palette.png`. The fresh headless state has no provider, so a sent chat is covered by unit tests, not a screenshot.
