---
increment: 0803-studio-tests-pill-dot-and-responsive
title: Studio Tests — kill stray pill dot + responsive eval-cases grid
type: bug
priority: P2
status: completed
created: 2026-04-28T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Studio Tests — kill stray pill dot + responsive eval-cases grid

## Context

Two cosmetic regressions surfaced in the Studio Tests / Eval-cases panel:

1. **Stray bullet on every filled pill.** `globals.css:268` defined `.pill::before { content:""; width:6px; height:6px; … background: currentColor }` on the **base** `.pill` class. Every filled badge in the studio (`StatusPill`, verdict pills, removed/new tags, leaderboard chips, etc.) inherits this dot, so the "--" StatusPill renders as `● --` next to each test row. The two modifiers actually intended to use the dot — `.pill-installed`, `.pill-own` — aren't referenced anywhere in TSX (grep verified).

2. **Eval-cases grid doesn't stack on narrow widths.** `TestsPanel.tsx:307` hard-codes `gridTemplateColumns: "280px 1fr"`. Below ~700px viewport (mobile, tablet portrait, narrow editor splits) the right detail pane is heavily clipped. Studio is desktop-first but should at least render legibly on a tablet portrait window.

**Source repo**: `repositories/anton-abyzov/vskill/` (eval-ui Studio bundle)
**Distribution**: ship as vskill 1.0.9 patch.

## Goals

- Filled `.pill` consumers (StatusPill, verdict, removed/new, leaderboard) render WITHOUT the leading dot.
- Indicator usage is preserved: `.pill-installed` and `.pill-own` continue to opt-in to the colored dot.
- TestsPanel grid stacks on narrow viewports (≤700px) and stays side-by-side on desktop.
- A regression test asserts the CSS contract so future stylesheet edits don't reintroduce the dot.

## Non-Goals

- Restoring the legacy 6-tab Studio IA (out of scope; 0792 owns IA).
- Full mobile chrome redesign of the studio (sidebars, command bar). Limited to the eval-cases grid.
- Visual restyling of the U/I unit-test badge (already distinct via background color).

## User Stories

### US-001: Cleanly rendered status pill
As a Studio user, I see a filled status badge ("--", "100%", "FAIL") without a stray bullet next to it, so the test-case row reads as `#1 Title  [U]  --` and not `#1 Title  [U]  ●  --`.

**Acceptance Criteria**
- [x] AC-US1-01: Computed `::before` content on a `<span class="pill">` is `none`.
- [x] AC-US1-02: Computed `::before` content on a `<span class="pill pill-installed">` is `""` (dot still renders for indicator usage).
- [x] AC-US1-03: All four StatusPill instances rendered in the test-case list inherit `before-content: none`.

### US-002: Responsive eval-cases grid
As a Studio user on a narrow window (≤700px), the eval-cases panel stacks: the test list is on top and the detail pane is below it, both fully readable.

**Acceptance Criteria**
- [x] AC-US2-01: At viewport width ≤700px, the eval-cases grid resolves to a single column (`grid-template-columns: 1fr`).
- [x] AC-US2-02: At viewport width ≥701px, the eval-cases grid resolves to `280px 1fr` (preserves existing desktop layout).
- [x] AC-US2-03: The test-case list rows still truncate the title with ellipsis on narrow widths (no horizontal overflow).

## Out of Scope

- Mobile-friendly studio shell (top nav, sidebars).
- Touch-target sizing audit.
