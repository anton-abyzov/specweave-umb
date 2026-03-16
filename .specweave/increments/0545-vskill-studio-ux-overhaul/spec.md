---
increment: 0545-vskill-studio-ux-overhaul
title: "vSkill Studio UX & Testing Overhaul"
type: feature
priority: P1
status: active
created: 2026-03-16
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: vSkill Studio UX & Testing Overhaul

## Problem Statement

vSkill Studio has three bugs that degrade trust in evaluation results: the pass rate color thresholds compare against a 0-100 scale while actual values are 0-1, the history timeline runs newest-first (confusing for trend analysis), and long-running activations hang indefinitely with no cancel option. Beyond bugs, users lack the ability to edit skill files in-browser, distinguish unit from integration tests, compare model outputs side-by-side, or understand why a verdict was reached.

## Goals

- Fix all three known bugs so evaluation data displays correctly and activations are cancellable
- Enable in-browser editing of any file in a skill directory
- Add unit/integration test type classification with credential gating
- Provide side-by-side model comparison with aggregate stats and rubric visualization
- Redesign history timeline to be chronological with per-run metadata
- Surface verdict reasoning via tooltips and actionable recommendations

## User Stories

### US-001: Pass Rate Display Bug Fixes (P0)
**Project**: vskill
**As a** skill author
**I want** pass rate colors to accurately reflect my evaluation results
**So that** I can trust the visual indicators when reviewing skill quality

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given a pass rate value of 0.85, when the color threshold logic evaluates it, then the color maps to green (>= 0.7 threshold on 0-1 scale)
- [ ] **AC-US1-02**: Given a pass rate value of 0.45, when the color threshold logic evaluates it, then the color maps to yellow (>= 0.4 and < 0.7 on 0-1 scale)
- [ ] **AC-US1-03**: Given a pass rate value of 0.15, when the color threshold logic evaluates it, then the color maps to red (< 0.4 on 0-1 scale)

---

### US-002: History Timeline Fix and Enhancement (P0)
**Project**: vskill
**As a** skill author
**I want** the history timeline to display runs left-to-right chronologically with per-run metadata
**So that** I can identify performance trends over time at a glance

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Given a history timeline with multiple runs, when rendered, then the leftmost point is the oldest run and the rightmost is the newest
- [ ] **AC-US2-02**: Given a run on the timeline, when displayed, then it shows duration in seconds, total tokens used, and model name as metadata
- [ ] **AC-US2-03**: Given a point on the timeline, when clicked, then the detail panel navigates to that run's full results view
- [ ] **AC-US2-04**: Given a timeline with 20+ runs, when rendered, then the axis labels remain readable with no overlap (auto-spacing or scroll)

---

### US-003: Activation Timeout and Cancellation (P1)
**Project**: vskill
**As a** skill author
**I want** activations to timeout after 120 seconds with a cancel button that preserves partial results
**So that** I am never stuck waiting indefinitely on a hanging evaluation

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Given an activation in progress, when 120 seconds elapse without completion, then the activation terminates and displays a timeout message
- [ ] **AC-US3-02**: Given an activation in progress, when the user clicks the Cancel button, then the activation stops and results for prompts that completed before cancellation are displayed
- [ ] **AC-US3-03**: Given a cancelled activation where 3 of 5 prompts completed, when the partial results are shown, then each completed prompt displays its verdict and score, and incomplete prompts show a "Cancelled" status
- [ ] **AC-US3-04**: Given an activation in progress, when rendered, then a Cancel button is visible alongside a progress indicator showing completed/total prompts

---

### US-004: File Browser Editing (P1)
**Project**: vskill
**As a** skill author
**I want** to view and edit any file in my skill directory from the Studio browser
**So that** I can make quick changes without switching to an external editor

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Given a file selected in the browser, when it is a JSON file, then it renders with syntax-highlighted formatted JSON in the preview pane
- [ ] **AC-US4-02**: Given any file in the skill directory, when the user clicks Edit, then a text editor opens with the file contents and a Save button that issues a PUT request to persist changes
- [ ] **AC-US4-03**: Given a file listing, when displayed, then each file shows its size in human-readable format (bytes, KB, MB)
- [ ] **AC-US4-04**: Given a user edits a file and clicks Save, when the PUT request succeeds, then a success toast appears and the preview refreshes with the updated content

---

### US-005: Unit and Integration Test Types (P1)
**Project**: vskill
**As a** skill author
**I want** to classify evals as unit or integration tests with credential gating for integration tests
**So that** I can run fast unit tests independently and only run integration tests when credentials are configured

**Acceptance Criteria**:
- [ ] **AC-US5-01**: Given an evals.json entry, when it contains an optional `testType` field set to "unit" or "integration", then the UI displays the corresponding badge next to the eval name
- [ ] **AC-US5-02**: Given an evals.json entry with no `testType` field, when rendered, then it defaults to displaying a "unit" badge (backward compatible)
- [ ] **AC-US5-03**: Given the eval list view, when the user selects a test type filter (All / Unit / Integration), then only evals matching the filter are displayed
- [ ] **AC-US5-04**: Given an integration test that requires credentials, when the required environment variables are not set, then the Run button is disabled and a message lists the specific missing credentials
- [ ] **AC-US5-05**: Given an integration test with all required credentials configured, when the user clicks Run, then the eval executes normally

