# Implementation Plan: Skill page Works-with colorful agent pills

## Overview

Simple extract-and-reuse refactoring. Move two `Record<string, string>` constants from the homepage into a shared lib file, then import them in both the homepage and the skill detail page. Update the skill detail page rendering to use brand-colored pill badges instead of plain grey squares.

## Architecture

### Components
- **`src/lib/agent-branding.ts`** (NEW): Shared exports for `AGENT_COLORS` and `AGENT_ICONS`
- **`src/app/page.tsx`** (MODIFY): Remove inline constants, import from shared lib
- **`src/app/skills/[name]/page.tsx`** (MODIFY): Import branding data, replace grey badges with colorful pills

### Data Model
No data model changes. The branding maps are static `Record<string, string>` lookup tables keyed by agent display name.

### API Contracts
No API changes.

## Technology Stack

- **Framework**: Next.js 15 (existing)
- **Language**: TypeScript (existing)
- **Styling**: Inline styles (existing pattern)

**Architecture Decisions**:
- **Shared lib file over component**: The branding data is just constants (not UI), so a plain TS file in `src/lib/` is the right home. A component would be overkill.
- **Keep inline styles**: The project uses inline styles throughout, not CSS modules. Following existing convention.
- **Match homepage style exactly**: Reuse the same pill structure (border radius 999px, icon + name, tinted background) from the homepage featured agents section.

## Implementation Phases

### Phase 1: Extract constants
1. Create `src/lib/agent-branding.ts` with `AGENT_COLORS` and `AGENT_ICONS`
2. Update `src/app/page.tsx` to import from shared lib
3. Verify homepage renders identically

### Phase 2: Update skill detail page
1. Import `AGENT_COLORS` and `AGENT_ICONS` in skill detail page
2. Replace the plain grey agent spans with branded pill badges
3. Verify visual output

### Phase 3: Verification
1. Build check
2. Visual verification of both pages

## Testing Strategy

- Build verification (`next build` must pass)
- Visual verification: homepage unchanged, skill detail page upgraded

## Technical Challenges

### Challenge 1: Agent name mismatch
The `AgentData.name` field from `getAgents()` must match the keys in `AGENT_COLORS`/`AGENT_ICONS`. If names don't match, the fallback (plain pill) handles it gracefully.
**Risk**: Low -- the branding maps already include most agent names.
