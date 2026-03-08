---
increment: 0455-skill-eval-ui
title: "Skill Eval UI"
generated_by: sw:test-aware-planner
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003, T-004, T-005]
  US-003: [T-006, T-007]
  US-004: [T-008, T-009]
  US-005: [T-010, T-011]
  US-006: [T-012]
  US-007: [T-013, T-014]
  US-008: [T-015, T-016]
total_tasks: 16
completed_tasks: 0
---

# Tasks: 0455 - Skill Eval UI

## User Story: US-001 - Eval Server Command

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, 0 completed

---

### T-001: Implement eval server HTTP foundation (router, SSE helpers, static serving)

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [ ] pending

**Test Plan**:
- **Given** `startEvalServer({ port: 3457, root: './plugins' })` is called
- **When** the server initializes
- **Then** it binds to the given port, serves `dist/eval-ui/index.html` for non-API routes, and gracefully shuts down on SIGINT

**Test Cases**:
1. **Unit**: `src/eval-server/__tests__/router.test.ts`
   - testRouteMatchWithParams(): verifies `:plugin` and `:skill` params extracted correctly
   - testRouteNotFound(): 404 for unregistered paths
   - testRouteMethodMismatch(): returns 405 for wrong HTTP method
   - **Coverage Target**: 95%

2. **Unit**: `src/eval-server/__tests__/eval-server.test.ts`
   - testServerStartsOnPort(): HTTP server binds and responds to GET /api/health
   - testServerGracefulShutdown(): `close()` resolves cleanly
   - testStaticFallback(): non-API GET returns index.html content
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval-server/router.ts` -- Router class adapted from specweave dashboard with path-param support (`:plugin`, `:skill`, `:timestamp`), `sendJson()`, `readBody()` helpers (~130 lines)
2. Create `repositories/anton-abyzov/vskill/src/eval-server/sse-helpers.ts` -- `sendSSEEvent(res, event, data)` and `sendSSEDone(res, data)` utilities (~30 lines)
3. Create `repositories/anton-abyzov/vskill/src/eval-server/eval-server.ts` -- `startEvalServer({ port, root })` using Node.js `http` module; static serving of `dist/eval-ui/` with MIME types; SPA fallback; `GET /api/health` route; graceful SIGINT/SIGTERM shutdown (~200 lines)
4. Write unit tests in `src/eval-server/__tests__/router.test.ts` and `src/eval-server/__tests__/eval-server.test.ts`
5. Run `npx vitest run src/eval-server` -- all tests must pass

---

### T-002: Implement CLI `vskill eval serve` command

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04
**Status**: [ ] pending

**Test Plan**:
- **Given** the user runs `vskill eval serve --port 4000 --root ./my-plugins`
- **When** the CLI parses arguments
- **Then** `startEvalServer` is called with `port: 4000` and `root: './my-plugins'`, prints the local URL, and exits cleanly on Ctrl+C

**Test Cases**:
1. **Unit**: `src/commands/eval/__tests__/serve.test.ts`
   - testServeDefaultOptions(): port=3457, root defaults to 'plugins'
   - testServeCustomPort(): --port 4000 parsed correctly
   - testServeCustomRoot(): --root ./my-plugins parsed correctly
   - testServePrintsUrl(): stdout includes `http://localhost:<port>`
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/commands/eval/serve.ts` -- parse `--port` (default 3457) and `--root` (default `plugins`) from `process.argv`, call `startEvalServer()`, print URL
2. Modify `repositories/anton-abyzov/vskill/src/commands/eval.ts` -- add `case 'serve':` branch that imports and calls the serve handler
3. Write unit tests mocking `startEvalServer` import
4. Run `npx vitest run src/commands/eval` -- all tests must pass

---

## User Story: US-002 - Skill Browser and Eval Case CRUD

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 3 total, 0 completed

---

### T-003: Implement benchmark-history, comparator, and activation-tester eval modules

**User Story**: US-002
**Satisfies ACs**: AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [ ] pending

**Test Plan**:
- **Given** a skill directory with `evals/` subdirectory
- **When** `writeHistoryEntry()` is called with a benchmark result
- **Then** a timestamped JSON file appears in `evals/history/` and `benchmark.json` is updated

**Test Cases**:
1. **Unit**: `src/eval/__tests__/benchmark-history.test.ts`
   - testWriteHistoryEntry(): file created with correct timestamp format (dashes not colons)
   - testListHistory(): returns sorted array with summary metadata
   - testReadHistoryEntry(): full result retrieved by timestamp
   - testComputeRegressions(): PASS->FAIL flagged, FAIL->PASS flagged as improvements
   - **Coverage Target**: 95%

2. **Unit**: `src/eval/__tests__/comparator.test.ts`
   - testRandomizesOutputOrder(): with/without outputs shuffled before scoring
   - testScoreParsing(): content+structure scores (1-5) parsed from LLM JSON response
   - testLabelMappingAfterScoring(): with/without labels correctly re-mapped after randomization
   - testVerdictExtraction(): "first"/"second"/"tie" parsed correctly
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval/benchmark-history.ts` -- `listHistory()`, `readHistoryEntry()`, `writeHistoryEntry()`, `computeRegressions()` (~120 lines)
2. Create `repositories/anton-abyzov/vskill/src/eval/comparator.ts` -- blind A/B comparison using `LlmClient`, randomized ordering, score parsing, label re-mapping (~100 lines)
3. Create `repositories/anton-abyzov/vskill/src/eval/activation-tester.ts` -- activation likelihood analysis, TP/TN/FP/FN classification, precision/recall computation (~80 lines)
4. Write all unit tests with mocked `LlmClient` (no real LLM calls)
5. Run `npx vitest run src/eval/__tests__` -- all tests pass

