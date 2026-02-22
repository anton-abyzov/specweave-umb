# Implementation Plan: Extensible Skills Standard Formalization

## Overview

This increment formalizes the Extensible Skills Standard across two repos: **vskill-platform** (detector, types, API, UI, seed data) and **specweave docs-site** (documentation restructure). The work is organized in three phases: foundation (types + detector), integration (API + UI + seed data), and documentation.

## Architecture

### Components

- **ExtensibilityTier enum** (`src/lib/types.ts`): New union type `'E0' | 'E1' | 'E2' | 'E3' | 'E4'` added to `SkillData`
- **Enhanced detector** (`src/lib/scanner/extensibility-detector.ts`): Upgraded from keyword-only to multi-signal detection (DCI blocks, frontmatter, keywords)
- **Portability mapper** (within detector): Maps detected mechanisms to compatible agent slugs
- **Stats endpoint** (`src/app/api/v1/stats/route.ts`): Extended with `extensibility` breakdown object
- **Skills page** (`src/app/skills/page.tsx`): Tier-aware filtering replacing boolean `?ext=true`
- **Skill detail page** (`src/app/skills/[name]/page.tsx`): Tier badge + portability display
- **Seed data** (`src/lib/seed-data.ts`): All 89 skills annotated with `extensibilityTier`

### Data Model Changes

```typescript
// New type (src/lib/types.ts)
export type ExtensibilityTier = 'E0' | 'E1' | 'E2' | 'E3' | 'E4';

// Extended SkillData
export interface SkillData {
  // ... existing fields ...
  extensible?: boolean;              // KEPT for backward compat (derived: tier >= E1)
  extensibilityTier?: ExtensibilityTier;  // NEW
  extensionPoints?: { type: string; description: string }[];  // KEPT
  portability?: Record<string, string[]>;  // NEW: mechanism -> agent slugs
}

// Extended ExtensibilityResult (scanner)
export interface ExtensibilityResult {
  extensible: boolean;               // KEPT
  tier: ExtensibilityTier;           // NEW
  extensionPoints: ExtensionPoint[];  // KEPT
  portability: Record<string, string[]>;  // NEW
}
```

### API Contracts

**`GET /api/v1/stats`** (extended response):
```json
{
  "totalSkills": 89,
  "verifiedCount": 45,
  "agentCount": 39,
  "scanCount": 89,
  "extensibility": {
    "total": 21,
    "e0": 68,
    "e1": 18,
    "e2": 0,
    "e3": 2,
    "e4": 1
  }
}
```

**`GET /skills?ext=E2`** (tier-aware filtering):
- `?ext=true` remains supported (backward compat, maps to "any tier >= E1")
- `?ext=E2` filters to skills with tier >= E2
- `?ext=E3` filters to skills with tier >= E3

## Technology Stack

- **Language**: TypeScript (ESM)
- **Framework**: Next.js 15, Cloudflare Workers
- **Testing**: Vitest (TDD mode)
- **Data**: KV store + seed data (no Prisma changes)
- **Docs**: Docusaurus (specweave docs-site)

**Architecture Decisions**:
- **Tier as string union, not number**: Using `'E0'`-`'E4'` strings instead of 0-4 numbers for self-documenting code and API responses. The "E" prefix avoids confusion with certification tiers.
- **Portability in detector, not separate module**: The portability matrix is static knowledge tied to detection results, so it belongs in the detector rather than a separate module.
- **Backward-compatible query params**: `?ext=true` is preserved alongside `?ext=E2+` to avoid breaking existing consumers.

## Implementation Phases

### Phase 1: Foundation (Types + Detector)
- Add `ExtensibilityTier` type to `types.ts`
- Extend `ExtensibilityResult` with `tier` and `portability`
- Implement DCI block detection regex in detector
- Implement frontmatter `extensibility:` parsing in detector
- Implement tier determination logic (highest signal wins)
- Implement portability mapping
- Full test coverage for all 5 tiers

### Phase 2: Integration (API + UI + Seed Data)
- Update seed data with `extensibilityTier` for all skills
- Update `SkillData` type with new fields
- Extend `/api/v1/stats` with extensibility breakdown
- Update `/skills` page filtering to support tier-based query
- Update skill detail page with tier badge and portability display
- Update data layer (`data.ts`) for tier-aware filtering

### Phase 3: Documentation
- Split `extensible-skills.md` into standard + guide
- Write formal standard with E0-E4 definitions using RFC language
- Move how-to content to implementation guide
- Update index, sidebar, and cross-references
- Update vskill-platform UI links

## Testing Strategy

- **TDD mode**: RED-GREEN-REFACTOR for all detector changes
- **Unit tests**: Detector tier classification, portability mapping
- **Integration tests**: Stats endpoint, skills API filtering
- **E2E validation**: Skills page renders tier badges correctly (manual)

## Technical Challenges

### Challenge 1: DCI Block Detection Accuracy
**Problem**: DCI blocks use backtick syntax `` !`...` `` which could match false positives in code examples within SKILL.md.
**Solution**: Require DCI blocks to be at the start of a line (after optional whitespace) and NOT inside fenced code blocks. Use a two-pass approach: first strip fenced code blocks, then scan for DCI patterns.
**Risk**: Low -- the `!` prefix is distinctive enough.

### Challenge 2: Backward Compatibility
**Problem**: Existing consumers use `extensible: boolean` and `?ext=true`. Breaking these would be a regression.
**Solution**: Keep `extensible` as a derived field (`tier >= E1`). Keep `?ext=true` working (maps to `tier >= E1`). New `?ext=E2` syntax is additive.
**Risk**: Minimal -- purely additive changes.

### Challenge 3: Seed Data Accuracy
**Problem**: Assigning accurate tiers to 89 skills requires knowing whether each skill's SKILL.md actually contains DCI blocks.
**Solution**: For seed data, use E1 for all currently-flagged extensible skills (they were keyword-detected). Only SpecWeave's own skills get E3/E4 (known to have DCI). This is honest and can be upgraded later when real SKILL.md scanning is implemented.
**Risk**: Low -- conservative classification is better than false positives.
