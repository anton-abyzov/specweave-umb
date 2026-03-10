---
id: US-002
feature: FS-458
title: "Baseline-Only Run Mode (P1)"
status: not_started
priority: P1
created: 2026-03-09
tldr: "**As a** skill author."
project: vskill
external:
  github:
    issue: 29
    url: https://github.com/anton-abyzov/vskill/issues/29
---

# US-002: Baseline-Only Run Mode (P1)

**Feature**: [FS-458](./FEATURE.md)

**As a** skill author
**I want** to run all eval cases without the skill (baseline mode) and have those results saved to history
**So that** I can measure how well the LLM performs without my skill for comparison

---

## Acceptance Criteria

- [ ] **AC-US2-01**: Given the eval server is running, when a POST request is made to `/api/skills/:plugin/:skill/baseline`, then all eval cases are executed with a plain "You are a helpful AI assistant" system prompt (no skill content)
- [ ] **AC-US2-02**: Given a baseline run completes, when the result is saved, then the history entry has `type: "baseline"` and includes per-case assertions, tokens, and duration
- [ ] **AC-US2-03**: Given a baseline run is in progress, when the client listens to the SSE stream, then it receives the same event types as benchmark (`case_start`, `output_ready`, `assertion_result`, `case_complete`, `done`)
- [ ] **AC-US2-04**: Given a baseline run completes, when viewing history, then the entry is visually distinguished from benchmark and comparison entries

---

## Implementation

**Increment**: [0458-eval-run-history](../../../../../increments/0458-eval-run-history/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Extract benchmark-runner.ts and implement baseline endpoint
- [x] **T-004**: Baseline visual distinction in HistoryPage
