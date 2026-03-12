---
id: US-004
feature: FS-502
title: "ConfigContext File Structure"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** developer."
project: vskill
external:
  github:
    issue: 99
    url: https://github.com/anton-abyzov/vskill/issues/99
---

# US-004: ConfigContext File Structure

**Feature**: [FS-502](./FEATURE.md)

**As a** developer
**I want** ConfigContext.tsx to follow the same file structure and conventions as the existing StudioContext.tsx
**So that** the codebase remains consistent and maintainable

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given ConfigContext.tsx, then it exports a `ConfigProvider` component and a `useConfig()` hook, uses `createContext` + `useReducer`, and lives at `src/eval-ui/src/ConfigContext.tsx`
- [x] **AC-US4-02**: Given App.tsx, when the app renders, then `ConfigProvider` wraps `StudioLayout` (either inside or outside `StudioProvider`, both are valid since they are independent)

---

## Implementation

**Increment**: [0502-config-context-sync](../../../../../increments/0502-config-context-sync/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Create ConfigContext.tsx with reducer, provider, and useConfig hook
- [x] **T-002**: Wire ConfigProvider into App.tsx
