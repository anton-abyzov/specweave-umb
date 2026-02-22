# 0320 — Architecture Plan

## Scope

Two-file change in `vskill-platform`:

1. **API route**: `src/app/api/v1/skills/search/route.ts`
2. **Component**: `src/app/components/SearchPalette.tsx`

## Design Decisions

### ADR-1: Inline formatNumber vs Shared Utility
**Decision**: Inline `formatStarCount` in SearchPalette (consistent with existing patterns in `skills/[name]/page.tsx` and `VerifiedSkillsTab.tsx` which each define their own `formatNumber` locally).
**Rationale**: Three inline copies is approaching extraction threshold but not the focus of this increment. Keep consistent with codebase for now.

### ADR-2: Star Icon Approach
**Decision**: Inline SVG star icon, same technique as `MiniTierBadge` in SearchPalette.
**Rationale**: No external icon library used in this codebase. SVG is the established pattern.

### ADR-3: Display Position
**Decision**: Star count placed between repo URL link and cert tier badge.
**Rationale**: Stars are a popularity signal (like repo URL context) rather than a trust signal (like cert tier), so they sit closer to the repo URL visually.

## Changes

### 1. Search API Route (`route.ts`)
- Add `githubStars: s.githubStars` to the results map (line ~23)
- `getSkills()` already returns full `SkillData` including `githubStars`, so no data layer changes needed

### 2. SearchPalette Component (`SearchPalette.tsx`)
- Add `githubStars: number` to `SearchResult` interface
- Add `formatStarCount(n: number): string` helper
- Add `StarCount` inline display element in the result row (between repo URL and `MiniTierBadge`)
- Thread `githubStars` through the `allItems` mapping
- Only render when `githubStars > 0`

## Risk Assessment

- **Low risk**: Both changes are additive — no existing behavior modified
- **No migration needed**: `githubStars` already exists in DB schema, seed data, and `SkillData` type
- **Cache-safe**: Search API already has `Cache-Control` headers; adding a field doesn't affect caching
