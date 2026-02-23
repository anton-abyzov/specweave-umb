---
id: US-002
feature: FS-325
title: NPM Downloads Only for Real Packages
status: complete
priority: P1
created: 2026-02-22
project: vskill-platform
external:
  github:
    issue: 1287
    url: https://github.com/anton-abyzov/specweave/issues/1287
---
# US-002: NPM Downloads Only for Real Packages

**Feature**: [FS-325](./FEATURE.md)

visitor viewing the NPM Downloads metric
**I want** only skills with a valid `npmPackage` field to contribute to the total
**So that** the download count reflects real npm registry data, not fabricated numbers

---

## Acceptance Criteria

- [x] **AC-US2-01**: `totalNpm` on the homepage is computed as `allSkills.filter(s => s.npmPackage).reduce(...)` -- only skills with `npmPackage` set contribute
- [x] **AC-US2-02**: The MiniBarChart for NPM Downloads only shows skills that have a `npmPackage` field
- [x] **AC-US2-03**: Seed data skills without `npmPackage` have their `npmDownloads` set to `0` (data cleanup)
- [x] **AC-US2-04**: The subtitle shows "from N packages" (where N = count of skills with `npmPackage`)
- [x] **AC-US2-05**: The `enrichSkillWithMetrics()` function skips npm fetching when `npmPackage` is absent (already the case -- verify with test)

---

## Implementation

**Increment**: [0325-homepage-metrics-accuracy](../../../../../increments/0325-homepage-metrics-accuracy/spec.md)

