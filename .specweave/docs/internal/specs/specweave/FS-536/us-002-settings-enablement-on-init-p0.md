---
id: US-002
feature: FS-536
title: Settings Enablement on Init (P0)
status: completed
priority: P0
created: 2026-03-15T00:00:00.000Z
tldr: "**As a** SpecWeave user running `specweave init` for the first time."
project: specweave
external_tools:
  ado:
    id: 208
  jira:
    key: SWE2E-267
---

# US-002: Settings Enablement on Init (P0)

**Feature**: [FS-536](./FEATURE.md)

**As a** SpecWeave user running `specweave init` for the first time
**I want** plugins to be enabled in `~/.claude/settings.json` automatically
**So that** Claude Code recognizes all plugins without requiring a separate `refresh-plugins` run

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given `installAllPlugins()` completes successfully, when the function returns, then `enablePluginsInSettings()` has been called with all successfully installed plugin names
- [x] **AC-US2-02**: Given `installAllPlugins()` installs 6 of 8 plugins successfully, when `enablePluginsInSettings()` is called, then only the 6 successful plugin names are passed (failed plugins are excluded)
- [x] **AC-US2-03**: Given `enablePluginsInSettings()` fails (returns false), when `installAllPlugins()` continues, then it logs a warning but does not fail the overall installation

---

## Implementation

**Increment**: [0536-plugin-discover-scope-fix](../../../../../increments/0536-plugin-discover-scope-fix/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
