---
id: US-SW-002
feature: FS-457
title: "Suggest-Only Recommendation Display"
status: not_started
priority: P0
created: 2026-03-09
tldr: "**As a** SpecWeave user."
project: specweave
related_projects: [vskill]
external:
  github:
    issue: 1522
    url: https://github.com/anton-abyzov/specweave/issues/1522
---

# US-SW-002: Suggest-Only Recommendation Display

**Feature**: [FS-457](./FEATURE.md)

**As a** SpecWeave user
**I want** clear, actionable plugin recommendations shown once per session
**So that** I can decide whether to install without being nagged repeatedly

---

## Acceptance Criteria

No acceptance criteria defined.

---

## Implementation

**Increment**: [0457-prevent-unwanted-agent-dotfolders](../../../../../increments/0457-prevent-unwanted-agent-dotfolders/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-003**: Verify suggestion message format includes name, reason, and install command
- [ ] **T-004**: Enforce once-per-session dedup for plugin suggestions
