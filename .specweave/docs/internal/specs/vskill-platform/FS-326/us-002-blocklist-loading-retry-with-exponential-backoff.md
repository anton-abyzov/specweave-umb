---
id: US-002
feature: FS-326
title: Blocklist Loading Retry with Exponential Backoff
status: complete
priority: P1
created: 2026-02-22
project: vskill-platform
---
# US-002: Blocklist Loading Retry with Exponential Backoff

**Feature**: [FS-326](./FEATURE.md)

Trust Center visitor
**I want** to retry loading the blocklist when it fails
**So that** temporary network or server errors don't leave me on a dead-end error screen

---

## Acceptance Criteria

- [x] **AC-US2-01**: When `GET /api/v1/blocklist` fails, BlockedSkillsTab shows an error message with a visible "Retry" button
- [x] **AC-US2-02**: Clicking Retry starts a fresh 3-attempt exponential backoff cycle (delays: ~1s, ~2s, ~4s with jitter)
- [x] **AC-US2-03**: During retry attempts, a loading/spinner state is shown (Retry button disabled or replaced with progress indicator)
- [x] **AC-US2-04**: If all 3 attempts fail, the error message reappears with the Retry button enabled again for another fresh cycle
- [x] **AC-US2-05**: If any attempt succeeds, the blocklist data renders normally and retry state resets

---

## Implementation

**Increment**: [0326-trust-center-fixes](../../../../../increments/0326-trust-center-fixes/spec.md)

