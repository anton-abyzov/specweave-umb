---
increment: 0502-config-context-sync
title: "Centralized config state for Skill Studio eval-ui"
status: active
total_tasks: 14
completed_tasks: 14
by_user_story:
  US-001: [T-009]
  US-002: [T-001, T-002]
  US-003: [T-003, T-004, T-005, T-006, T-007, T-008, T-010, T-011, T-012, T-013, T-014]
  US-004: [T-001, T-002]
---

# Tasks: 0502-config-context-sync

## User Story: US-004 + US-002 — ConfigContext File Structure & Centralized Provider

**Linked ACs**: AC-US4-01, AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 2 total, 0 completed

---

### T-001: Create ConfigContext.tsx with reducer, provider, and useConfig hook

**User Story**: US-004, US-002
**Satisfies ACs**: AC-US4-01, AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** the app has no ConfigContext.tsx yet
- **When** ConfigContext.tsx is created following the StudioContext.tsx pattern
- **Then** it exports `ConfigProvider` and `useConfig()`, uses `createContext + useReducer`, loads config exactly once on mount, exposes `{ config, loading, updateConfig }`, and throws when called outside provider

**Test Cases**:
1. **Unit**: `src/eval-ui/src/ConfigContext.test.tsx`
   - initialLoad(): ConfigProvider calls `api.getConfig()` exactly once and propagates config to child consumer
   - loadingState(): `loading` is true before fetch resolves and false after
   - updateConfigSuccess(): `api.setConfig()` called, context updated with returned ConfigResponse
   - updateConfigFailure(): context retains previous config, error re-thrown to caller
   - useConfigOutsideProvider(): throws "useConfig must be used within ConfigProvider"
   - fetchFailureOnMount(): after api.getConfig() rejects, `loading: false` and `config: null`
   - **Coverage Target**: 95%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval-ui/src/ConfigContext.tsx`
2. Define `ConfigState { config: ConfigResponse | null; loading: boolean }` and initial state
3. Define `ConfigAction` union: `SET_CONFIG { config: ConfigResponse }` | `SET_LOADING { loading: boolean }`
4. Implement `configReducer(state, action)` pure function
5. Create context with `createContext<ConfigContextValue | null>(null)`
6. Implement `useConfig()` hook — throws descriptive error if context is null
7. Implement `ConfigProvider` component: on mount dispatch SET_LOADING true, call `api.getConfig()`, on success dispatch SET_CONFIG, on error dispatch SET_LOADING false
8. Implement `updateConfig(provider, model)`: calls `api.setConfig()`, on success dispatches SET_CONFIG, on error re-throws
9. Wrap context value in `useMemo` to prevent unnecessary re-renders

---

### T-002: Wire ConfigProvider into App.tsx

**User Story**: US-004
**Satisfies ACs**: AC-US4-02
**Status**: [x] completed

**Test Plan**:
- **Given** ConfigContext.tsx exists and exports ConfigProvider
- **When** App.tsx is updated to wrap its tree with ConfigProvider
- **Then** ConfigProvider is the outermost wrapper containing StudioProvider and StudioLayout, so all nested components receive config from context

**Test Cases**:
1. **Unit**: `src/eval-ui/src/App.test.tsx`
   - appRendersWithConfigProvider(): render App, verify `api.getConfig()` mock was called exactly once (proves ConfigProvider initialized)
   - **Coverage Target**: 90%

**Implementation**:
1. Open `repositories/anton-abyzov/vskill/src/eval-ui/src/App.tsx`
2. Import `ConfigProvider` from `./ConfigContext`
3. Wrap the existing `<StudioProvider>` (and `<StudioLayout>`) with `<ConfigProvider>` as the outermost wrapper
4. Confirm no other changes to App.tsx logic

---

## User Story: US-001 — Instant Model Propagation on Selection

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Tasks**: 1 total, 0 completed

---

### T-009: Migrate ModelSelector to useConfig() and updateConfig() (Category C)

**User Story**: US-001, US-003
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US3-01
**Status**: [x] completed

**Test Plan**:
- **Given** ModelSelector previously had its own `useState<ConfigResponse>` and `useEffect(api.getConfig)`
- **When** ModelSelector is migrated to use `useConfig()` and `updateConfig()`
- **Then** selecting a model calls `updateConfig()` which updates context only after `api.setConfig()` succeeds, the error path retains prior context config, and button text in CreateSkillInline immediately reflects the change

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/ModelSelector.test.tsx`
   - displaysCurrentModelFromContext(): renders with config from ConfigProvider, shows correct model
   - selectModelCallsUpdateConfig(): user selects a model, `updateConfig()` is called with correct provider/model IDs
   - savingSpinnerShownDuringUpdate(): `saving` state is true while updateConfig() is in-flight
   - errorRetainsPriorConfig(): when updateConfig() rejects, ModelSelector reverts saving state; context still holds previous config
   - noDirectApiGetConfigCall(): `api.getConfig` is NOT called by ModelSelector (zero calls)
   - **Coverage Target**: 90%

