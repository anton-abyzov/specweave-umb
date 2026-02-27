# Implementation Plan: Homepage Improvements

## Overview

Three independent improvements to the vskill-platform homepage, all touching `src/app/page.tsx` and related data layer files. No new components needed. Changes are small and targeted.

## Architecture

### Components Modified
- `src/app/page.tsx`: Hero section CLI examples (US-001)
- `src/lib/data.ts`: `getSkillCategories()` fix (US-002) - already has Prisma merge logic, needs validation
- `src/lib/types.ts`: JSDoc on trendingScore fields (US-003)
- `src/lib/seed-data.ts`: Trending score delta adjustments + scale comment (US-003)

### No New Components
All changes are modifications to existing files. No new APIs, no new components, no schema changes.

## Technology Stack

- **Language/Framework**: TypeScript, Next.js 15
- **Testing**: Vitest (TDD mode)
- **Database**: Prisma (existing, no schema changes)

## Implementation Phases

### Phase 1: CLI Examples (US-001)
Replace the generic `$ npx vskill ...` code element in the hero section with two concrete examples:
1. `$ npx vskill install anthropics/skills` (install a real skill)
2. `$ npx vskill find security` (search the registry)

The `or bunx / pnpx / yarn dlx` hint stays.

**Files**: `src/app/page.tsx` only

### Phase 2: Category Chart Fix (US-002)
The `getSkillCategories()` function in `data.ts` already merges Prisma DB categories (lines 333-372). The issue is subtle: when no DB categories are available and KV is also empty, only seed data shows (118 skills). But the hero gets `totalSkills = allSkills.length` from `getSkills()` which does merge properly.

The fix: ensure `getSkillCategories()` uses the same merge strategy as `getSkills()` so category counts are consistent.

**Files**: `src/lib/data.ts`, `src/lib/__tests__/data.test.ts`, `src/lib/__tests__/data-prisma.test.ts`

### Phase 3: Trending Score Docs (US-003)
1. Add JSDoc to `trendingScore7d` and `trendingScore30d` in `SkillData` interface
2. Add a scale comment block at the top of the trending score section in seed-data.ts
3. Adjust select seed data entries to have more meaningful 7d vs 30d deltas for top trending skills (currently deltas are 2-4 pts, should be 5-15 for top skills to show clear momentum)

**Files**: `src/lib/types.ts`, `src/lib/seed-data.ts`

## Testing Strategy

- **TDD**: Write tests first for category chart fix (US-002)
- **Unit tests**: Validate `getSkillCategories()` returns merged counts
- **Snapshot/visual**: Manual check of CLI examples rendering
- **Data tests**: Verify seed data trendingScore deltas produce distinguishable momentum arrows

## Technical Challenges

### Challenge 1: Category Count Consistency
**Problem**: `getSkillCategories()` and `getSkills()` use slightly different merge strategies.
**Solution**: Align `getSkillCategories()` to use the same primary-Prisma/fallback-KV pattern as `getSkills()`.
**Risk**: Low - both already have the same pattern, just needs validation.
