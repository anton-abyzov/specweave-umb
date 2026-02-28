---
id: US-001
feature: FS-375
title: Remove fake skill seed data
status: complete
priority: P1
created: 2026-02-28
project: vskill-platform
external:
  github:
    issue: 1377
    url: https://github.com/anton-abyzov/specweave/issues/1377
---
# US-001: Remove fake skill seed data

**Feature**: [FS-375](./FEATURE.md)

platform operator
**I want** all 156 hardcoded fake skills removed from the seed data file
**So that** the database only contains skills that came through the real submission/scanning pipeline

---

## Acceptance Criteria

- [x] **AC-US1-01**: `seed-data.ts` is renamed to `agent-data.ts` and contains ONLY the `agents` array (44 entries) and `AgentData` type re-export
- [x] **AC-US1-02**: The `skills` export, `SeedSkillData` type, and all 156 skill objects are deleted from the file
- [x] **AC-US1-03**: All imports of `seed-data` across the codebase are updated to `agent-data`
- [x] **AC-US1-04**: `data.ts` imports `agents` from `./agent-data` instead of `./seed-data`
- [x] **AC-US1-05**: `agent-branding.ts` comment referencing `seed-data` is updated

---

## Implementation

**Increment**: [0375-remove-fake-seed-data](../../../../../increments/0375-remove-fake-seed-data/spec.md)

