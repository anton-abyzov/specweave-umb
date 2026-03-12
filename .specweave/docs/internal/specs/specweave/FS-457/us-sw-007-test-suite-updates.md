---
id: US-SW-007
feature: FS-457
title: "Test Suite Updates"
status: not_started
priority: P0
created: 2026-03-09
tldr: "**As a** SpecWeave contributor."
project: specweave
related_projects: [vskill]
external:
  github:
    issue: 1526
    url: "https://github.com/anton-abyzov/specweave/issues/1526"
---

# US-SW-007: Test Suite Updates

**Feature**: [FS-457](./FEATURE.md)

**As a** SpecWeave contributor
**I want** the test suite to reflect the new `suggestOnly: true` default
**So that** tests validate consent-first behavior and catch regressions

---

## Acceptance Criteria

No acceptance criteria defined.

---

## Implementation

**Increment**: [0457-prevent-unwanted-agent-dotfolders](../../../../../increments/0457-prevent-unwanted-agent-dotfolders/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-013**: Flip ~14 existing assertions from suggestOnly: false to suggestOnly: true
- [ ] **T-014**: Add new consent-flow tests (suggestion format, dedup, opt-out, LSP guard)
