---
id: US-SW-003
feature: FS-457
title: "LSP Plugin Consent Guard"
status: not_started
priority: P0
created: 2026-03-09
tldr: "**As a** SpecWeave user."
project: specweave
related_projects: [vskill]
external:
  github:
    issue: 1523
    url: https://github.com/anton-abyzov/specweave/issues/1523
---

# US-SW-003: LSP Plugin Consent Guard

**Feature**: [FS-457](./FEATURE.md)

**As a** SpecWeave user
**I want** LSP plugin auto-installation to respect the `suggestOnly` flag
**So that** LSP analyzers are not installed without my consent

---

## Acceptance Criteria

No acceptance criteria defined.

---

## Implementation

**Increment**: [0457-prevent-unwanted-agent-dotfolders](../../../../../increments/0457-prevent-unwanted-agent-dotfolders/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-005**: Add PLUGIN_SUGGEST_ONLY guard to LSP auto-install conditions
- [ ] **T-006**: Verify LSP CLI fallback works without installed LSP plugin
