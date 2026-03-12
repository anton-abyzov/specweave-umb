---
increment: 0502-config-context-sync
title: Centralized config state for Skill Studio eval-ui
type: feature
priority: P1
status: completed
created: 2026-03-12T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Centralized Config State for Skill Studio Eval-UI

## Problem Statement

The Skill Studio eval-ui has 12 independent `api.getConfig()` calls across 10 components. Each component fetches config on mount, creating isolated snapshots of server state. When the user changes the model via ModelSelector (the only mutation point), other components retain stale config until they are remounted. This causes the "Generate with {model}" button in CreateSkillInline to show a different model than what the user just selected in the sidebar.

## Goals

- Eliminate stale config state across all components by centralizing config into a single React Context
- Reduce 12 independent API calls to 1 on app startup
- Ensure model changes propagate instantly to all mounted components
- Follow the established StudioContext pattern (createContext + useReducer + custom hook)

## User Stories

### US-001: Instant Model Propagation on Selection
**Project**: vskill
**As a** skill author
**I want** all UI elements reflecting the active model to update immediately when I change the model in the sidebar selector
**So that** I have confidence that the correct model will be used for all actions

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given the user is on the studio page with ModelSelector and CreateSkillInline both visible, when the user selects a different model in ModelSelector, then the "Generate with {model}" button text in CreateSkillInline reflects the new model name without page reload or component remount
- [x] **AC-US1-02**: Given the user changes the model in ModelSelector and the `api.setConfig()` call succeeds, then the context state updates only after server confirmation (not optimistically)
- [x] **AC-US1-03**: Given the user changes the model in ModelSelector and the `api.setConfig()` call fails, then the context retains the previous confirmed config and ModelSelector shows the `saving` state followed by reverting to the prior selection

### US-002: Centralized Config Provider
**Project**: vskill
**As a** developer
**I want** a single ConfigContext that loads config once and shares it across all components
**So that** we eliminate redundant API calls and have a single source of truth for config state

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the app mounts, when ConfigProvider initializes, then exactly one `api.getConfig()` call is made (verified by checking network requests or API mock call count)
- [x] **AC-US2-02**: Given ConfigProvider has loaded config, when any component calls `useConfig()`, then it receives the current `ConfigResponse` object, a `loading` boolean, and an `updateConfig(provider, model)` function
- [x] **AC-US2-03**: Given a component calls `useConfig()` outside of a ConfigProvider, then it throws an error with message "useConfig must be used within ConfigProvider"

### US-003: Component Migration to Shared Context
**Project**: vskill
**As a** developer
**I want** all 10 components that currently call `api.getConfig()` independently to use the shared ConfigContext instead
**So that** config state is consistent everywhere and we remove duplicated fetch logic

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the codebase after migration, when searching for `api.getConfig()` in component files, then zero direct calls exist in: ModelSelector, LeftPanel, CreateSkillInline, SkillImprovePanel, AiEditBar, EditorPanel, ModelCompareModal, BenchmarkPage, ComparisonPage, CreateSkillPage
- [x] **AC-US3-02**: Given components that derive local model overrides from config (SkillImprovePanel, AiEditBar, CreateSkillPage), when they mount, then they initialize their local "selected model for this action" state from the context's config values while retaining independent local model selection
- [x] **AC-US3-03**: Given BenchmarkPage calls `handleStartBenchmark` or `handleStartBaseline`, when the run starts, then it reads the model from the context's cached value (no additional `api.getConfig()` call)

### US-004: ConfigContext File Structure
**Project**: vskill
**As a** developer
**I want** ConfigContext.tsx to follow the same file structure and conventions as the existing StudioContext.tsx
**So that** the codebase remains consistent and maintainable

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given ConfigContext.tsx, then it exports a `ConfigProvider` component and a `useConfig()` hook, uses `createContext` + `useReducer`, and lives at `src/eval-ui/src/ConfigContext.tsx`
- [x] **AC-US4-02**: Given App.tsx, when the app renders, then `ConfigProvider` wraps `StudioLayout` (either inside or outside `StudioProvider`, both are valid since they are independent)

## Out of Scope

- Server-side config API changes (endpoints remain unchanged)
- Real-time config sync via WebSocket or polling (config only changes via explicit user action)
- Config persistence across page reloads (browser refresh triggers a fresh fetch, same as current behavior)
- Refactoring StudioContext to also use ConfigContext (they are independent concerns)

## Technical Notes

### Dependencies
- React 18 (createContext, useReducer, useContext, useCallback, useMemo, useEffect)
- Existing `api.getConfig()` and `api.setConfig()` from `src/eval-ui/src/api.ts`
- Existing `ConfigResponse` type from `src/eval-ui/src/api.ts`

### Constraints
- Must follow the established StudioContext.tsx pattern for consistency
- `api.getConfig()` and `api.setConfig()` signatures must not change
- Local model override state in SkillImprovePanel, AiEditBar, and CreateSkillPage must remain functional

### Architecture Decisions
- **Context + useReducer over Zustand/Jotai**: Matches existing StudioContext pattern, no new dependencies
- **Server-confirmed updates over optimistic**: ModelSelector already shows a saving spinner; avoids rollback complexity
- **Loading flag exposed but not required**: Config loads from a local server (fast), so no skeleton/spinner needed, but the flag is available for future use

## Non-Functional Requirements

- **Performance**: Net reduction in API calls from 12 to 1 on initial load. Context propagation is synchronous React state, adding zero latency to model change UX.
- **Compatibility**: React 18+, TypeScript strict mode, Vite bundler (existing stack, no new constraints)

## Edge Cases

- **Config fetch fails on startup**: ConfigProvider sets `loading: false` and `config: null`. Components that destructure config must handle the null case (existing behavior preserved since components already render null when config is absent).
- **Rapid model switching**: User clicks multiple models quickly. Each `api.setConfig()` resolves independently. The last successful response wins and is dispatched to context. No race condition because ModelSelector's `saving` state disables further clicks until the current call resolves.
- **Component mounts after config loaded**: Late-mounting components (modals, route pages) receive the already-loaded config immediately from context, no additional fetch needed.

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Breaking a component during migration by removing local state it still needs | 0.3 | 5 | 1.5 | Each component migrated individually with its own test verifying identical behavior |
| Legacy route pages (BenchmarkPage, ComparisonPage, CreateSkillPage) rendering outside ConfigProvider | 0.1 | 3 | 0.3 | useConfig() throws descriptive error; these pages are currently unused but migrated for consistency |

## Success Metrics

- Zero `api.getConfig()` calls in component files after migration (only in ConfigContext.tsx)
- Model change in sidebar instantly reflected in all visible components (no stale state)
- All existing eval-ui tests pass after migration
