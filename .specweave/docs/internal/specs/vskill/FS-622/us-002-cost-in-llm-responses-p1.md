---
id: US-002
feature: FS-622
title: Cost in LLM Responses (P1)
status: completed
priority: P1
created: 2026-03-19T00:00:00.000Z
tldr: "**As a** skill developer."
project: vskill
external_tools:
  jira:
    key: SWE2E-715
  ado:
    id: 1554
---

# US-002: Cost in LLM Responses (P1)

**Feature**: [FS-622](./FEATURE.md)

**As a** skill developer
**I want** each LLM call to include cost data
**So that** costs propagate through benchmark and sweep results automatically

---

## Acceptance Criteria

- [x] **AC-US2-01**: Anthropic API client calculates cost from `input_tokens`/`output_tokens` using pricing engine
- [x] **AC-US2-02**: OpenRouter client preserves existing `total_cost` with fallback to pricing engine calculation
- [x] **AC-US2-03**: Ollama client returns `cost: 0` and `billingMode: "free"`
- [x] **AC-US2-04**: Claude CLI client returns `billingMode: "subscription"` (Max plan)
- [x] **AC-US2-05**: Codex CLI client returns `billingMode: "subscription"`
- [x] **AC-US2-06**: Gemini CLI client returns `billingMode: "free"` (free tier)
- [x] **AC-US2-07**: `GenerateResult` interface extended with `billingMode` field
- [x] **AC-US2-08**: `assembleBulkResult()` sums per-case costs into `totalCost` field
- [x] **AC-US2-09**: Sweep runner `aggregateRuns()` propagates real cost data

---

## Implementation

**Increment**: [0622-dashboard-cost-realtime-redesign](../../../../../increments/0622-dashboard-cost-realtime-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
