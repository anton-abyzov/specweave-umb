---
id: US-004
feature: FS-326
title: Auto-Refresh with Relative Time Indicator
status: complete
priority: P2
created: 2026-02-22
project: vskill-platform
---
# US-004: Auto-Refresh with Relative Time Indicator

**Feature**: [FS-326](./FEATURE.md)

Trust Center visitor
**I want** to see when the tier distribution was last refreshed and manually trigger a refresh
**So that** I know the data is current without reloading the entire page

---

## Acceptance Criteria

- [x] **AC-US4-01**: A relative time label (e.g., "updated 45s ago", "updated 2m ago") appears below the tier distribution cards, right-aligned
- [x] **AC-US4-02**: The label uses small muted text styling (`fontSize: 0.75rem`, `color: var(--text-faint)`)
- [x] **AC-US4-03**: A small circular refresh icon button appears next to the relative time label
- [x] **AC-US4-04**: Clicking the refresh button re-fetches `GET /api/v1/stats` and updates the tier cards
- [x] **AC-US4-05**: The relative time label updates live (ticks every ~15 seconds) without page reload
- [x] **AC-US4-06**: During refresh fetch, the refresh button shows a spinning/disabled state

---

## Implementation

**Increment**: [0326-trust-center-fixes](../../../../../increments/0326-trust-center-fixes/spec.md)

