---
id: US-003
feature: FS-476
title: "Eval freshness timestamp"
status: completed
priority: P1
created: "2026-03-10T00:00:00.000Z"
tldr: "**As a** user viewing a skill detail page."
project: vskill-platform
external:
  github:
    issue: 56
    url: "https://github.com/anton-abyzov/vskill-platform/issues/56"
---

# US-003: Eval freshness timestamp

**Feature**: [FS-476](./FEATURE.md)

**As a** user viewing a skill detail page
**I want** to see when a skill was last evaluated
**So that** I can assess whether the evaluation data is current

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given a skill with `lastEvalAt` set, when the eval section renders, then a relative timestamp (e.g., "3d ago") appears inline after the run count
- [x] **AC-US3-02**: Given a skill with `lastEvalAt` is null (never evaluated), when the eval section renders, then no freshness timestamp is shown
- [x] **AC-US3-03**: Given the eval-store `storeEvalRun` function, when the Skill record DB update is performed, then the update is awaited (not fire-and-forget) so failures propagate
- [x] **AC-US3-04**: Given the eval-store `storeEvalRun` function, when the Skill record DB update fails, then the error is logged and re-thrown (caller can handle retry)

---

## Implementation

**Increment**: [0476-skill-metadata-alignment](../../../../../increments/0476-skill-metadata-alignment/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: Await Skill DB update in eval-store and propagate failures
- [x] **T-005**: Display lastEvalAt freshness timestamp on skill detail page
