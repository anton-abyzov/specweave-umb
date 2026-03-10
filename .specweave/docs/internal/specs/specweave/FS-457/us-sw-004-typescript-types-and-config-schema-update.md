---
id: US-SW-004
feature: FS-457
title: "TypeScript Types and Config Schema Update"
status: not_started
priority: P0
created: 2026-03-09
tldr: "**As a** SpecWeave contributor."
project: specweave
related_projects: [vskill]
external:
  github:
    issue: 1524
    url: https://github.com/anton-abyzov/specweave/issues/1524
---

# US-SW-004: TypeScript Types and Config Schema Update

**Feature**: [FS-457](./FEATURE.md)

**As a** SpecWeave contributor
**I want** the `PluginAutoLoadConfig` interface and config schema to include the `suggestOnly` field
**So that** the type system and validation accurately reflect the available configuration

---

## Acceptance Criteria

No acceptance criteria defined.

---

## Implementation

**Increment**: [0457-prevent-unwanted-agent-dotfolders](../../../../../increments/0457-prevent-unwanted-agent-dotfolders/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-007**: Add suggestOnly to PluginAutoLoadConfig interface
- [ ] **T-008**: Add suggestOnly to specweave-config.schema.json
