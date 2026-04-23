---
increment: 0681-studio-update-notifications
title: Studio Update Notifications — Tasks
scope: UI integration only (reuses backend from earlier increments)
target_days: 3
status: planned
---

# Tasks: Studio Update Notifications

> **Scope**: UI-only integration into the main `vskill studio` chrome.
> Target codebase: `repositories/anton-abyzov/vskill/src/eval-ui/`
> Stack: Vite 6 + React 19 + Tailwind 4 + TypeScript 5.7 + Vitest 3 + Playwright

---

## Phase 1 — Shared Data Layer

_Goal: a single polling hook with visibility-pause, debounce, and dedup; wired through StudioContext so every consumer reads one source of truth._

---

### T-001: Implement useSkillUpdates() polling hook
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: AC-US1-04, AC-US3-05 | **Status**: [ ] pending
**Phase**: 1 | **Estimated**: 3h | **Test Level**: unit
**AC**: AC-US1-04, AC-US3-05
**Test Plan**:
  Given `useSkillUpdates({ intervalMs: 1000, debounceMs: 100 })` mounted in a React Testing Library container with fake timers and `api.getSkillUpdates` mocked to resolve `[{ name: "foo", installed: "1.0.0", latest: "1.1.0", updateAvailable: true }]`
  When the hook mounts, timers advance by 0ms then 1000ms, visibility is toggled to `hidden`, 5000ms pass, visibility returns to `visible` plus 100ms debounce elapses, and `refresh()` is invoked twice concurrently
  Then (a) the initial fetch fires on mount, (b) one fetch fires after the 1000ms tick, (c) zero fetches fire during the hidden window, (d) one fetch fires after visibility returns past the debounce threshold, (e) both concurrent `refresh()` calls resolve to the same in-flight promise (spy call count === 3 exactly), (f) `updatesMap.get("foo")` returns the fixture, (g) `updateCount === 1`
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useSkillUpdates.ts`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/useSkillUpdates.test.ts`
**Dependencies**: none
**Notes**: Use `AbortController` + `setTimeout(timeoutMs)` for per-fetch timeout (default 15_000ms). On timeout, preserve previous `updates` and set `error`. Expose `{ updates, updatesMap, updateCount, outdatedByOrigin, isRefreshing, lastFetchAt, error, refresh }`. `outdatedByOrigin` requires the caller to supply `skills` so the hook can partition by `origin` — or keep the partition computation in the provider. Prefer keeping it in the provider (T-002) so the hook stays decoupled from `SkillInfo`.

---

