---
id: US-004
feature: FS-327
title: Done phase displays flat results list
status: complete
priority: P2
created: 2026-02-22
project: vskill-platform
---
# US-004: Done phase displays flat results list

**Feature**: [FS-327](./FEATURE.md)

skill author
**I want** the done phase to show a simple flat list of results
**So that** I can quickly see the outcome of each skill submission

---

## Acceptance Criteria

- [x] **AC-US4-01**: The done phase displays a flat list of per-skill results (no plugin grouping, no collapsible sections)
- [x] **AC-US4-02**: Each result row shows skill name + status badge or link: "Already verified" (green), "Already pending" (yellow), error message (red), or "Track >>" link
- [x] **AC-US4-03**: The marketplace badge (if present) is shown above the results list
- [x] **AC-US4-04**: Summary line shows counts: "N submitted, N skipped, N failed"

---

## Implementation

**Increment**: [0327-submit-page-discovery-fix](../../../../../increments/0327-submit-page-discovery-fix/spec.md)

