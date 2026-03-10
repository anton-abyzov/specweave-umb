---
id: US-004
feature: FS-465
title: Assertion Health and Quality Indicators (P1)
status: not_started
priority: P1
created: 2026-03-09
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 44
    url: https://github.com/anton-abyzov/vskill/issues/44
---

# US-004: Assertion Health and Quality Indicators (P1)

**Feature**: [FS-465](./FEATURE.md)

**As a** skill developer
**I want** to see quality indicators on my assertions
**So that** I can identify flaky, non-discriminating, and regressed assertions

---

## Acceptance Criteria

- [ ] **AC-US4-01**: Given an assertion has a 30-70% pass rate across 3+ runs, when viewing it in the Tests panel, then a yellow "Flaky" badge appears next to it
- [ ] **AC-US4-02**: Given an assertion passes on both skill and baseline runs, when viewing it in the Tests panel, then a gray "Non-discriminating" badge appears next to it
- [ ] **AC-US4-03**: Given an assertion was passing in the previous run but fails in the latest run, when viewing it in the Tests panel, then a red downward arrow regression marker appears next to it
- [ ] **AC-US4-04**: Given quality badges are displayed, when inspecting the data source, then badge data is derived from the existing /api/skills/:plugin/:skill/stats and history APIs (no new backend endpoints)

---

## Implementation

**Increment**: [0465-skill-builder-redesign](../../../../../increments/0465-skill-builder-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
