# Links inside the viewer open in front

## Problem

A pull request, file or in-app browser link clicked inside the viewer overlay (a report, an artifact, a Library document) opened in the right panel or the page behind the overlay. The reader saw nothing happen: the target was hidden behind the modal they were reading. Reported by the user on October 19, 2026 with a screenshot of a report whose PR chip did nothing visible.

## Scope

In: PR links and chips, file links, timeline mention chips and media "open file" inside the overlay; in-app browser links and explicit "Open in panel" step out of the overlay; a route change closes it. Out: external system-browser links (unchanged); file links in a Library document with no thread in the browser client, which still offer only a copy-path menu (no thread to open a pane for; follow-up).

## Acceptance Criteria

- [x] AC-01: A PR link clicked inside the overlay shows the pull request in the overlay, topmost, with focus in it and a header naming it (`Pull request #N`, repository); nothing opens behind.
- [x] AC-02: A file link clicked inside a thread's viewer shows the file in the overlay the same way.
- [x] AC-03: Escape or the header Back returns to the viewer at the same scroll position, with focus back on the link that opened the target.
- [x] AC-04: "Open in panel", in-app browser links and route links close the overlay first, so what they open is in front.
- [x] AC-05: Headless regression coverage in light and dark at 1000 and 390 px, plus a check on the installed release.

## Approach

One store-level linked target in `viewerOverlayStore` (`showLinked`, `closeLinked`), shown by `ViewerLinkedPane` in the viewer's place while the viewer stays mounted, so its scroll survives. `lib/openInFront.ts` routes file and PR opens there while the overlay is up; `useOpenChangeRequestLink`, `ChatMarkdown`, `MessagesTimeline`, `ChatView` and `useOpenLink` call it. `ViewerOverlayRouteGuard` closes the overlay on a route change. `reportFileHost.ts` and the report's private file pane are removed. Shipped in specwithcode-dev PR #446 (1b33950ca7), released in 1.0.60. The closing review found that "Open in panel" from a chat file viewer opened nothing in 1.0.60 (AC-04): the panel was asked while the overlay was still up. PR #463 steps out first, clears a link target when a strip artifact is picked, and offers no panel for a thread-less PR.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 A linked target replaces the viewer inside the overlay rather than stacking a second modal (reversible).
### Open
- none

## Tasks

### T-01 Route in-overlay links to the overlay
- AC: AC-01, AC-02, AC-03, AC-04 | Files: apps/web/src/viewerOverlayStore.ts, apps/web/src/lib/openInFront.ts, apps/web/src/lib/openPullRequestLink.ts, apps/web/src/components/chat/ViewerLinkedPane.tsx, apps/web/src/components/ViewerOverlayHost.tsx | Test: vp test run apps/web/src/lib/openInFront.test.ts apps/web/src/lib/openPullRequestLink.overlay.test.tsx

### T-02 Headless fixture with screenshots
- AC: AC-05 | Files: apps/web/tests/viewer-links/ | Test: node apps/web/tests/viewer-links/verify.mjs ~/.specwithcode/m4/scratch/viewer-links-evidence

### T-03 PR, release and installed check
- AC: AC-01, AC-03, AC-05 | Files: ~/.specwithcode/m4/scratch/installed-viewer-check/ | Test: node ~/.specwithcode/m4/scratch/installed-viewer-check/check.mjs

### T-04 Fix the Open in panel regression the review found
- AC: AC-04 | Files: apps/web/src/components/chat/ThreadArtifacts.tsx, apps/web/src/components/chat/ThreadArtifacts.test.tsx, apps/web/src/components/ViewerOverlayHost.tsx, apps/web/src/lib/openPullRequestLink.ts, apps/web/src/lib/openPullRequestLink.overlay.test.tsx | Test: vp test run apps/web/src/components/chat/ThreadArtifacts.test.tsx apps/web/src/lib/openPullRequestLink.overlay.test.tsx

### T-05 Verify and close 0956
