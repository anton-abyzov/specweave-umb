# Library resizable columns and find

## Problem

In the project Library pane, long file and design names are clipped, while Date modified, Size and Kind keep fixed tracks. Columns can't be resized. Find keeps every folder in the results whatever the query, and it only searches rows that are already expanded, so it neither behaves like Finder nor states its scope.

Source facts, from `origin/main` `6041021dd1` (October 23, 2026), `apps/web/src/components/studio/shell/LibraryPane.tsx`, 597 lines:

- Filter predicate (lines 279-285): `needle === "" || row.kind === "directory" || row.name.toLowerCase().includes(needle)`. Every folder passes the filter, and only flattened, expanded rows are searched.
- Column tracks (`apps/web/src/components/studio/shell/panes.css:171-177`): `minmax(0, 1fr) 118px 70px 92px`. Under 460px a container query keeps only Name and Size.
- The table already declares `role="treegrid"` with four `columnheader` spans, but has no sortable headers and no full treegrid keyboard model.
- Main adds a Designs group (`DESIGNS_ROW`, row kind `design`, from `useProjectDesigns`). The design proposal inspected an older checkout (`bc3fabf567`) that lacks this group.

Design proposal (reviewable, design only): `/Users/antonabyzov/.specwithcode/m4/evidence/library-columns-design-20261024/proposal.md`. Static mockup: `/Users/antonabyzov/.specwithcode/m4/evidence/library-columns-design-20261024/mockup.html`. Captures: `/Users/antonabyzov/.specwithcode/m4/evidence/library-columns-design-20261024/wide-dark.png` and `/Users/antonabyzov/.specwithcode/m4/evidence/library-columns-design-20261024/narrow-light.png`. These are static captures; they don't show interaction or the installed app working.

## Scope

In:
- column resizing by pointer, keyboard and menu, with Fit and Reset;
- per-device persistence of widths and sort;
- sortable headers;
- an explicit Find scope (Current folder or collection, plus Loaded folders), with type-ahead kept separate from Find;
- ancestry shown on results, and state preserved across filtering;
- distinct copy for empty, loading, denied, offline, stale and error states;
- a coherent treegrid keyboard model, or a downgrade to list semantics.

Out:
- recursive or content search, or Spotlight;
- any new backend search API;
- syncing widths across devices;
- artifact shelf files (1049);
- Design gallery and editor (1041, 1046);
- the agent popover (1057).

## Ownership reconciliation (October 24, 2026)

- `LibraryPane.tsx` has no active owner. The `design-project-link`, `fix-1001-increment-binding-transport` and `fix-question-reply-provenance-1042` worktrees list it as changed, but their copies match `origin/main`. No 1041 or 1046 worktree changes it or the `sws-library` rules.
- 1049 owns `ArtifactShelfList.tsx`, `ThreadArtifacts.tsx`, `artifactShelf.ts`, `useArtifactShelfState.ts`, `nativeArtifacts.ts`, the kv card and the file reader close button. It does not own `LibraryPane.tsx`. This increment reuses 1049's artifact data as-is and edits none of those files.
- `panes.css` is shared: 1053 changes one subagent rule, and 1057 will change the subagent popover rules. This increment touches only `.sws-library-*` rules. Rebase on whichever merges first.
- `apps/web/src/components/studio/shell/` is in active use. Before claiming T-02, re-run the worktree scan for `LibraryPane.tsx`.

## Acceptance Criteria

