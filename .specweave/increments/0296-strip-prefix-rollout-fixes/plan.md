# Plan: Fix slug mismatch bugs from 0292 strip-prefix rollout

## Overview

Four localized bugs in the vskill-platform frontend and data layer resulting from incomplete rollout of the 0292 strip-prefix change. No new modules or architectural changes needed -- all fixes are surgical edits to existing files.

## Architecture

### Components Affected

- **Submit status page** (`src/app/submit/[id]/page.tsx`): Client component with inline slug regex
- **Homepage** (`src/app/page.tsx`): Server component with trending skill links
- **SearchPalette** (`src/app/components/SearchPalette.tsx`): Client component with skill links
- **Data layer** (`src/lib/data.ts`): `getSkillCategories()` and `getSkills()` KV skill merging
- **Slug utility** (NEW: `src/lib/slug.ts`): Extract `makeSlug()` for cross-boundary import

### Key Decision: Extract `makeSlug` to Shared Utility

**Problem**: `makeSlug()` lives in `submission-store.ts` which imports `@opennextjs/cloudflare` and `worker-context.ts`. Client components cannot import it without pulling in server-only dependencies.

**Solution**: Extract `makeSlug()` and `REPO_URL_RE` to `src/lib/slug.ts` (pure function, no deps). Both `submission-store.ts` and client components re-import from `slug.ts`. This avoids bundler issues with server-only code leaking into client bundles.

## Change Map

### Fix 1: Submit Page Slug (US-001)

**File**: `src/lib/slug.ts` (NEW)
- Export `makeSlug(repoUrl: string, skillName: string): string`

**File**: `src/lib/submission-store.ts`
- Replace local `makeSlug()` and `REPO_URL_RE` with re-exports from `slug.ts`

**File**: `src/app/submit/[id]/page.tsx`
- Import `makeSlug` from `@/lib/slug`
- Line 401: Replace `data.skillName.toLowerCase().replace(/[^a-z0-9]+/g, '-')` with `makeSlug("", data.skillName)`
- Line 420 (`ExternalScanStatus`): Replace inline regex with `makeSlug("", skillName)`

### Fix 2: URL Encoding (US-002)

**File**: `src/app/page.tsx`
- Line 217: Wrap `skill.name` with `encodeURIComponent()`

**File**: `src/app/components/SearchPalette.tsx`
- Line 108: Wrap `r.name` with `encodeURIComponent()`

### Fix 3: Category Counts (US-003)

**File**: `src/lib/data.ts`
- `getSkillCategories()`: Merge KV-published skills into category counts via `getCachedPublishedSkills()`, dedup against seed-data names, wrapped in try/catch for build-time safety

### Fix 4: Baseline Trending Score (US-004)

**File**: `src/lib/data.ts`
- `getSkills()` line 85-86: Change `trendingScore7d: 0` to `trendingScore7d: 1`, same for `30d`
- `getSkillByName()` lines 204-205: Same change

## Risk Assessment

- **Low risk**: All changes are isolated to UI rendering and data aggregation
- **No breaking changes**: `makeSlug()` logic is unchanged; we are just aligning consumer sites
- **Backward compatible**: `encodeURIComponent` on clean slugs is a no-op

## Testing Strategy

- TDD: Write tests first for `slug.ts`
- Unit test `getSkillCategories()` with mocked KV to verify counts include published skills
- Unit test `getSkills()` to verify baseline trending score > 0 for published skills
- Existing tests must continue to pass
