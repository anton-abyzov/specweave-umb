---
increment: 0539-umbrella-root-resolution-fix
type: bug-fix
complexity: low
estimated_effort: 1-2 hours
---

# Architecture Plan: Umbrella Root Resolution Fix

## Summary

Replace three `process.cwd()` calls with `resolveEffectiveRoot()` in artifact-creation paths, and deduplicate the `findProjectRoot()` copy in `platform.ts` by re-exporting from the canonical module. No new abstractions, no new files, no schema changes.

## Relevant ADRs

- **ADR-0142** (Umbrella Multi-Repo Support) -- Establishes that umbrella root owns `.specweave/` state, child repos have their own config but increments/state belong to the umbrella. This fix enforces that contract in three paths that were missed.
- **ADR-0014** (Root-level .specweave only) -- Confirms `.specweave/` artifacts must live at the project root, not in subdirectories.

No new ADR needed. This is a straightforward application of existing decisions.

## Root Cause

Three code paths use `process.cwd()` to derive `.specweave/` paths instead of `resolveEffectiveRoot()`. In umbrella mode, when CWD is a child repo, `process.cwd()` returns the child path, causing artifacts to land in `<child>/.specweave/` instead of `<umbrella>/.specweave/`.

A fourth issue is a full copy of `findProjectRoot()` in `platform.ts` (lines 110-127) that duplicates `utils/find-project-root.ts`.

## Changes

### Change 1: spec-detector.ts (line 94)

**File**: `src/core/specs/spec-detector.ts`
**Before**: `const specsFolder = path.join(process.cwd(), '.specweave/docs/internal/specs');`
**After**: `const specsFolder = path.join(resolveEffectiveRoot(), '.specweave/docs/internal/specs');`
**Import**: Add `import { resolveEffectiveRoot } from '../../utils/find-project-root.js';`

### Change 2: active-increment-manager.ts (line 47)

**File**: `src/core/increment/active-increment-manager.ts`
**Before**: `constructor(private rootDir: string = process.cwd())`
**After**: `constructor(private rootDir: string = resolveEffectiveRoot())`
**Import**: Add `import { resolveEffectiveRoot } from '../../utils/find-project-root.js';`

### Change 3: activation-tracker.ts (line 39)

**File**: `src/core/skills/activation-tracker.ts`
**Before**: `const root = projectRoot || process.cwd();`
**After**: `const root = projectRoot || resolveEffectiveRoot();`
**Import**: Add `import { resolveEffectiveRoot } from '../../utils/find-project-root.js';`

### Change 4: platform.ts deduplication (lines 110-127)

**File**: `src/hooks/platform.ts`
**Before**: Full `findProjectRoot()` function body (18 lines)
**After**: Re-export from canonical module:
```typescript
export { findProjectRoot } from '../utils/find-project-root.js';
```
Remove the inline function body entirely. Any existing callers of `platform.findProjectRoot()` continue to work -- same name, same signature, same behavior.

## Design Decisions

### Why resolveEffectiveRoot() and not findProjectRoot() or getProjectRoot()

`resolveEffectiveRoot()` is the only function that handles the umbrella-vs-single-repo decision. It returns:
- Umbrella root when inside an umbrella project (via `findUmbrellaRoot()`)
- Nearest project root in single-repo mode (via `findProjectRoot()`)
- `process.cwd()` as final fallback

The other functions do not walk up to the umbrella root.

### Why re-export instead of direct import in platform.ts callers

`platform.ts` is already imported by hooks and other callers as the "platform utilities" barrel. Changing every caller to import from `utils/find-project-root.ts` would be a larger diff with no benefit. Re-exporting preserves the existing import graph.

### No caching layer

`resolveEffectiveRoot()` does a filesystem walk-up on each call. This is already the pattern used by 15+ other call sites without measurable performance impact -- the OS page cache makes repeated `existsSync()` calls effectively free. Adding a cache would introduce invalidation complexity for no measurable gain.

## Testing Strategy

TDD approach per spec (test_mode: TDD, coverage_target: 90%):

1. **Unit tests per changed file** -- mock `resolveEffectiveRoot()` to return a controlled path, verify the downstream path construction uses it
2. **Single-repo regression** -- ensure `resolveEffectiveRoot()` returns CWD-equivalent when no umbrella config exists (existing behavior)
3. **Platform.ts re-export** -- verify `platform.findProjectRoot` is the same function reference as `utils/find-project-root.findProjectRoot`

Test files:
- `src/core/specs/__tests__/spec-detector.test.ts` (new or extend existing)
- `src/core/increment/__tests__/active-increment-manager.test.ts` (new or extend existing)
- `src/core/skills/__tests__/activation-tracker.test.ts` (new or extend existing)
- `src/hooks/__tests__/platform.test.ts` (new or extend existing)

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| `resolveEffectiveRoot()` import path wrong | ESM requires `.js` extension -- verified pattern matches existing imports in codebase |
| Platform.ts callers break | Re-export preserves exact signature; test verifies function identity |
| Single-repo regression | Explicit regression tests for non-umbrella mode |
| Circular import from platform.ts to utils | `platform.ts` is in `hooks/`, `find-project-root.ts` is in `utils/` -- no cycle possible |

## Component Boundaries

No new components. All changes are within existing modules:

```
src/utils/find-project-root.ts  (canonical, unchanged)
       |
       +---> src/core/specs/spec-detector.ts        (add import)
       +---> src/core/increment/active-increment-manager.ts  (add import)
       +---> src/core/skills/activation-tracker.ts   (add import)
       +---> src/hooks/platform.ts                   (re-export, remove duplicate)
```

## Domain Skill Recommendation

No domain skills needed. This is a pure backend TypeScript fix in the SpecWeave CLI with no frontend, database, or infrastructure components.