### T-002: Wire useSkillUpdates() into StudioContext and merge into skills
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US2-01 | **Status**: [ ] pending
**Phase**: 1 | **Estimated**: 2h | **Test Level**: integration
**AC**: AC-US1-03, AC-US1-04, AC-US2-01
**Test Plan**:
  Given a `StudioContext` provider wraps a tree containing two `SkillRow` stubs and two `SidebarSection` stubs, with `api.getSkills` returning one `source` skill and one `installed` skill, and `api.getSkillUpdates` returning an outdated record for the installed skill only
  When the tree renders
  Then (a) `api.getSkillUpdates` is called exactly once (spy assertion — FR-005), (b) the installed `SkillRow` receives `skill.updateAvailable === true` via the merged store, (c) the source `SkillRow` receives `skill.updateAvailable === false`, (d) `useStudio().outdatedByOrigin` returns `{ source: 0, installed: 1 }`, (e) `useStudio().refreshUpdates` is callable and deduped
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/StudioContext.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/StudioContext.updates.test.tsx`
**Dependencies**: T-001
**Notes**: Use existing `mergeUpdatesIntoSkills()` from `api.ts:409`. Compute `outdatedByOrigin` by grouping merged skills by `skill.origin`. Expose `updates`, `updateCount`, `outdatedByOrigin`, `isRefreshing`, `refreshUpdates` on the context value.

---

### T-003: Extract semver bump classifier to shared util
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [ ] pending
**Phase**: 1 | **Estimated**: 0.5h | **Test Level**: unit
**AC**: AC-US3-03
**Test Plan**:
  Given `classifyBump(installed, latest)` exported from `src/eval-ui/src/utils/semverBump.ts`
  When called with `("1.0.0", "2.0.0")`, `("1.0.0", "1.1.0")`, `("1.0.0", "1.0.1")`, `("abc", "1.0.0")`, and `("1.0.0", "xyz")`
  Then it returns `"major"`, `"minor"`, `"patch"`, `"patch"`, `"patch"` respectively (and the two unparseable cases log exactly one `console.warn` each)
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/utils/semverBump.ts`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/semverBump.test.ts`
**Dependencies**: none
**Notes**: Move the identical helper out of `pages/UpdatesPanel.tsx` and import from both places. DRY across two bump-color consumers.

---

## Phase 2 — Sidebar & Section Header

_Goal: every SkillRow reflects outdated status with a subtle glyph; every SidebarSection header shows a clickable N-updates chip when applicable._

---

### T-004: Replace SkillRow update pill with ↑ glyph
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [ ] pending
**Phase**: 2 | **Estimated**: 1h | **Test Level**: component
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Test Plan**:
  Given a `SkillRow` rendered three times with (a) `updateAvailable: true, currentVersion: "1.0.0", latestVersion: "1.1.0"`, (b) `updateAvailable: true, currentVersion: "1.0.0", latestVersion: null`, (c) `updateAvailable: false`
  When each is rendered and queried
  Then case (a) renders a node with `data-testid="skill-row-update-glyph"` containing a 10×10 SVG `path` with `d="M12 19V5"`, whose computed `color` resolves to `var(--color-own)`, and whose `title` attribute equals `"Update available: 1.0.0 → 1.1.0"`; case (b) renders the glyph with `title="Update available"`; case (c) returns `null` for `queryByTestId("skill-row-update-glyph")`; and `SkillRow` is exported as `React.memo(...)` (verified by `SkillRow.$$typeof === Symbol.for("react.memo")`)
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/SkillRow.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/SkillRow.glyph.test.tsx`
**Dependencies**: T-002
**Notes**: Remove existing lines 118–143 (`update` chip). Update any existing tests that asserted the old pill text — grep `update-available-chip` / `"update"` in `__tests__/` before edit.

---

### T-005: Add updateCount chip to SidebarSection header
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [ ] pending
**Phase**: 2 | **Estimated**: 1.5h | **Test Level**: component
**AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Test Plan**:
  Given `SidebarSection` rendered with (a) `origin="installed", count=5, updateCount=3` and (b) `origin="source", count=2, updateCount=0`
  When case (a) renders, user clicks the `"3 updates"` chip, and a jsdom hashchange spy observes the navigation
  Then (a) renders a `role="link"` element with `aria-label="3 updates available in installed section, view all"` containing the text `"3 updates"` styled with `color: var(--color-own)` and a `▾` caret; clicking the chip sets `window.location.hash === "#/updates"` exactly once and the section's `aria-expanded` is unchanged (confirming `stopPropagation`); keyboard `Tab → Enter` from the collapse button lands focus on the chip and then navigates identically; (b) renders no chip (query returns `null`) and a snapshot matches the pre-0681 baseline
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/SidebarSection.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/SidebarSection.updateCount.test.tsx`
**Dependencies**: T-002, T-003
**Notes**: Chip text: `{updateCount} updates ▾`. Wire `event.stopPropagation()` inside the chip's onClick. Ensure focus ring uses `outline: 2px solid var(--border-focus); outline-offset: 2px` on `:focus-visible`.

---

## Phase 3 — TopRail Bell

_Goal: persistent update presence in the top rail via a bell icon + count badge + lazy dropdown summary._

---

### T-006: Build UpdateBell component
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-06 | **Status**: [ ] pending
**Phase**: 3 | **Estimated**: 1.5h | **Test Level**: component
**AC**: AC-US3-01, AC-US3-02, AC-US3-06
**Test Plan**:
  Given `UpdateBell` rendered with three count values (0, 3, 12) inside a `StudioContext` providing a stub `refresh()` and stub `updates`
  When each variant mounts, the axe-core runner scans both light and dark themes, and the bell button is clicked
  Then (a) `count=0` renders the bell icon with `color: var(--text-secondary)` and no badge (`queryByTestId("update-bell-badge") === null`), (b) `count=3` renders the badge with text `"3"`, (c) `count=12` renders the badge with text `"9+"`, (d) axe-core reports zero serious/critical violations in both themes, (e) clicking the bell with `count=3` opens the dropdown (lazy Suspense resolves) — `queryByRole("dialog")` is non-null and `aria-expanded="true"` on the bell button
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/UpdateBell.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/UpdateBell.test.tsx`
**Dependencies**: T-002
**Notes**: Use `React.lazy(() => import("./UpdateBellDropdown"))`. Wrap in `<Suspense fallback={<span>Loading…</span>}>`. Icon: `assets/icons/update-bell.svg` — import as a URL and render via `<img alt="">` (icon is decorative; `aria-label` lives on the button).

