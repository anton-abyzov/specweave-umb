---
id: US-001
feature: FS-275
title: GitHub Issues Auto-Close When status:complete Label Applied
status: complete
priority: P1
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1208
    url: https://github.com/anton-abyzov/specweave/issues/1208
---
# US-001: GitHub Issues Auto-Close When status:complete Label Applied

**Feature**: [FS-275](./FEATURE.md)

developer using SpecWeave with GitHub sync
**I want** GitHub issues to be automatically closed when progress-sync determines the user story is complete
**So that** issues with `status:complete` label are not left in OPEN state (like issue #1198)

---

## Acceptance Criteria

- [x] **AC-US1-01**: `updateStatusLabels()` in `github-feature-sync.ts` closes the issue via `gh issue close` when the new status label is `status:complete` and the issue is currently OPEN
- [x] **AC-US1-02**: If the issue is already CLOSED, `updateStatusLabels()` does not attempt a redundant close operation
- [x] **AC-US1-03**: A completion comment is posted before closing (consistent with existing closure flows)
- [x] **AC-US1-04**: Unit tests verify that `updateStatusLabels()` with `overallComplete=true` triggers issue closure on an OPEN issue
- [x] **AC-US1-05**: Unit tests verify that `updateStatusLabels()` with `overallComplete=true` skips closure on an already-CLOSED issue

---

## Implementation

**Increment**: [0275-auto-close-on-status-complete](../../../../../increments/0275-auto-close-on-status-complete/spec.md)

