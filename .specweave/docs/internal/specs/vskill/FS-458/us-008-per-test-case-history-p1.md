---
id: US-008
feature: FS-458
title: "Per-Test-Case History (P1)"
status: completed
priority: P1
created: "2026-03-09T00:00:00.000Z"
tldr: "**As a** skill author."
project: vskill
external:
  github:
    issue: 35
    url: "https://github.com/anton-abyzov/vskill/issues/35"
---

# US-008: Per-Test-Case History (P1)

**Feature**: [FS-458](./FEATURE.md)

**As a** skill author
**I want** to view the history of a specific eval case (test case) across all runs, seeing how it performed with different models and over time
**So that** I can track individual test case quality and spot which cases regress when switching models

---

## Acceptance Criteria

- [x] **AC-US8-01**: Given the API endpoint `GET /api/skills/:plugin/:skill/history/case/:evalId`, when called with a valid eval ID, then it returns an array of per-run results for that case extracted from all history files, each including: timestamp, model, type, pass_rate, durationMs, tokens, inputTokens, outputTokens, assertions array, and provider
- [x] **AC-US8-02**: Given the BenchmarkPage shows eval case results, when a user clicks on a completed eval case card, then a per-case history panel expands below it showing all historical results for that case sorted newest-first, with model, pass rate, time, and tokens for each
- [x] **AC-US8-03**: Given the per-case history view, when multiple runs exist for that case, then a mini trend line shows pass rate across runs with model labels on each data point
- [x] **AC-US8-04**: Given the per-case history endpoint, when called with optional `?model=X` query param, then only results from that model are returned

---

## Implementation

**Increment**: [0458-eval-run-history](../../../../../increments/0458-eval-run-history/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-012**: getCaseHistory backend function and API endpoint
- [x] **T-013**: Per-case history panel on BenchmarkPage with mini trend line
