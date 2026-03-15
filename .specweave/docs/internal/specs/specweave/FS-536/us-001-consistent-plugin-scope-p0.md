---
id: US-001
feature: FS-536
title: Consistent Plugin Scope (P0)
status: completed
priority: P0
created: 2026-03-15T00:00:00.000Z
tldr: "**As a** SpecWeave user."
project: specweave
external_tools:
  ado:
    id: 194
  jira:
    key: SWE2E-266
---

# US-001: Consistent Plugin Scope (P0)

**Feature**: [FS-536](./FEATURE.md)

**As a** SpecWeave user
**I want** all SpecWeave plugins to install at user scope
**So that** Claude Code's Discover tab recognizes them as installed

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given `DEFAULT_PLUGIN_SCOPE_CONFIG` in `plugin-scope.ts`, when `specweaveScope` is read, then its value is `'user'`
- [x] **AC-US1-02**: Given the `sw` entry in `scopeOverrides`, when `specweaveScope` is already `'user'`, then the `sw` override is removed as redundant
- [x] **AC-US1-03**: Given a SpecWeave plugin name (e.g., `frontend`, `sw-github`), when `getPluginScope()` is called, then it returns `'user'`

---

## Implementation

**Increment**: [0536-plugin-discover-scope-fix](../../../../../increments/0536-plugin-discover-scope-fix/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
