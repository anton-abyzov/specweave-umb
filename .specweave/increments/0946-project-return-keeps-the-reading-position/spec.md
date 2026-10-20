# Project return keeps the reading position

## Problem

Switching projects in the SpecWithCode sidebar and coming back often showed the coordinator from the top: Friday's messages under "Load earlier messages" with a "New messages" pill (screenshot October 19, 2026). Since PR #377 a left project page stays mounted under a hidden React `<Activity>` (`display: none`). The coordinator conversation never put its reader back when shown; after its content changed while hidden it came back at the top, and the earlier-messages observer then mounted older pages measured from the top until everything was mounted. The user also asked for a clearer, always-present way to jump to the latest message.

## Scope

In: coordinator conversation scroll state across hidden/shown and remounted project pages; the "Jump to latest" control in the coordinator and threads (`anton-abyzov/specwithcode-dev`). Out: a worker thread's own position inside a kept project page (LegendList re-runs end positioning on reveal; owned by the live thread activity work), thread-to-thread switching in ChatView (already remembered per thread).

## Acceptance Criteria

- [ ] AC-01: A first visit to a conversation with no saved place opens at the latest message.
- [ ] AC-02: Leaving a project and returning lands a following reader on the latest message, including messages that arrived while away, without mounting older messages.
- [ ] AC-03: A reader further up returns to the same message at the same offset, through rapid A→B→A switching, after a reply arrived while away (marked new) and after older messages were mounted from the top; also after the page was unmounted and its history arrives later.
- [ ] AC-04: "Jump to latest" shows whenever the reader is further up, regardless of unread messages; it sits above the composer, has an accessible name, works from the keyboard, reaches the newest message and resumes following. The coordinator and threads use the same control.
- [ ] AC-05: Regression tests reproduce the failure on main and pass with the fix.

## Approach

`useConversationFollow` records each conversation's place on scroll (module map by environment:coordinator) and restores it in its open layout effect, which Activity re-runs on reveal; a place waiting for history restores on the next content change; hidden scroll events are ignored. `CoordinatorConversation` tags rows with `data-follow-anchor`, keeps its message window per conversation and skips the earlier-messages observer while hidden. `JumpToLatestButton` is shared by `CoordinatorConversation` and `ChatView`.

## Decisions

### Asked
- none
### Defaulted
- D-01: Thread pane position inside a kept project page is a follow-up for the owner of MessagesTimeline (live thread activity), not changed here.
- D-02: Jump control keeps its existing centered position above the composer; primary filled pill, "New" badge when unseen.

## Tasks

### T-01 Coordinator keeps its reading place across project switches
- AC: AC-01, AC-02, AC-03 | Files: apps/web/src/components/studio/useConversationFollow.ts, apps/web/src/components/studio/useConversationFollow.test.tsx, apps/web/src/components/studio/CoordinatorConversation.tsx, apps/web/src/components/studio/ProjectWorkspace.tsx, apps/web/src/components/studio/ProjectWorkspace.test-fixtures.tsx | Test: vp test run apps/web/src/components/studio/

### T-02 One clear Jump to latest control
- AC: AC-04 | Files: apps/web/src/components/chat/JumpToLatestButton.tsx, apps/web/src/components/ChatView.tsx, apps/web/src/components/studio/CoordinatorConversation.tsx, apps/web/src/components/studio/ProjectWorkspace.render.test.tsx | Test: vp test run apps/web/src/components/studio/ProjectWorkspace.render.test.tsx

### T-03 Headless regression check, PR, merge and installed check
- AC: AC-05 | Files: apps/web/tests/project-workspace/project-return-check.mjs, apps/web/tests/project-workspace/fixture.tsx, apps/web/tests/project-workspace/mocks.tsx | Test: node apps/web/tests/project-workspace/project-return-check.mjs

### T-04 Verify and close 0946
