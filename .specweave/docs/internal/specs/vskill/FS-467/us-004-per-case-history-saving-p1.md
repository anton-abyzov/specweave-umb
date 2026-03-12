---
id: US-004
feature: FS-467
title: "Per-Case History Saving (P1)"
status: completed
priority: P1
created: 2026-03-10
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 56
    url: "https://github.com/anton-abyzov/vskill/issues/56"
---

# US-004: Per-Case History Saving (P1)

**Feature**: [FS-467](./FEATURE.md)

**As a** skill developer
**I want** single-case runs to be saved to benchmark history
**So that** I can track per-case progress over time and compare results across iterations

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given a single-case run that completes successfully, when the server writes the history entry, then the entry includes a `scope: "single"` field and contains only the one executed case
- [x] **AC-US4-02**: Given a bulk run that completes, when the server writes the history entry, then the entry includes `scope: "bulk"` and contains all cases that completed (including errored ones)
- [x] **AC-US4-03**: Given a single-case history entry, when viewed in the history panel, then it is visually distinguishable from bulk run entries (e.g., labeled "Single: case-name" vs "Full Run")
- [x] **AC-US4-04**: Given a per-case history query (`GET /api/skills/:plugin/:skill/history/case/:evalId`), then entries from both single-case and bulk runs appear in the timeline

---

## Implementation

**Increment**: [0467-parallel-per-case-benchmark](../../../../../increments/0467-parallel-per-case-benchmark/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-009**: Save single-case and bulk-run history entries with `scope` field
- [x] **T-010**: Display `scope` differentiation in history panel UI
