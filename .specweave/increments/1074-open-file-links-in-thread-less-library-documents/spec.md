# Open file links in thread-less Library documents

## Problem

A Library document opened in the viewer overlay belongs to no thread. In the browser client, clicking a file link inside it (`permissionWatcher.ts` in a Library `report.md`) only shows the copy-path menu: no pane opens. ChatMarkdown's `openFileInPanel` returns when there is no `threadRef`, `MarkdownFileLink` counts a file as openable in the pane only with a thread, and `ViewerFileTarget.threadRef` is required, so the overlay's linked file pane cannot take a thread-less file. `LibraryFileViewer` also renders the document's ChatMarkdown without its environment, so the links are never checked against the host.

Evidence: the installed 1.0.76 viewer acceptance, `/Users/antonabyzov/.specwithcode/m4/scratch/installed-viewer-check/evidence/acceptance.md` ("Library file-link gap") and `/Users/antonabyzov/.specwithcode/m4/scratch/installed-viewer-check/evidence/installed-library-file-link.png`. Reported by the report-viewer owner as a follow-up to 1049, which is closed to new code.

## Scope

In: a file link inside a document shown in the viewer overlay with no thread (the Library viewer, and a file linked from it) opens in the overlay's linked file pane, with Back to the document. The linked pane reads the file from the target's own environment and offers "Open in panel" only when there is a thread whose panel can take it.

Out: Library documents outside the viewer overlay; folder links; media links (they need a thread's media viewer); the desktop app's editor behavior; ChatMarkdown styling and code highlighting (1038).

## Acceptance Criteria

- [ ] AC-01: In the Library viewer, a click on a file link in a markdown document opens that file in the overlay's linked file pane (header names the file; Back returns to the document), in the browser client, with no thread.
- [ ] AC-02: The linked file pane of a thread-less file shows no "Open in panel" button; a file opened from a thread still shows it and still opens the thread's panel.
- [ ] AC-03: `ViewerFileTarget` names the environment that reads the file and allows `threadRef: null`; every caller with a thread passes that thread's environment, so threaded file links open exactly where they did before (overlay, focused viewer or panel).
- [ ] AC-04: Outside the overlay, a thread-less file target opens nothing (no panel or focused viewer without a thread) instead of throwing.

## Approach

1. `apps/web/src/viewerOverlayStore.ts`: `ViewerFileTarget` gains `environmentId: EnvironmentId`; `threadRef` becomes `ScopedThreadRef | null`, as `ViewerPullRequestTarget` already is.
2. `apps/web/src/lib/openInFront.ts`: `openFileInFront` shows any target in the overlay when it is in front; otherwise a target without a thread stops there, since only a thread has a panel or a focused viewer. `moveFocusedFileToPanel` needs a thread.
3. `apps/web/src/components/ChatMarkdown.tsx`: the environment a file link reads from is the thread's, or, inside the viewer overlay, the explicit `environmentId`. `openFileInPanel` and the unresolved-file path use it; `MarkdownFileLink` takes `canOpenInPanel` from ChatMarkdown instead of testing `threadRef` itself.
4. `apps/web/src/components/chat/ViewerLinkedPane.tsx`: `LinkedFile` reads through `target.environmentId`, passes it to nested ChatMarkdown, and hides "Open in panel" without a thread.
5. `apps/web/src/components/studio/shell/LibraryFileViewer.tsx`: pass `environmentId` to the document's ChatMarkdown.
6. Callers with a thread (`MessagesTimeline.tsx`, `ChatView.tsx`, `ViewerOverlayHost.tsx`) pass `threadRef.environmentId`.

Rejected: a synthetic thread for Library documents (would route panel state to a thread that does not exist); opening thread-less files in the editor in the browser client (no local editor there).

Risk: ChatMarkdown with an environment checks Library links against the host, so a link to a missing file stops looking like a file chip. That matches thread messages.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Thread-less file links open only inside the viewer overlay, never as a panel (no thread owns a panel). Reversible.
- D-02: New increment, not a reopen of 1049 (closed to new code; T-09 installed check only). ChatMarkdown changes coordinated with the 1038 lane, which is complete.
### Open
- none

## Tasks

### T-01 Thread-less file targets in the overlay
- AC: AC-01, AC-02, AC-03, AC-04 | Files: apps/web/src/viewerOverlayStore.ts, apps/web/src/lib/openInFront.ts, apps/web/src/components/ChatMarkdown.tsx, apps/web/src/components/chat/ViewerLinkedPane.tsx, apps/web/src/components/studio/shell/LibraryFileViewer.tsx, apps/web/src/components/chat/MessagesTimeline.tsx, apps/web/src/components/ChatView.tsx, apps/web/src/components/ViewerOverlayHost.tsx | Test: `node node_modules/vite-plus/bin/vp test run apps/web/src/lib/openInFront.test.ts apps/web/src/components/chat/ViewerLinkedPane.test.tsx`, web typecheck

### T-02 Headless check of the Library viewer
- AC: AC-01, AC-02 | Files: headless check script and captures under /Users/antonabyzov/.specwithcode/m4/evidence/1074-library-file-links/ | Test: headless Chromium, narrow and wide, light and dark

### T-03 Verify and close 1074
- AC: AC-01, AC-02, AC-03, AC-04 | Files: none | Test: `specweave verify 1074`, fresh-context review, `specweave complete 1074` after installed acceptance on the release that carries it