**Implementation**:
1. Open `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ModelSelector.tsx`
2. Remove `useState<ConfigResponse | null>` and the `useEffect` that calls `api.getConfig()`
3. Add `import { useConfig } from "../ConfigContext"`
4. Add `const { config, updateConfig } = useConfig()` at the top of the component
5. Replace `api.setConfig(provider.id, model.id)` + `setConfig(result)` with `await updateConfig(provider.id, model.id)`
6. Simplify the catch block — remove the re-fetch `api.getConfig()` call (context retains last-good config automatically); keep only `setSaving(false)`
7. Keep local `saving` and `open` state unchanged
8. Remove `api` import if it is no longer used for any other call

---

## User Story: US-003 — Component Migration to Shared Context

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Tasks**: 9 total, 0 completed

---

### T-003: Migrate LeftPanel to useConfig() (Category A)

**User Story**: US-003
**Satisfies ACs**: AC-US3-01
**Status**: [x] completed

**Test Plan**:
- **Given** LeftPanel reads `config.projectName` via its own `api.getConfig()` fetch
- **When** LeftPanel is migrated to `useConfig()`
- **Then** `config.projectName` is read from context, no local fetch occurs, and rendered output is identical

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/LeftPanel.test.tsx`
   - rendersProjectName(): wrap with ConfigProvider providing mock config, verify projectName is displayed
   - noDirectApiGetConfigCall(): `api.getConfig` is not called by LeftPanel
   - **Coverage Target**: 85%

**Implementation**:
1. Open `repositories/anton-abyzov/vskill/src/eval-ui/src/components/LeftPanel.tsx`
2. Remove `useState<ConfigResponse | null>` and `useEffect(api.getConfig)`
3. Add `import { useConfig } from "../ConfigContext"` and `const { config } = useConfig()`
4. Remove `api` import if no longer needed

---

### T-004: Migrate CreateSkillInline to useConfig() (Category A)

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US1-01
**Status**: [x] completed

**Test Plan**:
- **Given** CreateSkillInline shows "Generate with {model}" using its own fetched config
- **When** CreateSkillInline is migrated to `useConfig()`
- **Then** button text reflects the context's current model, updating immediately when ModelSelector changes the model without remount

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/CreateSkillInline.test.tsx`
   - showsCorrectModelInButton(): wrapping with ConfigProvider supplying a given config shows the expected model name in the button
   - noDirectApiGetConfigCall(): `api.getConfig` is not called by CreateSkillInline
   - **Coverage Target**: 85%

**Implementation**:
1. Open `repositories/anton-abyzov/vskill/src/eval-ui/src/components/CreateSkillInline.tsx`
2. Remove `useState<ConfigResponse | null>` and `useEffect(api.getConfig)`
3. Add `import { useConfig } from "../ConfigContext"` and `const { config } = useConfig()`
4. Remove `api` import if no longer needed

---

### T-005: Migrate ModelCompareModal to useConfig() (Category A)

**User Story**: US-003
**Satisfies ACs**: AC-US3-01
**Status**: [x] completed

