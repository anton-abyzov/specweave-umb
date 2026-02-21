# Implementation Plan: Extensible Skills Filter -- Full-Stack UX

## Overview

Add extensible skill filtering across the full stack: extend the `SkillFilters` type, update `getSkills()` data layer, add API route param, and enhance the catalog page with an EXT badge, toggle filter, and conditional extension point type display.

All changes are additive -- no breaking changes to existing interfaces. The feature follows the existing server-rendered (RSC) pattern with URL-based state management (search params).

## Architecture

### Components Modified
- **`src/lib/types.ts`**: Add `extensible?: boolean` to `SkillFilters` interface
- **`src/lib/data.ts`**: Add extensible filter logic in `getSkills()`
- **`src/app/api/v1/skills/route.ts`**: Accept `extensible` query param, validate, pass to `getSkills()`
- **`src/app/skills/page.tsx`**: Add EXT badge on cards, toggle button in filter bar, extension point types in metrics row

### Data Model
No schema changes. Uses existing fields on `SkillData`:
- `extensible?: boolean` -- already present
- `extensionPoints?: { type: string; description: string }[]` -- already present

### API Contract Changes

**`GET /api/v1/skills`** -- existing endpoint, new optional param:

| Param | Type | Description |
|-------|------|-------------|
| `extensible` | `"true"` | When present, filters to only extensible skills |

Response shape unchanged. No new endpoints needed.

## Technology Stack

- **Framework**: Next.js 15 (RSC, server components)
- **Language**: TypeScript
- **Testing**: Vitest with ESM mocking (`vi.hoisted()` + `vi.mock()`)
- **Styling**: Inline styles (existing pattern -- no CSS modules or Tailwind)

**Architecture Decisions**:
- **URL state for filter toggle**: Consistent with existing category/tier/sort filters. No client-side state needed. Server-rendered toggle via `<a>` tags.
- **No new component files**: The EXT badge is simple enough to be inline in the catalog page (3-4 lines of JSX). If it grows later, extract to `components/ExtBadge.tsx`.
- **Count computed server-side**: The extensible count is computed from the already-fetched `allSkills` array, avoiding an extra data fetch.

## Implementation Phases

### Phase 1: Backend (types + data layer + API)
1. Add `extensible?: boolean` to `SkillFilters` in `types.ts`
2. Add filtering logic in `getSkills()` in `data.ts`
3. Add `extensible` param handling in `/api/v1/skills` route
4. Write tests for all three changes

### Phase 2: Frontend (catalog page)
1. Add EXT badge pill on skill cards (always visible for extensible skills)
2. Add extensible toggle button in Sort+Tier row with count
3. Add extension point types to metrics row (conditional on `ext=true`)
4. Wire up URL state (`ext` search param)

## Testing Strategy

- **Unit tests** for `getSkills()` extensible filter (data.test.ts) -- add mock skills with `extensible: true/false`, verify filtering
- **API route test** for `/api/v1/skills?extensible=true` -- verify param parsing and filtering
- **No component tests needed**: UI is server-rendered RSC with inline styles; visual verification via dev server. Existing catalog page has no component tests (consistent approach).

## Technical Challenges

### Challenge 1: Extensible count under combined filters
**Problem**: The count shown on the toggle ("Extensible N") must reflect how many extensible skills exist AFTER other filters (category, tier, search) are applied.
**Solution**: Compute from the already-fetched `allSkills` array using `.filter(s => s.extensible)`. This is a cheap in-memory operation on an already-filtered list.
**Risk**: None -- existing pattern used for `totalCount` already.
