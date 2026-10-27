# Design system page reads like a brand book and builds from scratch

## Problem

Anton compared SpecWithCode's design system page with a reference brand-book page (eight screenshots in the coordinator thread, October 26, 2026) and asked for the same approach: "when working with design systems, there are a lot of gaps in display and the way we specify and do everything from scratch."

Headless captures of the current page (`~/.specwithcode/m4/evidence/design-system-authoring/baseline/`) against the reference show these gaps:

- G1. Overview opens on a fact list. The reference opens on a cover: the system's name in its display type, its description and a mosaic of its own colors.
- G2. Section titles are meant to be serif display titles, but `--report-serif` is only defined under `.report-document`, so they render in the sans UI font at 24 px. Cards are tight and the chevron leads every title.
- G3. Value fields are invisible until hovered. The reference shows every value in a bordered field: a swatch inside the color field, a number with a `px` suffix for lengths.
- G4. Text colors carry no contrast check. The reference shows "✓ 14.2:1" on text colors per mode.
- G5. A mode that inherits the first mode's color is only faded. The reference says "Inherits Light".
- G6. Spacing and corner radius are bare numbers, with no picture of the size.
- G7. Typography has no way to add font files. The reference has "Upload font" and a Font files list ("No font files yet").
- G8. Building a system from scratch means adding every token by hand, one dialog at a time. There is no starting set for colors, type, spacing, radius or shadows.
- G9. Corner radius, Spacing and families such as Layout use generic icons in the section column.

## Scope

In: the design system page in `apps/web/src/components/design/systems/workspace/`: the Overview cover, section cards and titles, color/length/shadow value fields, contrast badges, inherited labels, spacing and radius previews, Typography font files, starter sets for empty sections and the welcome sheet, section icons. The headless fixture `apps/web/tests/design-workspace-1046` and focused unit tests.

