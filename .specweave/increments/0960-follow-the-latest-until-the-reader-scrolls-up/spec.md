# Follow the latest until the reader scrolls up

## Problem

The user presses "Jump to latest" too often (screenshot October 20, 2026). At the end of the coordinator conversation, any scroll event short of the end stopped following, whoever caused it: the browser's scroll anchoring, a picture loading in the person's own message, a narrowed panel, a row above growing. The view stayed put and offered "Jump to latest". In a thread, a click on a message stopped following whenever the view sat off the end, which includes the new-turn framing and the frame streamed text runs ahead.

## Scope

In: `useConversationFollow` (coordinator) and ChatView's follow gestures in `anton-abyzov/specwithcode-dev`. Out: the new-turn framing itself, the LegendList re-pin rules, the thread's position inside a kept project page.

## Acceptance Criteria

- [ ] AC-01: At the end of the coordinator conversation, streaming, late-loading pictures (including in the person's own message), a row growing, the end of a turn, a resized panel and scroll the browser makes on its own all keep the reader at the end with no "Jump to latest".
- [ ] AC-02: Only the reader's own upward scroll (wheel or trackpad, a dragged scrollbar or selection, a finger, an upward key, find) pauses following, and the message they read stays at the same offset while things arrive or the panel resizes.
- [ ] AC-03: Scrolling back to the end, End, or one "Jump to latest" resumes following with no further clicks, and returning from another project lands on the latest.
- [ ] AC-04: In a thread, a click on a message never stops following; a dragged selection, a scrollbar drag, an upward wheel, key or finger still does.
- [ ] AC-05: A headless check reproduces the coordinator failures on main and passes with the fix; unit tests cover the new rules.

## Approach

`useConversationFollow` notes the reader's upward input (wheel, upward keys, a moving pressed pointer or finger, and `noteReaderScroll` from find). A scroll away from the end leaves following only when that input is recent (400 ms, the gap between an input and the scroll it causes); otherwise a following reader is put back at the end. ChatView's pointerdown no longer breaks follow on a content click; a pressed mouse that moves and scrolls the list away from the end does, and touch breaks only when the finger moves down.

## Decisions

### Asked
- none
### Defaulted
- D-01: The new-turn framing in threads stays as it is; only clicks stop breaking it.

## Tasks

### T-01 Coordinator follows until the reader scrolls up
- AC: AC-01, AC-02, AC-03 | Files: apps/web/src/components/studio/useConversationFollow.ts, apps/web/src/lib/readerScroll.ts, apps/web/src/components/find/conversationFind.logic.ts, apps/web/src/components/studio/useConversationFollow.test.tsx, apps/web/src/components/studio/ProjectWorkspace.render.test.tsx | Test: vp test run apps/web/src/components/studio/

### T-02 Thread clicks keep following
- AC: AC-04 | Files: apps/web/src/components/ChatView.tsx | Test: thread-follow-check.mjs on a private server

### T-03 Headless check, PR, merge and release
- AC: AC-05 | Files: apps/web/tests/project-workspace/follow-latest-check.mjs, apps/web/tests/project-workspace/mocks.tsx, apps/web/tests/project-workspace/README.md | Test: node apps/web/tests/project-workspace/follow-latest-check.mjs

### T-04 Verify and close 0960