---

### US-006: Compare All Stats and Side-by-Side Diff (P1)
**Project**: vskill
**As a** skill author
**I want** to compare model outputs side-by-side with rubric scores, aggregate charts, and winner badges
**So that** I can make informed decisions about which model performs best for my skill

**Acceptance Criteria**:
- [ ] **AC-US6-01**: Given two or more model runs selected for comparison, when the comparison view renders, then each rubric criterion shows per-model scores in a horizontal bar or radar chart
- [ ] **AC-US6-02**: Given a comparison of model outputs for a prompt, when displayed side-by-side, then each output shows the first 500 characters with a "Show full output" toggle that expands to the complete text
- [ ] **AC-US6-03**: Given a comparison across all prompts, when a model has the highest aggregate score, then a "Winner" badge appears next to that model's name in the summary header
- [ ] **AC-US6-04**: Given a comparison view, when rendered, then an aggregate chart (bar chart) shows overall pass rate, average score, and average duration per model
- [ ] **AC-US6-05**: Given two model outputs displayed side-by-side, when both are visible, then text differences are not highlighted (plain text display, not a diff view)

---

### US-007: Verdict Explanation and Recommendations (P2)
**Project**: vskill
**As a** skill author
**I want** to understand why a verdict was reached and get recommendations for low-scoring evals
**So that** I can improve my skill prompts based on actionable feedback

**Acceptance Criteria**:
- [ ] **AC-US7-01**: Given a verdict cell in the results table, when the user hovers over it, then a tooltip displays the explanation text from `verdictExplanation()`
- [ ] **AC-US7-02**: Given a `verdictExplanation(verdict, score, rubric)` helper function, when called with a PASS verdict and score >= 0.7, then it returns a string explaining which rubric criteria were met
- [ ] **AC-US7-03**: Given a `verdictExplanation()` call with a FAIL verdict and score < 0.4, then it returns an explanation listing failed criteria and a recommendation string suggesting specific improvements
- [ ] **AC-US7-04**: Given an eval result with verdict INEFFECTIVE (score < 0.2), when displayed, then a "Recommendations" section appears below the result with actionable suggestions (e.g., "Consider adding examples to your system prompt")

## Out of Scope

- Real-time collaborative editing in the file browser
- Custom rubric creation UI (rubrics are defined in evals.json only)
- Model cost tracking or billing integration
- Export/import of comparison reports
- Git integration for file browser changes (no version control of edits)
- Drag-and-drop file upload in the file browser

## Non-Functional Requirements

- **Performance**: Timeline renders in < 200ms for up to 100 data points; comparison view loads in < 500ms for 3 models x 20 prompts
- **Accessibility**: All tooltips are keyboard-accessible (focusable elements with aria-describedby); color indicators have text alternatives
- **Compatibility**: Works in Chrome 120+, Firefox 120+, Safari 17+; existing evals.json files without `testType` field continue to work unchanged
- **Security**: PUT endpoint for file editing validates paths are within the skill directory (no path traversal)

## Edge Cases

- Pass rate value of exactly 0.0 or 1.0: color maps to red and green respectively
- evals.json with mixed entries (some with testType, some without): each entry uses its own value or defaults to "unit"
- Cancel pressed when 0 prompts have completed: shows "No results - activation was cancelled before any prompts completed"
- File browser on an empty skill directory: shows an empty state message, no errors
- Compare with only 1 model selected: disables comparison, shows message "Select 2+ models to compare"
- Verdict explanation for edge score (exactly on threshold boundary, e.g., 0.4): maps to yellow tier, not red
- File larger than 1MB opened in editor: loads normally (no artificial size limit, user accepted risk)

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| PUT file endpoint path traversal | 0.3 | 9 | 2.7 | Validate resolved path is within skill directory root |
| 120s timeout too short for large eval suites | 0.4 | 4 | 1.6 | Make timeout configurable in future increment |
| Backward-compat break if testType validation is too strict | 0.2 | 7 | 1.4 | Schema validation treats testType as optional, unknown values default to "unit" |

## Technical Notes

### Dependencies
- Existing Studio web app (React-based UI)
- evals.json schema (additive `testType` field)
- Activation API (needs timeout + cancel support)
- File system API (new PUT endpoint for writes)

### Constraints
- evals.json schema change must be purely additive (no breaking changes)
- `verdictExplanation()` is a pure function with no API calls (client-side only)
- Partial results on cancel depend on the activation API supporting mid-run termination

### Architecture Decisions
- `testType` defaults to "unit" when absent to maintain full backward compatibility
- File editing uses the same API server that serves the Studio UI (no separate service)
- Comparison truncation at 500 chars is a UI-only concern; full data is always available in state

## Success Metrics

- Zero incorrect pass rate colors reported after deployment (bug fix validation)
- 80% of Studio users interact with the timeline at least once per session (engagement)
- Average time to cancel a stuck activation drops from "never" to < 5 seconds
- File browser edit-save round-trip completes in < 2 seconds for files up to 100KB
