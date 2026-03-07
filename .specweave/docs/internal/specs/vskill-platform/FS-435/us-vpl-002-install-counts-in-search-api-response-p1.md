---
id: US-VPL-002
feature: FS-435
title: "Install counts in search API response (P1)"
status: not_started
priority: P1
created: 2026-03-05
tldr: "**As a** CLI developer consuming the search API."
project: vskill-platform
related_projects: [vskill]
external:
  github:
    issue: 40
    url: https://github.com/anton-abyzov/vskill-platform/issues/40
---

# US-VPL-002: Install counts in search API response (P1)

**Feature**: [FS-435](./FEATURE.md)

**As a** CLI developer consuming the search API
**I want** `vskillInstalls` included in search results
**So that** I can display install popularity in the CLI output

---

## Acceptance Criteria

No acceptance criteria defined.

---

## Implementation

**Increment**: [0435-find-command-redesign](../../../../../increments/0435-find-command-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Extend SearchIndexEntry and SearchResult types with vskillInstalls
- [x] **T-002**: Propagate vskillInstalls through buildSearchIndex and edge search path
- [x] **T-003**: Add vskillInstalls to Postgres search paths and blocklist
