# Artifacts New menu offers every artifact type: Design, Slides and Design system next to Sheet, Whiteboard and Document

## Problem

The owner asked on November 27, 2026: "Is there a way to start to create this whiteboard? … What about other types? Do we support only three of them compared to Claude Code Design? Find the gaps and implement it properly."

A project's Artifacts row has a **+** menu with only Sheet, Whiteboard and Document. Claude has seven artifact types. Its help center says you start one "from a template in the Artifacts tab" or by asking in any chat. The seven are Docs, Slides, Design, Motion, Data (dashboards), Sheets and Whiteboards. Claude desktop 6.28899.6 bundles the `design` and `slides` type runtimes and has settings flags for Design, Slides, Whiteboard, Dashboard and Motion.

SpecWithCode already has Design and Slides: the Design studio at `/design` builds both, and it also makes design systems. But you can only reach them from the sidebar **Design** row or the project's More menu, never from the **+** that the owner found. So the app looks like it supports three types when it supports five.

| Claude type | SpecWithCode today | After this increment |
|---|---|---|
| Docs | **+** › Document | same |
| Sheets | **+** › Sheet | same |
| Whiteboards | **+** › Whiteboard | same |
| Design | Design studio only | **+** › Design |
| Slides | Design studio only | **+** › Slides |
| (design systems) | Settings › Design systems | **+** › Design system |
| Motion | none; motion pages are in 1499 | out of scope (1499) |
| Data / dashboards | none; planned as 1342 slice 2 | out of scope, own increment |

## Scope

In:
- Three new **+** entries: **Design**, **Slides** and **Design system**. Each opens the Design studio's own New flow, preset to this project.
- `/design?new=` accepts `slides` as well as `design`.

Out:
- Data/dashboards, a new kind that needs its own increment (1342 slice 2).
- Motion, owned by 1499 (`motion-slide-artifacts`).
- Any change to the Design studio editor itself.

## Acceptance Criteria

- [x] AC-01: On a project whose Design studio works on this machine, the Artifacts **+** menu lists Sheet, Whiteboard, Document, Design, Slides and Design system.
- [x] AC-02: **+** › Design opens the New design dialog with this project already chosen as the owner. **+** › Slides opens the New slides dialog the same way.
- [x] AC-03: **+** › Design system opens this project's design systems page, as the gallery's own "Design system" entry does.
- [x] AC-04: A hand-edited `/design?new=` keeps working: `design` and `slides` open their dialog once, and any other value is ignored.
- [x] AC-05: Where the Design studio is unavailable (a project on another machine, or a scratch project), the three design entries are hidden, and Sheet, Whiteboard and Document stay.

## Approach

- `galleryModel.ts`: `DesignGallerySearch.new` becomes `"design" | "slides"`. `parseDesignGallerySearch` keeps only those two values. `newDesignPresetFromSearch` returns the kind with the preset.
- `DesignGalleryPage.tsx`: the one-shot `?new=` effect opens the dialog of that kind, not always `design`.
- New `apps/web/src/components/studio/shell/newDesignEntries.tsx`: `useNewDesignEntries({ projectId, available })` returns three `ArtifactNewEntry` items that navigate and return `null`, so the shelf opens no file.
- `ProjectArtifactShelf.tsx`: takes `projectId` and `designHere`, and appends the entries.
- `ProjectWorkspaceSurface.tsx`: passes `project.id` and the same `designHere` rule as the More menu (`project.environmentId === primaryEnvironmentId`, and not a scratch member).

Rejected:
- Creating a blank design directly from **+**. It would skip the system picker and the prompt the New dialog asks for, so the two ways of starting would behave differently.

## Decisions

### Asked
- D-01: Should the owner choose between closing the gaps and only explaining them? The coordinator says the owner prefers the recommended option, so this increment closes the gaps that already have an engine behind them.

### Defaulted (change any before sw-do)
- D-02: Design entries open the Design studio's New dialog instead of creating silently. Reversible.
- D-03: Data/dashboards is its own increment, following 1342's slice order. Reversible.

### Open
- none

## Tasks

### T-01 `?new=slides` opens New slides
- AC: AC-04, AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/design/gallery/galleryModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/design/gallery/DesignGalleryPage.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/design/gallery/galleryModel.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/web/src/components/design/gallery/galleryModel.test.ts

### T-02 Design, Slides and Design system in the Artifacts New menu
- AC: AC-01, AC-02, AC-03, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/newDesignEntries.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/newDesignEntries.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ProjectArtifactShelf.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/shell/newDesignEntries.test.tsx
