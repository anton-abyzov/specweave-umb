---
increment: 0681-studio-update-notifications
title: >-
  vSkill Studio — Update Notifications UI (Row Indicator, Section Badge,
  TopRail Bell, Detail CTA)
type: feature
priority: P1
status: planned
created: 2026-04-23T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: vSkill Studio Update Notifications — Row Indicator, Section Badge, TopRail Bell, Detail-Panel CTA

## Overview

The backend for detecting and applying skill updates already ships — `GET /api/skills/updates` returns `SkillUpdateInfo[]`, and both single-skill (`POST /api/skills/:plugin/:skill/update`) and bulk (`POST /api/skills/batch-update`) update routes stream SSE progress. A full-page `UpdatesPanel` exists for bulk selection. **The gap is in the main studio chrome** — a developer working in the studio cannot tell, at a glance, that any skill is outdated. They must navigate to `/updates` to discover and act.

This increment closes that gap by surfacing the update state in four existing chrome locations, without touching the backend:

1. **Sidebar row indicator** — a subtle `↑` glyph (not a loud pill) next to the skill name when `updateAvailable === true`, painted with `--color-own` (warm amber). Tooltip shows `installed → latest` delta.
2. **Section-header count chip** — `Installed · Claude · 3 updates ▾` where the `N updates` token is clickable and routes to the existing `UpdatesPanel`.
3. **TopRail `<UpdateBell />`** — a bell icon in the right action cluster next to `⌘K`. Shows a small count badge when >0. Click opens a dropdown summary listing outdated skills with bump-type dots (major/minor/patch) and a `View all` link to `UpdatesPanel`. Includes a manual `Refresh` action.
4. **RightPanel `<UpdateAction />`** — when the selected skill has `updateAvailable === true`, the detail panel renders a prominent `Update to X.Y.Z` button under the header. Pressing it runs the single-skill update via `useOptimisticAction` (shipped in 0674 T-053), streams SSE progress inline, and displays the existing `ChangelogViewer` as a collapsible preview below the button.

Cross-cutting: a new shared hook `useSkillUpdates()` polls `GET /api/skills/updates` every 5 minutes when the tab is visible, pauses when `document.visibilityState === "hidden"`, resumes on visibility change, debounces rapid visibility flips (500ms), and dedupes concurrent fetches per session. A manual refresh is exposed via the bell dropdown and by consuming the hook's `refresh()` return.

## Code Location & Scope

**Target codebase:** `repositories/anton-abyzov/vskill/src/eval-ui/` (the Vite + React SPA served by `npx vskill studio`).

**Files added (new):**
- `src/eval-ui/src/hooks/useSkillUpdates.ts`
- `src/eval-ui/src/components/UpdateBell.tsx`
- `src/eval-ui/src/components/UpdateBellDropdown.tsx`
- `src/eval-ui/src/components/UpdateAction.tsx` (RightPanel block)
- `src/eval-ui/src/__tests__/useSkillUpdates.test.ts`
- `src/eval-ui/src/__tests__/UpdateBell.test.tsx`
- `src/eval-ui/src/__tests__/UpdateAction.test.tsx`
- `src/eval-ui/e2e/update-notifications.spec.ts`

**Files modified (additive, in place):**
- `src/eval-ui/src/components/SkillRow.tsx` — replace the existing `update` pill (lines 118–143) with a subtle `↑` glyph and tooltip.
- `src/eval-ui/src/components/SidebarSection.tsx` — add `updateCount` prop plus inline `N updates` clickable chip.
- `src/eval-ui/src/components/TopRail.tsx` — mount `<UpdateBell />` in the right action cluster (between `ModelSelector` and the `⌘K` button).
- `src/eval-ui/src/components/RightPanel.tsx` — render `<UpdateAction />` below `DetailHeader` on the Overview tab when `skill.updateAvailable`.
- `src/eval-ui/src/StudioContext.tsx` — mount `useSkillUpdates()` once at the root and expose its result through context so all four consumers share one fetch.

