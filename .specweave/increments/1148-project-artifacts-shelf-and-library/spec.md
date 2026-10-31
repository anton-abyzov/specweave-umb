# Project artifacts shelf and library

## Problem

A SpecWithCode project has no single place that shows what its threads produced. Each thread has its own artifacts list, and the Library tab lists the hub's registered artifacts and raw folders, but the project view never surfaces the reports, screenshots, pages, designs and pull requests the work left behind. The Claude projects Threads panel shows these as an artifacts shelf above the threads, with pinning and a View all into Library > Artifacts; the owner asked for the equivalent.

## Scope

In: an artifacts shelf above the project's Threads list (cards with thumbnail or kind tile, title, age, pin, a ... menu, View all), and an Artifacts view in the Library tab (list with Name, Thread, Date modified, Size and Kind; grid; Type filter). A project artifact is: a design or deck, a file threads wrote into SpecWeave output (`.specweave/reports/**`, each increment's `reports/`), a hub-registered file or link, a pull request a thread opened or linked, and a page, image or document a thread named (from this device's thread artifact lists). Ordered pinned first, then most recently updated. Pins are per project on this device, as thread artifact pins are.

Out: syncing pins across devices, renaming or deleting artifacts from the shelf, server-side thumbnails.

## Acceptance Criteria

- [ ] AC-01: The Library snapshot lists the newest output files under `.specweave/reports/` and increment `reports/` folders (newest first, capped, no symlinks, nothing outside the project); older servers without the field still work.
- [ ] AC-02: The project artifacts model merges designs, outputs, hub artifacts, pull requests and thread-named files once each, pinned first then newest, with type filtering.
- [ ] AC-03: The Threads pane shows an artifacts shelf with cards (thumbnail or kind tile, title, age), pin and a ... menu (Open, Pin/Unpin, Open thread, Copy path or link), and View all opens Library's Artifacts view; the shelf is hidden when the project has no artifacts.
- [ ] AC-04: The Library has an Artifacts view (list and grid, Type filter, pin) in the same order, readable in light and dark themes.

## Approach

Contract: optional `outputs` on `ProjectLibrarySnapshot` (packages/contracts/src/projectLibrary.ts). Server: `readProjectLibrary` scans the output folders with lstat (apps/server/src/project/ProjectLibrary.ts). Web: pure model `studio/projectArtifacts.ts`, pins hook `useProjectArtifactPins`, data hook `useProjectArtifacts`, shelf component `ProjectArtifactShelf.tsx` in ThreadsPane, and an Artifacts section in LibraryPane. Rejected: server-side pins (no project settings field for UI state; thread pins are already device-local) and reading every thread's messages to collect artifacts (too costly for large projects; the per-thread snapshots already hold them).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Pins are device-local per project, like thread artifact pins → localStorage (reversible).
- D-02 Thread-named files come from the per-thread snapshots this device recorded → only threads opened here contribute them (reversible).
### Open
- none

## Tasks

### T-01 Output files in the Library snapshot
- AC: AC-01 | Files: repositories/anton-abyzov/specweave-studio/packages/contracts/src/projectLibrary.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/project/ProjectLibrary.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/project/ProjectLibrary.test.ts | Test: cd repositories/anton-abyzov/specweave-studio/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/project/ProjectLibrary.test.ts

### T-02 Project artifacts model and pins
- AC: AC-02 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/studio/projectArtifacts.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/studio/projectArtifacts.test.ts | Test: cd repositories/anton-abyzov/specweave-studio/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/studio/projectArtifacts.test.ts

### T-03 Shelf above Threads and Library Artifacts view
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/shell/ProjectArtifactShelf.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/shell/ThreadsPane.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/shell/LibraryPane.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/shell/panes.css, repositories/anton-abyzov/specweave-studio/CHANGELOG.md | Test: cd repositories/anton-abyzov/specweave-studio/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/shell/ProjectArtifactShelf.test.tsx

### T-04 Verify and close 1148
- AC: AC-03, AC-04 | Files: .specweave/increments/1148-project-artifacts-shelf-and-library/reports/ | Test: headless light and dark screenshots of the shelf and Library Artifacts view saved to reports/
