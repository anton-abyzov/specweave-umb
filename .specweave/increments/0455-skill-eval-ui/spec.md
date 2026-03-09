---
increment: 0455-skill-eval-ui
title: "Skill Eval UI"
type: feature
priority: P1
status: planned
created: 2026-03-08
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Eval UI

## Problem Statement

Skill developers currently manage evals through JSON files and CLI commands only. There is no visual way to browse, edit, run, or compare eval results across benchmark runs. Diagnosing regressions, tuning skill descriptions for activation, and understanding the WITH-skill vs WITHOUT-skill delta all require manual JSON inspection. This slows the skill quality feedback loop.

## Goals

- Provide a local-first web UI for full CRUD on eval cases and their assertions
- Enable side-by-side WITH-skill vs WITHOUT-skill benchmarking with blind comparison scoring
- Track benchmark history with timestamped runs and automatic regression detection
- Test auto-activation reliability by analyzing SKILL.md descriptions against sample prompts
- Ship as a new `vskill eval serve` command with zero additional runtime dependencies on the backend

## User Stories

### US-001: Eval Server Command (P1)
**Project**: vskill
**As a** skill developer
**I want** to run `vskill eval serve [--port 3457] [--root ./plugins]` to launch a local eval UI
**So that** I can access the eval editor and benchmark tools from a browser

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given the vskill CLI is installed globally, when I run `vskill eval serve`, then a Node.js HTTP server starts on port 3457 (default) and prints the local URL
- [x] **AC-US1-02**: Given the server is running, when I open `http://localhost:3457` in a browser, then the React SPA loads from bundled `dist/eval-ui/` assets
- [x] **AC-US1-03**: Given I pass `--port 4000 --root ./my-plugins`, when the server starts, then it binds to port 4000 and scans `./my-plugins` for skills instead of the default `plugins/` directory
- [x] **AC-US1-04**: Given the server is running, when I press Ctrl+C, then the server shuts down gracefully

---

### US-002: Skill Browser and Eval Case CRUD (P1)
**Project**: vskill
**As a** skill developer
**I want** to browse all discovered skills and create, read, update, and delete eval cases with inline assertion editing
**So that** I can manage evals visually instead of editing JSON by hand

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the UI is loaded, when I view the skills list, then I see all skills discovered by `skill-scanner.ts` grouped by plugin, showing eval count and benchmark status per skill
- [x] **AC-US2-02**: Given I select a skill, when I view its eval cases, then I see each case's name, prompt (truncated), assertion count, and last benchmark status
- [x] **AC-US2-03**: Given I click "Add Eval Case", when I fill in name/prompt/expected_output and add at least one assertion, then the new case is appended to `evals.json` on disk with the next available ID
- [x] **AC-US2-04**: Given I edit an existing eval case's prompt or name, when I save, then `evals.json` is updated on disk immediately (direct filesystem persistence, no draft state)
- [x] **AC-US2-05**: Given I am editing an eval case, when I add, edit, or delete individual assertions inline, then each assertion change persists to `evals.json` on save with proper ID uniqueness validation

---

### US-003: Assertion-Level Benchmark Runner (P1)
**Project**: vskill
**As a** skill developer
**I want** to run benchmarks from the UI that grade each assertion as PASS/FAIL with evidence-based reasoning
**So that** I can see exactly which assertions pass or fail without using the CLI

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given I select a skill with evals, when I click "Run Benchmark", then the system sends each eval prompt to the LLM via `llm.ts`, judges each assertion via `judge.ts`, and displays results in real-time as they complete
- [x] **AC-US3-02**: Given a benchmark run completes, when I view results, then each assertion shows PASS/FAIL status with the judge's reasoning text
- [x] **AC-US3-03**: Given a benchmark run completes, when results are saved, then a timestamped JSON file is written to `evals/history/YYYY-MM-DDTHH-MM-SSZ.json` and the latest is also written to `evals/benchmark.json` (backward compatible)
- [x] **AC-US3-04**: Given the LLM is unreachable or times out during a benchmark, when an error occurs, then the affected eval case shows "error" status with the error message, and remaining cases continue executing

---

### US-004: WITH vs WITHOUT Skill Comparison (P1)
**Project**: vskill
**As a** skill developer
**I want** to run each eval prompt both WITH and WITHOUT the skill loaded, then see a blind comparison
**So that** I can measure whether my skill actually improves LLM output quality

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given I click "Run Comparison", when the system executes, then each eval prompt is sent twice: once with SKILL.md as system context and once without, producing two outputs per case
- [x] **AC-US4-02**: Given both outputs are generated, when the blind comparator scores them, then each output receives a content score (1-5) and a structure score (1-5), plus a "which is better" verdict -- without the comparator knowing which output had the skill loaded
- [x] **AC-US4-03**: Given comparison results are ready, when I view them in the UI, then I see a side-by-side view with scores, verdict, and the ability to reveal which response was WITH-skill vs WITHOUT-skill
- [x] **AC-US4-04**: Given a comparison completes, when results are persisted, then they are stored in the same `evals/history/` timestamped file with a `type: "comparison"` discriminator

---

### US-005: Benchmark History and Regression Detection (P1)
**Project**: vskill
**As a** skill developer
**I want** to view benchmark history across runs and see which assertions regressed or improved
**So that** I can track skill quality over time and catch regressions early

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given a skill has multiple benchmark runs in `evals/history/`, when I view the history tab, then I see a chronological list of runs with timestamp, model, and overall pass rate
- [x] **AC-US5-02**: Given I select two runs, when I view the diff, then assertions that changed from PASS to FAIL are highlighted as regressions, and FAIL to PASS as improvements
- [x] **AC-US5-03**: Given a new benchmark run completes, when an assertion that passed in the previous run now fails, then the UI displays a regression warning badge next to that assertion
- [x] **AC-US5-04**: Given history files exist, when I view a single run's detail, then I see the full benchmark result including per-case pass rates, assertion-level reasoning, and model info

