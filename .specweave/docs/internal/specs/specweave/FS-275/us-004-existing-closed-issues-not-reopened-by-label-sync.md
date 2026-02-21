---
id: US-004
feature: FS-275
title: Existing Closed Issues Not Reopened by Label Sync
status: complete
priority: P1
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1211
    url: "https://github.com/anton-abyzov/specweave/issues/1211"
---
# US-004: Existing Closed Issues Not Reopened by Label Sync

**Feature**: [FS-275](./FEATURE.md)

developer
**I want** the auto-close fix to be idempotent and safe
**So that** already-closed issues are not reopened or double-closed

---

## Acceptance Criteria

- [x] **AC-US4-01**: Running progress-sync on an already-closed issue with `status:complete` label is a no-op (does not post duplicate comments or attempt re-close)
- [x] **AC-US4-02**: The fix does not interfere with the existing `updateUserStoryIssue()` closure path in `github-feature-sync.ts` (no double-close race)
- [x] **AC-US4-03**: Unit tests verify idempotency: calling `updateStatusLabels()` twice with `overallComplete=true` on a CLOSED issue produces no side effects

---

## Implementation

**Increment**: [0275-auto-close-on-status-complete](../../../../../increments/0275-auto-close-on-status-complete/spec.md)

