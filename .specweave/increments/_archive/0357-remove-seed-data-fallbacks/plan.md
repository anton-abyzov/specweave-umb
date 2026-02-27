# Plan: 0357 Remove Seed Data Fallbacks

## Approach

Remove all seed-data fallback paths from the runtime data layer, delete redundant seed scripts, strip volatile trending scores from seed-data.ts, and update tests. Agent data stays as-is (separate concern).

## Key Files

| File | Action |
|------|--------|
| `src/lib/data.ts` | Remove 6 catch-block fallbacks + `applyFiltersInMemory()` |
| `src/app/api/v1/admin/health/skills/route.ts` | Remove seed import + `seed_count` field |
| `src/app/api/v1/admin/health/skills/__tests__/route.test.ts` | Remove `seed_count` assertion |
| `scripts/seed-skills.ts` | Delete |
| `scripts/seed-skills-to-db.ts` | Delete |
| `src/lib/seed-data.ts` | Remove `trendingScore7d`/`trendingScore30d` from 118 entries |
| `src/lib/types.ts` | Make trending fields optional on seed type |
| `prisma/seed.ts` | Default trending scores to 0 when writing to DB |
| `src/lib/__tests__/seed-data-trending.test.ts` | Delete |
| `src/lib/__tests__/data.test.ts` | Rewrite skill tests for empty-state fallback |
| `src/lib/__tests__/data-prisma.test.ts` | Fix merge assumptions |

## Execution Order

1. T-001: Remove fallbacks from data.ts (core change)
2. T-002: Remove seed count from health check
3. T-003: Delete redundant seed scripts
4. T-004: Remove trending scores from seed-data.ts
5. T-005: Delete seed-data-trending.test.ts
6. T-006: Rewrite data.test.ts skill tests
7. T-007: Fix data-prisma.test.ts
8. T-008: Run tests and verify
