---
id: US-003
feature: FS-414
title: "Cached Data Visual Distinction"
status: not_started
priority: P1
created: "2026-03-03T00:00:00.000Z"
tldr: "**As a** queue operator."
project: vskill-platform
external:
  github:
    issue: 39
    url: "https://github.com/anton-abyzov/vskill-platform/issues/39"
---

# US-003: Cached Data Visual Distinction

**Feature**: [FS-414](./FEATURE.md)

**As a** queue operator
**I want** to know when stat cards are showing KV-cached data versus freshly fetched data
**So that** I can trust the numbers I see and understand when they might be up to 5 minutes stale

---

## Acceptance Criteria

- [ ] **AC-US3-01**: Given the stats were last updated from the KV-cached endpoint (initial load or fetch without live reconciliation), when `StatCard` receives `isCached={true}`, then the card renders with a 3px left border accent in a muted amber/yellow tone (`#B45309` at 40% opacity or equivalent)
- [ ] **AC-US3-02**: Given live data has arrived (reconciliation has run or a fresh `/api/v1/submissions/stats` fetch succeeded), when `StatCard` receives `isCached={false}`, then the left border accent transitions away over 600ms CSS transition and the card returns to its default border style
- [ ] **AC-US3-03**: Given the stat cards grid, when any card shows a cached border accent, then no tooltip or text label is added — the accent is the sole indicator (non-intrusive)

---

## Implementation

**Increment**: [0414-smooth-queue-stats](../../../../../increments/0414-smooth-queue-stats/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-005**: Add `isCached` prop and border accent to `StatCard`
- [x] **T-006**: Add `statsAreCached` state to `QueuePageClient` and wire to `StatCard` instances