---

### US-006: Auto-Activation Description Testing (P2)
**Project**: vskill
**As a** skill developer
**I want** to test how reliably my SKILL.md description triggers for sample prompts
**So that** I can optimize the description to reduce false positives and false negatives

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given I navigate to the activation test tab for a skill, when I enter sample prompts (one per line), then the system uses the LLM to evaluate whether each prompt would trigger the skill's SKILL.md description
- [x] **AC-US6-02**: Given sample prompts are evaluated, when results are displayed, then each prompt shows: activation likelihood (yes/no), confidence level, and reasoning explaining why it would or would not trigger
- [x] **AC-US6-03**: Given I mark prompts as "should activate" or "should not activate", when the test runs, then the report classifies results as true positive, true negative, false positive, or false negative
- [x] **AC-US6-04**: Given activation test results are ready, when I view the summary, then I see precision, recall, and an overall activation reliability score

---

### US-007: REST API Layer (P1)
**Project**: vskill
**As a** the frontend SPA
**I want** a REST API served by the eval server
**So that** all UI operations have a backend contract to call

**Acceptance Criteria**:
- [x] **AC-US7-01**: Given the server is running, when the SPA calls `GET /api/skills`, then it receives a JSON array of all discovered skills with plugin name, skill name, eval count, and benchmark status
- [x] **AC-US7-02**: Given a valid skill path, when the SPA calls `GET /api/skills/:plugin/:skill/evals`, then it receives the full `evals.json` content for that skill
- [x] **AC-US7-03**: Given valid eval case data, when the SPA calls `PUT /api/skills/:plugin/:skill/evals`, then the server validates and writes the updated `evals.json` to disk, returning the saved content
- [x] **AC-US7-04**: Given a benchmark or comparison request, when the SPA calls `POST /api/skills/:plugin/:skill/benchmark` or `POST /api/skills/:plugin/:skill/compare`, then the server streams progress via Server-Sent Events (SSE) and writes results to history on completion
- [x] **AC-US7-05**: Given a skill with history, when the SPA calls `GET /api/skills/:plugin/:skill/history`, then it receives a list of all timestamped benchmark/comparison runs with summary metadata

---

### US-008: Playwright E2E Tests (P1)
**Project**: vskill
**As a** contributor to vskill
**I want** Playwright E2E tests covering all major UI workflows
**So that** UI regressions are caught automatically

**Acceptance Criteria**:
- [x] **AC-US8-01**: Given the E2E test suite, when Playwright runs, then all tests use `page.route()` to intercept LLM API calls and return deterministic mock responses (no real LLM calls)
- [x] **AC-US8-02**: Given a test fixture with sample plugins/skills/evals, when E2E tests run, then they cover: skill browsing, eval case CRUD (create, edit, delete), and assertion inline editing
- [x] **AC-US8-03**: Given mock LLM responses, when E2E tests exercise the benchmark flow, then they verify: progress display during run, final results rendering, and history file creation
- [x] **AC-US8-04**: Given mock comparator responses, when E2E tests exercise the comparison flow, then they verify: side-by-side display, content/structure scores, and verdict rendering
- [x] **AC-US8-05**: Given E2E tests run in CI, when `npx playwright test` executes, then all tests pass with the eval server started programmatically (no manual server start required)

## Out of Scope

- Cloud/remote deployment of the eval UI (local-only for this increment)
- Multi-user collaboration or auth on the eval server
- Real-time file watching for external evals.json changes (manual refresh only)
- Custom LLM provider configuration from the UI (use env vars as today)
- Skill creation or SKILL.md editing from the eval UI
- Integration with vskill-platform or verified-skill.com

## Technical Notes

### Dependencies
- Existing `src/eval/` modules: `schema.ts`, `llm.ts`, `judge.ts`, `benchmark.ts`, `skill-scanner.ts`, `prompt-builder.ts`
- Node.js `http` module + router pattern (zero new backend deps)
- React 19 + Vite + Tailwind CSS v4 for frontend SPA (dev dependencies only, bundled to `dist/eval-ui/`)

### Constraints
- Backend must use Node.js `http` module with a router pattern (no Express, no Fastify)
- Frontend bundle must be committed to `dist/eval-ui/` so the global CLI can serve it without build tools
- All `.ts` imports must use `.js` extensions (vskill uses `--moduleResolution nodenext`)
- LLM provider selection remains env-var-based (VSKILL_EVAL_PROVIDER, VSKILL_EVAL_MODEL)

### New Eval Modules
- `src/eval/comparator.ts` -- Blind A/B comparison with content (1-5) + structure (1-5) scoring
- `src/eval/activation-tester.ts` -- SKILL.md activation analysis against sample prompts
- `src/eval/benchmark-history.ts` -- Read/write timestamped history files, regression diff computation

### Architecture Decisions
- SSE for benchmark/comparison progress (not WebSockets) to avoid additional dependencies
- History stored as individual JSON files per run (not a single array file) for git-friendliness and merge safety
- Blind comparator does NOT know which output is WITH-skill vs WITHOUT-skill; the reveal happens only in the UI layer

## Success Metrics

- All 6 existing evals.json files load and render correctly in the UI
- Benchmark results match CLI `vskill eval run` output for the same inputs
- Regression detection correctly identifies PASS-to-FAIL transitions across runs
- E2E test suite covers all 8 user stories with deterministic mock responses
- Zero new runtime dependencies added to the vskill package.json for the backend
