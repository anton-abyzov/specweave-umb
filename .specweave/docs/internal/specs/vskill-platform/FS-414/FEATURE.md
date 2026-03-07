---
id: FS-414
title: "Smooth Queue Stats Display"
type: feature
status: completed
priority: P1
created: 2026-03-03T00:00:00.000Z
lastUpdated: 2026-03-07
tldr: "The `/queue` page displays 6 stat cards (Total, Active, Published, Rejected, Blocked, Avg Score)."
complexity: medium
stakeholder_relevant: true
---

# Smooth Queue Stats Display

## TL;DR

**What**: The `/queue` page displays 6 stat cards (Total, Active, Published, Rejected, Blocked, Avg Score).
**Status**: completed | **Priority**: P1
**User Stories**: 3

![Smooth Queue Stats Display illustration](assets/feature-fs-414.jpg)

## Overview

The `/queue` page displays 6 stat cards (Total, Active, Published, Rejected, Blocked, Avg Score). These numbers update in three situations: SSE `state_changed` events trigger optimistic counter changes, a periodic `/api/v1/submissions/stats` fetch refreshes all counts, and a reconciliation effect corrects drift between the live submission list and the KV-cached stats endpoint. Each of these triggers a hard instant jump in the displayed number, which is jarring — particularly for the "Active" card which changes most frequently.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0414-smooth-queue-stats](../../../../../increments/0414-smooth-queue-stats/spec.md) | ✅ completed | 2026-03-03T00:00:00.000Z |

## User Stories

- [US-001: Animated Number Transitions](./us-001-animated-number-transitions.md)
- [US-002: Direction Indicators on Value Change](./us-002-direction-indicators-on-value-change.md)
- [US-003: Cached Data Visual Distinction](./us-003-cached-data-visual-distinction.md)
