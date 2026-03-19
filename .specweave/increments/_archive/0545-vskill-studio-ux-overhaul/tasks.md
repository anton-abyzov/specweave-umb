---
increment: 0545-vskill-studio-ux-overhaul
generated: 2026-03-16
total_tasks: 27
completed_tasks: 27
---

# Tasks: vSkill Studio UX & Testing Overhaul

## Task Notation

- `[ ]`: Not started
- `[x]`: Completed
- **Lane A**: Bug fixes + backend schema (parallelizable with Lane B after T-015/T-016 land)
- **Lane B**: Frontend features (depends on T-015 and T-016 for schema types)

---

## US-001: Pass Rate Display Bug Fixes (P0) — Lane A

### T-001: Fix pass rate color threshold scale in DetailHeader.tsx
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] Completed
**Test**: Given `passRateColor(0.85)` is called → When the threshold logic evaluates the value → Then it returns green (threshold >= 0.7 on 0-1 scale); given `passRateColor(0.45)` → returns yellow (>= 0.4 and < 0.7); given `passRateColor(0.15)` → returns red (< 0.4)

### T-002: Unit tests for passRateColor helper with 0-1 scale values
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] Completed
**Test**: Given a Vitest test suite for `passRateColor()` covering values 0.0, 0.15, 0.39, 0.4, 0.45, 0.69, 0.7, 0.85, 1.0 → When Vitest runs → Then all assertions pass and boundary values (0.4, 0.7) map to the correct tier

---

## US-002: History Timeline Fix and Enhancement (P0) — Lane A

### T-003: Reverse history sort order in HistoryPanel.tsx (oldest-first)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Status**: [x] Completed
**Test**: Given a history array returned by the API in newest-first order → When HistoryPanel renders → Then the entries are reversed before passing to TrendChart so the leftmost x-axis point is the oldest run

### T-004: Add duration, tokens, and model metadata to TrendChart tooltip
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02
**Status**: [x] Completed
**Test**: Given TrendChart rendered with run metadata (duration: 42s, tokens: 1200, model: "gpt-4o") → When the user hovers over a data point → Then the tooltip displays all three fields

### T-005: Make timeline points clickable to navigate to run detail
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03
**Status**: [x] Completed
**Test**: Given a timeline with three run points → When the user clicks the second point → Then the workspace navigates to that run's full results view (correct runId is dispatched)

### T-006: Auto-space x-axis labels for 20+ run timelines
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04
**Status**: [x] Completed
**Test**: Given TrendChart rendered with 25 data points → When the component mounts → Then visible x-axis labels have no overlap (labelIndices() skips labels as needed) and the chart container supports horizontal scroll if points exceed viewport width

---

## US-003: Activation Timeout and Cancellation (P1) — Lane A

### T-007: Add 120s client-side timeout via AbortController in WorkspaceContext.tsx
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01
**Status**: [x] Completed
**Test**: Given an activation started via WorkspaceContext → When 120 seconds elapse without an SSE completion event → Then the AbortController aborts the SSE connection and an `ACTIVATION_TIMEOUT` action is dispatched, displaying a timeout message in the UI

### T-008: Add Cancel button to ActivationPanel.tsx with partial result preservation
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [x] Completed
**Test**: Given an activation in progress with 3 of 5 prompts completed → When the user clicks Cancel → Then the SSE stream stops, completed prompts retain their verdict/score, and incomplete prompts show "Cancelled" status; a Cancel button and progress indicator ("3 / 5") are visible throughout the run

### T-009: Unit tests for timeout and cancel reducer actions in WorkspaceContext
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Completed
**Test**: Given reducer tests for `ACTIVATION_TIMEOUT` and `ACTIVATION_CANCEL` with a state of 3 completed + 2 pending prompts → When Vitest runs → Then the resulting state marks incomplete prompts as "Cancelled" and sets `activationStatus` to "cancelled" or "timeout" respectively

