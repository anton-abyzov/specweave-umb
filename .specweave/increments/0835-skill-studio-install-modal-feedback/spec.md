---
increment: 0835-skill-studio-install-modal-feedback
title: 'Skill Studio: in-panel install feedback + escape hotkey'
type: feature
priority: P1
status: completed
created: 2026-05-09T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Studio — in-panel install feedback + escape hotkey

## Overview

The Skill Studio detail page (`/studio/find/[owner]/[repo]/[skill]`) renders an `InstallPanel` whose "Install" button copies the install command to clipboard. Today the post-click feedback is a small muted inline message ("Run `<command>` in your terminal") rendered below the multi-variant code block. From the user's vantage point — especially on a wider monitor where the message lives below the fold of the install action — the feedback is easy to miss and reads as an unreadable toast.

This increment promotes the feedback to a prominent in-panel banner with explicit success/error states, places it directly under the Install CTA so the eye lands on it, and wires the page-level Escape hotkey hinted at by the existing "Esc" affordance so keyboard users can return to results without reaching for the mouse.

## User Stories

### US-001: Prominent install feedback inside the install panel (P1)
**Project**: vskill-platform

**As a** developer browsing skills in Skill Studio
**I want** clear feedback inside the install panel after I click "Install"
**So that** I know whether the command was copied to my clipboard without hunting for a tiny toast

**Acceptance Criteria**:
- [x] **AC-US1-01**: After a successful clipboard write, the panel renders a banner directly under the Install button with: a leading `✓` glyph, the text "Copied — paste in your terminal to install", and the copied command shown in monospace below. Font size is at least `0.9375rem` (15px) and uses `var(--status-success-text)` / `var(--status-success-bg)` / `var(--status-success-border)` design tokens.
- [x] **AC-US1-02**: When the clipboard write fails (insecure context, permission denied, or both clipboard + execCommand fallbacks return false), the panel renders a banner with a leading `✕` glyph, the text "Copy failed — please copy manually", and the command rendered selectable in monospace. Banner uses `var(--status-danger-text)` / `var(--status-danger-bg)` / `var(--status-danger-border)`.
- [x] **AC-US1-03**: The banner has `role="status"` and `aria-live="polite"` so screen readers announce success/error without stealing focus.
- [x] **AC-US1-04**: The banner replaces the existing `data-testid="studio-install-toast"` element. Tests targeting that selector continue to pass; new selectors `studio-install-feedback-success` and `studio-install-feedback-error` exist for the two states.
- [x] **AC-US1-05**: Both the primary "Install" button and the per-variant "Copy" buttons drive the same feedback banner via the shared `runInstallAction` callback (and a parameterized variant copy handler) — no behavior divergence between the two paths.
- [x] **AC-US1-06**: After 6 seconds the banner auto-dismisses (idle state). Clicking Install again resets the timer and re-asserts the banner.

### US-002: Escape returns to results from the detail page (P1)
**Project**: vskill-platform

**As a** keyboard-driven user on a Skill Studio detail page
**I want** Escape to take me back to the search results
**So that** the visible "Esc" affordance on the page actually works without needing the mouse

**Acceptance Criteria**:
- [x] **AC-US2-01**: Pressing Escape on the detail page navigates the router to `backHref` (the same destination as the "← Back to results" link).
- [x] **AC-US2-02**: When the global SearchPalette is open, Escape closes the palette FIRST and does NOT trigger detail-page back navigation. The palette's existing Esc handler keeps precedence.
- [x] **AC-US2-03**: Escape is ignored when focus is inside an `<input>`, `<textarea>`, `<select>`, or any element with `contenteditable="true"` so keyboard users editing text are not bounced off the page.
- [x] **AC-US2-04**: A visible `<kbd>Esc</kbd>` affordance appears next to the "← Back to results" link so the keyboard shortcut is discoverable. The affordance uses the same kbd styling as `SearchPalette` for consistency.
- [x] **AC-US2-05**: The Escape listener is registered on mount and removed on unmount. No listener leaks across navigations (verified by spy-test: `removeEventListener` is called with the same handler reference on cleanup).

### US-003: Predictable next-step affordance after success (P2)
**Project**: vskill-platform

**As a** developer who just copied an install command
**I want** an obvious path back to results without losing my command
**So that** I can keep browsing without re-typing my query

**Acceptance Criteria**:
- [x] **AC-US3-01**: On a successful copy via the **primary Install CTA**, the "← Back to results" link receives keyboard focus (`focus()`) so pressing Enter completes the round-trip without using the mouse. Per-variant Copy chips (npm/bun/pnpm/yarn/alternative) deliberately do NOT move focus so users can keep browsing variants without being yanked to the page header.
- [x] **AC-US3-02**: The page does NOT auto-navigate away on success — the user keeps the command on screen and explicitly chooses to return (Enter on focused link, click, or Esc).
- [x] **AC-US3-03**: Focus management respects `prefers-reduced-motion` users: no scroll-to-top, no scroll-into-view smooth animation. Just `link.focus({ preventScroll: true })`.

## Functional Requirements

### FR-001: Feedback state machine
`InstallPanel` exposes three feedback states: `idle | success | error`. A successful clipboard write transitions to `success`; a failed write transitions to `error`. Auto-dismiss returns to `idle` after 6 seconds. A subsequent click resets the timer.

### FR-002: Page-level Escape handler
The Studio detail page (`page.tsx`) mounts a small client component (`DetailPageEscape`) that registers a `keydown` listener on `window` for `key === "Escape"`. The handler:
1. Bails if the SearchPalette is open (`document.querySelector('[data-testid="search-palette-open"]')` or equivalent state attribute).
2. Bails if focus is in an editable target (`isInteractiveTarget` predicate).
3. Calls `router.push(backHref)`.

The handler unregisters on unmount.

### FR-003: Escape kbd affordance
A `<kbd>Esc</kbd>` chip renders inline next to the "← Back to results" link so keyboard discoverability matches the existing visual convention from `SearchPalette`.

## Success Criteria

- All ACs above pass via Vitest unit tests + Playwright e2e.
- Lighthouse a11y score for `/studio/find/[owner]/[repo]/[skill]` does not regress (current baseline >= 95).
- No new console errors in dev or prod build.
- Manual smoke: in `npx vskill@latest studio`, the install banner is the first thing the eye lands on after clicking Install on a 13" laptop screen.

## Out of Scope

- Adding a real install endpoint (current behavior is clipboard-copy only — out of scope for this increment).
- Changing the multi-variant terminal block layout.
- Modifying the SearchPalette's own Esc behavior.
- Adding a "Open in terminal" deep link.
- Toast/banner for the per-variant Copy chip rows (they share the banner with the primary CTA per AC-US1-05; per-variant inline confirmations stay out of scope).

## Dependencies

- Existing `InstallPanel.tsx` and `page.tsx` in `repositories/anton-abyzov/vskill-platform/src/app/studio/find/[owner]/[repo]/[skill]/`.
- Existing `SearchPalette.tsx` Escape semantics (no changes required).
- Status design tokens (`--status-success-*`, `--status-danger-*`) already defined in the platform stylesheet.
