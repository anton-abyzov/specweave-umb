---
id: US-001
feature: FS-445
title: Per-repo cap in trending results (P1)
status: completed
priority: P1
created: 2026-03-07
tldr: "**As a** homepage visitor."
project: vskill-platform
external:
  github:
    issue: 41
    url: "https://github.com/anton-abyzov/vskill-platform/issues/41"
---

# US-001: Per-repo cap in trending results (P1)

**Feature**: [FS-445](./FEATURE.md)

**As a** homepage visitor
**I want** the trending section to show at most 3 skills from the same repository
**So that** I discover a diverse set of trending tools rather than seeing one repo dominate

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a `diversifyTrending()` function in `stats-compute.ts`, when called with `maxPerRepo=3`, then no more than 3 skills from the same `repoUrl` appear in the result
- [x] **AC-US1-02**: Given skills with empty `repoUrl`, when diversity filtering runs, then the `author` field is used as the grouping key instead
- [x] **AC-US1-03**: Given the diversity filter, when skills are processed, then the original input order (momentum-sorted) is preserved for non-filtered entries

---

## Implementation

**Increment**: [0445-trending-diversity](../../../../../increments/0445-trending-diversity/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Implement diversifyTrending pure function
- [x] **T-002**: Write unit tests for diversifyTrending
