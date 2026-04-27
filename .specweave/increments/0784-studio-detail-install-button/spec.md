---
increment: 0784-studio-detail-install-button
title: "Studio detail: primary Install button + readability pass"
type: feature
priority: P2
status: planned
created: 2026-04-27
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio detail — primary Install button + readability pass

## Overview

In Skill Studio's skill detail page (`/studio/find/[owner]/[repo]/[skill]`), the only install affordance today is a small **Copy** chip overlaid on the install-command terminal block. There is no prominent "Install" call-to-action — users see only a command line. The public marketplace (`verified-skill.com`) renders a primary blue **Install** button on its results cards via [InstallButton.tsx](repositories/anton-abyzov/vskill-platform/src/app/studio/find/components/InstallButton.tsx). This increment ports that pattern to the Studio detail page so that selecting a skill always offers a clear primary CTA, while preserving the command line + Copy chip for transparency.

The same surface has a readability problem: several supporting labels in the detail header use `--text-faint` (`#767676` against `#FFFFFF` ≈ 4.54:1), only barely WCAG-AA. Those swap to `--text-muted` (`#666666`, ≈ 5.74:1) where they're informational text rather than decoration.

## User Stories

### US-001: Primary Install button on Studio skill detail (P2)
**Project**: vskill-platform

**As a** Skill Studio user viewing a skill's detail page
**I want** a prominent **Install** button as the primary action
**So that** I can install the skill in one click without parsing the install command

**Acceptance Criteria**:
- [x] **AC-US1-01**: A button with visible text "Install" renders inside `InstallPanel`, above the existing `TerminalBlock`, with `data-testid="studio-install-primary-button"`.
- [x] **AC-US1-02**: Clicking the Install button writes the version-aware install command (e.g. `vskill install anton-abyzov/hi-anton/hi-anton` for the default version, `…@<version>` when a non-default version is selected) to `navigator.clipboard`.
- [x] **AC-US1-03**: After a successful copy, a `role="status"` toast appears containing the text "Run `vskill install …`" matching the copied command.
- [x] **AC-US1-04**: A successful click fires exactly one `POST /api/v1/studio/telemetry/install-copy` request via `authFetch` with body `{ skillName, q: "", ts, version? }` (version omitted when default selection).
- [x] **AC-US1-05**: The Install button is `disabled` when the skill name fails the existing `SAFE_NAME` regex (`/^[a-zA-Z0-9._@/-]+$/`).
- [x] **AC-US1-06**: When the skill is on the blocklist (`isBlocked && blockedEntry`), the Install button is NOT rendered (the panel short-circuits to `BlockedSkillView`, matching existing behavior).
- [x] **AC-US1-07**: The existing terminal block + Copy overlay button remain visible and functional. Both buttons share a single `runInstallAction()` callback so they have identical copy + toast + telemetry behavior.
- [x] **AC-US1-08**: Clicking the Copy overlay then the Install button (or vice-versa) fires telemetry twice and triggers two clipboard writes — neither button gates the other.

---

### US-002: Readable text on Studio skill detail (P2)
**Project**: vskill-platform

**As a** Skill Studio user with average vision in light theme
**I want** informational labels on the detail page to meet WCAG-AA contrast
**So that** I can read publisher, version, and supporting metadata without strain

**Acceptance Criteria**:
- [x] **AC-US2-01**: In `page.tsx`, the publisher prefix `<span>` inside the title uses `var(--text-muted)` (was `--text-faint`).
- [x] **AC-US2-02**: In `page.tsx`, the "Skill v…" chip in the badge row uses `var(--text-muted)` (was `--text-faint`).
- [x] **AC-US2-03**: In `page.tsx`, `bylineStyle.color` is `var(--text-muted)` (was `--text-faint`). The dot-separator (`bylineSep`) keeps `--text-faint` since it is decorative.
- [x] **AC-US2-04**: In `page.tsx`, the "See all versions →" link uses `var(--accent-teal)` to match the existing "Submit your skill →" link affordance.
- [x] **AC-US2-05**: In `InstallPanel.tsx`, the footer "Don't see what you need?" surrounding text uses `var(--text-muted)` (was `--text-faint`). The "Submit your skill →" button keeps `--accent-teal`.
- [x] **AC-US2-06**: No new CSS variables are introduced. Dark theme is unaffected (in dark theme `--text-faint` and `--text-muted` already resolve to the same `#8B949E`).

## Functional Requirements

### FR-001: Shared install action handler
Both the new primary Install button and the existing Copy overlay invoke a single `runInstallAction()` callback that performs: clipboard write (with `execCommand` fallback), toast set with timer-managed dismiss, and fire-and-forget `authFetch` telemetry. Side effects are identical regardless of which button was clicked.

### FR-002: Visual parity with results-card InstallButton
The new button uses the same primary-blue Tailwind utility classes used in `src/app/studio/find/components/InstallButton.tsx` (`bg-blue-600 hover:bg-blue-700 text-white rounded-md` family). This keeps "blue = install" consistent across the app.

### FR-003: Telemetry payload stability
The existing `install-copy` telemetry payload schema (`{ skillName, q, ts, version? }`) is unchanged. No new fields, no migration. Adding a `source: "primary" | "copy"` field is explicitly deferred.

## Success Criteria

- 100% of new and existing `InstallPanel.test.tsx` cases pass.
- Build passes without new TypeScript errors.
- Manual smoke test on `/studio/find/<owner>/<repo>/<skill>` shows the Install button visible above the terminal block, click fires telemetry (Network tab) and toast.
- Light-theme DevTools color-pick on the swapped labels reads `#666666`, not `#767676`.

## Out of Scope

- Wiring the Install button to a real local install via the eval-server install-engine endpoint (the endpoint is hard-coded to a 2-engine allow-list and extending it requires its own ADR + security review).
- Restyling badges, taint warnings, or the version picker.
- Adding a `source` field to telemetry to A/B which button users prefer.
- WCAG AAA pass on dark theme.
- Reworking the results-card `InstallButton.tsx` (already correct).

## Dependencies

- Existing endpoint `POST /api/v1/studio/telemetry/install-copy` ([route.ts](repositories/anton-abyzov/vskill-platform/src/app/api/v1/studio/telemetry/[kind]/route.ts) family) — no changes.
- Existing `authFetch` helper at `@/lib/auth-fetch` — no changes.
- Existing `BlockedSkillView` short-circuit in `InstallPanel.tsx` — no changes.
- Tailwind already configured for the Next.js app — no changes.
