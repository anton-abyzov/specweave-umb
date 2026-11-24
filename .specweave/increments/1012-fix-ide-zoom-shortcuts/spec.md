# 1012 Fix IDE zoom shortcuts

## Problem
The desktop View menu already has Command/Ctrl equals, plus, minus and zero, but the focused embedded preview suppresses every non-editing menu accelerator. App zoom silently stops there.

## Scope
In: preserve app zoom accelerators while the embedded preview has focus, cross-platform modifier rules, existing menu routing and preview isolation regression checks. Out: new global shortcuts, editor/terminal font shortcuts, popup behavior changes, release or installation.

## Acceptance Criteria
- [ ] AC-01: A focused embedded preview permits Command equals/plus/minus/zero on macOS and Ctrl equivalents on Windows/Linux to reach the existing main-window zoom menu.
- [ ] AC-02: Unfocused injected input, composing text, AltGr, unrelated shortcuts and popup host shortcuts remain suppressed; editor and terminal handlers are unchanged.
- [ ] AC-03: Every zoom accelerator routes to main-window zoom; reset returns to zero and embedded preview zoom is restored independently.

## Approach
Add a narrow platform-aware zoom-chord predicate beside the desktop window code. Allow only this predicate plus existing editing chords through the focused preview menu filter; keep popup filtering unchanged. Exercise actual before-input-event listeners and existing menu and DesktopWindow services with focused tests. Installed native acceptance is reported separately from source proof.

## Decisions
### Defaulted
- Use the existing native application menu, without adding DOM or global key handlers.
- Keep popup shortcuts unchanged and reserve modified variants for their current consumers.
### Open
- none

## Tasks

### T-01 Repair focused preview zoom routing
- AC: AC-01, AC-02, AC-03 | Files: apps/desktop/src/window/zoomShortcut.ts, apps/desktop/src/window/zoomShortcut.test.ts, apps/desktop/src/preview/Manager.ts, apps/desktop/src/preview/Manager.test.ts, apps/desktop/src/window/DesktopApplicationMenu.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/desktop/src/window/zoomShortcut.test.ts apps/desktop/src/preview/Manager.test.ts apps/desktop/src/window/DesktopApplicationMenu.test.ts apps/desktop/src/window/DesktopWindow.test.ts

## Finish
Verify and close 1012.
