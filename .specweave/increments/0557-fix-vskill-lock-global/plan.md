# Architecture Plan: Fix vskill.lock creation in non-SpecWeave projects

## Problem Statement

`specweave update` (and `specweave refresh-plugins`) calls `installPlugin()` in `plugin-copier.ts`, which calls `getProjectRoot()` to determine where to write `vskill.lock`. When no `.specweave/config.json` exists in the directory tree (e.g., running from a non-SpecWeave project), `getProjectRoot()` falls back to `process.cwd()`, creating a stray `vskill.lock` in whatever directory the user happens to be in.

## Root Cause

Line 313 in `plugin-copier.ts`:
```typescript
const lockDir = getProjectRoot();  // Falls back to process.cwd()
```

The bundled plugin hash cache (`vskill.lock`) is a **global concern** -- it tracks which bundled plugins are installed in the Claude Code plugin cache (`~/.claude/plugins/cache/`), not which plugins are active in a specific project. Writing it to a project directory (or worse, an arbitrary `cwd`) conflates two different scopes.

## Design Decision: Global Lock for Bundled Plugins

### Scope Separation

| Concern | Scope | Location | File |
|---------|-------|----------|------|
| Bundled plugin hashes (sw, sw-github, etc.) | Global (per-user) | `~/.specweave/` | `plugins-lock.json` |
| Project-scoped third-party skills | Project | `<project>/` | `vskill.lock` |

Bundled plugins are installed globally into `~/.claude/plugins/cache/` and tracked in `~/.claude/settings.json`. Their hash cache belongs at the same global level: `~/.specweave/plugins-lock.json`.

Project-local `vskill.lock` remains reserved for `vskill install` (third-party, project-scoped skills installed into `.claude/skills/`).

### New Utility: `getGlobalLockDir()`

```
~/.specweave/
  plugins-lock.json    <-- NEW: bundled plugin hash cache
  logs/                <-- existing
```

A new function `getGlobalLockDir()` in `plugin-copier.ts` returns `~/.specweave/`, creating it if needed. This replaces `getProjectRoot()` as the lockfile location for `installPlugin()`.

**Why `~/.specweave/` and not `~/.claude/`?** The `~/.claude/` directory is owned by Claude Code and may be wiped or reorganized by Anthropic at any time. `~/.specweave/` is SpecWeave's own global directory (already exists in practice with `logs/`).

**Why `plugins-lock.json` and not `vskill.lock`?** Clear naming distinction: `plugins-lock.json` is the global bundled cache; `vskill.lock` is the project-local third-party lockfile. No ambiguity about which file serves which purpose.

## Components Affected

### 1. `plugin-copier.ts` (PRIMARY -- 4 changes)

**a) Add `getGlobalLockDir()` function**

```typescript
export function getGlobalLockDir(): string {
  const dir = join(homedir(), '.specweave');
  mkdirSync(dir, { recursive: true });
  return dir;
}
```

**b) Add `GLOBAL_LOCKFILE_NAME` constant**

```typescript
const LOCKFILE_NAME = 'vskill.lock';              // project-local (unchanged)
const GLOBAL_LOCKFILE_NAME = 'plugins-lock.json';  // global bundled cache
```

**c) Add global-aware read/write helpers**

New functions that read/write the global lockfile specifically:
```typescript
export function readGlobalLockfile(): VskillLock | null
export function writeGlobalLockfile(lock: VskillLock): void
export function ensureGlobalLockfile(): VskillLock
```

These wrap the existing `readLockfile`/`writeLockfile` logic with the global dir + global filename.

**d) Update `installPlugin()` to use global lock**

Replace:
```typescript
const lockDir = getProjectRoot();
const lock = ensureLockfile(lockDir);
// ...
writeLockfile(lock, lockDir);
```

With:
```typescript
const lock = ensureGlobalLockfile();
// ...
writeGlobalLockfile(lock);
```

### 2. `copyPluginSkillsToProject()` in `plugin-copier.ts` -- NO CHANGE

This function already takes an explicit `projectRoot` parameter and uses it correctly for the lockfile. It tracks which skills were copied to a specific project's `.claude/skills/` directory. The `projectRoot` is always explicitly passed by the caller (`refreshPluginsCommand` passes `getProjectRoot()`), so it only writes to actual SpecWeave projects.

### 3. `installation-health-checker.ts` (1 change)

`checkLockfileIntegrity()` reads `vskill.lock` from `projectRoot`. Must be updated to ALSO check `~/.specweave/plugins-lock.json` for bundled plugin entries.

**Approach**: Check global lockfile first for bundled entries, then project-local `vskill.lock` for third-party entries. Merge results for the integrity report.

### 4. `detect-intent.ts` (1 change)

Reads `vskill.lock` at project root to determine which plugins are already installed. Must also check the global `plugins-lock.json` so bundled plugins are not recommended for re-install.

**Approach**: Read both files, merge the `skills` maps, use the union set for `installedVskillPlugins`.

### 5. `cleanup-stale-plugins.ts` -- NO CHANGE

`cleanupOrphanedChildLocks()` removes stray `vskill.lock` in child repos. No change needed -- it correctly targets project-scoped `vskill.lock` files. The migration logic (below) handles cleaning up old bundled-only lockfiles.

### 6. `uninstall.ts` (1 change)

Lists and removes `vskill.lock` during uninstall. Should also remove `~/.specweave/plugins-lock.json` during full uninstall.