---

### T-007: Build UpdateBellDropdown (lazy-loaded popover)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06 | **Status**: [ ] pending
**Phase**: 3 | **Estimated**: 3h | **Test Level**: component
**AC**: AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06
**Test Plan**:
  Given `UpdateBellDropdown` rendered with `updates = [{ name: "plugin-a/skill-x", installed: "1.0.0", latest: "2.0.0", updateAvailable: true }, { name: "plugin-b/skill-y", installed: "1.0.0", latest: "1.1.0", updateAvailable: true }]`, a stub `onRefresh`, a stub `onSelectSkill`, and a stub `onViewAll`
  When the dropdown mounts, the user presses `↓` twice and then `Enter`, the Refresh button is clicked while `isRefreshing=true`, the View-all link is clicked, and the user presses `Escape`
  Then (a) two rows render, each with a colored semver dot — first row dot color resolves to `var(--red)` (major), second to `var(--yellow)` (minor) — verified via `classifyBump` integration, (b) `↓` moves focus between rows and `Enter` invokes `onSelectSkill` with the focused skill descriptor, (c) while `isRefreshing=true` the Refresh button renders text `"Refreshing…"` and is `disabled`, (d) clicking View-all calls `onViewAll` and the popover closes, (e) `Escape` calls the `onClose` prop and returns focus to the trigger via the parent-provided ref
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/UpdateBellDropdown.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/UpdateBellDropdown.test.tsx`
**Dependencies**: T-003, T-006
**Notes**: Popover uses `role="dialog"` + `aria-modal="false"`. Focus trap can be minimal — Tab cycles among rows + Refresh + View all. Reuse the outside-click pattern from `CommandPalette.tsx`.

---

### T-008: Mount UpdateBell in TopRail right action cluster
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [ ] pending
**Phase**: 3 | **Estimated**: 0.5h | **Test Level**: component
**AC**: AC-US3-01
**Test Plan**:
  Given `TopRail` rendered inside a `StudioContext` that returns `updateCount=2`
  When the component renders
  Then the right action cluster contains, in DOM order: `<ModelSelector>` → `<UpdateBell>` (with badge text `"2"`) → the `⌘K` command-palette button; all three are `flex`-aligned with `gap: 8`; existing `data-toprail-right` container still wraps them unchanged
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/TopRail.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/TopRail.updateBell.test.tsx`
**Dependencies**: T-006
**Notes**: Insert between `<span data-slot="model-selector">` and the `⌘K` button. Do not change existing layout of the right cluster.

---