**Out of scope:**
- `src/eval-server/**` — no route changes.
- `UpdatesPanel` itself is reused **unchanged**; no redesign.
- `vskill` CLI (`outdated`, `update`) — unchanged.
- Server-push / websocket-based discovery (see ADR in plan.md — polling is the chosen architecture).

**Existing building blocks consumed (no rewrites):**
- `api.getSkillUpdates()` → `SkillUpdateInfo[]` (`src/eval-ui/src/api.ts:387`).
- `mergeUpdatesIntoSkills()` (`src/eval-ui/src/api.ts:409`).
- `useOptimisticAction` (`src/eval-ui/src/hooks/useOptimisticAction.ts` — 0674 T-053).
- `ChangelogViewer` (`src/eval-ui/src/components/ChangelogViewer.tsx`).
- `api.startSingleUpdate()` SSE helper (existing wrapper in `src/eval-ui/src/api.ts`).
- `useToast()` (via `useOptimisticAction`).
- Icon SVGs at `src/eval-ui/src/assets/icons/{update-bell,update-available,up-to-date,changelog}.svg` — generated in parallel via nanobanana; this increment consumes them.

## Personas

- **P1 — Skill Author / Consumer** (primary): lives in the studio day-to-day. Wants to know immediately when an installed skill has a new version, without having to run `vskill outdated`.
- **P2 — Release-Conscious Reviewer**: needs to see which skills have breaking (`major`) changes at a glance before updating.

## User Stories

### US-001: Sidebar Row Update Indicator (P1)
**Project**: vskill

**As a** developer scanning the sidebar for the skill I want to edit
**I want** a subtle inline indicator that an installed skill has an update available
**So that** I see outdated state without a loud pill or a trip to the UpdatesPanel

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given a rendered `SkillRow` where `skill.updateAvailable === true`, when the row renders, then a 10×10px `↑` glyph appears to the right of the version number with `color: var(--color-own)`, `stroke-width: 2`, and no background fill. The pill-style `update` chip currently rendered by `SkillRow.tsx` lines 118–143 is removed as part of this change — the chip is replaced, not supplemented.
- [ ] **AC-US1-02**: Given the `↑` glyph is present, when the user hovers it (or focuses its parent row), then a native `title` tooltip reads `Update available: {installed} → {latest}` using `skill.currentVersion` and `skill.latestVersion`. When `latestVersion` is missing, the tooltip reads `Update available`.
- [ ] **AC-US1-03**: Given `skill.updateAvailable === false` OR `skill.updateAvailable === undefined`, when the row renders, then no update glyph is rendered (`queryByTestId("skill-row-update-glyph")` returns `null`).
- [ ] **AC-US1-04**: Given a sidebar with ≥100 skill rows and 10 outdated, when `useSkillUpdates()` polls and merges updates, then only the 10 rows whose outdated status changed re-render (keyed by skill name; `SkillRow` wrapped with `React.memo` and shallow-prop comparison). Verified via a render-count spy in unit tests.

---

### US-002: Section-Header Update Count Chip (P1)
**Project**: vskill

**As a** developer with many installed skills
**I want** each sidebar section header to tell me how many updates are pending in that section
**So that** I can decide whether to enter the UpdatesPanel or keep working

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Given `SidebarSection` receives a new optional `updateCount: number` prop, when `updateCount > 0`, then the header renders an inline chip after the section label+count: a text token `{updateCount} updates` styled with `color: var(--color-own)`, `font-family: var(--font-mono)`, and a caret glyph `▾` indicating the chip is clickable.
- [ ] **AC-US2-02**: Given the `N updates` chip is rendered, when the user clicks it, then the app navigates to `#/updates` and the click does not toggle the section collapse state (`event.stopPropagation()` is called in the chip handler since the parent header button already handles collapse on click).
- [ ] **AC-US2-03**: Given `updateCount === 0` OR `updateCount === undefined`, when the header renders, then no update chip is rendered and the header layout is identical to the pre-0681 baseline (verified via snapshot test).
- [ ] **AC-US2-04**: Given the `N updates` chip, when rendered, then its accessible name is `{N} updates available in {origin} section, view all` (via `aria-label`) and it carries `role="link"` so screen readers announce it as navigation, not as a state-mutating button.
- [ ] **AC-US2-05**: Given a keyboard user, when they tab through the sidebar, then focus lands on the section-collapse button first and on the `N updates` chip second; pressing `Enter` on the chip performs the same navigation as click; focus ring uses the shared `--border-focus` token at 2px.

