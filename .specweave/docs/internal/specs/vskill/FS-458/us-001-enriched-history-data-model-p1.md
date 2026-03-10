---
id: US-001
feature: FS-458
title: "Enriched History Data Model (P1)"
status: not_started
priority: P1
created: 2026-03-09
tldr: "**As a** skill author."
project: vskill
external:
  github:
    issue: 28
    url: https://github.com/anton-abyzov/vskill/issues/28
---

# US-001: Enriched History Data Model (P1)

**Feature**: [FS-458](./FEATURE.md)

**As a** skill author
**I want** history entries to store full per-case metrics including input/output token breakdown, duration in seconds, and per-assertion pass/fail results
**So that** I can analyze exactly how each eval case performed across runs

---

## Acceptance Criteria

- [ ] **AC-US1-01**: Given a benchmark run completes, when the history entry is written, then each case includes `inputTokens`, `outputTokens`, `durationMs`, and the full `assertions` array with individual pass/fail
- [ ] **AC-US1-02**: Given a comparison run completes, when the history entry is written, then each case includes a `comparisonDetail` object with `skillDurationMs`, `skillTokens`, `baselineDurationMs`, `baselineTokens`, `skillContentScore`, `skillStructureScore`, `baselineContentScore`, `baselineStructureScore`, and `winner`
- [ ] **AC-US1-03**: Given an old history entry without enriched fields is loaded, when displayed in the UI, then missing fields show "--" or "N/A" instead of errors
- [ ] **AC-US1-04**: Given the new fields are added, when existing code reads a history entry, then all new fields are optional (backward compatible) and the system does not break on old entries

---

## Implementation

**Increment**: [0458-eval-run-history](../../../../../increments/0458-eval-run-history/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Extend BenchmarkCase and add ComparisonCaseDetail types
- [x] **T-002**: Backward-compatible UI rendering for missing enriched fields
