# Linux app header layout polish

## Problem

On Linux, Electron draws the minimize, maximize and close buttons over the top-right of the window (Window Controls Overlay). In a project with a thread open, the thread panel's header keeps every control at full width. "Replies: Concise · Folded steps", Resolve, ⋯, Expand and Close slide under the native buttons, and Expand and Close end up past the window edge. The coordinator header beside it has the same problem: its labels fold only at a viewport width of 760px or less, so in a narrow column "Folded steps" runs into the thread panel.

Evidence: the user's photo `~/Downloads/IMG_0005.HEIC` (Ministorm, October 31, 2026) and real captures on Ministorm with 1.0.140 under a headless GNOME Shell 50, at window widths of 1600, 1280, 1024 and 820. The thread-panel header overlaps the native buttons at every width (`/tmp/linuxhdr/before/`). The same screen says "This Mac" on Linux and shows "Connect machines: Up to 1000000" without digit grouping.

## Scope

In: thread-panel and coordinator header fitting at every width and at 125% scale; folded controls stay reachable; Linux-correct wording and a readable limit on the Connect screens. Out: Electron's own window-button drawing, the Windows layout (it shares this CSS and benefits), and redesigning the panels.

## Acceptance Criteria

- [ ] AC-01: On Linux, no thread-panel header control overlaps the native window buttons or passes the window edge, at widths 820–1600 and at 125% scale.
- [ ] AC-02: The coordinator header's controls stay inside their column: none overlaps the thread panel at those widths.
- [ ] AC-03: Folded controls keep their accessible names and tooltips, and a hidden Expand panel button is offered in the Thread actions menu.
- [ ] AC-04: The phone card names "this computer" on Linux and Windows ("this Mac" on macOS), and the Connect limit shows grouped digits ("Up to 1,000,000").
- [ ] AC-05: The update is released, installed on Ministorm and verified there with before and after screenshots.

## Approach

`shell.css`: `.sws-topbar` becomes a size container. The replies label folds at 620px of header, and the Overview label at 480px. In `.sws-thread-head`, the replies label folds at 640px. At 360px or less, the title's minimum width drops to 0 and Expand folds away; the replies menu stays as an icon. `ProjectThreadHeader.tsx` adds Expand/Restore to the Thread actions menu while its button is hidden, reusing the folded-controls pattern. `PhoneConnectSettings.tsx` gets platform-aware wording. `managedTunnelPolicy.ts` formats the limit with `toLocaleString("en-US")`.

Rejected: clipping the header with `overflow: hidden`, which hides Close instead of fixing the layout; shrinking the native-controls inset, which Electron owns. Risk: container queries measure the content box, so the thresholds already count the 125px inset.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 A 1,000,000 cap shows as "Up to 1,000,000", not "Unlimited" (accurate; reversible).
### Open
- none

## Tasks

### T-01 Fit the thread-panel and coordinator headers
- AC: AC-01, AC-02, AC-03 | Files: apps/web/src/components/studio/shell/shell.css, apps/web/src/components/studio/shell/ProjectThreadHeader.tsx | Test: headless GNOME capture on Ministorm, `/tmp/measure.js` reports no overlapping or offscreen controls at 1600/1280/1024/820 and 125%

### T-02 Linux wording and readable Connect limit
- AC: AC-04 | Files: apps/web/src/components/settings/PhoneConnectSettings.tsx, apps/web/src/cloud/managedTunnelPolicy.ts, apps/web/src/cloud/managedTunnelPolicy.test.tsx | Test: `pnpm --filter @specweave-studio/web exec vp test run src/cloud/managedTunnelPolicy.test.tsx`

### T-03 Release and verify on Ministorm
- AC: AC-05 | Files: none | Test: Ministorm runs the new version; after captures show no overlaps

### T-04 Verify and close 1154
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: none | Test: `specweave verify 1154`