## Phase 4 — Detail Panel CTA

_Goal: prominent `Update to X.Y.Z` block on the selected skill's detail panel with inline SSE progress and a collapsible changelog._

---

### T-009: Build UpdateAction with useOptimisticAction + SSE
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06, AC-US4-07 | **Status**: [ ] pending
**Phase**: 4 | **Estimated**: 3h | **Test Level**: component
**AC**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06, AC-US4-07
**Test Plan**:
  Given `UpdateAction` rendered with three skill fixtures: (a) `{ updateAvailable: true, latestVersion: "1.4.0" }`, (b) `{ updateAvailable: true, latestVersion: null }`, (c) `{ updateAvailable: false }` — with `api.startSingleUpdate` mocked to emit a fake SSE sequence [`progress: updating`, `progress: downloading`, `done`] and a `refreshUpdates` spy supplied by context; plus a fourth variant emitting `error: { error: "disk full" }`; plus a fifth variant emitting no `done`/`error` within 60s of fake-timer
  When case (a) renders and the button is clicked, case (b) renders, case (c) renders, the fourth variant's button is clicked, and the fifth variant's button is clicked with fake timers advanced 60_001ms
  Then (a1) the button text reads `"Update to 1.4.0"`, clicking switches it to `"Updating…"` and `disabled`, `progress` events update the inline status line with `"updating"` then `"downloading"`, and on `done` a success toast `"Updated <skill>."` fires exactly once and `refreshUpdates` is called exactly once; (b) the button text reads `"Update"` (no version suffix) and clicking still wires through; (c) `queryByRole("button", { name: /Update/ })` returns `null`; (4) the error toast text equals `"Couldn't update <skill> — disk full"` with a `Retry` action and the button returns to idle enabled state; (5) the timeout path fires the same error toast shape with `"TIMEOUT"` and the `EventSource.close()` spy is called exactly once
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/UpdateAction.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/UpdateAction.test.tsx`
**Dependencies**: T-002, T-003
**Notes**: Use `useOptimisticAction({ timeoutMs: 60_000 })`. Inline progress status uses `--text-muted` small text. The `Preview changelog` toggle imports `ChangelogViewer` lazily to keep the detail-panel initial paint fast. Clear the SSE timer on all resolution paths — `done`, `error`, unmount.

---

### T-010: Mount UpdateAction in RightPanel Overview tab
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [ ] pending
**Phase**: 4 | **Estimated**: 0.5h | **Test Level**: component
**AC**: AC-US4-01, AC-US4-02
**Test Plan**:
  Given `RightPanel` rendered with a `selectedSkillInfo` whose `updateAvailable=true, latestVersion="1.2.0"`, and then re-rendered with `updateAvailable=false`
  When each render is queried
  Then the first render shows the DOM order `DetailHeader → UpdateAction(button "Update to 1.2.0") → TabBar → MetadataTab`; the second render shows `DetailHeader → TabBar → MetadataTab` (no reserved space where `UpdateAction` would have been — `UpdateAction` returns null rather than a padded placeholder)
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/RightPanel.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/RightPanel.updateAction.test.tsx`
**Dependencies**: T-009
**Notes**: Import and render `<UpdateAction skill={selectedSkillInfo} />` directly below `<DetailHeader>` inside the detail shell.

---

## Phase 5 — E2E & Closure

_Goal: end-to-end verification across all four surfaces; polling / SSE / refresh path exercised once from the outside._

---

