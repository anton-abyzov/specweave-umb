---
increment: 0800-studio-tests-discoverability-and-readonly-run
title: Studio Tests Discoverability + Read-only Eval Run for Installed Skills
type: feature
priority: P1
status: completed
created: 2026-04-29T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Studio Tests Discoverability + Read-only Eval Run for Installed Skills

## Context

After increment 0792 (Studio IA redesign — 6 tabs → 4) the dedicated **Tests** tab from increment 0563 was folded into:
- **Edit tab → eval-cases section** (authoring)
- **Run tab → Benchmark mode** (execution)

Two problems remain:

1. **Discoverability** — Eval-cases authoring is hidden inside an Edit-tab disclosure (`<details>`); execution lives behind a Run sub-mode. There's no inline CTA from the eval-cases section to the Run tab and no surface that signals "this skill has N tests". Users who relied on the old Tests tab can't find their evals quickly.

2. **Read-only run for installed skills** — `TestsPanel.tsx:651` currently gates the per-case **Run** button on `!isReadOnly`, where `isReadOnly = skillInfo.origin === "installed"` ([RightPanel.tsx:402](repositories/anton-abyzov/vskill/src/eval-ui/src/components/RightPanel.tsx:402)). Result: when a user installs a skill that ships an `evals.json`, they can navigate to the Run tab but cannot actually run any of the author-shipped tests. The backend endpoint `POST /api/skills/:plugin/:skill/benchmark` already accepts the request regardless of origin ([api-routes.ts:2948](repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts:2948)) — the gate is purely frontend.

**Source repo**: `repositories/anton-abyzov/vskill/` (eval-ui Studio bundle)
**Distribution**: publish vskill 1.0.x patch once all ACs pass

## Goals

- Make eval-cases discoverable from Edit AND Overview without restoring a 5th top-level tab
- Wire a deep-link path from Edit → Run that auto-executes (`?tab=run&mode=benchmark&autorun=1`)
- Allow installed-skill users to **run** author-shipped evals while keeping authoring controls (Add/Edit/Delete) hidden
- Add a clear read-only banner so installed users understand why authoring is locked
- Preserve 0792's 4-tab IA decision

## Non-Goals

- Restoring the 5th top-level Tests tab (rejected — would partially revert 0792)
- Backend changes (no API additions; existing endpoints already work)
- Changes to authoring controls for source skills (Add/Edit/Delete unchanged)
- Cloud/remote eval execution
- Eval generation flow changes (existing AI-gen path stays as-is)

## User Stories

### US-001: Eval-cases discoverable from Edit + Overview
**Project**: vskill

**As a** skill author
**I want** to find and run my eval cases from anywhere in Studio
**So that** I'm not forced to remember that "Tests" now lives inside an Edit-tab disclosure

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given I am viewing a source skill that has eval cases, when I look at the Overview tab, then I see a small "**N tests**" chip rendered next to the existing skill metadata; the chip links to `?tab=run&mode=benchmark`
- [x] **AC-US1-02**: Given I open the Edit tab and expand the eval-cases section (`editor-eval-cases-section`), when the section is open and `cases.length > 0`, then a primary "Run all" button is rendered in the section header
- [x] **AC-US1-03**: Given I click the "Run all" button in the Edit eval-cases section, when the navigation completes, then the URL becomes `?tab=run&mode=benchmark&autorun=1` AND the Run tab is mounted with the Benchmark sub-mode
- [x] **AC-US1-04**: Given I land on Run tab via `?autorun=1`, when the eval cases finish loading and `cases.length > 0`, then a benchmark run is dispatched automatically exactly once (subsequent renders do not re-fire); the `autorun` query param is stripped from the URL after dispatch
- [x] **AC-US1-05**: Given a source skill with zero eval cases, when I view the Edit eval-cases section, then the "Run all" button is NOT rendered (existing empty-state with Create/Generate buttons unchanged)
- [x] **AC-US1-06**: Given a source skill with zero eval cases, when I view the Overview tab, then the "N tests" chip is NOT rendered

### US-002: Read-only eval run for installed skills
**Project**: vskill

**As a** user of an installed skill that ships eval cases
**I want** to run the author's evals against my own LLM credentials
**So that** I can verify the skill works in my environment without being forced to re-install as source

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given an installed skill (`origin === "installed"`) with `evals.json` containing N cases, when I open the Run tab, then the Benchmark mode lists all N cases AND each case row shows a clickable "Run" button
- [x] **AC-US2-02**: Given an installed skill with eval cases, when I view the Run tab in Benchmark mode, then a "Run all" button is visible at the panel header AND clicking it dispatches a full benchmark run via the existing `POST /api/skills/:plugin/:skill/benchmark` endpoint
- [x] **AC-US2-03**: Given an installed skill, when I view the Run tab Benchmark mode, then the "Add test case", per-case "Edit", and per-case "Delete" controls are NOT rendered (only Run controls visible)
- [x] **AC-US2-04**: Given an installed skill, when I view the Run tab Benchmark mode, then an info banner is rendered above the case list with text: "Read-only — to author or modify tests, install this skill as source via `vskill plugin new`."
- [x] **AC-US2-05**: Given an installed skill with NO `evals.json` (`exists: false`), when I view the Run tab, then the existing empty state is shown WITHOUT Create/Generate buttons (those remain source-only)
- [x] **AC-US2-06**: Given an installed skill, when I view the Edit tab, then the eval-cases section continues to render in read-only mode (existing 0792 behavior — no regression) AND the new "Run all" CTA from US-001 is also hidden (Run lives on the Run tab for installed)
- [x] **AC-US2-07**: Given an installed skill with `evals.json`, when I view the Overview tab, then the "N tests" chip from AC-US1-01 IS rendered (linking to `?tab=run&mode=benchmark`)

