---
id: US-SPE-001
feature: FS-427
title: Specweave CLI Version Display
status: not_started
priority: P1
created: 2026-03-05
tldr: "**As a** developer."
project: specweave
related_projects:
  - vskill
  - vskill-platform
external:
  github:
    issue: 1490
    url: https://github.com/anton-abyzov/specweave/issues/1490
---

# US-SPE-001: Specweave CLI Version Display

**Feature**: [FS-427](./FEATURE.md)

**As a** developer
**I want** to see the specweave version in sync output
**So that** I can verify which version is running

---

## Acceptance Criteria

- [ ] **AC-SPE-US1-01**: Sync output includes specweave version number
- [ ] **AC-SPE-US1-02**: Version matches package.json

---

## Implementation

**Increment**: [0427-umbrella-sync-lifecycle-test](../../../../../increments/0427-umbrella-sync-lifecycle-test/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-001**: Verify sync-progress routes to all three repos
