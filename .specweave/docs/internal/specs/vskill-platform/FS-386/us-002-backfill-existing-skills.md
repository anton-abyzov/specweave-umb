---
id: US-002
feature: FS-386
title: Backfill Existing Skills
status: complete
priority: P1
created: 2026-02-27
project: vskill-platform
external:
  github:
    issue: 1417
    url: https://github.com/anton-abyzov/specweave/issues/1417
---
# US-002: Backfill Existing Skills

**Feature**: [FS-386](./FEATURE.md)

platform operator
**I want** existing published skills to have their `skillPath` populated
**So that** all skills show the View Source link, not just newly published ones

---

## Acceptance Criteria

- [x] **AC-US2-01**: Backfill script queries Skills with null skillPath and populates from linked Submissions
- [x] **AC-US2-02**: Script supports dry-run mode and execute mode
- [x] **AC-US2-03**: Script logs updated/skipped counts

---

## Implementation

**Increment**: [0386-skill-path-view-source](../../../../../increments/0386-skill-path-view-source/spec.md)

