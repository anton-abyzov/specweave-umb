# Artifact cards show document previews

## Problem

The Artifacts shelf above Threads shows empty cards with one giant green icon, because most of a project's 495 artifacts are pull requests and the card only knows an icon for them. Documents already preview, but with one sandboxed iframe per HTML card and full-size images per image card, so that approach will not scale to hundreds of cards. The user wants cards like Claude's: a small rendered page on a soft tinted background, and asked what that costs in CPU, memory and disk.

## Scope

In: page-style card thumbnails in the shelf and Library grid; lazy, in-view-only previews; a bounded in-memory cache; a designed card for pull requests, links, designs and other non-document kinds; a repeatable cost benchmark over real report files.

Out: server-side thumbnail generation, a disk cache, changes to what counts as an artifact, the Library list view's rows.

## Acceptance Criteria

- [ ] AC-01: A markdown, text, data or HTML artifact card shows a small page of that document on a soft tinted background, with a second sheet behind it; an image card shows the image scaled down.
- [ ] AC-02: A pull request card shows its state, number, title and repository on a sheet tinted by state, with no giant icon. Links, designs, decks, videos and unreadable files get an equivalent sheet with their own facts.
- [ ] AC-03: A preview is read and rendered only for a card near the viewport, at most 3 at a time, and a card scrolled past quickly reads nothing.
- [ ] AC-04: HTML previews run no script, load nothing from the network and create no iframe.
- [ ] AC-05: Finished previews are kept small in a memory cache bounded by bytes, which evicts least recently used entries; nothing is written to disk. A changed file gets a new preview.
- [ ] AC-06: Scrolling the Library grid across 495 artifacts stays smooth: benchmark p95 frame interval at or under 34 ms, and renderer memory no higher than before this change.
- [ ] AC-07: A benchmark reports CPU, memory and disk per preview and across 495 artifacts, before and after, using real report files on the M4.
- [ ] AC-08: Merged with `gh pr merge --squash --admin`, released, and checked in the installed app on the M4.

## Approach

`apps/web/src/studio/artifactPreview.ts` holds the pure rules (format, lines, key) and the LRU cache. `apps/web/src/studio/artifactPreviewRaster.ts` draws HTML through an SVG `foreignObject` image, which browsers render with scripts and network off, and scales images with `createImageBitmap`, both into a WebP data URL about 336x210. `ProjectArtifactShelf.tsx` gates work with one shared IntersectionObserver and a three-slot limiter. `panes.css` draws the tinted sheet.

Rejected: one iframe per card (a browsing context each), server-side thumbnails (needs a contract change and disk), a persistent cache (re-rendering what is in view is cheap enough to measure, and disk stays at zero).

Risks: a Chromium-only canvas path, so a tainted or failed raster falls back to the page's text as lines; `foreignObject` needs well-formed XHTML, so the page goes through DOMParser and XMLSerializer first.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Lazy previews only for cards in view, cached small and evicted (set by the user's coordinator).
- D-02 Pull requests and other non-document artifacts get a facts card: title, number and state rather than one giant icon (set by the user's coordinator).
- D-03 No disk cache: memory only, unless measurements show re-rendering is expensive.
### Open
- none

## Tasks

### T-01 Benchmark harness and before numbers
- AC: AC-07 | Files: apps/web/tests/project-artifacts/bench.mjs, apps/web/tests/project-artifacts/main.tsx, apps/web/tests/project-artifacts/mocks.tsx | Test: node apps/web/tests/project-artifacts/bench.mjs

### T-02 Preview rules, cache and raster
- AC: AC-03, AC-04, AC-05 | Files: apps/web/src/studio/artifactPreview.ts, apps/web/src/studio/artifactPreviewRaster.ts, apps/web/src/studio/artifactPreview.test.ts | Test: vp test run apps/web/src/studio/artifactPreview.test.ts

### T-03 Card design and lazy thumbnails
- AC: AC-01, AC-02, AC-03 | Files: apps/web/src/components/studio/shell/ProjectArtifactShelf.tsx, apps/web/src/components/studio/shell/panes.css, apps/web/src/studio/projectArtifacts.ts, apps/web/src/components/studio/shell/ProjectArtifactShelf.test.tsx | Test: vp test run apps/web/src/components/studio/shell/ProjectArtifactShelf.test.tsx

### T-04 After numbers and headless screenshots
- AC: AC-06, AC-07 | Files: apps/web/tests/project-artifacts/verify.mjs | Test: node apps/web/tests/project-artifacts/verify.mjs

### T-05 Merge, release and installed check
- AC: AC-08 | Files: none | Test: installed app on the M4 shows the new cards
