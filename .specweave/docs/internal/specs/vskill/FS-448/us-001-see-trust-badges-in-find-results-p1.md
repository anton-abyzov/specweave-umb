---
id: US-001
feature: FS-448
title: See trust badges in find results (P1)
status: completed
priority: P1
created: 2026-03-07
tldr: "**As a** CLI user searching for skills."
project: vskill
related_projects:
  - vskill-platform
external:
  github:
    issue: 83
    url: "https://github.com/anton-abyzov/vskill/issues/83"
---

# US-001: See trust badges in find results (P1)

**Feature**: [FS-448](./FEATURE.md)

**As a** CLI user searching for skills
**I want** to see a colored trust badge next to each skill in `vskill find` output
**So that** I can quickly assess the trustworthiness of a skill before installing it

---

## Acceptance Criteria

- [x] **AC-US1-01**: T4 skills display a green checkmark with "certified" label
- [x] **AC-US1-02**: T3 skills display a cyan checkmark with "verified" label
- [x] **AC-US1-03**: T2 skills display a yellow question mark with "maybe" label
- [x] **AC-US1-04**: T1 skills display a dim question mark with "maybe" label
- [x] **AC-US1-05**: Blocked skills (T0) show "BLOCKED" in red instead of a trust badge
- [x] **AC-US1-06**: Skills with no trustTier show no badge (empty string)

---

## Implementation

**Increment**: [0448-trust-badges-find](../../../../../increments/0448-trust-badges-find/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
