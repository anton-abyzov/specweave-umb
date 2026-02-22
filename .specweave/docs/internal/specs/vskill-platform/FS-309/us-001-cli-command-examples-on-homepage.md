---
id: US-001
feature: FS-309
title: CLI Command Examples on Homepage
status: complete
priority: P1
created: 2026-02-22
project: vskill-platform
external:
  github:
    issue: 1258
    url: https://github.com/anton-abyzov/specweave/issues/1258
---
# US-001: CLI Command Examples on Homepage

**Feature**: [FS-309](./FEATURE.md)

developer visiting the homepage
**I want** to see real vskill install and find command examples
**So that** I can immediately understand how to use the CLI without reading separate docs

---

## Acceptance Criteria

- [x] **AC-US1-01**: The hero section shows at least one concrete `vskill install` example (e.g., `$ npx vskill install anthropics/skills`)
- [x] **AC-US1-02**: The hero section shows at least one concrete `vskill find` example (e.g., `$ npx vskill find security`)
- [x] **AC-US1-03**: The examples use real skill names/repos that exist in the seed data
- [x] **AC-US1-04**: The `or bunx / pnpx / yarn dlx` hint is preserved

---

## Implementation

**Increment**: [0309-homepage-improvements](../../../../../increments/0309-homepage-improvements/spec.md)

