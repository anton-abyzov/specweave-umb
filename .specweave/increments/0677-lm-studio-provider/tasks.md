---
increment: 0677-lm-studio-provider
title: LM Studio Provider — Tasks
scope: Adapter + detection probe + UI selector entries + tests
target_days: 2
status: planned
---

# Tasks: LM Studio Provider

> Target codebase: `repositories/anton-abyzov/vskill/`
> Stack: Node 20 + TypeScript 5.7 + Vitest 3 + Playwright
> TDD: write tests first, then adapter/detection code.

---

### T-001: Write Vitest unit test suite for the LM Studio adapter
**User Story**: US-001, US-004 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US4-01 | **Status**: [x] completed
**Estimated**: 2h | **Test Level**: unit
**Test Plan**:
  Given `src/eval/__tests__/lm-studio.test.ts` mocks the global `fetch`
  When the adapter is invoked under five scenarios — (a) happy-path streaming, (b) HTTP 404, (c) HTTP 500 with body, (d) network error / fetch throw, (e) `LM_STUDIO_BASE_URL` env override
  Then all five tests assert: the request URL matches the expected base URL, the `Authorization` header is exactly `Bearer lm-studio`, the request body is OpenAI-shaped, stream tokens are forwarded to the callback, and errors include both the HTTP status and the first 200 chars of the response body; total suite runtime < 200 ms
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval/__tests__/lm-studio.test.ts`
**Dependencies**: none

---

### T-002: Implement the LM Studio adapter in `src/eval/llm.ts`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Estimated**: 2h | **Test Level**: unit
**Test Plan**:
  Given the failing tests from T-001 and the OpenRouter adapter at `src/eval/llm.ts:358` as the template
  When the LM Studio adapter function is added (cloned from OpenRouter with base URL `process.env.LM_STUDIO_BASE_URL ?? "http://localhost:1234/v1"`, dummy bearer token `lm-studio`, provider id `"lm-studio"`) and the provider union type is extended to include `"lm-studio"`
  Then all five tests from T-001 pass, `npx tsc --noEmit` passes with no new errors, and diff against the OpenRouter path shows only the three constants changed plus any imports
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval/llm.ts`
**Dependencies**: T-001
**Notes**: Per ADR-0677-01, do not abstract a shared "OpenAI-compatible" factory in this increment.

---

### T-003: Write Vitest integration test for `detectAvailableProviders()` including LM Studio
**User Story**: US-002, US-004 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US4-02 | **Status**: [x] completed
**Estimated**: 1.5h | **Test Level**: integration
**Test Plan**:
  Given `src/eval-server/__tests__/detect-providers.test.ts` stubs `fetch` with per-URL responses (mock LM Studio `/v1/models` returning `{ data: [{ id: "qwen2.5-coder-7b" }] }`, mock Ollama `/api/tags` returning its own payload)
  When `detectAvailableProviders()` is called once, then called a second time within 30 s, then called after advancing the fake timer past 30 s
  Then the first call returns a providers array containing `{ id: "lm-studio", name: "LM Studio", models: ["qwen2.5-coder-7b"] }`, the second call returns from cache (fetch invocation count unchanged), the third call re-probes (fetch count increments), and when LM Studio's stub is switched to throw a timeout error the probe silently omits LM Studio from the result
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-server/__tests__/detect-providers.test.ts`
**Dependencies**: T-002

---

### T-004: Implement LM Studio probe in `detectAvailableProviders()`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Estimated**: 1h | **Test Level**: integration
**Test Plan**:
  Given the existing Ollama probe in `src/eval-server/api-routes.ts:381-405` as the template and the failing tests from T-003
  When `probeLMStudio()` is added (mirroring the Ollama probe: `fetch(${base}/models, { signal: AbortSignal.timeout(500) })`, parse `data[].id`, push into the providers array, silent catch) and both probes are dispatched via `Promise.all`
  Then all T-003 tests pass, the total detection time under dual-timeout remains ≤ 550 ms (asserted via fake timers), and the 30-second cache TTL is shared with the Ollama entry
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts`
**Dependencies**: T-003

---

### T-005: Verify/add LM Studio in the Comparison and RunPanel dropdowns (jsdom smoke)
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US4-03 | **Status**: [x] completed
**Estimated**: 1.5h | **Test Level**: unit
**Test Plan**:
  Given `src/eval-ui/src/__tests__/run-panel-selector.test.tsx` renders `RunPanel` and `ComparisonPage` with `detectAvailableProviders` mocked under three conditions — (a) returns LM Studio with two models, (b) returns LM Studio with zero models, (c) does not return LM Studio
  When the provider dropdown is opened in each render
  Then case (a) shows an "LM Studio" option group with both models listed alphabetically, case (b) shows the group with a single disabled child "No models loaded — open LM Studio and load a model", and case (c) shows no "LM Studio" group at all; both pages render identically for each case
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/run-panel-selector.test.tsx`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/ComparisonPage.tsx` (add provider option if dropdown is not data-driven)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/RunPanel.tsx` (same)
**Dependencies**: T-004
**Notes**: If the dropdowns are already data-driven off `detectAvailableProviders()`, no UI source change is needed — only the test is added.

---

### T-006: Add Playwright E2E smoke test with `test.skip()` fallback
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04 | **Status**: [x] completed
**Estimated**: 1h | **Test Level**: e2e
**Test Plan**:
  Given `tests/e2e/lm-studio.spec.ts` calls `fetch("http://localhost:1234/v1/models", { signal: AbortSignal.timeout(500) })` in a `beforeAll` hook
  When the endpoint is unreachable, the suite calls `test.skip(true, "LM Studio not reachable at localhost:1234")`; when reachable, the test opens the Studio Comparison page, selects LM Studio, picks the first model, submits a trivial prompt ("echo hi"), and asserts a non-empty completion within 30 s
  Then CI runs without LM Studio installed show the test as "skipped" (not failed), and local runs with LM Studio up show it as "passed"
**Files**:
  - `repositories/anton-abyzov/vskill/tests/e2e/lm-studio.spec.ts`
**Dependencies**: T-005

---

### T-007: Document `LM_STUDIO_BASE_URL` env override in README
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Estimated**: 0.25h | **Test Level**: docs
**Test Plan**:
  Given `README.md` at the repo root (or the existing providers docs page if present)
  When a short subsection "LM Studio" is added alongside the existing Ollama section
  Then it documents: the default URL `http://localhost:1234/v1`, the `LM_STUDIO_BASE_URL` override, and a one-liner confirming no API key is required; markdown lint passes
**Files**:
  - `repositories/anton-abyzov/vskill/README.md`
**Dependencies**: T-002

---

### T-008: Run full test suite + type check as closure gate
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**Estimated**: 0.5h | **Test Level**: integration
**Test Plan**:
  Given all preceding tasks are complete
  When `npx tsc --noEmit`, `npx vitest run`, and `npx playwright test` are executed at the vskill repo root
  Then tsc exits 0, Vitest reports ≥ 90% coverage on the touched files, Playwright reports the LM Studio E2E as passed-or-skipped (never failed); no new ESLint errors are introduced
**Files**:
  - (none — verification only)
**Dependencies**: T-001, T-002, T-003, T-004, T-005, T-006, T-007
