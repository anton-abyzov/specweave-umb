---
id: US-001
feature: FS-414
title: "Animated Number Transitions"
status: not_started
priority: P1
created: 2026-03-03T00:00:00.000Z
tldr: "**As a** queue operator."
project: vskill-platform
external:
  github:
    issue: 37
    url: https://github.com/anton-abyzov/vskill-platform/issues/37
---

# US-001: Animated Number Transitions

**Feature**: [FS-414](./FEATURE.md)

**As a** queue operator
**I want** stat card numbers to animate smoothly when they change
**So that** I can follow value changes without disorienting visual jumps

---

## Acceptance Criteria

- [ ] **AC-US1-01**: Given any stat card value changes, when the new value arrives, then the displayed number interpolates from the old value to the new value over 400ms using an easeOutCubic curve, updating via requestAnimationFrame on each frame
- [ ] **AC-US1-02**: Given a user has `prefers-reduced-motion: reduce` set at the OS level, when a stat card value changes, then the new value is shown immediately with no animation (the hook skips the rAF loop)
- [ ] **AC-US1-03**: Given the animation is in progress and a new target value arrives before the current animation completes, when the hook receives the updated target, then the animation restarts from the current animated value to the new target (no queuing, no gap)
- [ ] **AC-US1-04**: Given the `useAnimatedNumber` hook, when the component unmounts mid-animation, then the in-flight `requestAnimationFrame` callback is cancelled via `cancelAnimationFrame` to prevent memory leaks and state updates on unmounted components

---

## Implementation

**Increment**: [0414-smooth-queue-stats](../../../../../increments/0414-smooth-queue-stats/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Implement `useAnimatedNumber` hook
- [x] **T-002**: Write unit tests for `useAnimatedNumber`
