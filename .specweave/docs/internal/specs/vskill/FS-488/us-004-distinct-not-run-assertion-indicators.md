---
id: US-004
feature: FS-488
title: "Distinct 'Not Run' Assertion Indicators"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** skill author."
project: vskill
---

# US-004: Distinct "Not Run" Assertion Indicators

**Feature**: [FS-488](./FEATURE.md)

**As a** skill author
**I want** assertions that have not been evaluated to display a visually distinct indicator
**So that** I can immediately distinguish "not run" from "running" or "passed/failed" states

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given an assertion with no result (not yet evaluated), when displayed, then it shows a circle with a dashed border instead of a solid gray fill
- [x] **AC-US4-02**: Given an assertion with a pass/fail result, when displayed, then it continues to show the existing green check or red X icon (no regression)

---

## Implementation

**Increment**: [0488-skill-studio-status-ux](../../../../../increments/0488-skill-studio-status-ux/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-005**: Replace solid gray circle with dashed-border "not run" indicator
