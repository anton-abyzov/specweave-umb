# Sidebar chats hold still during live updates

## Problem

The SpecWithCode sidebar's Chats list reordered itself while delegated workers ran (screenshot October 19, 2026: 0949+0950, 0948 and 0951 swapping places). The list's "Last activity" sort, its date headings and its recency filter used the thread shell's `updatedAt`, which the server projection moves forward on every domain event (`ProjectionStore.applyToProjection`): each streamed item, tool call, approval and status change. Several busy chats therefore traded places on every event, the row under the pointer moved, Ctrl+] walked to the wrong neighbour and a chat the person had just written to could sit below busier ones. The project Threads pane already sorted on `threadActivityAt` (created, last user message, last requested turn); the sidebar did not.

## Scope

In: sidebar chat sort, date headings and recency filter (`apps/web/src/studio/shellModel.ts`) in `anton-abyzov/specwithcode-dev`, with unit, component and headless fixture checks. Out: which project a delegated thread belongs to (owned by 0947 move-thread-project), the legacy and inbox sidebars (no `updatedAt` sort), pull request lists.

## Acceptance Criteria

- [ ] AC-01: Streamed items, tool calls, approvals, background tasks and status changes on any number of chats never change the chats' order, date heading or recency-filter membership; rows still show the newest state.
- [ ] AC-02: Equal activity times keep a fixed order (thread id) whatever order the server sends rows in; the open chat stays marked and keeps its DOM row through updates.
- [ ] AC-03: Explicit work still moves a chat: a sent message, a new requested turn or a new chat puts it on top; keyboard next/previous follow the rows on screen.
- [ ] AC-04: Regression tests fail on main and pass with the fix; a headless fixture of the real sidebar under 40 ms live events shows zero reorders and no frame over 250 ms at desktop and phone widths.

## Approach

"Last activity" for chats uses `threadActivityAt` (shared with the Threads pane): `compareChats("activity")` returns `compareByActivity`, and the date bucket and recency filter read the same key. Created and name sorts are unchanged.

## Decisions

### Asked
- none
### Defaulted
- D-01: A coordinator handing a chat a new turn counts as new work and moves it (it sets `latestRun.requestedAt`); continuous streaming inside that turn does not.

## Tasks

### T-01 Chat list sorts on asked-for activity
- AC: AC-01, AC-02, AC-03 | Files: apps/web/src/studio/shellModel.ts, apps/web/src/studio/shellModel.test.ts, apps/web/src/components/studio/shell/StudioSidebar.test.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/studio/shellModel.test.ts apps/web/src/components/studio/shell/StudioSidebar.test.tsx

### T-02 Headless live-update fixture, PR and merge
- AC: AC-04 | Files: apps/web/tests/sidebar-stable-order/vite.config.ts, apps/web/tests/sidebar-stable-order/main.tsx, apps/web/tests/sidebar-stable-order/mocks.tsx, apps/web/tests/sidebar-stable-order/verify.mjs | Test: node apps/web/tests/sidebar-stable-order/verify.mjs

### T-03 Verify and close 0952
