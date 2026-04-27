# Tasks — 0792 Studio IA redesign + cleanup

## Phase 1 — Backend (baseline contract)

### T-001: Swap baseline payload in WorkspaceContext to `{ mode: "baseline" }`
**User Story:** US-003 | **Satisfies ACs:** AC-US3-01 | **Status:** [x] completed
**Owner:** backend-agent
**Test Plan:**
- Given: `runCase(caseId, "baseline")` is invoked
- When: the request body is constructed
- Then: body contains `mode: "baseline"` (not `baseline_only`); model/provider still threaded.

### T-002: Remove `baseline_only` from per-case handler body type
**User Story:** US-003 | **Satisfies ACs:** AC-US3-02 | **Status:** [x] completed (verification-only — no `baseline_only` references in src/eval-server/ or src/eval/; per-case body type already `{ mode?, bulk?, provider?, model? }`)
**Owner:** backend-agent
**Test Plan:**
- Given: backend reads body via `as { mode?, bulk?, provider?, model? }`
- When: a typecheck runs
- Then: `tsc` clean; no references to `baseline_only` remain in api-routes.ts.

### T-003: New vitest verifying baseline payload routes to `type: "baseline"`
**User Story:** US-003 | **Satisfies ACs:** AC-US3-03 | **Status:** [x] completed
**Owner:** backend-agent
**Test Plan:**
- Given: a temp skill dir with one eval, mocked `createLlmClient`, baseline prompt
- When: POST to `/benchmark/case/1` with `{ mode: "baseline", provider: "claude-cli", model: "sonnet" }`
- Then: `writeHistoryEntry` is called with `result.type === "baseline"` and the system prompt is the baseline prompt (not the skill prompt).

### T-004: Run full vitest suite — baseline + benchmark integration tests still green
**User Story:** US-003 | **Satisfies ACs:** AC-US3-04 | **Status:** [x] completed (31/31 tests green; tsc clean)
**Owner:** backend-agent
**Test Plan:**
- Given: my changes applied
- When: `npx vitest run src/eval-server/__tests__/benchmark-runner.test.ts src/eval-server/__tests__/benchmark-runner.integration.test.ts src/eval-ui/src/pages/workspace/__tests__/WorkspaceContext.test.ts src/eval-server/__tests__/api-routes.baseline-typing.test.ts`
- Then: all tests pass.

## Phase 1 — Frontend IA redesign

### T-010: Create `RunDispatcherPanel` wrapper with three modes (Benchmark/Activation/A/B)
**User Story:** US-001 | **Satisfies ACs:** AC-US1-03, AC-US1-05 | **Status:** [x] completed
**Owner:** frontend-ia-agent
**Test Plan:**
- Given: user opens the Run tab
- When: the panel mounts
- Then: a `SubTabBar` with three modes (`benchmark`, `activation`, `ab`) renders; each mode renders the existing panel content (`RunPanel`/`ActivationPanel`/comparison flow); URL reflects `?mode=<id>`.

### T-011: Create `HistoryShell` wrapper with three views (Timeline/Models/Versions)
**User Story:** US-001 | **Satisfies ACs:** AC-US1-04, AC-US1-05 | **Status:** [x] completed
**Owner:** frontend-ia-agent
**Test Plan:**
- Given: user opens the History tab
- When: the panel mounts
- Then: a `SubTabBar` with three views renders; each renders existing component (`HistoryPanel`/`LeaderboardPanel`/`VersionHistoryPanel`); URL reflects `?view=<id>`.