**Test Plan**:
- **Given** ModelCompareModal reads `config.providers` via its own fetch
- **When** migrated to `useConfig()`
- **Then** providers list comes from context, no local fetch is made

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/ModelCompareModal.test.tsx`
   - rendersProvidersFromContext(): with ConfigProvider supplying mock providers, modal renders provider options
   - noDirectApiGetConfigCall(): `api.getConfig` not called by ModelCompareModal
   - **Coverage Target**: 85%

**Implementation**:
1. Open `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ModelCompareModal.tsx`
2. Remove local `useState<ConfigResponse | null>` and `useEffect(api.getConfig)`
3. Add `import { useConfig } from "../ConfigContext"` and `const { config } = useConfig()`
4. Remove `api` import if no longer needed

---

### T-006: Migrate EditorPanel to useConfig() (Category A)

**User Story**: US-003
**Satisfies ACs**: AC-US3-01
**Status**: [x] completed

**Test Plan**:
- **Given** EditorPanel reads config for model display via its own fetch
- **When** migrated to `useConfig()`
- **Then** model info comes from context, no local fetch occurs

**Test Cases**:
1. **Unit**: `src/eval-ui/src/pages/workspace/EditorPanel.test.tsx`
   - rendersModelFromContext(): with ConfigProvider mock, EditorPanel shows correct model info
   - noDirectApiGetConfigCall(): `api.getConfig` not called by EditorPanel
   - **Coverage Target**: 85%

**Implementation**:
1. Open `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/EditorPanel.tsx`
2. Remove local `useState<ConfigResponse | null>` and `useEffect(api.getConfig)`
3. Add `import { useConfig } from "../../ConfigContext"` (adjust for nested path)
4. Add `const { config } = useConfig()`
5. Remove `api` import if no longer needed

---

### T-007: Migrate BenchmarkPage to useConfig() — 3 call sites (Category A)

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** BenchmarkPage has 3 `api.getConfig()` calls (mount, handleStartBenchmark, handleStartBaseline)
- **When** migrated to `useConfig()`
- **Then** all 3 call sites are replaced with a single `const { config } = useConfig()` and model is read from context at call time with no additional API calls

**Test Cases**:
1. **Unit**: `src/eval-ui/src/pages/BenchmarkPage.test.tsx`
   - readsModelFromContextOnStartBenchmark(): `handleStartBenchmark` uses `config.model` from context, zero `api.getConfig()` calls
   - readsModelFromContextOnStartBaseline(): same for `handleStartBaseline`
   - noDirectApiGetConfigCall(): `api.getConfig` called zero times by BenchmarkPage
   - **Coverage Target**: 85%

**Implementation**:
1. Open `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/BenchmarkPage.tsx`
2. Remove `useState<ConfigResponse | null>` and all `useEffect`/inline `api.getConfig()` calls (3 locations)
3. Add `import { useConfig } from "../ConfigContext"` and `const { config } = useConfig()` at component top
4. Replace all inline config fetches in `handleStartBenchmark` and `handleStartBaseline` with the destructured `config` from context
5. Remove `api` import if no longer needed

---

### T-008: Migrate ComparisonPage to useConfig() (Category A)

**User Story**: US-003
**Satisfies ACs**: AC-US3-01
**Status**: [x] completed

**Test Plan**:
- **Given** ComparisonPage reads `config.model` via its own fetch
- **When** migrated to `useConfig()`
- **Then** model comes from context, no local fetch is made

**Test Cases**:
1. **Unit**: `src/eval-ui/src/pages/ComparisonPage.test.tsx`
   - rendersModelFromContext(): ConfigProvider mock propagates model to ComparisonPage
   - noDirectApiGetConfigCall(): `api.getConfig` not called by ComparisonPage
   - **Coverage Target**: 85%

**Implementation**:
1. Open `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/ComparisonPage.tsx`
2. Remove local `useState<ConfigResponse | null>` and `useEffect(api.getConfig)`
3. Add `import { useConfig } from "../ConfigContext"` and `const { config } = useConfig()`
4. Remove `api` import if no longer needed

---

### T-010: Migrate SkillImprovePanel to useConfig() preserving local model override (Category B)

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] completed

**Test Plan**:
- **Given** SkillImprovePanel fetches config to populate provider/model dropdowns and sets a local default selection
- **When** migrated to `useConfig()`
- **Then** provider list comes from context, local `selectedProvider`/`selectedModel` state initializes via `useEffect([config])`, and the user can override the selection independently

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/SkillImprovePanel.test.tsx`
   - initializesLocalModelFromContext(): when ConfigProvider provides config with claude-cli available, local provider defaults to "claude-cli"
   - localOverrideIndependentOfContext(): user's local model selection is not overwritten by a subsequent context config change
   - noDirectApiGetConfigCall(): `api.getConfig` not called
   - **Coverage Target**: 85%

**Implementation**:
1. Open `repositories/anton-abyzov/vskill/src/eval-ui/src/components/SkillImprovePanel.tsx`
2. Remove local `useState<ConfigResponse | null>` and `useEffect(api.getConfig)`
3. Add `import { useConfig } from "../ConfigContext"` and `const { config } = useConfig()`
4. Move the default-selection logic into a `useEffect` depending on `[config]`:
   ```tsx
   useEffect(() => {
     if (!config) return;
     const hasCli = config.providers.find(p => p.id === "claude-cli" && p.available);
     if (hasCli) {
       setSelectedProvider("claude-cli");
       setSelectedModel("opus");
     }
   }, [config]);
   ```
