# Design canvas editor

## Problem

A design needs an editor where the user and an agent work on the same document: chat on one side, canvas on the other. Claude's editor (screenshot SS2, claude-design-inventory.md section 3-4) has pages, artboards, select, pan, text, frame, note, pen and line tools, zoom, a selection mini toolbar, present mode, per-artboard export and autosave. SpecWithCode has no canvas; 0972 provides the document, store and agent tools this editor edits.

## Scope

In: the `/design/$designKey` editor with the bound agent thread beside the canvas, pages, frames as artboards, the tools select, hand, frame, text, rectangle, ellipse, line, pen, note and image, direct manipulation (move, resize, multi-select, duplicate, delete, nudge, align), undo and redo, a properties panel that offers design-system tokens, the selection mini toolbar (fill, comment, ask agent), comments anchored to nodes, zoom and fit, present mode, export (PNG and HTML per frame, PDF of all frames), autosave with conflict handling, live updates when the agent edits, and "Implement this frame" that sends the frame to a coding thread.

Out: auto-layout and constraints, vector boolean operations, real-time multi-user cursors, slides-specific features (0975).

## Acceptance Criteria

- [ ] AC-01: Opening a design shows the bound thread on the left and the canvas on the right, with a draggable divider, a "Canvas only" toggle and a page menu. Opening a design with no thread offers "Start a thread" (project worker model by default).
- [ ] AC-02: Tools select (V), hand (H or Space), frame (F), text (T), rectangle (R), ellipse (O), line (L), pen (P), note (N) and image (upload) create nodes through the 0972 reducer. Pen draws a polyline path; Shift constrains angles and squares.
- [ ] AC-03: Select, multi-select (Shift and marquee), move, resize from 8 handles, nudge with arrows (Shift for 10 px), duplicate (Cmd+D), delete, bring forward and back, align and distribute. Undo and redo (Cmd+Z, Shift+Cmd+Z) cover every operation including agent edits made in this session.
- [ ] AC-04: Zoom with Cmd plus scroll and pinch, the zoom menu (fit, 50%, 100%, 200%), and zoom to selection. Frames show their label with export and focus actions.
- [ ] AC-05: The properties panel edits position, size, fill, stroke, radius, opacity and text style. Color and type fields offer the design system's tokens and store `{token}` references; a token change in the system updates every node that uses it.
- [ ] AC-06: The selection mini toolbar has fill, comment and "Ask agent", which sends the selection (ids, a PNG of the selection and a short description) to the bound thread as a message.
- [ ] AC-07: Comments pin to a node or a canvas point, open in a side list, can be resolved, and agents read and resolve them through `design_apply`.
- [ ] AC-08: Edits autosave within one second of the last change. When the agent and the user edit at once, both edits land: the client rebases its pending operations on the newer revision and only a true conflict (same property of the same node) shows "Updated by the agent" with keep mine or take theirs.
- [ ] AC-09: Agent edits appear on the canvas within one second without a reload.
- [ ] AC-10: Export PNG (1x, 2x) and standalone HTML per frame, and one PDF of all frames, all rendered by the shared renderer in the headless browser. Present mode shows frames full screen in order with arrow keys and Esc.
- [ ] AC-11: `html` nodes (agent-written HTML) render in an opaque-origin sandboxed iframe with the existing render bootstrap; they never get same-origin access.
- [ ] AC-12: "Implement this frame" opens a picker for a coding thread in the design's project (new or existing) and sends the frame's JSON, PNG, used tokens and matching design-system components.
- [ ] AC-13: The canvas stays at 60 fps with 500 nodes on a page (headless performance trace) and does not repaint while idle.
- [ ] AC-15: Share in the editor header opens a dialog that shows the owner, who has access (this Mac, the owner's paired devices and linked machines, agent threads) and sets the members and agents levels (edit, comment, view), with Copy link and the export formats. The dialog states that public web links are not available in this build instead of showing a dead control.
- [ ] AC-16: The bound thread shows on the left; a binding to another machine's thread shows that machine with "Open there" (when linked) and "Start a thread here".
- [ ] AC-14: Headless screenshots and a recording of drawing, editing, an agent edit arriving, a comment, export and present mode, light and dark. Keyboard-only use reaches every tool.

## Approach

`apps/web/src/routes/design.$designKey.tsx`; `apps/web/src/components/design/canvas/` (`DesignCanvas.tsx` with a transform layer, `NodeView.tsx` using shared `nodeStyle`, `useCanvasTools.ts` state machine, `SelectionLayer.tsx`, `PropertiesPanel.tsx`, `MiniToolbar.tsx`, `CommentsPanel.tsx`, `PresentMode.tsx`), `designSession.ts` (pending operations, rebase on revision, undo stack). Server export through `DesignService.export` using `HtmlRender` headless Chrome. DOM rendering with absolutely positioned elements from the shared style function, so the canvas, thumbnails and exports render the same document the same way; a `<canvas>` renderer was rejected because text editing, accessibility and HTML nodes would need a second implementation.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Operation rebase with property-level conflicts instead of whole-document last-writer-wins.
- D-02: Share controls access inside the user's own devices, machines and agents, plus app links; public web publication is out of this build and needs explicit consent (see 0972 D-02).
### Open
- none

## Tasks

### T-01 Editor route and split layout
- AC: AC-01 | Files: routes/design.$designKey.tsx, components/design/DesignEditor.tsx | Test: component test

### T-02 Canvas, tools and manipulation
- AC: AC-02, AC-03, AC-04 | Files: components/design/canvas/* | Test: tool state machine tests, component tests

### T-03 Properties panel and tokens
- AC: AC-05 | Files: PropertiesPanel.tsx | Test: component tests

### T-04 Mini toolbar, comments and Ask agent
- AC: AC-06, AC-07 | Files: MiniToolbar.tsx, CommentsPanel.tsx | Test: component tests

### T-05 Session sync, autosave and conflicts
- AC: AC-08, AC-09 | Files: designSession.ts, live subscription | Test: rebase and conflict tests, server push test

### T-06 Export and present
- AC: AC-10, AC-11 | Files: PresentMode.tsx, DesignService export | Test: export tests in headless Chrome

### T-07 Implement this frame
- AC: AC-12 | Files: ImplementFrameDialog.tsx | Test: component test

### T-10 Share dialog and bound thread
- AC: AC-15, AC-16 | Files: components/design/editor/ShareDialog.tsx, editor header | Test: component tests, headless screenshots

### T-08 Performance and evidence
- AC: AC-13, AC-14 | Files: apps/web/tests/design-canvas/* | Test: headless Playwright trace, screenshots, recording

### T-09 Verify and close 0974
- AC: all | Files: none | Test: specweave verify, fresh-context review, specweave complete
