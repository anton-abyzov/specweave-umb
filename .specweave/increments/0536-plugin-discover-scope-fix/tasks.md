---
increment: 0536-plugin-discover-scope-fix
generated: 2026-03-15
test_mode: TDD
coverage_target: 90
---

# Tasks: Fix Plugin Discover Tab Scope Mismatch

## US-001: Consistent Plugin Scope

### T-001: Change `specweaveScope` default from `'project'` to `'user'` and remove redundant `sw` override
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed
**Test**: Given `DEFAULT_PLUGIN_SCOPE_CONFIG` in `plugin-scope.ts` → When `specweaveScope` is read and `getPluginScope()` is called for any SpecWeave plugin (e.g., `frontend`, `sw-github`) → Then `specweaveScope` equals `'user'`, the `sw` `scopeOverrides` entry is absent, and `getPluginScope()` returns `'user'` for all SpecWeave marketplace plugin names

---

## US-002: Settings Enablement on Init

### T-002: Call `enablePluginsInSettings()` after `installAllPlugins()` completes
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed
**Test**: Given `installAllPlugins()` runs with 8 plugins where 6 succeed and 2 fail → When the function returns → Then `enablePluginsInSettings()` is called exactly once with the 6 successful plugin names (failed plugins excluded), and if `enablePluginsInSettings()` returns false then a warning is logged but the function does not throw or return an error status

---

## US-003: Settings Enablement Regardless of Install Method

### T-003: Remove `useNativeCli` guard from `enablePluginsInSettings` call in `refresh-plugins.ts`
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] completed
**Test**: Given `refreshPluginsCommand()` has installed plugins successfully → When `useNativeCli` is false → Then `enablePluginsInSettings()` is still called with the installed plugin names; and when `useNativeCli` is true → Then `enablePluginsInSettings()` is also called (existing behavior preserved)