---

## US-004: File Browser Editing (P1) — Lane A (backend) + Lane B (frontend)

### T-010: Add PUT /api/skills/:plugin/:skill/file route with path traversal protection
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-04
**Status**: [x] Completed
**Test**: Given a PUT request with `{ "path": "evals/evals.json", "content": "..." }` → When the handler resolves the path relative to the skill directory → Then the file is written and `{ ok: true, path, size }` is returned; given path `../../etc/passwd` → Then a 403 is returned and no file is written

### T-011: Add saveSkillFile() method to frontend api.ts
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-04
**Status**: [x] Completed
**Test**: Given `saveSkillFile(plugin, skill, "evals/evals.json", "content")` is called → When the PUT fetch completes successfully → Then it returns the parsed `{ ok, path, size }` response; when the server returns non-2xx → Then it rejects with a descriptive error

### T-012: Add file size display (human-readable) and Edit button to SkillFileBrowser.tsx
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03
**Status**: [x] Completed
**Test**: Given a file listing with a file of 2048 bytes → When rendered → Then it displays "2 KB"; given the user clicks Edit on any file → Then EditorPanel opens with that file's contents loaded

### T-013: Wire EditorPanel Save to PUT endpoint with JSON syntax highlighting and success toast
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-04
**Status**: [x] Completed
**Test**: Given a .json file opened in EditorPanel → When rendered → Then the content is displayed with syntax-highlighted JSON; when Save is clicked and PUT succeeds → Then a success toast appears and the preview pane refreshes with the updated content

### T-014: Unit tests for PUT route path traversal rejection and valid save round-trip
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-04
**Status**: [x] Completed
**Test**: Given Vitest tests for the PUT handler → When called with a valid relative path → Then the file is written successfully; when called with a traversal path (`../outside`) → Then it returns 403 and no file is written

---

## US-005: Unit and Integration Test Types (P1) — Lane A (backend) + Lane B (frontend)

### T-015: Add optional testType and requiredCredentials fields to backend schema.ts
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-04, AC-US5-05
**Status**: [x] Completed
**Test**: Given `loadAndValidateEvals()` called with an evals.json entry that omits `testType` → When the validator runs → Then the entry passes validation and `testType` defaults to `"unit"`; given `testType: "integration"` and `requiredCredentials: ["OPENAI_KEY"]` → Then both fields are preserved in the output unchanged

### T-016: Mirror testType and requiredCredentials in frontend types.ts
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02
**Status**: [x] Completed
**Test**: Given the `EvalCase` TypeScript interface updated with optional `testType` and `requiredCredentials` fields → When TypeScript compiles → Then entries without `testType` are typed as `"unit"` via a default helper; unknown string values fall back to `"unit"` at runtime

### T-017: Add testType badge and All/Unit/Integration filter tabs to TestsPanel.tsx
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [x] Completed
**Test**: Given TestsPanel rendered with 2 unit evals, 1 integration eval, and 1 eval without testType → When rendered → Then each shows the correct badge ("unit" badge for entries without the field); when the "Integration" filter tab is selected → Then only the integration eval is displayed

### T-018: Implement credential gate — disabled Run button with missing credentials message
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04, AC-US5-05
**Status**: [x] Completed
**Test**: Given an integration eval with `requiredCredentials: ["OPENAI_KEY", "STRIPE_KEY"]` and OPENAI_KEY not set → When TestsPanel renders → Then the Run button is disabled and a message displays "Missing: OPENAI_KEY"; when both credentials are set → Then the Run button is enabled

### T-019: Unit tests for schema validation with testType field (all cases)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02
**Status**: [x] Completed
**Test**: Given Vitest tests for the evals.json validator covering: no testType, testType "unit", testType "integration", unknown testType value → When run → Then all cases pass validation with correct defaulting behavior and no existing evals.json is broken

---