### 7. `migrate-to-vskill.ts` (1 change)

`shouldOfferMigration()` checks for `vskill.lock` in `lockDir || process.cwd()`. Should also check `~/.specweave/plugins-lock.json` to avoid offering migration when plugins are already tracked globally.

## Migration Strategy

A one-time migration runs during `refreshPluginsCommand()`:

1. Read existing `vskill.lock` from project root (if it exists)
2. Extract entries where `source === 'local:specweave'` (bundled plugins)
3. Write those entries to `~/.specweave/plugins-lock.json`
4. Remove the bundled entries from the project-local `vskill.lock`
5. If the project-local `vskill.lock` is now empty (no third-party entries), delete it

This migration is **idempotent** -- running it multiple times is safe.

**Implementation location**: New function `migrateBundledToGlobalLock()` in `plugin-copier.ts`, called from `refreshPluginsCommand()` before plugin installation.

```typescript
export function migrateBundledToGlobalLock(projectRoot: string): {
  migratedCount: number;
  deletedProjectLock: boolean;
}
```

## Data Flow

### Before (current -- broken)

```
specweave update
    |
    v
installPlugin("sw", specweaveRoot)
    |
    v
getProjectRoot()          <-- falls back to cwd if no .specweave/
    |
    v
ensureLockfile(cwd)       <-- creates vskill.lock in random dir
    |
    v
writeLockfile(lock, cwd)  <-- writes bundled hash to random dir
```

### After (fixed)

```
specweave update
    |
    v
installPlugin("sw", specweaveRoot)
    |
    v
getGlobalLockDir()        <-- always ~/.specweave/
    |
    v
ensureGlobalLockfile()    <-- reads/creates ~/.specweave/plugins-lock.json
    |
    v
writeGlobalLockfile(lock) <-- writes bundled hash to ~/.specweave/
```

## File Structure

```
~/.specweave/
  plugins-lock.json     <-- NEW: global bundled plugin hash cache
  logs/                 <-- existing

<project>/
  vskill.lock           <-- UNCHANGED: project-scoped third-party skills only
```

### `plugins-lock.json` schema (same as `VskillLock` interface)

```json
{
  "version": 1,
  "agents": ["claude-code"],
  "skills": {
    "sw": {
      "version": "1.0.0",
      "sha": "abc123def456",
      "tier": "BUNDLED",
      "installedAt": "2026-03-17T00:00:00Z",
      "source": "local:specweave"
    }
  },
  "createdAt": "2026-03-17T00:00:00Z",
  "updatedAt": "2026-03-17T00:00:00Z"
}
```

Reuses the existing `VskillLock` interface -- no schema changes needed.

## Testing Strategy (TDD)

All tests use temp directories and `homedir()` mocking to avoid real filesystem side effects.

### Unit Tests (plugin-copier.test.ts -- extend existing)

1. `getGlobalLockDir()` creates `~/.specweave/` and returns path
2. `readGlobalLockfile()` returns null when no file exists
3. `writeGlobalLockfile()` + `readGlobalLockfile()` round-trip
4. `ensureGlobalLockfile()` creates new file when none exists
5. `ensureGlobalLockfile()` returns existing file when present
6. `migrateBundledToGlobalLock()` moves bundled entries, leaves third-party
7. `migrateBundledToGlobalLock()` deletes empty project lockfile after migration
8. `migrateBundledToGlobalLock()` is idempotent (second run is no-op)

### Consumer Tests

9. `checkLockfileIntegrity()` reads from global lockfile for bundled entries
10. `detect-intent` merges global + project installed sets

### Integration Verification

11. `installPlugin()` writes to `~/.specweave/plugins-lock.json`, NOT `cwd`
12. Running from a non-SpecWeave directory does NOT create any `vskill.lock`

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Existing `vskill.lock` not migrated | Low | Medium | Migration runs in `refreshPluginsCommand()` on every update |
| `~/.specweave/` permissions issues | Low | Low | `mkdirSync` with `recursive: true`; non-fatal fallback |
| Concurrent writes to global lockfile | Low | Low | Same risk as current design; lockfile is a cache, not critical state |
| Doctor check breaks during transition | Medium | Low | Check both files with graceful degradation |

## Out of Scope

- Changing `vskill install` behavior (already project-scoped correctly)
- Changing the `VskillLock` interface or adding new fields
- Moving other global state to `~/.specweave/`
- Changing `copyPluginSkillsToProject()` lockfile behavior (already correct)
- Changing the `refresh-plugins.ts` caller-side `getProjectRoot()` for the `copyPluginSkillsToProject` path (only affects SpecWeave project contexts where it is correct)

## Implementation Order

1. Add `getGlobalLockDir()`, global lockfile read/write/ensure functions to `plugin-copier.ts`
2. Add `migrateBundledToGlobalLock()` to `plugin-copier.ts`
3. Update `installPlugin()` to use global lock functions (remove `getProjectRoot()` import dependency)
4. Update `refreshPluginsCommand()` to call migration before install
5. Update `installation-health-checker.ts` to check both lockfiles
6. Update `detect-intent.ts` to check both lockfiles
7. Update `uninstall.ts` to also remove global lockfile
8. Update `migrate-to-vskill.ts` to check global lockfile
9. Write and extend tests throughout (TDD: red-green-refactor per step)
