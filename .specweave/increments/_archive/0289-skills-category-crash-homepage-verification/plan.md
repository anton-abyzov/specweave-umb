# Implementation Plan: Fix skills category crash and improve homepage verification section

## Overview

Two changes in the vskill-platform Next.js app:
1. **Bug fix**: Remove `onClick` handler from Server Component in `/skills/page.tsx` by replacing `<span onClick>` with `<a href>` for repo links.
2. **UI improvement**: Replace the TreeList in homepage verification section with a more visually rich three-tier layout.

## Architecture

### Components Changed
- `src/app/skills/page.tsx` (Server Component) -- replace onClick span with anchor tag
- `src/app/page.tsx` (Server Component) -- replace TreeList verification section with inline redesigned layout

### No New Components Needed
The fix for the skills page is a simple element swap (span with onClick -> anchor tag). The homepage redesign uses existing CSS variables and inline styles consistent with the rest of the page.

## Technology Stack

- **Framework**: Next.js 15 (App Router, React Server Components)
- **Styling**: Inline styles with CSS custom properties
- **Testing**: Vitest

**Architecture Decisions**:
- **Use `<a>` instead of extracting Client Component**: The repo link just needs to open a URL in a new tab. An `<a>` with `target="_blank"` achieves this without JavaScript. This is simpler than creating a Client Component wrapper.
- **Inline redesign vs new component**: The verification section is only used on the homepage. Keeping it inline avoids component proliferation for a one-off section.

## Implementation Phases

### Phase 1: Fix Skills Page Crash (P1)
1. Replace `<span onClick={...}>` with `<a href={...} target="_blank" rel="noopener noreferrer">` in skills list rows
2. Verify the page renders without errors for all filter combinations

### Phase 2: Redesign Verification Section (P2)
1. Replace TreeList usage with a three-column/card layout showing Scanned/Verified/Certified tiers
2. Add visual tier indicators using existing TierBadge or terminal-style markers
3. Add "Learn more" link to /trust page

## Testing Strategy

- Unit test: Verify skills page renders without errors (mock data, check no onClick in output)
- Manual verification: Load /skills and /skills?category=X in dev mode, confirm HTTP 200
- Build test: `next build` succeeds without errors
- Visual: Homepage verification section renders three distinct tiers

## Technical Challenges

### Challenge 1: Server Component Constraints
**Solution**: Use only HTML elements and CSS for interactivity (links via `<a>` tags). No event handlers in Server Components.
**Risk**: Low -- standard HTML pattern.