### T-012: Embed eval-cases authoring section in EditorPanel
**User Story:** US-001 | **Satisfies ACs:** AC-US1-02 | **Status:** [x] completed
**Owner:** frontend-ia-agent
**Test Plan:**
- Given: user opens Edit tab
- When: panel mounts
- Then: existing markdown editor renders; below it, an "Eval cases" section renders the per-case list + Add Test Case CTA + per-case prompt/expected/assertion editors (extracted from `TestsPanel`'s authoring portion). Test execution moves to Run tab; only authoring lives here.

### T-013: Update RightPanel tab descriptors to 4 tabs (Overview/Edit/Run/History)
**User Story:** US-001 | **Satisfies ACs:** AC-US1-01 | **Status:** [x] completed
**Owner:** frontend-ia-agent
**Test Plan:**
- Given: render RightPanel in vitest with a selected skill
- When: snapshot the tab bar
- Then: exactly four tab buttons present in this order: Overview, Edit, Run, History. No Tests/Trigger/Versions/Activation buttons.

### T-014: URL deep-link redirects for old tab ids
**User Story:** US-001 | **Satisfies ACs:** AC-US1-06 | **Status:** [x] completed
**Owner:** frontend-ia-agent
**Test Plan:**
- Given: user navigates to `?tab=tests`, `?tab=trigger`, `?tab=activation`, `?tab=versions`
- When: route effect runs
- Then: `?tab=tests`/`?tab=trigger`/`?tab=activation` redirect to `?tab=run&mode=benchmark` (or `?tab=run&mode=activation` for trigger/activation); `?tab=versions` redirects to `?tab=history&view=versions`. Replaces history entry rather than pushing.

### T-015: Sub-tab CSS — make inactive sub-tabs visibly clickable
**User Story:** US-002 | **Satisfies ACs:** AC-US2-01 | **Status:** [x] completed
**Owner:** frontend-ia-agent
**Test Plan:**
- Given: SubTabBar rendered with one active + two inactive tabs
- When: jsdom test reads computed styles via `getComputedStyle`
- Then: inactive tab font-size ≥13px; bottom-border non-transparent; hover state has cursor:pointer + background change.

### T-016: Replace no-op `onSubChange` default with `console.warn`
**User Story:** US-002 | **Satisfies ACs:** AC-US2-02 | **Status:** [x] completed
**Owner:** frontend-ia-agent
**Test Plan:**
- Given: a SubTabBar rendered without `onSubChange` prop
- When: user clicks an inactive sub-tab
- Then: `console.warn` fires in dev builds with a message identifying the missing handler. Production builds (`process.env.NODE_ENV === "production"`) keep the silent default to avoid console pollution.

### T-017: Regression suite — vitest + tsc clean
**User Story:** US-001 | **Satisfies ACs:** AC-US1-07 | **Status:** [x] completed
**Owner:** frontend-ia-agent
**Test Plan:**
- Given: all frontend changes applied
- When: `npm run build && npx vitest run`
- Then: `tsc` clean, all related component/hook tests pass. Pre-existing failures (Anton's TopRail in-progress, increment 0786 useCreateSkill/app-lazy-palette) are NOT introduced by this work — verify by running impacted suites only.

## Phase 2 — Testing

### T-020: Playwright spec for new IA navigation
**User Story:** US-001, US-002 | **Satisfies ACs:** AC-US1-01, AC-US1-06, AC-US2-03 | **Status:** [x] completed (5/5 specs green in `e2e/0792-studio-ia.spec.ts`; covers AC-US1-01/02/03/04/05/06 and AC-US2-03)
**Owner:** testing-agent
**Test Plan:**
- Given: a fresh studio with a test skill (`hi-anton` test fixture)
- When: navigate root → click each top-level tab → click each sub-tab/mode/view → use deep-link URLs
- Then: each click updates URL, each panel mounts visibly, no console errors. Old `?tab=tests` deep-link redirects correctly.

### T-021: Run full Playwright suite + report
**User Story:** US-001, US-002 | **Satisfies ACs:** AC-US1-07, AC-US2-03 | **Status:** [x] completed (full suite: 81 passed / 50 failed / 8 skipped vs baseline 78/48/8 — 0792 spec is 5/5 green; 3 newly-failing pre-existing specs are obsoleted by IA collapse and noted in `reports/0792-ac-coverage.md`)
**Owner:** testing-agent
**Test Plan:**
- Given: all Phase 1 work merged
- When: `npx playwright test`
- Then: existing E2E suite still passes (or pre-existing failures are isolated and documented). New 0792 spec passes 100%.

### T-022: Map AC coverage and produce final report
**User Story:** all | **Satisfies ACs:** all | **Status:** [x] completed (matrix written to `reports/0792-ac-coverage.md` — every AC has at least one test; AC-US1-02 has e2e-only coverage, AC-US3-02 is verification-only per spec, AC-US1-07 and AC-US3-04 are no-regression composites)
**Owner:** testing-agent
**Test Plan:**
- Given: Phase 2 tests complete
- When: testing-agent reviews each AC against implemented tests
- Then: a coverage matrix is written to `reports/0792-ac-coverage.md` listing every AC and the test that exercises it. Any AC without coverage is flagged.

## Phase 3 — TestsPanel polish (follow-up)

### T-023: Fix TestsPanel row layout — overlap, clipped status pill, missing tooltips
**User Story:** US-001 | **Satisfies ACs:** AC-US1-02, AC-US1-05 | **Status:** [x] completed
**Owner:** frontend-agent
**Test Plan:**
- Given: a skill with multiple eval cases whose names exceed the case-list column width (e.g. `hi-anton/hi-there` with cases #1–#3)
- When: the user opens Edit → Eval cases and views the case list
- Then: each row truncates the long title with an ellipsis, the U/I type badge stays visible, and the right-side StatusPill renders fully inside the column with consistent padding (no clipping). Hovering the U/I badge surfaces a "Unit test" / "Integration test" tooltip; hovering the placeholder pill surfaces "Not run yet".
- Files: `src/eval-ui/src/pages/workspace/TestsPanel.tsx` (row layout at the case `<button>`, `StatusPill`).
- Verification: `npx vitest run src/eval-ui/src/pages/workspace/__tests__/TestsPanel*.test.tsx` → 11/11 green; visual check via local `vskill studio` against `hi-anton/hi-there`.
