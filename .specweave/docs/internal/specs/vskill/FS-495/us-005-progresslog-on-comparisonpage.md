---
id: US-005
feature: FS-495
title: "ProgressLog on ComparisonPage"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** Skill Studio user."
project: vskill
---

# US-005: ProgressLog on ComparisonPage

**Feature**: [FS-495](./FEATURE.md)

**As a** Skill Studio user
**I want** to see a ProgressLog on the ComparisonPage during a running comparison
**So that** I get real-time feedback about which phase is executing instead of a static spinner

---

## Acceptance Criteria

- [x] **AC-US5-01**: Given a comparison is running, when progress SSE events arrive, then ComparisonPage renders a ProgressLog component with accumulated entries
- [x] **AC-US5-02**: Given a comparison completes or errors, when `running` becomes false, then the ProgressLog stops showing the active spinner
- [x] **AC-US5-03**: Given multiple eval cases run sequentially, when a new case starts, then progress entries for the new case appear with fresh phase labels (per-case reset via eval_id context)

---

## Implementation

**Increment**: [0495-comparison-progress-observability](../../../../../increments/0495-comparison-progress-observability/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-008**: Render ProgressLog in ComparisonPage using SSE progress events
