---
id: US-004
feature: FS-504
title: Result Ranking with Exact Match Priority (P1)
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** CLI user."
project: vskill
external_tools:
  jira:
    key: SWE2E-262
  ado:
    id: 210
---

# US-004: Result Ranking with Exact Match Priority (P1)

**Feature**: [FS-504](./FEATURE.md)

**As a** CLI user
**I want** results ranked by relevance and trust
**So that** the most likely correct skill appears first

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given search results, then results are sorted: blocked at end, then by cert tier (CERTIFIED > VERIFIED > other), then by GitHub stars descending, then by score descending -- matching the `find` command ranking
- [x] **AC-US4-02**: Given a result whose `skillSlug` exactly matches the input query (case-insensitive), then that result is promoted to first position among non-blocked results regardless of cert tier or stars
- [x] **AC-US4-03**: Given all search results are blocked, then the CLI displays the blocked results and prints an error that no installable skills were found

---

## Implementation

**Increment**: [0504-install-skill-discovery](../../../../../increments/0504-install-skill-discovery/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-006**: Validate ranking function edge cases
- [x] **T-007**: Regression tests for existing `owner/repo` and `owner/repo/skill` paths
