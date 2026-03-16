# Implementation Plan: Unify skill page badges

## Overview

Remove TierBadge rendering from the skill detail page badge row. Keep TrustBadge as the sole badge. Single-file change.

## File

`repositories/anton-abyzov/vskill-platform/src/app/skills/[owner]/[repo]/[skill]/page.tsx`

## Changes

1. Remove `import TierBadge from "@/app/components/TierBadge"`
2. Remove the `<span>` wrapping TierBadge (lines 177-179)
3. Keep TrustBadge rendering (lines 180-183)

## Risk

- **Tainted indicator**: Covered separately by `TaintWarning` component (line 248)
- **Other pages**: Unaffected — they only show TierBadge, no duplication

## Testing

- Unit test: assert TierBadge absent, TrustBadge present on skill detail page
- Full suite: `npx vitest run` for regression check
