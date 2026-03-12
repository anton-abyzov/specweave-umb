---
id: US-002
feature: FS-443
title: "CERTIFIED-first ordering preserved (P1)"
status: completed
priority: P1
created: "2026-03-07T00:00:00.000Z"
tldr: "**As a** developer searching for skills."
project: vskill-platform
external:
  github:
    issue: 30
    url: "https://github.com/anton-abyzov/vskill-platform/issues/30"
---

# US-002: CERTIFIED-first ordering preserved (P1)

**Feature**: [FS-443](./FEATURE.md)

**As a** developer searching for skills
**I want** CERTIFIED vendor skills to always appear before non-certified skills
**So that** I see trusted, officially certified skills first regardless of star count

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given a CERTIFIED skill with fewer stars than a non-certified skill, when search results are returned, then the CERTIFIED skill appears first
- [x] **AC-US2-02**: Given the sort order change, when existing tests run, then CERTIFIED-first ordering is verified across all 3 search paths

---

## Implementation

**Increment**: [0443-search-rank-by-stars](../../../../../increments/0443-search-rank-by-stars/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-005**: Verify CERTIFIED skill ranks above non-certified regardless of stars
- [x] **T-006**: Run full test suite to confirm all ACs pass
