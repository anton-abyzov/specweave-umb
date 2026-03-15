---
increment: 0536-plugin-discover-scope-fix
type: bugfix
complexity: low
domain_skills_needed: none
---

# Architecture Plan: Fix Plugin Discover Tab Scope Mismatch

## Problem Summary

Claude Code's Discover tab only recognizes user-scoped plugins as "installed." SpecWeave's `DEFAULT_PLUGIN_SCOPE_CONFIG` sets `specweaveScope: 'project'` with only `sw` overridden to `'user'`, so 7 of 8 plugins appear uninstalled in Discover despite working correctly.

Two additional gaps: `installAllPlugins()` never calls `enablePluginsInSettings()`, and `refreshPluginsCommand()` only calls it when `useNativeCli` is true.

## Decision: Change Default Scope vs. Override Per-Plugin

**Chosen: Change `specweaveScope` to `'user'`** -- single-line change, all SpecWeave plugins get user scope automatically. LSP plugins remain at project scope via separate `lspScope` field.

Alternative (add 7 more `scopeOverrides` entries) rejected -- violates DRY, the `specweaveScope` field exists precisely for this purpose.

## Change Map

### Change 1: `plugin-scope.ts` -- Fix scope default

**File**: `src/core/types/plugin-scope.ts`

```
specweaveScope: 'project' --> specweaveScope: 'user'
```

Remove the now-redundant `sw` entry from `scopeOverrides` (when `specweaveScope` is `'user'`, overriding `sw` to `'user'` is a no-op).

**Impact**: `getPluginScope()` returns `'user'` for all SpecWeave marketplace plugins. LSP plugins unaffected (separate `lspScope` path). Third-party plugins unaffected (separate `defaultScope` path).

### Change 2: `plugin-installer.ts` -- Call enablePluginsInSettings after install

**File**: `src/cli/helpers/init/plugin-installer.ts`

After the install loop completes, if `successCount > 0`, call `enablePluginsInSettings(successPluginNames)`. Collect successful plugin names during the loop (already have `failedPlugins` -- add a `successPluginNames` array). Log a warning if enablement fails; do not fail the overall install.

**Import needed**: `enablePluginsInSettings` from `./claude-plugin-enabler.js`

### Change 3: `refresh-plugins.ts` -- Remove useNativeCli guard

**File**: `src/cli/commands/refresh-plugins.ts`

Change the condition on line 184 from:

```typescript
if (useNativeCli && installedPluginNames.length > 0) {
```

to:

```typescript
if (installedPluginNames.length > 0) {
```

This ensures direct-copy installs also get settings enablement.

## Data Flow

```
specweave init
  --> installAllPlugins()
    --> copies skills to .claude/skills/
    --> NEW: enablePluginsInSettings(successNames)
      --> writes to ~/.claude/settings.json

specweave refresh-plugins
  --> refreshPluginsCommand()
    --> copies/installs plugins
    --> enablePluginsInSettings(installedNames)  <-- now unconditional
      --> writes to ~/.claude/settings.json

getPluginScope("frontend", "specweave")
  --> no override found
  --> not LSP
  --> is SpecWeave plugin
  --> returns specweaveScope = "user"  <-- was "project"
```

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Existing project-scoped entries persist | `enablePluginsInSettings` is additive (adds user-scope entries); next `refresh-plugins` normalizes |
| `enablePluginsInSettings` failure blocks init | Caught with warning log, never throws |
| LSP plugins accidentally get user scope | `lspScope` check runs before `specweaveScope` in resolution order -- no change |

## Testing Strategy

- Unit tests for `getPluginScope()`: verify all SpecWeave plugin names return `'user'`
- Unit test: `installAllPlugins()` calls `enablePluginsInSettings` with correct names
- Unit test: `refreshPluginsCommand()` calls `enablePluginsInSettings` regardless of `useNativeCli`
- Existing tests for `formatScopeFlag` and `getScopeArgs` remain valid (no API change)

## No ADR Needed

This is a config value change and two call-site additions. No new components, no new patterns, no architectural decisions beyond what already exists.

## No Domain Skills Needed

All changes are in core SpecWeave TypeScript files. No frontend, backend, or infrastructure plugins apply.
