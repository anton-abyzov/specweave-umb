# Architecture Plan: Centralized Config State for Eval-UI

## Overview

Introduce a `ConfigContext` that loads config once at app startup and shares it across all 10+ components that currently make independent `api.getConfig()` calls. Follows the established `StudioContext.tsx` pattern exactly (createContext + useReducer + useMemo + custom hook).

## Architecture Decision

**Pattern**: React Context + useReducer (matches StudioContext.tsx)

Alternatives considered and rejected:
- **Zustand/Jotai**: Would work well but introduces a new dependency. The codebase already has a clear pattern with StudioContext. Consistency wins here since the config state is simple (single object, one writer).
- **Lifting state into StudioContext**: StudioContext manages skill selection and UI mode -- orthogonal concerns. Mixing config into it would bloat the reducer and violate single responsibility. The spec explicitly says "they are independent concerns."
- **Custom hook with module-level cache (useConfig + stale closure)**: Tempting for simplicity but loses React's re-render propagation. Components would not update when ModelSelector writes new config without explicit subscription wiring.

**Decision**: New file `ConfigContext.tsx` at `src/eval-ui/src/ConfigContext.tsx` using the same structural pattern as `StudioContext.tsx`.

## Component Design

### ConfigContext.tsx

```
Exports:
  - ConfigProvider (component)
  - useConfig() (hook)

State shape (ConfigState):
  config: ConfigResponse | null
  loading: boolean

Actions (ConfigAction):
  SET_CONFIG   { config: ConfigResponse }
  SET_LOADING  { loading: boolean }

Context value (ConfigContextValue):
  config: ConfigResponse | null
  loading: boolean
  updateConfig: (provider: string, model?: string) => Promise<void>
```

**File structure** mirrors StudioContext.tsx sections:
1. State interface + initial state
2. Action union type
3. Reducer function
4. Context creation + useConfig hook (throws if outside provider)
5. ConfigProvider component

### Provider behavior

```
ConfigProvider mount:
  1. dispatch SET_LOADING true
  2. api.getConfig()
  3. on success: dispatch SET_CONFIG with response
  4. on error: dispatch SET_LOADING false (config stays null)

updateConfig(provider, model):
  1. api.setConfig(provider, model)
  2. on success: dispatch SET_CONFIG with returned ConfigResponse
  3. on error: re-throw (caller handles UI feedback)
  4. Does NOT dispatch SET_LOADING -- the caller (ModelSelector) manages its own saving spinner
```

**Why updateConfig does not manage loading state**: ModelSelector already has its own `saving` boolean that controls the spinner and disables clicks. Adding a global loading flag would either duplicate that state or require ModelSelector to read from two sources. The context's `loading` flag is only for the initial fetch.

**Why updateConfig re-throws on error**: ModelSelector's error handling (catch block fetches current config to revert) is specific to its UI. The context should not prescribe error recovery strategy -- it just persists the last known-good state.

### App.tsx wiring

```tsx
<ConfigProvider>
  <StudioProvider>
    <StudioLayout ... />
  </StudioProvider>
</ConfigProvider>
```

ConfigProvider wraps outside StudioProvider. Order does not matter functionally (they are independent), but placing ConfigProvider outermost communicates that config is app-level infrastructure. StudioProvider's skill-fetch does not depend on config.

## Data Flow

```
                    api.getConfig()
                         |
                         v
               +-------------------+
               |  ConfigProvider   |
               |  (single fetch)   |
               +--------+----------+
                        |
           React Context propagation
                        |
        +-------+-------+-------+--------+
        |       |       |       |        |
   ModelSel  LeftPanel  Create  Improve  EditorPanel ...
   (R+W)      (R)      Inline   Panel     (R)
                         (R)     (R)

   ModelSelector calls updateConfig() --> dispatches SET_CONFIG
   All consumers re-render with new config
```

**R** = read-only consumer (useConfig().config)
**R+W** = reads config AND calls updateConfig()

## Migration Strategy

### Component categories

**Category A -- Simple readers** (replace `useState<ConfigResponse | null>` + `useEffect(api.getConfig)` with `useConfig()`):
- LeftPanel: reads `config.projectName`
- ModelCompareModal: reads `config.providers`
- EditorPanel: reads `config` for model display
- ComparisonPage: reads `config.model`
- BenchmarkPage: reads `config.model` (mount + handleStartBenchmark + handleStartBaseline)
- CreateSkillInline: reads `config` for button label and provider availability

**Category B -- Readers with local model override** (read config from context for provider list, but keep local `selectedProvider`/`selectedModel` state):
- SkillImprovePanel: reads providers, initializes local provider/model defaults
- AiEditBar: reads providers, initializes local provider/model defaults
- CreateSkillPage: reads providers + model, initializes local AI provider/model

