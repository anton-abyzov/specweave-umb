---
id: US-003
feature: FS-375
title: Harden enrichment 404 handling
status: complete
priority: P1
created: 2026-02-28
project: vskill-platform
---
# US-003: Harden enrichment 404 handling

**Feature**: [FS-375](./FEATURE.md)

platform operator
**I want** the enrichment cron to handle GitHub 404s more robustly for skills with deleted/invalid repos
**So that** 404 responses are tracked and skills with persistently dead repos can be flagged

---

## Acceptance Criteria

- [x] **AC-US3-01**: When enrichment encounters a GitHub 404, it increments a `repo404Count` counter on the skill record
- [x] **AC-US3-02**: When `repo404Count` reaches a configurable threshold (default: 3), the skill's `isDeprecated` flag is set to `true` with a deprecation reason
- [x] **AC-US3-03**: A successful GitHub response (200) resets `repo404Count` to 0
- [x] **AC-US3-04**: The enrichment test suite has tests for 404 counter increment, threshold deprecation, and counter reset on success
- [x] **AC-US3-05**: The existing "does NOT auto-deprecate on single 404" test is updated to reflect the counter-based approach

---

## Implementation

**Increment**: [0375-remove-fake-seed-data](../../../../../increments/0375-remove-fake-seed-data/spec.md)

