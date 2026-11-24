# Fix missing Linux chat button

## Problem

On a fresh Linux installation the user sees a plus next to Projects but none next to Chats (user report, October 24, 2026).

Source at `origin/main` 6856331848 shows two causes, both platform-independent in code but likely together on a fresh Linux machine:

1. The Chats heading in `apps/web/src/components/studio/shell/StudioSidebar.tsx` only renders the filter menu (`chatTools`). The only way to start a chat is the "New chat" row at the top of the sidebar, so the Chats section has no add control on any platform, while Projects has one.
2. "New chat" starts a chat in the machine's Scratch project ("No project"). `ManagedProjectFolders.scratchRoot` (`apps/server/src/project/ManagedProjectFolders.ts`) probes `git rev-parse --is-inside-work-tree` in the data dir and hides Scratch when the probe fails. A fresh Linux desktop often has no `git`, so the probe fails, `serverConfig.scratchWorkspaceRoot` is absent, `scratchEnvironmentId` returns null, and the sidebar's `newChat` (and the `chat.new` shortcut) return without starting anything or saying why.

## Scope

In: an add-chat plus in the Chats heading; Scratch offered when Git cannot run but the data dir is outside any checkout; a visible message instead of a silent no-op when no machine can start a chat. Out: installing Git, changing the Projects section, the legacy sidebar layout, Linux packaging.

## Acceptance Criteria

- [x] AC-01: The Chats heading shows a "New chat" plus button next to the filter menu; clicking it starts a new chat the same way as the "New chat" row.
- [x] AC-02: When `git` cannot run, a data dir with no `.git` in itself or any parent still offers Scratch (`scratchRoot` is Some), and a data dir inside a checkout still offers none.
- [x] AC-03: When no connected machine offers Scratch, the sidebar "New chat" row, the Chats plus and the `chat.new` shortcut show an error toast that explains why, instead of doing nothing.
- [x] AC-04: A headless fresh-state fixture shows the Chats plus, and clicking it opens a new chat draft; screenshots saved to files.

## Approach

1. `ManagedProjectFolders.ts`: on a non-interrupt probe failure, fall back to a filesystem walk from the data dir up to the root looking for a `.git` entry; offer Scratch only when none is found. A filesystem error in the fallback still hides Scratch.
2. `useScratchProject.ts`: add `reportNoChatMachine()` (one shared toast). `StudioSidebar.tsx` and `routes/_chat.tsx` call it when `scratchEnvironmentId` returns null.
3. `StudioSidebar.tsx`: render a `PlusIcon` button with `aria-label="New chat"` in the Chats heading, calling `newChat`.

Rejected: hiding the plus when no machine offers Scratch (the user would still see no way to add a chat); treating every probe failure as "not a checkout" (would offer Scratch inside a dotfiles home when Git times out).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Chats plus label → "New chat", same tooltip wording as the row (reversible).
- D-02 Git-less detection → walk for `.git` from the data dir to the filesystem root (reversible).
### Open
- none

## Tasks

### T-01 Offer Scratch when Git cannot run
- AC: AC-02 | Files: apps/server/src/project/ManagedProjectFolders.ts, apps/server/src/project/ManagedProjectFolders.test.ts | Test: cd apps/server && npx vitest run src/project/ManagedProjectFolders.test.ts

### T-02 Chats heading plus and no-machine message
- AC: AC-01, AC-03 | Files: apps/web/src/components/studio/shell/StudioSidebar.tsx, apps/web/src/hooks/useScratchProject.ts, apps/web/src/routes/_chat.tsx, apps/web/src/components/studio/shell/StudioSidebar.test.tsx | Test: cd apps/web && npx vitest run src/components/studio/shell/StudioSidebar.test.tsx

### T-03 Headless fresh-state check
- AC: AC-04 | Files: apps/web/tests/chats-new-chat/verify.mjs | Test: node apps/web/tests/chats-new-chat/verify.mjs

### T-04 Verify and close 1061
- AC: AC-01, AC-02, AC-03, AC-04 | Files: none | Test: specweave verify 1061-fix-missing-linux-chat-button
