---
id: US-002
feature: FS-420
title: Vendor discovery runs on cron schedule (P1)
status: not_started
priority: P1
created: 2026-03-03
tldr: "**As a** platform operator."
project: vskill-platform
external:
  github:
    issue: 3
    url: https://github.com/anton-abyzov/vskill-platform/issues/3
---

# US-002: Vendor discovery runs on cron schedule (P1)

**Feature**: [FS-420](./FEATURE.md)

**As a** platform operator
**I want** vendor-orgs discovery to run automatically on the hourly cron
**So that** vendor skill freshness doesn't depend on manual admin intervention

---

## Acceptance Criteria

- [ ] **AC-US2-01**: Given the cron scheduled handler fires at the :00 minute, when discovery runs, then `vendor-orgs` is included in the sources list alongside `npm`
- [ ] **AC-US2-02**: Given vendor-orgs discovery runs hourly with dedup bypass, when a vendor adds a new skill, then it appears in search results within ~1 hour

---

## Implementation

**Increment**: [0420-vendor-skill-freshness](../../../../../increments/0420-vendor-skill-freshness/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Add vendor-orgs to cron hourly discovery sources
