# Implementation Plan: Homepage trust signals and UX clarity improvements

## Overview

Pure frontend changes across 3 existing files in `vskill-platform`. No new components, no API changes, no data model changes. All data fields needed are already present in `SkillData`.

## Architecture

### Files Modified

1. **`src/app/page.tsx`** (homepage): Scanner attribution in security banner, hero text change, stats label disambiguation
2. **`src/app/skills/[name]/page.tsx`** (skill detail): Add NPM downloads StatCard, add "Last Updated" MetaRow, fix pattern count
3. **`src/app/skills/[name]/security/page.tsx`** (security report): Normalize pattern count to 38

### No New Components

All changes are inline edits to existing JSX. The StatCard and MetaRow sub-components in `skills/[name]/page.tsx` are already defined and reusable.

## Technology Stack

- **Framework**: Next.js 15 (App Router, RSC)
- **Styling**: Inline styles (existing pattern in the codebase)
- **Font**: Geist Mono (via CSS var `--font-geist-mono`)

**Architecture Decisions**:
- **Inline attribution text over separate component**: The attribution is a single `<span>` inside the existing banner `<a>` tag. Creating a component for it would be over-engineering.
- **"security-scanned" terminology**: Avoids collision with the "VERIFIED" tier badge name while still conveying trust. Alternative "registered" considered but doesn't convey security scanning.

## Implementation Phases

### Phase 1: Homepage Banner & Hero (US-001, US-002)
- Add scanner attribution `<span>` inside the security callout `<a>` element
- Change hero text from "{N} verified skills" to "{N} security-scanned skills"
- Update inline stats to use tier-colored labels with explicit "tier" suffix

### Phase 2: Skill Detail Page (US-003)
- Add NPM downloads StatCard (conditionally rendered when > 0)
- Add "Last Updated" MetaRow using `formatDate(skill.updatedAt)`
- Fix pattern count from "37" to "38" in Security section label

### Phase 3: Pattern Count Normalization
- Audit all hardcoded "37" references and update to "38" to match `patterns.ts`
- Files: `page.tsx` (homepage banner), `skills/[name]/page.tsx`, `skills/[name]/security/page.tsx`

## Testing Strategy

Manual visual verification:
- Homepage loads with new banner attribution and disambiguated counts
- Skill detail page shows NPM downloads and "Last Updated"
- Pattern counts are consistent across all pages (38)

## Technical Challenges

### Challenge 1: Pattern count drift
**Solution**: The banner currently hardcodes "37 vulnerability patterns scanned" but `patterns.ts` has 38 patterns. Update all hardcoded references. Consider a future improvement to make this dynamic, but out of scope for this increment.
**Risk**: Low -- just string changes.
