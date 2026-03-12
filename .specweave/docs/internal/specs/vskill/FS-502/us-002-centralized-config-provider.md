---
id: US-002
feature: FS-502
title: Centralized Config Provider
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** developer."
project: vskill
external:
  github:
    issue: 97
    url: https://github.com/anton-abyzov/vskill/issues/97
---

# US-002: Centralized Config Provider

**Feature**: [FS-502](./FEATURE.md)

**As a** developer
**I want** a single ConfigContext that loads config once and shares it across all components
**So that** we eliminate redundant API calls and have a single source of truth for config state

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given the app mounts, when ConfigProvider initializes, then exactly one `api.getConfig()` call is made (verified by checking network requests or API mock call count)
- [x] **AC-US2-02**: Given ConfigProvider has loaded config, when any component calls `useConfig()`, then it receives the current `ConfigResponse` object, a `loading` boolean, and an `updateConfig(provider, model)` function
- [x] **AC-US2-03**: Given a component calls `useConfig()` outside of a ConfigProvider, then it throws an error with message "useConfig must be used within ConfigProvider"

---

## Implementation

**Increment**: [0502-config-context-sync](../../../../../increments/0502-config-context-sync/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Create ConfigContext.tsx with reducer, provider, and useConfig hook
- [x] **T-014**: Run full test suite and confirm no regressions
