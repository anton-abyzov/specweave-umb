---
id: US-001
feature: FS-376
title: "Fix CFR threshold boundary (P1)"
status: completed
priority: P1
created: 2026-02-25T00:00:00.000Z
tldr: "**As a** developer reviewing DORA metrics
**I want** the CFR tier classifier to match documented thresholds (0-15% = Elite)
**So that** a 15% CFR is correctly classified as Elite, not High."
project: specweave
---

# US-001: Fix CFR threshold boundary (P1)

**Feature**: [FS-376](./FEATURE.md)

**As a** developer reviewing DORA metrics
**I want** the CFR tier classifier to match documented thresholds (0-15% = Elite)
**So that** a 15% CFR is correctly classified as Elite, not High

---

## Acceptance Criteria

- [x] **AC-US1-01**: `classifyChangeFailureRate(15)` returns `'Elite'` (was returning `'High'` due to strict `< 15`)
- [x] **AC-US1-02**: `classifyChangeFailureRate(30)` returns `'High'` (boundary inclusive)
- [x] **AC-US1-03**: `classifyChangeFailureRate(45)` returns `'Medium'` (boundary inclusive)
- [x] **AC-US1-04**: Existing tier classifications for values not on boundaries remain unchanged

---

## Implementation

**Increment**: [0376-fix-dora-metrics-pipeline](../../../../../increments/0376-fix-dora-metrics-pipeline/spec.md)

**Tasks**: See increment tasks.md for implementation details.
