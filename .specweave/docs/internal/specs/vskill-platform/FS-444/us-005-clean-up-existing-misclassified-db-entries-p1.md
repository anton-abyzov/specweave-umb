---
id: US-005
feature: FS-444
title: "Clean Up Existing Misclassified DB Entries (P1)"
status: completed
priority: P0
created: 2026-03-07T00:00:00.000Z
tldr: "**As a** marketplace maintainer."
project: vskill-platform
external:
  github:
    issue: 35
    url: https://github.com/anton-abyzov/vskill-platform/issues/35
---

# US-005: Clean Up Existing Misclassified DB Entries (P1)

**Feature**: [FS-444](./FEATURE.md)

**As a** marketplace maintainer
**I want** existing framework plugin entries removed from the marketplace
**So that** users only see legitimate community skills

---

## Acceptance Criteria

- [x] **AC-US5-01**: Given submissions with `skillPath` matching `plugins/specweave*/skills/`, when the cleanup script runs, then their state is set to REJECTED with reason `framework_plugin`
- [x] **AC-US5-02**: Given published Skill rows linked to those submissions, when the cleanup script runs, then the Skill rows are hard-deleted from the database
- [x] **AC-US5-03**: The cleanup script logs how many submissions were rejected and how many Skill rows were deleted
- [x] **AC-US5-04**: The cleanup script is idempotent -- running it twice produces no additional changes

---

## Implementation

**Increment**: [0444-filter-framework-plugin-skills](../../../../../increments/0444-filter-framework-plugin-skills/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-013**: Create and run cleanup-framework-plugins.ts script