### T-011: Playwright E2E — update notifications full flow
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: AC-US1-01, AC-US2-01, AC-US3-01, AC-US3-02, AC-US3-03, AC-US4-01, AC-US4-03, AC-US4-04, AC-US4-07 | **Status**: [ ] pending
**Phase**: 5 | **Estimated**: 2.5h | **Test Level**: e2e
**AC**: AC-US1-01, AC-US2-01, AC-US3-01, AC-US3-02, AC-US3-03, AC-US4-01, AC-US4-03, AC-US4-04, AC-US4-07
**Test Plan**:
  Given a Playwright fixture that boots the studio against a mocked eval-server returning a workspace with 2 outdated installed skills (`plugin-a/skill-x 1.0.0→2.0.0` major, `plugin-b/skill-y 1.0.0→1.1.0` minor) and an SSE mock for `POST /api/skills/plugin-a/skill-x/update` emitting `progress: updating`, `progress: done`, then `done`
  When the studio loads and the test performs: (1) assert bell badge `"2"`, (2) assert sidebar `Installed` header chip `"2 updates ▾"`, (3) assert first outdated row has `[data-testid="skill-row-update-glyph"]`, (4) click bell → dropdown opens → assert 2 rows + 2 bump dots (red + amber), (5) click first dropdown row → main sidebar selection switches to `skill-x`, (6) detail panel shows `Update to 2.0.0` button, (7) click the button → button text becomes `Updating…`, (8) SSE emits `done`, (9) assert toast text `"Updated skill-x."`, (10) assert bell badge now reads `"1"` and sidebar chip now reads `"1 update ▾"` (singular copy not required by AC but the count must decrement)
  Then all 10 assertions pass; no residual SSE connection is left open (network panel idle after `done`); no console error was logged during the run
**Files**:
  - `repositories/anton-abyzov/vskill/e2e/update-notifications.spec.ts`
  - `repositories/anton-abyzov/vskill/e2e/fixtures/updates-fixture.ts` (new — mocks api responses)
**Dependencies**: T-001–T-010
**Notes**: Reuse existing Playwright test harness at `repositories/anton-abyzov/vskill/e2e/` (already wired for the studio SPA). The SSE mock can be implemented via Playwright's `route.fulfill({ contentType: "text/event-stream", body: "...\n\n" })` pattern already used in 0674 E2E specs.

---

### T-012: Bundle-size and a11y regression gates
**User Story**: US-003 | **Satisfies ACs**: AC-US3-06 | **Status**: [ ] pending
**Phase**: 5 | **Estimated**: 1h | **Test Level**: unit
**AC**: AC-US3-06
**Test Plan**:
  Given `npm run build` runs with `vite build --reporter json` and the resulting chunk map is parsed, and `axe-core` runs against the TopRail open-dropdown fixture in both themes
  When the build completes and the a11y scan completes
  Then (a) the gzipped delta of the `main` chunk (vs `main` branch baseline captured in `scripts/bundle-baseline.json`) is ≤ 8 KB, (b) the `UpdateBellDropdown` code appears in a separate lazy chunk (name matches `/UpdateBellDropdown.*\.js$/`) whose size alone is ≤ 6 KB gzipped, (c) axe-core reports zero `serious`/`critical` violations in both themes with the dropdown open and closed
**Files**:
  - `repositories/anton-abyzov/vskill/scripts/check-bundle-delta.ts`
  - `repositories/anton-abyzov/vskill/scripts/bundle-baseline.json` (new — captured on main)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/update-bell.a11y.test.tsx`
**Dependencies**: T-006, T-007
**Notes**: The baseline JSON is checked in once on main before this increment lands; the script fails CI if the delta exceeds 8 KB. A11y test reuses the axe-core harness established in 0674.

---

## Summary

- **Total tasks**: 12
- **Phase 1 (data layer)**: 3 tasks — hook, context wiring, util extraction
- **Phase 2 (sidebar)**: 2 tasks — row glyph, section chip
- **Phase 3 (top rail)**: 3 tasks — bell, dropdown, mount
- **Phase 4 (detail panel)**: 2 tasks — UpdateAction + mount
- **Phase 5 (closure)**: 2 tasks — E2E + bundle/a11y gates

**Test-level split**: 7 component, 3 unit, 1 integration, 1 e2e — matching the 0674 pyramid.
