---
id: US-002
feature: FS-414
title: "Direction Indicators on Value Change"
status: not_started
priority: P1
created: "2026-03-03T00:00:00.000Z"
tldr: "**As a** queue operator."
project: vskill-platform
external:
  github:
    issue: 38
    url: "https://github.com/anton-abyzov/vskill-platform/issues/38"
---

# US-002: Direction Indicators on Value Change

**Feature**: [FS-414](./FEATURE.md)

**As a** queue operator
**I want** to see a brief directional arrow when a stat number changes
**So that** I can instantly perceive whether the count went up or down without comparing old and new values

---

## Acceptance Criteria

- [ ] **AC-US2-01**: Given a stat card value increases, when the animation starts, then a green upward arrow (↑) appears next to the number and fades out after approximately 1500ms
- [ ] **AC-US2-02**: Given a stat card value decreases, when the animation starts, then a red downward arrow (↓) appears next to the number and fades out after approximately 1500ms
- [ ] **AC-US2-03**: Given `prefers-reduced-motion` is active, when a value changes, then direction indicators are shown without fade animation (appear then disappear at 1500ms with no CSS transition)

---

## Implementation

**Increment**: [0414-smooth-queue-stats](../../../../../increments/0414-smooth-queue-stats/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Add direction indicator to `StatCard`
- [x] **T-004**: Integrate `useAnimatedNumber` into `StatCard`