---

### US-003: TopRail Update Bell + Dropdown Summary (P1)
**Project**: vskill

**As a** developer focused on the editor
**I want** a persistent indicator in the top rail that shows when any skill has an update
**So that** I can discover and act on updates without leaving the current view

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Given `TopRail` renders with `<UpdateBell />` mounted in the right action cluster (between `ModelSelector` and the `⌘K` button), when `useSkillUpdates()` reports zero outdated skills, then the bell icon (from `assets/icons/update-bell.svg`) renders with `color: var(--text-secondary)` and no count badge is visible.
- [ ] **AC-US3-02**: Given `useSkillUpdates()` reports N>0 outdated skills, when the bell renders, then it shows a count badge in the top-right corner — circular, `background: var(--color-own)`, `color: var(--color-paper)`, tabular-nums, font-size 9px. If N > 9 the badge text reads `9+`.
- [ ] **AC-US3-03**: Given the bell has a count, when the user clicks it, then a dropdown anchored to the bell opens containing: (a) a header `N updates available`, (b) a scrollable list of outdated skills showing `plugin/skill`, `{installed} → {latest}`, and a colored bump-type dot (red for major, amber for minor, green for patch — derived client-side from semver comparison), (c) a `Refresh` text button that calls `useSkillUpdates().refresh()`, (d) a `View all` link that navigates to `#/updates`. The dropdown closes on Escape, on outside-click, or after navigating.
- [ ] **AC-US3-04**: Given the dropdown is open, when the user presses `↑`/`↓`, then focus moves between the skill rows within the dropdown; pressing `Enter` on a row calls the existing `selectSkill()` action on `StudioContext` (selecting the skill in the main sidebar) and closes the dropdown.
- [ ] **AC-US3-05**: Given the dropdown's `Refresh` action is clicked, when the refresh is in flight, then the `Refresh` button shows a compact `Refreshing…` label and is disabled for the duration; dedup prevents concurrent fetches (FR-002).
- [ ] **AC-US3-06**: Given the bell is rendered in either theme, when measured with axe-core, then there are zero critical/serious violations; the dropdown carries `role="dialog"` + `aria-modal="false"` (it's a popover), traps focus while open, and returns focus to the bell button on close.

---

### US-004: RightPanel Update Action + SSE Progress (P1)
**Project**: vskill

**As a** developer inspecting a specific installed skill
**I want** a prominent `Update to X.Y.Z` action inside the detail panel with inline progress and a changelog preview
**So that** I can update the skill I'm looking at without context-switching to `UpdatesPanel`

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Given a skill is selected in `RightPanel` with `skill.updateAvailable === true` AND `skill.latestVersion != null`, when the Overview tab renders, then an `<UpdateAction />` block appears directly under `DetailHeader` containing: (a) a primary button labelled `Update to {latestVersion}`, (b) a secondary-style link `Preview changelog` that toggles the existing `<ChangelogViewer />` inline below.
- [ ] **AC-US4-02**: Given `skill.updateAvailable !== true`, when the Overview tab renders, then `<UpdateAction />` renders `null` (no button, no reserved space).
- [ ] **AC-US4-03**: Given the user clicks `Update to {latestVersion}`, when the action fires, then `useOptimisticAction` is invoked — the button immediately switches to an `Updating…` disabled state (optimistic UI); under the hood it opens the `POST /api/skills/{plugin}/{skill}/update` SSE stream and subscribes to `progress` / `done` / `error` events.
- [ ] **AC-US4-04**: Given the SSE stream emits `progress` events, when received, then a thin progress line below the button shows the most recent `status` field from the event payload (e.g., `updating`, `downloading`, `verifying`, `done`). On `done`, the button hides and a success toast reads `Updated {skill}.` (period, not exclamation, per voice rules inherited from 0674 NFR-005).
- [ ] **AC-US4-05**: Given the SSE stream emits `error` (or the backend responds 409), when received, then `useOptimisticAction` rolls back (button returns to `Update to X.Y.Z` enabled state); a sticky error toast fires with `Couldn't update {skill} — {error.message}` and a `Retry` action that re-invokes the update.
- [ ] **AC-US4-06**: Given the SSE stream has not emitted `done` or `error` within 60 seconds, when the timeout fires, then the action is treated as failed (`code: "TIMEOUT"`); the SSE connection is closed via `EventSource.close()`; the error-toast-with-retry path runs.
- [ ] **AC-US4-07**: Given the update completes successfully, when `done` is received, then `useSkillUpdates().refresh()` is invoked (the shared update map refetches immediately); the sidebar row's `↑` glyph disappears for that skill in the same tick as the header count chip decrements and the TopRail bell badge decrements.

---

## Functional Requirements

### FR-001: Shared `useSkillUpdates()` Hook — Single Source of Truth
All four surfaces (sidebar row, section-header chip, top-rail bell, right-panel action) consume the same hook value. The hook is invoked once at the app root (inside `StudioContext`) and its state is provided via context. Components never call `api.getSkillUpdates()` directly.

### FR-002: Polling Cadence
- **Visible tab**: poll every 300_000ms (5 minutes) after the initial fetch.
- **Hidden tab** (`document.visibilityState === "hidden"`): cancel the pending interval; resume on `visibilitychange` returning to `visible`.
- **Debounce**: 500ms on `visibilitychange` to avoid thrash when the user alt-tabs rapidly.
- **Dedup**: if a fetch is already in flight, a second call to `refresh()` resolves to the same pending promise.
- **Manual refresh**: `refresh()` is exposed on the hook handle.
- **Initial fetch**: runs immediately on mount if `lastFetchAt` is unknown or older than 60 seconds.

### FR-003: Classification Reuse
No new classification. Updates come from the existing `vskill outdated --json` pipeline via `GET /api/skills/updates`. Client merges `SkillUpdateInfo[]` into `SkillInfo[]` via the existing `mergeUpdatesIntoSkills()`.

### FR-004: Bump-Type Derivation (Client-Side Only)
The dropdown classifies each outdated skill as major / minor / patch using semver comparison on `installed` vs `latest`. If either version is unparseable, classify as `patch` (least-scary default) and log a dev-console warning. This is display-only; no backend involvement.

### FR-005: No Duplicate Polling
Because all surfaces read through context, exactly one `fetch` per poll is issued regardless of how many rows / chips / bells / buttons are mounted.

### FR-006: Accessibility
- Every new interactive element has an accessible name.
- Focus is trapped inside the dropdown while open; Escape closes and returns focus to the trigger.
- Live updates announced via `aria-live="polite"` when the count changes (reuse existing `AriaLive` component).

### FR-007: Voice Rules (inherited from 0674 NFR-005)
No emoji, no celebration language, no exclamation points in product strings. Sentences are short and declarative: `3 updates available`, `Update to 1.4.0`, `Preview changelog`, `Updated obsidian-brain.`, `Couldn't update obsidian-brain — network error.`, `Refreshing…`.

## Non-Functional Requirements

### NFR-001: Performance
- Initial paint of `TopRail` unaffected (lazy-import `UpdateBellDropdown` so the closed bell ships ≤2KB gzipped).
- Polling fetch runs via `requestIdleCallback` where available, `setTimeout(0)` fallback — never blocks input.
- `SkillRow` is `React.memo`-wrapped; only outdated-status-changed rows re-render on poll.

### NFR-002: Accessibility
axe-core zero-serious-violations in both themes with the dropdown open AND closed.

### NFR-003: Test Coverage
- Unit: ≥90% line coverage on new files.
- Integration: fake-timer tests for polling cadence, visibility-pause, dedup, 60s SSE timeout, rollback path.
- E2E (Playwright): spec covering `launch studio with outdated skills → see badge on bell → open dropdown → see list → click skill → Update action fires → SSE progress visible → success toast on done → badge disappears`.

### NFR-004: Bundle Size
Incremental bundle growth ≤ 8 KB gzipped (dropdown lazy-chunked).

### NFR-005: Theme Parity
All colors reference existing semantic tokens (`--color-own`, `--text-secondary`, `--color-paper`, `--border-default`, `--border-focus`). No new tokens. Both themes pass the 0674 contrast matrix.

## Success Criteria

- **Discoverability**: within 10 seconds of opening the studio with at least one outdated skill, the user sees at minimum one update affordance (bell badge, section chip, or row glyph) without scrolling.
- **One-click update**: with a skill selected that has an update, the user completes the update in one click + wait for SSE — no page navigation required.
- **No duplicate fetches**: network panel shows exactly one `GET /api/skills/updates` per visible 5-minute interval; zero while hidden.
- **Zero regressions**: all existing `SkillRow`, `SidebarSection`, `TopRail`, `RightPanel`, and `UpdatesPanel` tests continue to pass.

## Out of Scope

- Backend changes of any kind (no new routes, no modifications to existing routes).
- Redesign of the `UpdatesPanel` page.
- Push-based discovery (SSE / websocket broadcast of new-version events from the server).
- Auto-update behavior — updates remain explicitly user-triggered.
- Batch update UX inside the detail panel (batch lives on `UpdatesPanel` only).
- Changelog parsing / formatting (the existing `ChangelogViewer` is consumed as-is).
- Cross-tab coordination of polling (each tab polls independently — accepted since `vskill outdated` is cheap and local).

## Dependencies

- `GET /api/skills/updates` — confirmed at `src/eval-server/api-routes.ts:635`.
- `POST /api/skills/:plugin/:skill/update` SSE — confirmed at `src/eval-server/api-routes.ts:736`.
- `api.getSkillUpdates()` + `SkillUpdateInfo` + `mergeUpdatesIntoSkills()` — `src/eval-ui/src/api.ts:387–433`.
- `useOptimisticAction` — `src/eval-ui/src/hooks/useOptimisticAction.ts` (0674 T-053).
- `ChangelogViewer` — `src/eval-ui/src/components/ChangelogViewer.tsx`.
- `UpdatesPanel` hash route `#/updates` exists.
- Icon SVGs generated in parallel — consumed, not produced, here.

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Polling burns battery on background tabs | 0.6 | 3 | 1.8 | `visibilitychange` pause + 5 min cadence + 500ms debounce |
| Multiple tabs cause N× outdated checks | 0.5 | 2 | 1.0 | Accepted — `vskill outdated` is cheap + local; documented in NFR |
| SSE connection dropped mid-update leaves button stuck | 0.4 | 3 | 1.2 | 60s timeout in `useOptimisticAction` + rollback + retry toast |
| Existing row-level `update` pill relied on by tests | 0.5 | 2 | 1.0 | Grep test usage; replace with `↑` glyph + stable `data-testid="skill-row-update-glyph"` |
| Dropdown focus management regresses a11y | 0.3 | 4 | 1.2 | Focus-trap pattern reused from `ShortcutModal`; axe CI gate |
| `↑` glyph too subtle at 10px on dark theme | 0.4 | 2 | 0.8 | Verify in `theme-contrast.test.ts`; bump to 11px if ratio <3:1 |

## Edge Cases

- **Update-available skill gets uninstalled mid-session**: next poll returns a shorter list; `<UpdateAction />` unmounts gracefully.
- **Two updates complete in the same tick (dropdown open)**: SSE `done` events arrive serially; `refresh()` deduped; dropdown list updates in one re-render.
- **Click `Update` while a batch update runs on `UpdatesPanel`**: backend returns 409 Conflict. Toast: `Couldn't update {skill} — another update is in progress.`; single-click path is not entangled with batch state.
- **Offline / eval-server disconnected**: fetch rejects; stale count persists; bell retains last-known state; existing `DisconnectBanner` covers the visible disconnect signal.
- **`updateAvailable: true` but `latestVersion: null`**: row tooltip is the generic `Update available`; `<UpdateAction />` renders button as `Update` (no version suffix).
- **Theme switch while dropdown open**: no re-render needed — tokens are CSS variables.
