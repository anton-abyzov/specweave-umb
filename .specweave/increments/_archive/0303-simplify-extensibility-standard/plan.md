# Implementation Plan: Simplify Extensible Skills Standard — 3 Clear Categories

## Overview

This is a simplification refactor: replace the 5-tier E0-E4 extensibility model with 3 clear categories across vskill-platform (code) and specweave (docs). No changes to DCI, skill-memories, or Reflect systems.

## Architecture

### Components Affected

**vskill-platform** (primary):
- `src/lib/types.ts` — `ExtensibilityTier` type definition
- `src/lib/scanner/extensibility-detector.ts` — detection logic (main rewrite)
- `src/lib/scanner/__tests__/extensibility-detector.test.ts` — test rewrite
- `src/lib/data.ts` — `getExtensibilityStats()`, tier filtering
- `src/lib/__tests__/data.test.ts` — stats/filter tests
- `src/lib/seed-data.ts` — reclassify 21 skills
- `src/app/skills/page.tsx` — list page filter UI
- `src/app/skills/[name]/page.tsx` — detail page tier display

**specweave** (docs only):
- `docs-site/docs/skills/extensible/extensible-skills-standard.md`
- `docs-site/docs/skills/extensible/extensible-skills-guide.md`
- `docs-site/docs/skills/extensible/extensible-skills.md`

### Data Model Changes

```typescript
// Before
export type ExtensibilityTier = "E0" | "E1" | "E2" | "E3" | "E4";

// After
export type ExtensibilityTier = "extensible" | "semi-extensible" | "not-extensible";
```

```typescript
// Before
export interface ExtensibilityResult {
  extensible: boolean;
  tier: ExtensibilityTier;
  extensionPoints: ExtensionPoint[];
  portability: Record<string, string[]>;  // REMOVED
}

// After
export interface ExtensibilityResult {
  extensible: boolean;
  tier: ExtensibilityTier;
  extensionPoints: ExtensionPoint[];
}
```

### Detection Logic Changes

```
Before:                              After:
E4 = DCI + memories + reflect    →   extensible = DCI + skill-memories
E3 = DCI block                   →   extensible = DCI + skill-memories
E2 = frontmatter extensibility   →   REMOVED (0 adoption)
E1 = keyword signals             →   semi-extensible = keyword signals
E0 = no signals                  →   not-extensible = no signals
```

Key simplifications:
1. No frontmatter detection — removed entirely
2. No portability matrix — removed entirely
3. DCI without skill-memories: still `semi-extensible` (rare edge case — DCI block exists but doesn't reference skill-memories)
4. Reflect/auto-learn reference: no longer affects classification (orthogonal feature)

## Technology Stack

No new dependencies. This is a pure refactor within existing TypeScript + Next.js + Vitest stack.

## Implementation Phases

### Phase 1: Core Type and Detector (US-001)
1. Change `ExtensibilityTier` type in `types.ts`
2. Rewrite `extensibility-detector.ts` with simplified logic
3. Remove `portability` from `ExtensibilityResult`
4. Update `data.ts` stats and filtering
5. Rewrite all detector tests

### Phase 2: Seed Data and UI (US-002)
1. Reclassify all 21 skills in `seed-data.ts`
2. Update skills list page filter UI
3. Update skill detail page tier display
4. Verify URL param backward compat

### Phase 3: Documentation (US-003)
1. Rewrite extensible-skills-standard.md
2. Simplify extensible-skills-guide.md
3. Update extensible-skills.md landing page

## Testing Strategy

- Unit tests: Rewrite `extensibility-detector.test.ts` covering all 3 tiers, edge cases (fenced code blocks, empty input, DCI without memories), and backward compat boolean
- Integration: Verify `getExtensibilityStats()` returns correct 3-category breakdown
- Manual: Check platform UI filters and skill detail pages render correctly

## Technical Challenges

### Challenge 1: Backward Compatibility of `extensible: boolean`
**Solution**: Derive as `tier !== "not-extensible"`. Both `extensible` and `semi-extensible` map to `true`.
**Risk**: Low — single derivation point.

### Challenge 2: URL Query Param Migration
**Solution**: `ext=true` continues to mean "any extensible". New params `ext=extensible` and `ext=semi-extensible` for specific filtering. Old `ext=E1` etc. params are not supported (no one uses them externally).
**Risk**: Low — internal platform only.

### Challenge 3: DCI Without skill-memories Reference
**Solution**: A DCI block that doesn't reference `skill-memories` is classified as `semi-extensible` (it has a customization mechanism but not the standard one). Only DCI + skill-memories = `extensible`.
**Risk**: Edge case — no current skills hit this path.
