# Redesign the Overview start page

## Problem

Anton's November 6, 2026 screenshot of Overview ("Control desk") shows 16 chats waiting. The count appears four times, and the first three waiting chats show twice above the fold, in Needs you and again at the top of Sessions. Needs you pages 3 at a time (6 pages), so 13 of the 16 are hidden. Sessions pages 941 chats 8 at a time (118 pages). "Partial observations; some hosts are not current" doesn't name the machine or the fix. The filter tablist has no arrow-key handling. Status colours are hard-coded hex, not theme tokens. The page says "session" and "host" while the sidebar says "chat" and "machine". Review and mockup: `~/.specwithcode/m4/evidence/overview-redesign-1249/compare.html`.

## Scope

In: the web Overview (`apps/web/src/components/studio/StudioOverview.tsx`, `overview.css`, `apps/web/src/studio/overviewModel.ts`, i18n phrases), laid out as in `~/.specwithcode/m4/evidence/overview-redesign-1249/proposal.html`. Also in, from Anton's approval: machine filtering, clickable counts, a compact Blocked note (`apps/web/src/components/chat/ThreadBlockerNote.tsx`) and a collapsible Artifacts strip in the file preview. Out: the mobile home screen (follow-up increment), CapacityFleet internals, and new data such as ask excerpts.

## Acceptance Criteria

- [ ] AC-01: The headline states the waiting count ("16 chats need you", or a clear-desk line when there are none), with one summary line linking projects and machines. The four stat cards, the eyebrow and "Control desk" are gone.
- [ ] AC-02: When attention is incomplete, a notice names each machine that is not current and its state (offline, reconnecting, catching up), and links to Connections. The app keeps no last-report time, so none is shown. The phrase "Partial observations" no longer appears.
- [ ] AC-03: Needs you is one compact list grouped by attention kind, ordered failed, sign-in, approval, answer, plan, reply, limited, held, stalled. It shows 8 rows, then "Show N more" that expands in place, with no pager.
- [ ] AC-04: Working lists running chats, with an empty state when there are none. Recent lists only chats that are neither waiting nor working, with Open/Done tabs, Today/Yesterday/Earlier groups, a name filter and "Show 20 more" instead of a pager.
- [ ] AC-05: On wide screens (≥ 1100 px content), Projects (with per-project waiting counts) and Machines (state, version, last report) sit in a right rail. Below that width they follow Recent. The settings link cards and the footer taglines are removed.
- [ ] AC-06: Keyboard: J/K move a visible selection through the Needs you, Working and Recent rows, Enter opens it, N opens the new-chat chooser, and / focuses the filter. None of these fire while typing in an input. The Open/Done tabs use arrow keys with roving tabindex.
- [ ] AC-07: Status colours use theme tokens (`--warning`, `--warning-surface`, `--destructive`, `--destructive-surface`, `--success`), with no hard-coded amber or red hex in `overview.css`.
- [ ] AC-08: Visible wording uses chat and machine: "New chat" replaces "New session" and "Machines" replaces "Hosts".
- [ ] AC-09: Headless screenshots in light and dark at 1440, 1024, 768 and 390 px, plus 580 px (the 840 px Electron minimum with the sidebar), match the mockup's layout with no horizontal overflow.
- [ ] AC-10: Everything that looks clickable is a real link or button with a focus ring: every row, the summary's projects/machines/working links, each project's waiting-count chip (filters Needs you to that project), the notice's Check connection, Manage and Connections.
- [ ] AC-11: Clicking a machine filters Needs you, Working and Recent to that machine and shows its projects with their counts. A removable "On m1 ×" chip clears the filter. The machine row's gear opens Connections (the page has no per-machine anchor yet).
- [ ] AC-12: The thread's Blocked note no longer covers the transcript. It shows one line ("Blocked: <first sentence>") that expands on click and collapses again. When the latest reply already shows the same blocker text in view, the note stays collapsed to that line.
- [ ] AC-13: The file preview's Artifacts strip can be collapsed to its header ("Artifacts 4 ⌄"). The choice persists per device, and the collapsed state gives the preview the freed height.

