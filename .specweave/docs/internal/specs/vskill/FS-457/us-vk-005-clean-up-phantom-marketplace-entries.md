---
id: US-VK-005
feature: FS-457
title: Clean Up Phantom Marketplace Entries
status: not_started
priority: P0
created: 2026-03-09
tldr: "**As a** vskill maintainer."
project: vskill
related_projects:
  - specweave
external:
  github:
    issue: 17
    url: https://github.com/anton-abyzov/vskill/issues/17
---

# US-VK-005: Clean Up Phantom Marketplace Entries

**Feature**: [FS-457](./FEATURE.md)

**As a** vskill maintainer
**I want** the marketplace.json to only list plugins that actually exist on disk
**So that** users and tooling do not reference unavailable plugins

---

## Acceptance Criteria

No acceptance criteria defined.

---

## Implementation

**Increment**: [0457-prevent-unwanted-agent-dotfolders](../../../../../increments/0457-prevent-unwanted-agent-dotfolders/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-009**: Remove phantom plugins from vskill marketplace.json
- [ ] **T-010**: Remove phantom plugin references from specweave code and tests