These components use config to populate dropdowns and set defaults, but the user can override the model locally per-action. The local override state stays. Only the initial `api.getConfig()` fetch + `setConfig()` local state is replaced with `useConfig()`.

**Category C -- Reader + writer**:
- ModelSelector: reads config for display, calls `updateConfig()` on selection

### Migration per component

Each component migration is atomic and testable independently:

1. Remove `useState<ConfigResponse | null>` and the `useEffect` that calls `api.getConfig()`
2. Add `import { useConfig } from "../ConfigContext"` (or `"../../ConfigContext"` for nested paths)
3. Add `const { config } = useConfig()` (or destructure `loading`/`updateConfig` as needed)
4. Remove `import { api }` if api was only used for getConfig (keep if other api methods are used)

For **Category B** components, the local provider/model override initialization moves to a `useEffect` depending on `config`:

```tsx
const { config } = useConfig();
useEffect(() => {
  if (!config) return;
  const hasCli = config.providers.find(p => p.id === "claude-cli" && p.available);
  if (hasCli) {
    setSelectedProvider("claude-cli");
    setSelectedModel("opus");
  }
}, [config]);
```

For **ModelSelector** (Category C):
- Replace local `config`/`setConfig` state with `useConfig()`
- Replace `api.setConfig()` + `setConfig(result)` with `updateConfig(provider.id, model.id)`
- Keep local `saving`, `open` state
- Error handling: on catch, context retains previous config (updateConfig only dispatches on success), so the re-fetch fallback is no longer needed

### BenchmarkPage special case

BenchmarkPage has 3 `api.getConfig()` calls: mount (line 64), handleStartBenchmark (line 88), handleStartBaseline (line 97). The latter two re-fetch to get the "latest" model before starting a run. After migration, the context always holds the latest config (ModelSelector updates it on change), so all three become unnecessary. Replace with `const { config } = useConfig()` and read `config.model` directly.

### ModelSelector error recovery simplification

Current behavior: on `setConfig` failure, re-fetches via `api.getConfig()` to revert UI.
After migration: context retains the last-good config automatically (updateConfig only dispatches on success). The catch block simplifies to just resetting `saving` state. Net improvement -- removes a network call from the error path.

### Unused pages (BenchmarkPage, ComparisonPage, CreateSkillPage)

Not mounted in the current App tree. Migrated for consistency. If used standalone without ConfigProvider, `useConfig()` throws a descriptive error (matches `useStudio()` pattern).

## Testing Strategy

### Unit tests for ConfigContext.tsx

1. **Initial load**: Render ConfigProvider, verify `api.getConfig()` called once, config propagated to child
2. **Loading states**: `loading: true` before fetch resolves, `loading: false` after
3. **updateConfig success**: Verify `api.setConfig()` called, context updated with response
4. **updateConfig failure**: Verify context retains previous config, error re-thrown
5. **useConfig outside provider**: Throws "useConfig must be used within ConfigProvider"
6. **Fetch failure on mount**: `loading: false`, `config: null`

### Integration tests per component

Existing component tests (if any) should pass with ConfigProvider wrapper added to test render setup. Each migrated component verified to render the same output.

## File Changes Summary

| File | Change |
|------|--------|
| `src/eval-ui/src/ConfigContext.tsx` | **NEW** -- context, reducer, provider, hook |
| `src/eval-ui/src/App.tsx` | Wrap with ConfigProvider |
| `src/eval-ui/src/components/ModelSelector.tsx` | Use useConfig() + updateConfig(), remove local fetch |
| `src/eval-ui/src/components/LeftPanel.tsx` | Use useConfig().config.projectName |
| `src/eval-ui/src/components/CreateSkillInline.tsx` | Use useConfig().config |
| `src/eval-ui/src/components/SkillImprovePanel.tsx` | Use useConfig().config, keep local override state |
| `src/eval-ui/src/components/AiEditBar.tsx` | Use useConfig().config, keep local override state |
| `src/eval-ui/src/components/ModelCompareModal.tsx` | Use useConfig().config |
| `src/eval-ui/src/pages/workspace/EditorPanel.tsx` | Use useConfig().config |
| `src/eval-ui/src/pages/BenchmarkPage.tsx` | Use useConfig().config, remove 3 api.getConfig() calls |
| `src/eval-ui/src/pages/ComparisonPage.tsx` | Use useConfig().config |
| `src/eval-ui/src/pages/CreateSkillPage.tsx` | Use useConfig().config, keep local override state |

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Component breaks during migration (removes state it still needs) | Each component migrated as separate task with own test |
| Unused pages rendered outside ConfigProvider | useConfig() throws descriptive error; pages are currently dead code |
| ModelSelector error recovery behavior change | Context retains last-good config on failure -- net improvement |

## No New Dependencies

Pure React 18 APIs: createContext, useReducer, useContext, useCallback, useMemo, useEffect. Zero new packages.