5. Keep all local `selectedProvider`, `selectedModel` state and their setters
6. Remove `api` import if no longer needed

---

### T-011: Migrate AiEditBar to useConfig() preserving local model override (Category B)

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] completed

**Test Plan**:
- **Given** AiEditBar fetches config to populate provider/model options and sets a local default
- **When** migrated to `useConfig()`
- **Then** provider list comes from context, local state initializes from context config via `useEffect([config])`, user can override locally

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/AiEditBar.test.tsx`
   - initializesLocalModelFromContext(): context config with available providers sets correct local defaults
   - noDirectApiGetConfigCall(): `api.getConfig` not called
   - **Coverage Target**: 85%

**Implementation**:
1. Open `repositories/anton-abyzov/vskill/src/eval-ui/src/components/AiEditBar.tsx`
2. Remove local config fetch state and `useEffect(api.getConfig)`
3. Add `import { useConfig } from "../ConfigContext"` and `const { config } = useConfig()`
4. Add `useEffect(() => { if (!config) return; /* set local defaults */ }, [config])`
5. Keep local `selectedProvider`, `selectedModel` state
6. Remove `api` import if no longer needed

---

### T-012: Migrate CreateSkillPage to useConfig() preserving local model override (Category B)

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] completed

**Test Plan**:
- **Given** CreateSkillPage fetches config to set local AI provider/model defaults
- **When** migrated to `useConfig()`
- **Then** provider/model list comes from context, local AI provider/model state initializes from context config, user can override locally

**Test Cases**:
1. **Unit**: `src/eval-ui/src/pages/CreateSkillPage.test.tsx`
   - initializesLocalAiModelFromContext(): ConfigProvider config propagates to local AI provider/model state via useEffect
   - noDirectApiGetConfigCall(): `api.getConfig` not called
   - **Coverage Target**: 85%

**Implementation**:
1. Open `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/CreateSkillPage.tsx`
2. Remove local config fetch state and `useEffect(api.getConfig)`
3. Add `import { useConfig } from "../ConfigContext"` (adjust path for pages directory)
4. Add `const { config } = useConfig()`
5. Add `useEffect(() => { if (!config) return; /* init local AI provider/model */ }, [config])`
6. Keep local `selectedAiProvider`, `selectedAiModel` (or equivalent) state
7. Remove `api` import if no longer needed

---

### T-013: Verify zero api.getConfig() calls in all migrated component files

**User Story**: US-003
**Satisfies ACs**: AC-US3-01
**Status**: [x] completed

**Test Plan**:
- **Given** all 10 components have been migrated
- **When** the codebase is searched for `api.getConfig()` in component and page files
- **Then** zero results are found in: ModelSelector, LeftPanel, CreateSkillInline, SkillImprovePanel, AiEditBar, EditorPanel, ModelCompareModal, BenchmarkPage, ComparisonPage, CreateSkillPage

**Test Cases**:
1. **Static check**:
   - Run `grep -r "api\.getConfig" repositories/anton-abyzov/vskill/src/eval-ui/src/components/ repositories/anton-abyzov/vskill/src/eval-ui/src/pages/`
   - Expected: empty output (zero matches)
   - **Coverage Target**: 100% pass/fail gate

**Implementation**:
1. Run the grep command above
2. Confirm zero results
3. If any remain, return to the relevant task and complete the migration

---

### T-014: Run full test suite and confirm no regressions

**User Story**: US-002, US-003
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US3-01
**Status**: [x] completed

**Test Plan**:
- **Given** all migration tasks are complete
- **When** the full Vitest test suite is run in the vskill repository
- **Then** all tests pass, coverage targets are met, and no existing tests regressed

**Test Cases**:
1. **Integration**: Run `npx vitest run` in `repositories/anton-abyzov/vskill/`
   - All ConfigContext unit tests pass
   - All migrated component tests pass
   - No pre-existing tests broken by missing ConfigProvider wrapper in test setup
   - **Coverage Target**: 90% overall for eval-ui/src

**Implementation**:
1. Run `npx vitest run` from `repositories/anton-abyzov/vskill/`
2. Fix any broken tests that fail due to missing ConfigProvider wrapper in existing test setup
3. Verify coverage report meets 90% target for eval-ui/src