## US-006: Compare All Stats and Side-by-Side Diff (P1) — Lane B

### T-020: Implement rubric criterion per-model score chart in ComparisonPage.tsx
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01
**Status**: [x] Completed
**Test**: Given ComparisonPage rendered with 2 model runs each containing rubric scores for 3 criteria → When the comparison view mounts → Then an inline SVG horizontal bar chart shows each criterion with per-model scores rendered side by side

### T-021: Implement side-by-side model output display with 500-char truncation and expand toggle
**User Story**: US-006 | **Satisfies ACs**: AC-US6-02, AC-US6-05
**Status**: [x] Completed
**Test**: Given two model outputs for the same prompt where one output has 800 characters → When ComparisonPage renders the output pair → Then each output shows the first 500 characters with a "Show full output" toggle; when toggled → Then the complete text is visible; no diff highlighting is applied (plain text only)

### T-022: Compute aggregate stats and render winner badge in ComparisonPage.tsx
**User Story**: US-006 | **Satisfies ACs**: AC-US6-03, AC-US6-04
**Status**: [x] Completed
**Test**: Given two models where model-A has aggregate pass rate 0.8 and model-B has 0.6 → When ComparisonPage renders the summary header → Then model-A shows a "Winner" badge; the aggregate chart shows overall pass rate, average score, and average duration per model as a bar chart

### T-023: Unit tests for aggregate score computation and winner badge logic
**User Story**: US-006 | **Satisfies ACs**: AC-US6-03, AC-US6-04
**Status**: [x] Completed
**Test**: Given pure-function tests for `computeAggregateStats(runs)` and `pickWinner(stats)` with controlled input data → When Vitest runs → Then aggregate pass rate, average score, and average duration are computed correctly; given a tie → Then winner badge is not shown (or a defined tie-break rule is applied consistently)

---

## US-007: Verdict Explanation and Recommendations (P2) — Lane B

### T-024: Implement verdictExplanation() pure function in verdict.ts
**User Story**: US-007 | **Satisfies ACs**: AC-US7-02, AC-US7-03
**Status**: [x] Completed
**Test**: Given `verdictExplanation("PASS", 0.85, rubric)` is called → When evaluated → Then it returns `{ explanation: string }` naming which rubric criteria were met; given `verdictExplanation("FAIL", 0.3, rubric)` → Then it returns `{ explanation: string, recommendations: string[] }` listing failed criteria and at least one improvement suggestion

### T-025: Unit tests for verdictExplanation() across all verdict tiers and boundary scores
**User Story**: US-007 | **Satisfies ACs**: AC-US7-02, AC-US7-03
**Status**: [x] Completed
**Test**: Given Vitest tests for `verdictExplanation()` with inputs: PASS score 0.7, PASS score 1.0, FAIL score 0.39, FAIL score 0.0, INEFFECTIVE score 0.15, boundary score exactly 0.4 → When all tests run → Then each returns the correct explanation tier; recommendations are present only for FAIL/INEFFECTIVE; boundary 0.4 maps to yellow not red

### T-026: Add verdict tooltip (hover) to verdict cell in TestsPanel.tsx
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01
**Status**: [x] Completed
**Test**: Given a verdict cell rendered with verdict "PASS" and score 0.85 → When the user hovers over the cell → Then a tooltip appears showing the explanation from `verdictExplanation()`; the trigger element has `aria-describedby` pointing to the tooltip content for keyboard accessibility

### T-027: Add Recommendations section below INEFFECTIVE results in TestsPanel.tsx
**User Story**: US-007 | **Satisfies ACs**: AC-US7-04
**Status**: [x] Completed
**Test**: Given an eval result with verdict INEFFECTIVE and score 0.1 → When TestsPanel renders → Then a "Recommendations" section appears below that result with at least one actionable suggestion (e.g., "Consider adding examples to your system prompt"); given a PASS result → Then no Recommendations section is rendered
