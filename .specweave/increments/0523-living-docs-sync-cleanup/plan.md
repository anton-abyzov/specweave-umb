---
increment: 0523-living-docs-sync-cleanup
type: plan
status: active
created: 2026-03-14
---

# Architecture Plan: Living Docs Sync Cleanup

## Overview

Pure internal refactor of `living-docs-sync.ts` (2326 LOC) and a one-line comment fix in `project-resolution.ts`. Three bugs fixed, three DRY violations resolved. No new APIs, no behavioral changes beyond Bug 1 correctness fix. No new ADRs required.

## Files in Scope

| File | Changes |
|------|---------|
| `src/core/living-docs/living-docs-sync.ts` | Bugs 1-2, DRY 1-3 |
| `src/core/project/project-resolution.ts` | Bug 3 (comment fix) |

## Bug Fixes

### Bug 1: Cross-Reference Uses Unfiltered `groups` (Lines 321, 365)

**Root cause**: `generateCrossReferences()` at line 321 passes `[...groups.keys()]` (all projects including filtered-out ones) instead of `[...validGroups.keys()]`. Same issue at line 365 where `allTargetPaths` is derived from `groups`.

**Fix**: Replace `groups` with `validGroups` at both locations.

```
Line 321:  [...groups.keys()]      ->  [...validGroups.keys()]
Line 365:  [...groups.keys()]      ->  [...validGroups.keys()]
```

**Risk**: None. `validGroups` is a strict subset of `groups`, filtered between lines 264-282. Using `validGroups` is the clearly intended behavior since the rest of the loop already iterates over `validGroups`.

### Bug 2: Dead `detectMultiProjectMode` Method (Lines 1189-1288)

**Root cause**: Private method (~100 LOC) superseded by `src/utils/multi-project-detector.ts`. Zero callers confirmed via grep (method is private, no reflection usage in TS).

**Fix**: Delete lines 1189-1288 entirely.

**Risk**: Near-zero. Method is `private`, TypeScript compiler would catch any remaining callers.

### Bug 3: Wrong ADR Citation in `project-resolution.ts` (Line 10)

**Root cause**: Header comment references "ADR-0140" (Code Execution Over Direct MCP Tool Calls) but should reference "ADR-0195" (Remove Frontmatter Project Field). ADR-0140 exists and is unrelated to project resolution.

**Fix**: Replace `ADR-0140` with `ADR-0195` in the comment on line 10.

## DRY Extractions

### DRY 1: SKIP_EXTERNAL_SYNC Parsing (Lines 430-431, 626-627)

**Current**: Identical 2-line pattern duplicated in cross-project path (line 430) and single-project path (line 626):
```ts
const skipExternalSync = ['true', '1', 'yes'].includes(
  (process.env.SKIP_EXTERNAL_SYNC || '').toLowerCase().trim()
);
```

**Fix**: Compute once at the top of `syncIncrement()`, before the cross-project/single-project branch. Store in a `const skipExternalSync` that both paths reference.

**Placement**: After line ~230 (after options are validated, before the cross-project branch at line ~250). The env var is stable for the lifetime of the function call.

### DRY 2: Image Generation + TL;DR Injection (Lines 333-358, 507-538)

**Current**: Two near-identical blocks of ~25 lines each. Differences:
- Cross-project path derives `docContext` from `crossProjectPath` and `featureFile` from a `path.join`
- Single-project path derives `docContext` from `projectPath` and uses the existing `featureFile` variable

**Fix**: Extract to a private method on `LivingDocsSync`:

```ts
private async generateAndInjectImage(
  featureFolderPath: string,
  featureFilePath: string,
  title: string,
  featureId: string,
  content: string,
  result: SyncResult
): Promise<string>
```

Returns modified `content` with image markdown injected (or original content if skipped/failed). Encapsulates:
1. `SPECWEAVE_SKIP_IMAGE_GEN` check
2. `DocContext` derivation (from path)
3. `generateLivingDocsImagesEnhanced()` call
4. TL;DR regex replacement
5. Logging
6. Error handling (non-blocking)

Both call sites become a single line each.

### DRY 3: Static `gray-matter` Import (Lines 308, 496)

**Current**: Two dynamic imports `await import('gray-matter')` in the cross-project path (line 308) and single-project path (line 496).

**Fix**: Add static import at top of file (near line 20):
```ts
import matter from 'gray-matter';
```

Replace both `const matter = await import('gray-matter'); matter.default(...)` patterns with direct `matter(...)` calls. The module is always used (never conditionally skipped), and all other dependencies use static imports.

## Execution Order

Tasks should be executed in this order to minimize merge conflict risk:

1. **T-001**: Bug 1 fix (`groups` -> `validGroups`) -- smallest, most critical
2. **T-002**: Bug 3 fix (ADR citation) -- isolated file, no dependencies
3. **T-003**: DRY 3 (static gray-matter import) -- removes dynamic imports before DRY 2 touches same region
4. **T-004**: DRY 1 (SKIP_EXTERNAL_SYNC hoisting) -- changes line numbers but not logic
5. **T-005**: DRY 2 (image generation helper extraction) -- largest change, depends on DRY 3
6. **T-006**: Bug 2 (dead method deletion) -- pure removal, safe to do last

## Verification Strategy

- All existing tests must pass after each task (no new tests required per spec)
- `grep -r 'detectMultiProjectMode' src/` confirms zero remaining references after T-006
- `grep -c "await import('gray-matter')" src/core/living-docs/living-docs-sync.ts` returns 0 after T-003
- `grep -c "SKIP_EXTERNAL_SYNC" src/core/living-docs/living-docs-sync.ts` confirms single parse point after T-004

## No Domain Skill Delegation Needed

This is a pure TypeScript refactor within existing files. No frontend, backend framework, or infrastructure changes. No domain skills required.
