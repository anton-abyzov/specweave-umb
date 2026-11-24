# Artifacts drop pull requests and show Markdown like documents

## Problem

Artifacts lists pull requests beside documents, so a project of 495 artifacts is mostly pull request cards that repeat the PRs tab. Anton asked why they count as artifacts at all. Markdown cards are also poor next to Claude's desktop app: a page of 5.5px text lines on a flat tint, where Claude shows a small picture of the rendered document on a tinted card, with the title and age on one line.

## Scope

In: remove pull requests from every artifact list, count and filter; draw Markdown cards as a real small document page with the viewer's structure; cards with a stacked page, per-document tint, title and age on one line; Library list with Name, Thread, Date modified with the full date, Size, sortable headers. Out: thumbnails under thread rows, server-side thumbnails, changes to the PRs tab, live publishing tests.

## Acceptance Criteria

- [ ] AC-01: No pull request appears on the shelf, in Library > Artifacts, its count or its Type filter, whichever source named it; the PRs tab is unchanged.
- [ ] AC-02: A Markdown card shows a raster of its own rendered page: serif title, facts, headings, body and tables from the same `markdownDocument` the viewer uses, with no script or network access.
- [ ] AC-03: Cards show a page standing on a tinted card with a slightly rotated sheet behind it, a tint that differs between documents and stays stable, and the title and age on one line, the title being the document's own heading when the file name is all we had.
- [ ] AC-04: Library list columns are Name, Thread, Date modified (for example Oct 30, 2026, 3:09 PM) and Size; each header sorts, and pinned artifacts stay first.
- [ ] AC-05: Previews stay lazy and bounded: no card reads before it nears the view, far cards hold no preview, and scrolling 495 cards keeps p99 frame time within 2x of the #1178 result (9.3 ms) on the same benchmark.
- [ ] AC-06: The viewer opens a Markdown artifact as a document with its title and facts, light and dark.
- [ ] AC-07: Shipped in a release and checked headless on the installed M4 app, screenshots saved to files.

## Approach

Observed in Claude's shipped code (see `reports/rea-findings.md`): thumbnails are screenshots of the rendered document taken once, cached, and framed by CSS. Our own design keeps the #1178 pipeline: render the Markdown once through `markdownDocument` and react-markdown to inert XHTML, raster via the SVG `foreignObject` path, keep only the WebP in the memory cache. `react-dom/server` loads lazily, only when the first Markdown card reads. Own code and own CSS; no Anthropic source or assets are copied.

Files: `apps/web/src/studio/projectArtifacts.ts`, `useProjectArtifacts.ts`, `artifactPreview.ts`, `artifactPreviewRaster.ts`, new `artifactPreviewMarkdown.tsx`, `components/studio/shell/ProjectArtifactShelf.tsx`, `ProjectArtifactsLibrary.tsx`, `panes.css`, `ProjectWorkspaceSurface.tsx`, tests and fixture under `apps/web/tests/project-artifacts/`.

Rejected: live DOM per card (hundreds of layout trees); server thumbnails (needs storage and a writer on every machine); a hidden browser capture per file (slots and memory far above a raster).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 A link registered in the hub that points at a pull request is dropped too; the PRs tab is where pull requests live.
- D-02 Pages stay white in dark mode, slightly dimmed, because they picture a sheet of paper.
- D-03 The Kind column goes; the row icon and Type filter carry it, and a missing file says so in the Name cell.
### Open
- none

## Tasks

### T-01 Remove pull requests from artifacts
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/projectArtifacts.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/useProjectArtifacts.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/studio/projectArtifacts.test.ts

### T-02 Draw Markdown cards as real pages
- AC: AC-02, AC-03, AC-05 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/artifactPreviewMarkdown.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/artifactPreviewRaster.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/ProjectArtifactShelf.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/panes.css | Test: node apps/web/tests/project-artifacts/verify.mjs

### T-03 Library list columns and sorting
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/ProjectArtifactsLibrary.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/projectArtifacts.ts | Test: node apps/web/tests/project-artifacts/verify.mjs

### T-04 Viewer check and before and after evidence
- AC: AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/tests/project-artifacts/verify.mjs, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/project-artifacts/bench.mjs | Test: node apps/web/tests/project-artifacts/bench.mjs

### T-05 Merge, release and installed check
- AC: AC-07 | Files: none | Test: headless check against the installed app