### US-003: Restore per-case pass/fail visualization on Run tab
**Project**: vskill

**As a** Studio user (author or installed-skill consumer)
**I want** to see each test case's execution history with green ✓ / red ✗ assertion-level indicators in a split-lane (Skill | Baseline) grid
**So that** I can tell at a glance which assertions pass or fail per run — the visualization the previous Tests tab provided before the 0792 IA collapse

**Background**: The components that rendered this view — `CaseHistorySection`, `HistoryEntryCard`, `getLane`, `useCaseHistory`, `MiniTrend` — are still defined inside `TestsPanel.tsx` but unreachable: gated on `!embedded`, while TestsPanel is now only ever rendered with `embedded={true}` (in EditorPanel's eval-cases disclosure). Only an aggregate `ScoreBar` remains in `RunPanel.tsx:367` (Skill vs Baseline pass-rate bars), losing per-case + per-assertion granularity.

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a skill with at least one eval case AND at least one prior run recorded, when I open the Run tab in Benchmark mode, then below each case's run controls a "Execution History" disclosure is rendered using the existing `CaseHistorySection` component (no visual regression — same look as the pre-0792 Tests tab)
- [x] **AC-US3-02**: Given the Execution History disclosure is expanded, when there are both Skill (`benchmark` type) and Baseline (`baseline` type) runs, then runs are split across two columns: left = Skill, right = Baseline; comparison runs span the full width — matching the historic split-lane layout
- [x] **AC-US3-03**: Given a single `HistoryEntryCard` is rendered, when the entry has assertions, then each assertion shows a green ✓ circle (pass) or red ✗ circle (fail) followed by the assertion text — identical to the historic visualization
- [x] **AC-US3-04**: Given a case has ≥2 prior runs, when the disclosure is expanded, then a `MiniTrend` sparkline is rendered above the split-lane grid showing pass-rate trend
- [x] **AC-US3-05**: Given a case has ZERO prior runs, when I expand the disclosure, then the "No history for this case" message is shown (existing copy, no regression)
- [x] **AC-US3-06**: Given the visualization components were previously private to `TestsPanel.tsx`, when this increment lands, then `CaseHistorySection`, `HistoryEntryCard`, `useCaseHistory` are exported from `TestsPanel.tsx` and imported by `RunPanel.tsx` via a `PerCaseHistory` wrapper (minimal-change variant of the original extract-to-`CaseHistory.tsx` plan; same end-user behavior — components are now reachable from RunPanel, no behavior regression for the existing TestsPanel usage)
- [x] **AC-US3-07**: Given an installed skill with prior runs, when I view the Run tab, then the per-case Execution History grid IS rendered (this surface is read-safe; runs were performed by the user against their own creds)

## Out of Scope

- Restoring the deprecated 5th top-level Tests tab
- Eval-runner backend changes
- New eval-generation features
- A/B mode read-only support (only Benchmark mode in scope; A/B remains source-only)
- Cross-skill eval sharing or remote evals

## Non-Functional Requirements

- **Compatibility**: All changes within `src/eval-ui/` React components. No backend, no schema, no new API.
- **Performance**: Bundle delta < 2 KB. No new network calls. Autorun is a one-shot `useEffect` keyed off `cases.length > 0 && autorunFlag`.
- **Accessibility**: New "Run all" button uses existing `data-testid` patterns; banner uses `role="status"` for SR users.
- **Bundle distribution**: vskill ships pre-built `src/eval-ui/dist/`. CI/release flow must run `vite build` before `npm publish` (existing prepublish hook).

## Edge Cases

- **Autorun + slow eval load**: `useEffect` fires only after `evals.exists && cases.length > 0` to avoid running on stale data
- **Autorun + duplicate fires (StrictMode dev)**: idempotency guard via local `useRef` flag — autorun fires at most once per mount
- **URL has `?autorun=1` but skill has no cases**: param stripped silently; no toast/error
- **Origin flips while on Run tab** (rare — re-install): `useEffect` cleanup re-evaluates `isReadOnly`; banner appears/disappears
- **Installed skill with malformed `evals.json`**: existing 0563 validation-error empty state still rendered (not changed)
- **`?tab=tests` legacy redirect**: still resolves to `?tab=run&mode=benchmark` (no change)

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Read-only gate split (Run kept, Edit hidden) introduces dual-flag bugs | 0.3 | 3 | 0.9 | Single source of truth: derive two flags `canEdit` (origin=source) and `canRun` (cases.length>0) at RightPanel level, pass down explicitly |
| Autorun fires twice in dev StrictMode and triggers two backend runs | 0.4 | 2 | 0.8 | useRef-based once-flag; vitest covers double-mount case |
| Edit-tab "Run all" CTA confuses users (clicked, navigated away unexpectedly) | 0.2 | 2 | 0.4 | Button text + tooltip make navigation explicit ("Run all → opens Run tab") |
| Bundle build skipped on publish, ships stale UI | 0.2 | 4 | 0.8 | Verify `npm pack --dry-run` includes updated dist/ before publish; document in tasks |

## Success Metrics

- All ACs pass via vitest + playwright
- Zero regressions in existing eval-runner tests (Run tab benchmark, edit-tab eval-case authoring)
- Manual smoke: install a third-party skill that ships evals.json → run all tests succeed end-to-end with no Edit-tab fields visible
- vskill 1.0.x patch publishes successfully and `npx vskill@latest studio` shows the new behavior
