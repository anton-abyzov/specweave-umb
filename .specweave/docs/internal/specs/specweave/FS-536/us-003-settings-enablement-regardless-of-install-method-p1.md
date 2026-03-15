---
id: US-003
feature: FS-536
title: Settings Enablement Regardless of Install Method (P1)
status: completed
priority: P0
created: 2026-03-15T00:00:00.000Z
tldr: "**As a** SpecWeave user running `specweave refresh-plugins`."
project: specweave
external_tools:
  ado:
    id: 209
  jira:
    key: SWE2E-268
---

# US-003: Settings Enablement Regardless of Install Method (P1)

**Feature**: [FS-536](./FEATURE.md)

**As a** SpecWeave user running `specweave refresh-plugins`
**I want** plugins to be enabled in settings regardless of whether Claude CLI is available
**So that** direct-copy installs (non-Claude editors) also get proper settings registration

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given `useNativeCli` is false, when `refreshPluginsCommand()` completes with installed plugins, then `enablePluginsInSettings()` is still called
- [x] **AC-US3-02**: Given `useNativeCli` is true, when `refreshPluginsCommand()` completes with installed plugins, then `enablePluginsInSettings()` is called (existing behavior preserved)

---

## Implementation

**Increment**: [0536-plugin-discover-scope-fix](../../../../../increments/0536-plugin-discover-scope-fix/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
