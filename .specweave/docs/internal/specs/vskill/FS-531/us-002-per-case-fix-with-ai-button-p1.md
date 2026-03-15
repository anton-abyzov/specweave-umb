---
id: US-002
feature: FS-531
title: "Per-Case Fix with AI Button (P1)"
status: completed
priority: P1
created: 2026-03-15T00:00:00.000Z
tldr: "**As a** skill developer reviewing comparison results."
project: vskill
---

# US-002: Per-Case Fix with AI Button (P1)

**Feature**: [FS-531](./FEATURE.md)

**As a** skill developer reviewing comparison results
**I want** a "Fix" button on each comparison card that has failing assertions
**So that** I can navigate directly to the improve page scoped to that case instead of using only the global fix action

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given a comparison card where the case has completed with at least one failing assertion, when the card renders, then a "Fix" button is visible inline in the bottom area of the card near the assertions
- [x] **AC-US2-02**: Given a comparison card where the case has completed with zero failing assertions, when the card renders, then no "Fix" button is shown
- [x] **AC-US2-03**: Given a comparison card where the case has zero total assertions, when the card renders, then no "Fix" button is shown
- [x] **AC-US2-04**: Given the user clicks a per-case "Fix" button, when navigation occurs, then the browser navigates to the workspace improve page with `eval_id` query parameter scoped to that case
- [x] **AC-US2-05**: Given the user clicks a per-case "Fix" button, when the improve page loads, then the failing assertion context from that case is included in the navigation state

---

## Implementation

**Increment**: [0531-benchmark-comparison-ux](../../../../../increments/0531-benchmark-comparison-ux/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
