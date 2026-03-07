---
id: US-001
feature: FS-453
title: Remove redundant TierBadge from skill detail page
status: complete
priority: P1
created: 2026-03-07
project: vskill-platform
external:
  github:
    issue: 1513
    url: https://github.com/anton-abyzov/specweave/issues/1513
---
# US-001: Remove redundant TierBadge from skill detail page

**Feature**: [FS-453](./FEATURE.md)

skill consumer
**I want** a single unified trust badge on the skill detail page
**So that** I'm not confused by redundant "VERIFIED" + "T3 VERIFIED" badges

---

## Acceptance Criteria

- [x] **AC-US1-01**: TierBadge component is not rendered on the skill detail page
- [x] **AC-US1-02**: TrustBadge remains visible with correct tier display
- [x] **AC-US1-03**: TierBadge import is removed from the skill detail page file

---

## Implementation

**Increment**: [0453-unify-skill-page-badges](../../../../../increments/0453-unify-skill-page-badges/spec.md)