- [ ] AC-01: Columns resize by pointer drag (8px target, pointer capture), by keyboard on a focusable separator (Left/Right 8px, Shift 32px, Home/End to bounds, Escape restores the start width) and from a column menu (Fit loaded names, Reset widths). Bounds hold. A drag never sorts or opens a row. Widths and sort persist per device per Library view. Corrupt or missing storage falls back to defaults.
- [ ] AC-02: Find's Current folder scope matches folders as well as files by name. Folders that don't match are no longer kept. Loaded folders is a separate, labelled scope that searches only cached entries and never triggers a directory load. The Designs and Artifacts collections search their own loaded snapshot and report partial coverage while loading.
- [ ] AC-03: Type-ahead (list focused, printable keys) only moves the selection and never filters, expands or fetches. It ignores inputs, IME composition and shortcut chords. In Find, Escape clears the query, then a second Escape returns focus to the list without closing the reader.
- [ ] AC-04: Sorting by Name, Modified, Size or Kind keeps folders first. Unknown values sort last, and ties break on a stable id. Filtering, sorting, refresh and late responses keep the selected row's identity, expansion and scroll anchor, including when two entries share a name. Results show their parent path.
- [ ] AC-05: No matches, empty folder, loading, permission denied, offline, stale and failed load each have distinct copy and a safe action (Clear filters, or Retry for that scope). No extra grant is ever requested automatically.
- [ ] AC-06: The treegrid exposes the full keyboard model, or it is downgraded to list or tree semantics with separate sort buttons. axe reports no violations. Headless captures and interaction checks pass at 390, 768 and 1440px, in dark and light, at 200% zoom, keyboard-only and with touch emulation, and with a large loaded dataset under rapid query and scope switching. Each run sets `headless: true`, `PWDEBUG=0` and `PLAYWRIGHT_HTML_OPEN=never`, and saves its files under this increment's `evidence/`.
- [ ] AC-07: A fresh-context review passes.

## Approach

1. New file `apps/web/src/components/studio/shell/libraryFind.ts`: pure scope, match, sort and type-ahead functions, unit-tested. The filter predicate moves out of `LibraryPane.tsx` and into this file.
2. New file `apps/web/src/components/studio/shell/libraryColumns.ts`: width state, clamping, versioned localStorage schema, and Fit measured from loaded rows only.
3. `LibraryPane.tsx`: header separators, sort buttons, the Find scope control, state copy, and the treegrid decision.
4. `panes.css`: `.sws-library-*` only. Tracks become CSS variables (`--lib-col-modified` and so on), and Name stays `minmax(0, 1fr)`.
5. Headless fixture at `apps/web/tests/library-columns/`.

Corrections to the proposal:

- Default widths stay at main's 118/70/92px. The proposal's 150/80/100 would widen the metadata columns, the opposite of giving names room.
- Main already declares a treegrid, so the choice is to finish it or downgrade it, not to keep it as it is.
- The compact layout builds on the existing 460px container query rather than adding a second breakpoint.

Rejected:
- Recursive descendant search, because there is no authorized, bounded backend search.
- Width sync across devices.
- Filtering while the person types into the list.

## Decisions

### Asked
- none (awaits Anton's review of the proposal)
### Defaulted (change any before sw-do)
- D-01: Defaults are main's 118/70/92px. Resize bounds are the proposal's Name 220-900, Modified 112-260, Size 64-160 and Kind 80-220, to be checked at 200% zoom.
- D-02: Find defaults to Current folder. Loaded folders is opt-in.
- D-03: The treegrid is downgraded to list semantics with sort buttons unless T-03 completes the full treegrid model within the 1,500-line file limit.
### Open
- none

## Tasks

### T-01 Anton reviews the proposal and these corrections
- AC: AC-01, AC-02 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/library-columns-design-20261024/proposal.md | Test: test -s /Users/antonabyzov/.specwithcode/m4/evidence/library-columns-design-20261024/proposal.md

### T-02 Pure find, sort and type-ahead functions
- AC: AC-02, AC-03, AC-04 | Files: apps/web/src/components/studio/shell/libraryFind.ts, apps/web/src/components/studio/shell/libraryFind.test.ts | Test: npx vp test run apps/web/src/components/studio/shell/libraryFind.test.ts

### T-03 Resizable columns, persistence, sort headers, treegrid decision
- AC: AC-01, AC-04, AC-06 | Files: apps/web/src/components/studio/shell/libraryColumns.ts, apps/web/src/components/studio/shell/LibraryPane.tsx, apps/web/src/components/studio/shell/panes.css | Test: npx vp test run apps/web/src/components/studio/shell/libraryColumns.test.ts

### T-04 Find scope control and state copy
- AC: AC-02, AC-05 | Files: apps/web/src/components/studio/shell/LibraryPane.tsx | Test: npx vp test run apps/web/src/components/studio/shell/LibraryPane.test.tsx

### T-05 Headless interaction and capture matrix
- AC: AC-06 | Files: apps/web/tests/library-columns/ | Test: PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never node apps/web/tests/library-columns/verify.mjs

### T-06 Verify and close 1059
- AC: AC-07 | Files: .specweave/increments/1059-library-resizable-columns-and-find/reports/review.md | Test: specweave verify 1059-library-resizable-columns-and-find
