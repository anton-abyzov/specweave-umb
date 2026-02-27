# Plan — 0352 Fix Certification Tier Display

## Approach

Sequential execution: T-001 → T-008. All changes are in the types/UI/data-mapping layer — no schema migrations, no infrastructure changes.

## Key Files

| File | Changes |
|------|---------|
| `src/lib/types.ts` | Add SCANNED to CertificationTier union |
| `src/lib/data.ts` | Fix tierMap, update buildWhereClause filter |
| `src/app/components/TierBadge.tsx` | Add ScannedIcon, gray styling, 3-tier branching |
| `src/app/api/v1/skills/[name]/badge/route.ts` | Add SCANNED to color/label records |
| `src/app/skills/page.tsx` | Add SCANNED to TIER_OPTIONS |
| `src/lib/submission-store.ts` | Add certTier upgrade logic on Tier 2 PASS |
| `src/app/api/v1/admin/reports/[id]/route.ts` | Move trust recalc outside auto-block conditional |
| `src/app/skills/[name]/page.tsx` | Add tooltip title attrs to badge wrappers |
| `src/lib/__tests__/data-db-first.test.ts` | Update SCANNED→VERIFIED assertion |

## Verification

1. `npx vitest run src/lib/__tests__/data-db-first.test.ts`
2. `npx vitest run src/lib/trust/__tests__/`
3. `npx vitest run` (full suite)
4. Visual: skill detail page with SCANNED skill shows gray shield badge