---

### T-004: Implement REST API routes for skill browsing and eval CRUD

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [ ] pending

**Test Plan**:
- **Given** a valid `PUT /api/skills/:plugin/:skill/evals` request with updated eval case data
- **When** the handler processes the body
- **Then** the updated evals.json is written to disk and the saved content returned with HTTP 200

**Test Cases**:
1. **Unit**: `src/eval-server/__tests__/api-routes.test.ts`
   - testGetSkillsList(): returns SkillInfo[] array with eval count and benchmark status
   - testGetEvalsForSkill(): returns full evals.json content
   - testPutEvalsValidData(): writes to disk, returns saved content
   - testPutEvalsInvalidBody(): returns 400 with validation error
   - testGetHistoryList(): returns sorted HistorySummary[]
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` -- register all REST handlers on Router: `GET /api/skills`, `GET /api/skills/:plugin/:skill/evals`, `PUT /api/skills/:plugin/:skill/evals`, `GET /api/skills/:plugin/:skill/history`, `GET /api/skills/:plugin/:skill/history/:timestamp` (~300 lines)
2. Mock `skill-scanner.ts`, `schema.ts`, and filesystem in tests
3. Run `npx vitest run src/eval-server/__tests__/api-routes` -- all tests pass

---

### T-005: Build frontend skill browser and eval case CRUD pages

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [ ] pending

**Test Plan**:
- **Given** the SPA loads in a browser
- **When** I click "Add Eval Case", fill in name/prompt/expected_output, add one assertion, and click Save
- **Then** a PUT /api/skills/:plugin/:skill/evals request is made with the new case and the list updates

**Test Cases**:
1. **Component**: `src/eval-ui/src/pages/__tests__/SkillDetailPage.test.tsx`
   - testRenderEvalCaseList(): cases shown with name, prompt truncated, assertion count
   - testAddEvalCase(): form submit calls api.putEvals with new case appended
   - testEditEvalCase(): changes persisted immediately on save (no draft state)
   - testInlineAssertionEdit(): assertion add/edit/delete triggers save with updated ID list
   - **Coverage Target**: 85%

**Implementation**:
1. Scaffold `src/eval-ui/` directory: `index.html`, `tsconfig.json` (bundler resolution), `vite.config.ts`
2. Create `src/eval-ui/src/types.ts` -- API response type interfaces mirroring backend shapes
3. Create `src/eval-ui/src/api.ts` -- fetch wrappers for all REST endpoints
4. Create `src/eval-ui/src/sse.ts` -- `fetch()` + `ReadableStream` SSE consumer hook
5. Create `src/eval-ui/src/main.tsx` and `App.tsx` -- React root, layout shell, hash-based routing
6. Create `src/eval-ui/src/pages/SkillListPage.tsx` -- skill browser grouped by plugin with eval counts
7. Create `src/eval-ui/src/pages/SkillDetailPage.tsx` -- eval case list with CRUD actions
8. Create `src/eval-ui/src/components/EvalCaseForm.tsx` -- create/edit form
9. Create `src/eval-ui/src/components/AssertionEditor.tsx` -- inline assertion add/edit/delete
10. Run `npm run build:eval-ui` -- builds to `dist/eval-ui/` without errors

---

## User Story: US-003 - Assertion-Level Benchmark Runner

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 2 total, 0 completed

---

### T-006: Implement SSE benchmark endpoint with per-assertion progress streaming

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [ ] pending

**Test Plan**:
- **Given** a `POST /api/skills/:plugin/:skill/benchmark` request
- **When** the LLM times out for one eval case
- **Then** that case shows "error" status with the message and remaining cases continue executing

**Test Cases**:
1. **Unit**: `src/eval-server/__tests__/api-routes.test.ts` (benchmark section)
   - testBenchmarkStreamsSSEEvents(): case_start, assertion_result, case_complete events emitted per case
   - testBenchmarkWritesHistoryOnCompletion(): timestamped file + benchmark.json written after done event
   - testBenchmarkLlmError(): error status per case, execution continues to next case
   - testBenchmarkClientDisconnect(): aborted flag set, remaining cases skipped
   - **Coverage Target**: 90%

**Implementation**:
1. Add `POST /api/skills/:plugin/:skill/benchmark` SSE handler to `api-routes.ts`: set `Content-Type: text/event-stream` headers, load evals.json, iterate cases calling `benchmark.ts`, emit SSE events per assertion result, catch per-case errors, emit `done` event with full result, write history via `benchmark-history.ts`, handle client disconnect via `res.on('close')`
2. Run `npx vitest run src/eval-server/__tests__/api-routes` -- benchmark tests pass

---

### T-007: Build benchmark runner UI with real-time progress display

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [ ] pending

**Test Plan**:
- **Given** the BenchmarkPage is rendered for a skill with 2 eval cases
- **When** I click "Run Benchmark" and SSE events arrive
- **Then** results appear in real-time per assertion with PASS/FAIL status and judge reasoning

**Test Cases**:
1. **Component**: `src/eval-ui/src/pages/__tests__/BenchmarkPage.test.tsx`
   - testBenchmarkProgressDisplay(): spinner shown during run, results update per SSE event
   - testAssertionPassFailBadges(): PASS in green, FAIL in red with reasoning text
   - testBenchmarkErrorCase(): error status shown with message, other cases still render
   - **Coverage Target**: 85%

**Implementation**:
1. Create `src/eval-ui/src/pages/BenchmarkPage.tsx` -- "Run Benchmark" button, SSE progress via `sse.ts` hook
2. Create `src/eval-ui/src/components/BenchmarkProgress.tsx` -- real-time per-case progress indicator
3. Create `src/eval-ui/src/components/BenchmarkResults.tsx` -- final results with PASS/FAIL assertion badges and reasoning text
4. Wire benchmark page into `App.tsx` routing
5. Run `npm run build:eval-ui` -- no build errors

---

## User Story: US-004 - WITH vs WITHOUT Skill Comparison

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Tasks**: 2 total, 0 completed

---

### T-008: Implement SSE comparison endpoint with blind A/B scoring

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [ ] pending

**Test Plan**:
- **Given** a `POST /api/skills/:plugin/:skill/compare` request
- **When** both WITH and WITHOUT outputs are generated for each eval case
- **Then** the comparator LLM scores them blindly, the server maps labels back, and a `type: "comparison"` history entry is written

**Test Cases**:
1. **Unit**: `src/eval-server/__tests__/api-routes.test.ts` (comparison section)
   - testComparisonGeneratesBothOutputs(): WITH and WITHOUT LLM calls made per case
   - testComparisonBlindScoring(): comparator receives randomized order without labels
   - testComparisonLabelMapping(): WITH/WITHOUT correctly identified in final result
   - testComparisonHistoryType(): history entry has `type: "comparison"` discriminator
   - **Coverage Target**: 90%

**Implementation**:
1. Add `POST /api/skills/:plugin/:skill/compare` SSE handler to `api-routes.ts`: generate WITH output (SKILL.md as system context) and WITHOUT output per eval case, call `comparator.ts` with randomized order, emit `case_start`, `outputs_ready`, `comparison_scored` SSE events, emit `done` with full comparison result, write history with `type: "comparison"`
2. Run `npx vitest run src/eval-server/__tests__/api-routes` -- comparison tests pass

---

### T-009: Build comparison UI with side-by-side view and reveal toggle

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [ ] pending

**Test Plan**:
- **Given** a comparison run has completed and results are displayed
- **When** I click "Reveal" on a case
- **Then** the side-by-side view shows which response was WITH-skill vs WITHOUT-skill with labeled content/structure scores

**Test Cases**:
1. **Component**: `src/eval-ui/src/pages/__tests__/ComparisonPage.test.tsx`
   - testSideBySideDisplay(): two output panels rendered with scores and verdict
   - testRevealToggle(): clicking Reveal labels panels WITH/WITHOUT skill
   - testComparisonProgressStream(): SSE events update UI per case in real-time
   - **Coverage Target**: 85%

**Implementation**:
1. Create `src/eval-ui/src/pages/ComparisonPage.tsx` -- "Run Comparison" button, SSE progress via `sse.ts` hook
2. Create `src/eval-ui/src/components/ComparisonView.tsx` -- side-by-side output panels with content/structure `ScoreBadge` components, verdict display, "Reveal" toggle button
3. Create `src/eval-ui/src/components/ScoreBadge.tsx` -- displays 1-5 score for content or structure
4. Wire comparison page into `App.tsx` routing
5. Run `npm run build:eval-ui` -- no build errors

---

## User Story: US-005 - Benchmark History and Regression Detection

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Tasks**: 2 total, 0 completed

---

### T-010: Implement history API endpoints with regression computation

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Status**: [ ] pending

**Test Plan**:
- **Given** two benchmark runs exist for a skill where assertion A was PASS then FAIL
- **When** `computeRegressions(current, previous)` is called
- **Then** assertion A is flagged as a regression with PASS->FAIL transition

**Test Cases**:
1. **Unit**: `src/eval/__tests__/benchmark-history.test.ts` (regression section)
   - testRegressionPassToFail(): regression entry created for each PASS->FAIL transition
   - testImprovementFailToPass(): improvement entry for each FAIL->PASS transition
   - testNoChangeSameStatus(): unchanged assertions not included in diff
   - **Coverage Target**: 95%

2. **Unit**: `src/eval-server/__tests__/api-routes.test.ts` (history section)
   - testGetHistoryList(): chronological list with timestamp, model, pass rate per run
   - testGetHistoryEntry(): full result including per-case pass rates, assertion reasoning, model info
   - **Coverage Target**: 90%

**Implementation**:
1. Confirm `computeRegressions()` in `benchmark-history.ts` handles all transition cases correctly
2. Confirm history API routes `GET /api/skills/:plugin/:skill/history` and `GET /api/skills/:plugin/:skill/history/:timestamp` return correct shapes including regression fields
3. Run `npx vitest run src/eval/__tests__/benchmark-history` and `src/eval-server/__tests__/api-routes` -- all pass

---

### T-011: Build history timeline and regression diff UI

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Status**: [ ] pending

**Test Plan**:
- **Given** a skill has 3 benchmark runs in history
- **When** I select two runs to compare
- **Then** assertions that regressed (PASS->FAIL) are highlighted in red and improvements (FAIL->PASS) in green

**Test Cases**:
1. **Component**: `src/eval-ui/src/pages/__tests__/HistoryPage.test.tsx`
   - testHistoryChronologicalList(): runs listed newest-first with timestamp, model, pass rate
   - testRegressionWarningBadge(): badge shown on assertions that regressed in latest run
   - testRunDiffView(): two-run comparison shows regression and improvement highlights
   - testSingleRunDetail(): full assertion-level reasoning and model info visible
   - **Coverage Target**: 85%

**Implementation**:
1. Create `src/eval-ui/src/pages/HistoryPage.tsx` -- chronological run list, two-run selection for diff, single run detail view
2. Create `src/eval-ui/src/components/HistoryTimeline.tsx` -- run list with timestamp, model, overall pass rate
3. Create `src/eval-ui/src/components/RegressionDiff.tsx` -- assertion-level diff display between two runs with PASS->FAIL in red, FAIL->PASS in green
4. Wire regression warning badge into `BenchmarkResults.tsx` when previous run data available
5. Wire history page into `App.tsx` routing
6. Run `npm run build:eval-ui` -- no build errors

---

## User Story: US-006 - Auto-Activation Description Testing (P2)

**Linked ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04
**Tasks**: 1 total, 0 completed

---

### T-012: Implement activation tester endpoint and UI tab

**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04
**Status**: [ ] pending

**Test Plan**:
- **Given** sample prompts with "should activate" or "should not activate" labels
- **When** the activation test completes
- **Then** the summary shows precision, recall, and overall reliability score with TP/TN/FP/FN classification per prompt

**Test Cases**:
1. **Unit**: `src/eval/__tests__/activation-tester.test.ts`
   - testActivationLikelihoodResponse(): `{ activate, confidence, reasoning }` parsed from LLM JSON
   - testTpTnFpFnClassification(): TP when expected=should_activate and activate=true, etc.
   - testPrecisionRecallComputation(): precision=TP/(TP+FP), recall=TP/(TP+FN), reliability=(TP+TN)/total
   - **Coverage Target**: 90%

2. **Component**: `src/eval-ui/src/pages/__tests__/ActivationTestPage.test.tsx`
   - testPromptTextareaInput(): one prompt per line, each parsed as separate test
   - testResultsDisplay(): activation=yes/no, confidence, reasoning shown per prompt
   - testSummaryScores(): precision, recall, reliability displayed in summary panel
   - **Coverage Target**: 85%

**Implementation**:
1. Flesh out `activation-tester.ts` fully (skeleton created in T-003)
2. Add `POST /api/skills/:plugin/:skill/activation-test` SSE handler to `api-routes.ts`
3. Create `src/eval-ui/src/pages/ActivationTestPage.tsx` -- prompt textarea (one per line), expected classification toggle, results table, summary scores panel
4. Wire activation test page into `App.tsx` routing
5. Run `npx vitest run src/eval/__tests__/activation-tester` -- all tests pass
6. Run `npm run build:eval-ui` -- no build errors

---

## User Story: US-007 - REST API Layer

**Linked ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05
**Tasks**: 2 total, 0 completed

---

### T-013: Validate complete REST API contract against spec

**User Story**: US-007
**Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05
**Status**: [ ] pending

**Test Plan**:
- **Given** all API route handlers registered in `api-routes.ts`
- **When** integration tests call each endpoint with valid and invalid inputs
- **Then** response shapes match the contract defined in plan.md D-005

**Test Cases**:
1. **Integration**: `src/eval-server/__tests__/api-routes.test.ts` (full contract validation)
   - testGetSkillsReturnsSkillInfoArray(): plugin, skillName, evalCount, benchmarkStatus fields present
   - testGetEvalsReturnsFullEvalsFile(): complete evals.json structure returned
   - testPutEvalsValidatesAndWrites(): 400 on schema violation, 200 + saved content on valid data
   - testBenchmarkSseContentType(): response header `Content-Type: text/event-stream` set
   - testCompareSseContentType(): same as benchmark
   - testHistoryReturnsSummaryList(): timestamp, model, passRate per entry
   - **Coverage Target**: 90%

**Implementation**:
1. Review all routes in `api-routes.ts` against D-005 API contract from plan.md
2. Add missing validation (schema check on PUT body using `schema.ts`)
3. Add `GET /api/health` to confirm server operational status
4. Add 404 handler for unknown `/api/*` routes
5. Run `npx vitest run src/eval-server/__tests__` -- all integration tests pass

---

### T-014: Wire complete build pipeline (tsconfig, package.json, prepublish)

**User Story**: US-007
**Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05
**Status**: [ ] pending

**Test Plan**:
- **Given** the repository with all new source files
- **When** `npm run build && npm run build:eval-ui` runs
- **Then** `dist/` contains compiled server JS and `dist/eval-ui/` contains the React SPA bundle with no TypeScript errors

**Test Cases**:
1. **Build verification** (manual gate):
   - `npm run build` exits 0 with no TS errors
   - `npm run build:eval-ui` exits 0, `dist/eval-ui/index.html` exists
   - `node dist/eval-server/eval-server.js` starts without import errors
   - **Coverage Target**: N/A (build gate)

**Implementation**:
1. Modify root `tsconfig.json` to add `"exclude": ["src/eval-ui"]`
2. Add `build:eval-ui` and `dev:eval-ui` scripts to `package.json`
3. Add `prepublishOnly` script running `npm run build && npm run build:eval-ui`
4. Add React 19, Vite 6, Tailwind v4, React Router v7, and their `@types/*` to `devDependencies`
5. Add `.gitignore` exception `!dist/eval-ui/` so bundle is committed to git
6. Run `npm run build && npm run build:eval-ui` -- both exit 0

---

## User Story: US-008 - Playwright E2E Tests

**Linked ACs**: AC-US8-01, AC-US8-02, AC-US8-03, AC-US8-04, AC-US8-05
**Tasks**: 2 total, 0 completed

---

### T-015: Create Playwright test fixtures and server setup

**User Story**: US-008
**Satisfies ACs**: AC-US8-01, AC-US8-05
**Status**: [ ] pending

**Test Plan**:
- **Given** `npx playwright test` runs in CI
- **When** the global setup starts the eval server programmatically using a fixture plugin directory
- **Then** the server is available at a test port before any test runs and shuts down after all tests complete

**Test Cases**:
1. **E2E infrastructure**:
   - globalSetup starts server on port 3458 (test port) pointing to `e2e/fixtures/`
   - globalTeardown shuts server down cleanly
   - `page.route('**/api/**')` intercepts LLM-backed endpoints
   - All tests use deterministic mock SSE responses (no real LLM calls)
   - **Coverage Target**: 100% of AC scenarios

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/e2e/fixtures/` -- sample plugin with 2 skills, each with 2 eval cases and assertions
2. Create or modify `playwright.config.ts` with `globalSetup`, `baseURL: 'http://localhost:3458'`, `webServer` config
3. Create `e2e/global-setup.ts` -- programmatically start `startEvalServer({ port: 3458, root: 'e2e/fixtures' })`
4. Create `e2e/mock-helpers.ts` -- reusable `page.route()` intercepts for benchmark SSE, comparison SSE, and activation test SSE returning deterministic mock JSON
5. Run `npx playwright test --list` -- tests listed without errors

---

### T-016: Write Playwright E2E tests for all major UI workflows

**User Story**: US-008
**Satisfies ACs**: AC-US8-02, AC-US8-03, AC-US8-04, AC-US8-05
**Status**: [ ] pending

**Test Plan**:
- **Given** mock LLM responses via `page.route()` and the fixture plugin directory
- **When** all Playwright tests run with `npx playwright test`
- **Then** all tests pass covering skill browsing, eval CRUD, benchmark flow, comparison flow, and history view

**Test Cases**:
1. **E2E**: `e2e/eval-ui.spec.ts`
   - skillBrowsing(): skill list renders with plugin grouping and eval counts
   - evalCaseCreate(): "Add Eval Case" form submits and new case appears in list
   - evalCaseEdit(): editing existing case updates name/prompt immediately on save
   - assertionInlineEdit(): adding/deleting assertion saves correctly
   - benchmarkRun(): clicking Run Benchmark shows progress per assertion then final results
   - benchmarkHistory(): completed run appears in history tab with timestamp and pass rate
   - comparisonRun(): side-by-side display with scores and Reveal toggle works
   - regressionWarning(): regression badge shown when assertion regressed since last run
   - **Coverage Target**: 100% of AC scenarios from US-001 through US-008

**Implementation**:
1. Create `e2e/eval-ui.spec.ts` with all test cases above using mock helpers from T-015
2. Each test verifies DOM state after interactions using `expect(page.locator(...)).toBeVisible()` patterns
3. Benchmark and comparison tests verify SSE progress display using mock streaming responses
4. History test verifies run summary rendered after mock benchmark completes
5. Run `npx playwright test` -- all tests pass
