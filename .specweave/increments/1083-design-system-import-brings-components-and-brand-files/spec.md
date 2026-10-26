# Design system import brings components and brand files

## Problem

EasyChamp's saved design system "Matchday (EasyChamp UI Kit)" shows 273 tokens but "No components yet" and an empty Assets section, while the same kit in Claude Design shows components and assets. Its `system.json` records one source, `ec-uikit/src/styles/tokens.css`: it was imported before the scan grouped a package's component barrels into its suggestion. Rescan only rereads recorded sources, so it can never add the 26 component barrels (321 components) the scan now offers. Separately, no import path copies brand files (README, logos, fonts) into the system's stored files, so Assets stays empty for every imported system.

## Scope

In: Rescan adds the component (or token) sources the package now offers when the system has none of that kind; code imports propose brand files from the package and from folders holding copies of its tokens, the review lists them, and confirm stores the ticked ones without overwriting stored files. Re-import EasyChamp. Out: Storybook rendering of components, Claude Design import, a SpecWithCode release.

## Acceptance Criteria

- [ ] AC-01: Rescanning a code system that has tokens but no components, in a package whose scan offers component sources, returns a "changed" proposal whose components come from those sources and names them as added.
- [ ] AC-02: A code proposal lists brand files found in the package (README, docs Markdown, brand/logo images, fonts with their licenses) and in brand or fonts folders next to copies of its tokens, deduplicated by content, within size and count caps, skipping paths the system already stores.
- [ ] AC-03: Confirming a proposal writes the ticked brand files into the system's stored files (README to Overview, images to Assets, fonts to Typography, Markdown to docs) and leaves unticked or already stored files alone; reads stay inside the project root.
- [ ] AC-04: The review dialog shows the brand files with checkboxes; the rescan notice counts added sources.
- [ ] AC-05: EasyChamp's Matchday system, rescanned and confirmed, shows its components and its brand assets in the app.

## Approach

Contracts: optional `files` on a proposal, `excludeFiles` on confirm, `copies` on a code propose, `added` on a changed rescan. Server: `brandFiles.ts` finds brand files with a byte-safe `readBytesInsideRoot`; `DesignSystemService` attaches them in `finish` for code proposals, writes them in `confirm`, and widens `rescan` with a fresh scan. Web: review lists files, ScanFromCode passes copies, rescan toast counts added sources.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Rescan adds offered sources only for a kind the system holds none of (components when it has no components), so deliberate deselections of extra token files are not re-proposed on every rescan.
- D-02 Brand files never overwrite a stored file; a stored path is skipped.
- D-03 Brand files alone make a rescan "changed" only when the system stores no files yet.

### Open
- none

## Tasks

### T-01 Rescan adds offered component sources
- AC: AC-01 | Files: apps/server/src/design/systems/DesignSystemService.ts, packages/contracts/src/designSystemImport.ts | Test: pnpm --dir apps/server exec vp test run src/design/systems/DesignSystemService.test.ts

### T-02 Brand files in proposals and confirm
- AC: AC-02, AC-03 | Files: apps/server/src/design/systems/brandFiles.ts, apps/server/src/design/systems/scanCandidates.ts, apps/server/src/design/systems/DesignSystemService.ts | Test: pnpm --dir apps/server exec vp test run src/design/systems/brandFiles.test.ts src/design/systems/DesignSystemService.test.ts

### T-03 Review and rescan UI
- AC: AC-04 | Files: apps/web/src/components/design/systems/DesignSystemReview.tsx, apps/web/src/components/design/systems/reviewModel.ts, apps/web/src/components/design/systems/ScanFromCode.tsx | Test: pnpm --dir apps/web exec vp test run src/components/design/systems

### T-04 Re-import EasyChamp and verify in the app
- AC: AC-05 | Files: (EasyChamp .specweave/design) | Test: rescan and confirm through the service, then a headless screenshot of Components and Assets
