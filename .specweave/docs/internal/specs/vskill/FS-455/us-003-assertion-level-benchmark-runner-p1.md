---
id: US-003
feature: FS-455
title: "Assertion-Level Benchmark Runner (P1)"
status: completed
priority: P1
created: 2026-03-08T00:00:00.000Z
tldr: "**As a** skill developer."
project: vskill
---

# US-003: Assertion-Level Benchmark Runner (P1)

**Feature**: [FS-455](./FEATURE.md)

**As a** skill developer
**I want** to run benchmarks from the UI that grade each assertion as PASS/FAIL with evidence-based reasoning
**So that** I can see exactly which assertions pass or fail without using the CLI

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given I select a skill with evals, when I click "Run Benchmark", then the system sends each eval prompt to the LLM via `llm.ts`, judges each assertion via `judge.ts`, and displays results in real-time as they complete
- [x] **AC-US3-02**: Given a benchmark run completes, when I view results, then each assertion shows PASS/FAIL status with the judge's reasoning text
- [x] **AC-US3-03**: Given a benchmark run completes, when results are saved, then a timestamped JSON file is written to `evals/history/YYYY-MM-DDTHH-MM-SSZ.json` and the latest is also written to `evals/benchmark.json` (backward compatible)
- [x] **AC-US3-04**: Given the LLM is unreachable or times out during a benchmark, when an error occurs, then the affected eval case shows "error" status with the error message, and remaining cases continue executing

---

## Implementation

**Increment**: [0455-skill-eval-ui](../../../../../increments/0455-skill-eval-ui/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-006**: Implement SSE benchmark endpoint with per-assertion progress streaming
- [x] **T-007**: Build benchmark runner UI with real-time progress display
