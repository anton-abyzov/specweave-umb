---
id: US-002
feature: FS-504
title: "Interactive Disambiguation for Multiple Matches (P1)"
status: not_started
priority: P1
created: 2026-03-12
tldr: "**As a** CLI user in an interactive terminal."
project: vskill
---

# US-002: Interactive Disambiguation for Multiple Matches (P1)

**Feature**: [FS-504](./FEATURE.md)

**As a** CLI user in an interactive terminal
**I want** to choose from ranked search results when my query matches multiple skills
**So that** I can install the correct skill without retyping the command

---

## Acceptance Criteria

- [ ] **AC-US2-01**: Given multiple non-blocked results and a TTY environment, then the CLI displays results using the same format as `vskill find` (skill ID, stars, trust badge, URL) and presents an interactive `promptChoice` selection
- [ ] **AC-US2-02**: Given the user selects a result from the interactive prompt, then the CLI re-invokes `addCommand("owner/repo/skill", opts)` with the selected result's slug fields
- [ ] **AC-US2-03**: Given results contain both blocked and non-blocked skills, then blocked skills are displayed with BLOCKED label but are not selectable in the interactive prompt

---

## Implementation

**Increment**: [0504-install-skill-discovery](../../../../../increments/0504-install-skill-discovery/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-003**: TTY interactive disambiguation with `promptChoice`
- [ ] **T-004**: Display format parity with `vskill find`
