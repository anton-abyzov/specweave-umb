---
id: US-001
feature: FS-504
title: "Search Registry on Flat Name Install (P1)"
status: not_started
priority: P1
created: 2026-03-12
tldr: "**As a** CLI user."
project: vskill
---

# US-001: Search Registry on Flat Name Install (P1)

**Feature**: [FS-504](./FEATURE.md)

**As a** CLI user
**I want** `vskill install skill-creator` to search the registry automatically
**So that** I do not need to run `vskill find` as a separate step

---

## Acceptance Criteria

- [ ] **AC-US1-01**: Given a flat name input (no slashes), when `installFromRegistry` is invoked, then `searchSkills(flatName)` is called instead of `getSkill(flatName)`
- [ ] **AC-US1-02**: Given `searchSkills()` returns exactly one non-blocked result, then installation proceeds automatically by re-invoking `addCommand("owner/repo/skill", opts)` using the result's slug fields
- [ ] **AC-US1-03**: Given `searchSkills()` returns zero results, then the CLI prints an error message and suggests `vskill find <query>` for broader search
- [ ] **AC-US1-04**: Given `searchSkills()` throws an error (network failure, API down), then the CLI falls back to the existing `getSkill()` + `installFromRegistry` behavior

---

## Implementation

**Increment**: [0504-install-skill-discovery](../../../../../increments/0504-install-skill-discovery/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-001**: Create `src/utils/skill-display.ts` with extracted helpers and `rankSearchResults`
- [ ] **T-002**: Implement `resolveViaSearch()` in `add.ts` and wire flat-name branch