## Approach

Rewrite the render part of `StudioOverview.tsx`. Data derivation (`deriveSessions`, attention completeness, project grouping) stays. Add `attentionRank(kind)` to `overviewModel.ts` and a small `groupByDay` helper. Move the waiting count into the masthead and delete `Stat`, `Pager` and the control links. Keep the draft chooser and CapacityFleet, placing CapacityFleet below the rail on wide screens and last on narrow ones. Machines read from `useEnvironments()` plus the attention members' freshness. The keyboard lives in one `useOverviewKeys` hook on the page root. Keep the file under 1,500 lines by moving rows to `OverviewRows.tsx`. Rejected: keeping the stat cards smaller (still repeats the count) and infinite scroll (unbounded rendering of 941 rows).

## Decisions

### Asked
- D-01 Approve the redesign in `compare.html`? → Yes, as proposed (Anton, November 6, 2026), plus: render well on every device, every link clickable, machines clickable to their projects, Blocked note must not hide the thread, Artifacts strip collapsible, small polish where it helps.
### Defaulted (change any before sw-do)
- D-02 Vocabulary → "chat" and "machine", to match the sidebar.
- D-03 Mobile home Needs you group → separate follow-up increment.
- D-04 Shared checkout `specwithcode-dev`: start only after "1249 may branch" from Worker card task line. When done, leave it clean on `main` and send "1254 may branch" to the Grok install fails on M1 thread (1254), which hands to 1250 after it.
### Open
- none

## Tasks

### T-01 Order and group attention, day groups
- AC: AC-03, AC-04 | Files: apps/web/src/studio/overviewModel.ts, apps/web/src/studio/overviewModel.test.ts | Test: cd apps/web && npx vitest run src/studio/overviewModel.test.ts

### T-02 New Overview layout, wording and tokens
- AC: AC-01, AC-02, AC-04, AC-05, AC-07, AC-08 | Files: apps/web/src/components/studio/StudioOverview.tsx, apps/web/src/components/studio/OverviewRows.tsx, apps/web/src/components/studio/overview.css, apps/web/src/i18n/phrases/*.ts | Test: cd apps/web && npx vitest run src/components/studio/StudioOverview.test.tsx

### T-03 Keyboard navigation
- AC: AC-06 | Files: apps/web/src/components/studio/useOverviewKeys.ts, apps/web/src/components/studio/StudioOverview.test.tsx | Test: cd apps/web && npx vitest run src/components/studio/StudioOverview.test.tsx

### T-04 Headless screenshots and PR
- AC: AC-09 | Files: apps/web/src/components/studio/overview.css | Test: headless Playwright capture, light and dark at 1440 and 390 px, saved to ~/.specwithcode/m4/evidence/overview-redesign-1249/built/

### T-05 Machine filter and clickable counts
- AC: AC-10, AC-11 | Files: apps/web/src/components/studio/StudioOverview.tsx, apps/web/src/components/studio/OverviewRows.tsx, apps/web/src/components/studio/StudioOverview.test.tsx | Test: cd apps/web && npx vitest run src/components/studio/StudioOverview.test.tsx

### T-06 Compact Blocked note and collapsible Artifacts strip
- AC: AC-12, AC-13 | Files: apps/web/src/components/chat/ThreadBlockerNote.tsx, apps/web/src/components/chat/ThreadBlockerNote.test.tsx, apps/web/src/components/files/FilePreviewPanel.tsx | Test: cd apps/web && npx vitest run src/components/chat/ThreadBlockerNote.test.tsx

### T-07 Verify and close 1249
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13 | Files: .specweave/increments/1249-redesign-the-overview-start-page/spec.md | Test: specweave verify 1249-redesign-the-overview-start-page
