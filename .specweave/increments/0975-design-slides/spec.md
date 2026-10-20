# Slides on the design canvas

## Problem

The user asked for slides as a follow-on to designs, in separate implementation threads, reusing the design artifact and design system instead of a second editor. Claude ships Slides as a sibling artifact type with a slide list, slide menu (Duplicate, Add after, Move, Skip, Delete), present mode keys and PDF/PPTX export (claude-design-inventory.md section 6).

## Scope

In: `kind: "slides"` documents from 0972 where each page is one 16:9 frame, the Slides card in the gallery, a slide rail in the 0974 editor, slide menu actions, layouts built from the design system, speaker notes, present mode with presenter view, PDF and PPTX export, and agent authoring through the same `design_*` tools.

Out: a separate slide editor, Google Slides upload, sharing or publishing, transitions beyond a fade.

## Acceptance Criteria

- [ ] AC-01: "Slides" in Make something new creates a slides document (1920x1080 frames) in the chosen owner with the chosen design system.
- [ ] AC-02: The 0974 editor shows a slide rail with thumbnails for slides documents; the rail supports reorder by drag and keyboard, and the slide menu has Duplicate, Add after, Move up, Move down, Skip and Delete. No code path forks the canvas.
- [ ] AC-03: Layouts (title, section, title and body, two columns, image and caption, quote) are generated from the design system's type and color tokens and are editable nodes after insertion.
- [ ] AC-04: Each slide has speaker notes stored in the document.
- [ ] AC-05: Present mode supports arrow keys, Space, Page Up and Down, Home, End, number keys, F for full screen and Esc; skipped slides are left out; the presenter view shows the current slide, next slide, notes and a timer.
- [ ] AC-06: Export PDF (one page per slide, at the slide's size) and PPTX (text stays editable text, shapes stay shapes, html nodes become images) from the shared renderer.
- [ ] AC-07: An agent asked for a deck creates and edits it with `design_create` and `design_apply` only; tests drive this through the MCP handlers.
- [ ] AC-08: Headless screenshots of the rail, layouts, presenter view and an exported PDF page, light and dark; the PPTX opens in a validation step (python-pptx read-back) with the expected slide count and text.

## Approach

Reuse `DesignEditor` with a `SlideRail.tsx` and `SlideMenu.tsx`; `packages/shared/src/design/slideLayouts.ts` builds layouts from tokens; `PresenterView.tsx`; PPTX through a maintained MIT library (pptxgenjs, license checked) in `apps/server/src/design/export/pptx.ts`. The presentations skill guides layout quality.

## Decisions

### Asked
- D-01: Slides start after foundation and Figma, in their own threads (user, October 20, 2026).
### Defaulted (change any before sw-do)
- D-02: Slides are pages of a design document, not a new artifact type.
### Open
- none

## Tasks

### T-01 Slides document and gallery card
- AC: AC-01 | Files: gallery create flow, shared defaults | Test: component and reducer tests

### T-02 Slide rail and menu
- AC: AC-02, AC-04 | Files: SlideRail.tsx, SlideMenu.tsx | Test: component tests

### T-03 Layouts from tokens
- AC: AC-03 | Files: packages/shared/src/design/slideLayouts.ts | Test: unit tests

### T-04 Present and presenter view
- AC: AC-05 | Files: PresentMode.tsx, PresenterView.tsx | Test: keyboard tests

### T-05 PDF and PPTX export
- AC: AC-06 | Files: apps/server/src/design/export/pptx.ts, pdf | Test: export tests with read-back

### T-06 Agent authoring and evidence
- AC: AC-07, AC-08 | Files: handler tests, apps/web/tests/design-slides/* | Test: MCP handler tests, headless Playwright

### T-07 Verify and close 0975
- AC: all | Files: none | Test: specweave verify, fresh-context review, specweave complete