Out: server, contracts and RPC changes (the operations limit of 2,000 per apply is enough); the component preview runner and import (1083/1084, PRs #816 and #834); release and installation (the release owner's); the sample Weave brand as anyone's default.

## Acceptance Criteria

- [ ] AC-01: Overview opens on a cover built from the system's own data: its name in its display font when it has one, its description, and a mosaic of up to eight of its own base-mode colors. A system with no colors shows the cover without a mosaic. Facts (modes, contents, sources, designs, revision) follow in a compact list.
- [ ] AC-02: Section titles render in the serif display face at 32 px or more in rounded cards with generous padding; a section still collapses and its count and "+ Add" stay in the header.
- [ ] AC-03: Every color value sits in a visible bordered field with its swatch inside, opening the existing color editor. Spacing and corner radius values in px, rem or em show a number field with the unit as a suffix; other values show a visible bordered text field. Enter or leaving saves and Escape restores, as before.
- [ ] AC-04: Text colors (ink, text, foreground, fg, on-…) show their contrast ratio against the mode's ground (or, for on-X, against X) in each mode: a check at 4.5:1 or more, a warning below.
- [ ] AC-05: A later mode without its own color shows its inherited swatch and the words "Inherits <first mode>".
- [ ] AC-06: Spacing rows show a bar of the value's length, and corner radius rows show a corner drawn at that radius.
- [ ] AC-07: Typography has "Upload font" in its header and in its empty state, storing woff, woff2, ttf and otf files under `fonts/`, and ends with a Font files list that says "No font files yet" when empty.
- [ ] AC-08: An empty Colors, Typography, Spacing, Corner radius or Shadows section offers a starter set built from neutral defaults (an accent the person picks for colors, a font family for type). The welcome sheet offers all five at once. Each adds every token in one undoable edit, skips names already present, and never uses a sample brand's names or values.
- [ ] AC-09: The section column uses distinct icons for Spacing, Corner radius, Layout, Size and Motion.

## Approach

Web only, in the workspace folder:

1. `starterSets.ts` (new, pure): palette from an accent (neutrals tinted toward its hue, light and dark values for a light first mode and any dark mode), type scale from a family, 4 px spacing scale, radius set, two shadows. A new `add-many` intent in `systemEditIntents.ts` maps to one `put_token` per new name; `inverseOperations` already deletes tokens that did not exist, so Undo works unchanged.
2. `contrast.ts` (new, pure): relative luminance and ratio with alpha composited over the ground, plus which tokens are text colors and what they sit on.
3. `OverviewCover.tsx` (new) and `OverviewSection.tsx`: cover, mosaic and compact facts.
4. `SystemWorkspace.tsx`: the page root defines the serif face; the Overview card has no sticky header (the cover's name is its heading); titles grow; starter offers in `Empty`. Edits stay away from the lines PR #834 changes.
5. `ColorTable.tsx`, `NameValueTable.tsx`, `tokenRows.tsx`: bordered fields, contrast badges, "Inherits", unit fields, previews, roomier rows.
6. `TypographyTable.tsx` plus `FontFiles.tsx` (new): Upload font and the font file list, reusing `planUploads`, `uploadAll` and `useSystemFilesApi`.
7. `SystemNav.tsx`: icons.
8. Fixture: an empty-system scene exercising the starter sets; captures in light and dark at 1440 and 390 px.

Rejected: generating raster icons with Kie AI for the section column. Lucide covers every section, follows `currentColor` in both themes and matches the rest of the app's strokes; raster icons would not.

Risks: PR #834 changes `SystemWorkspace.tsx` imports and the Components branch of `SectionBody`; this increment leaves those lines alone and rebases if #834 merges first.

## Decisions

### Asked
- none (the coordinator gave the default interpretation; Anton's request is the brief)
### Defaulted (change any before sw-do)
- D-01 Starter colors derive from one accent the person picks (default a neutral blue, `#2f6fed`, chosen apart from the Weave sample's `#3b6cf6`), never from a sample brand. Names use the plain `color-*`, `font-*` (families), `type-*` (styles), `space-*`, `radius-*`, `shadow-*` prefixes. An accent that is not hex or rgb() disables Add rather than falling back.
- D-02 Contrast badges show only on text colors (ink, text, foreground, fg, on-…), as the reference does, not on every color.
- D-03 Kie AI icons are not used: lucide covers all sections and adapts to both themes. Recorded in the report.
- D-04 Spacing and radius previews are added although the reference has none, because the coordinator asked for visual previews of spacing and radii.
### Open
- none

## Tasks

### T-01 Starter sets and the add-many edit
- AC: AC-08 | Files: apps/web/src/components/design/systems/workspace/starterSets.ts, systemEditIntents.ts, starterSets.test.ts, systemEditIntents.test.ts | Test: `node node_modules/vite-plus/bin/vp test run apps/web/src/components/design/systems/workspace/starterSets.test.ts apps/web/src/components/design/systems/workspace/systemEditIntents.test.ts`

### T-02 Contrast model
- AC: AC-04 | Files: apps/web/src/components/design/systems/workspace/contrast.ts, contrast.test.ts | Test: `node node_modules/vite-plus/bin/vp test run apps/web/src/components/design/systems/workspace/contrast.test.ts`

### T-03 Overview cover and section cards
- AC: AC-01, AC-02 | Files: OverviewCover.tsx, OverviewSection.tsx, SystemWorkspace.tsx | Test: workspace unit tests plus headless captures `scene=system` light and dark

### T-04 Visible value fields, contrast badges, inherited labels and previews
- AC: AC-03, AC-04, AC-05, AC-06 | Files: ColorTable.tsx, NameValueTable.tsx, ShadowTable.tsx, tokenRows.tsx | Test: `tables.test.tsx` plus headless captures

### T-05 Typography font files
- AC: AC-07 | Files: TypographyTable.tsx, FontFiles.tsx, SystemWorkspace.tsx | Test: focused unit test plus headless capture

### T-06 Starter offers on empty sections and the welcome sheet
- AC: AC-08 | Files: SystemWorkspace.tsx, StarterOffer.tsx, WelcomeSheet.tsx | Test: headless fixture `scene=empty`: add every starter set, then Undo

### T-07 Section icons
- AC: AC-09 | Files: SystemNav.tsx | Test: headless capture of the section column

### T-08 Verify and close 1090
- AC: AC-01 to AC-09 | Files: reports/ | Test: web typecheck, focused workspace tests, headless captures light and dark at 1440 and 390 px, PR checks green, fresh-context review
