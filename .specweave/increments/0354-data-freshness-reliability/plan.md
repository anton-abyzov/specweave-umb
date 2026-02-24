# Plan — 0354 Data Freshness & Reliability

## Approach

1. Schema migration first (T-001: metricsRefreshedAt)
2. Fix enrichment logic (T-002 through T-005: remove guards, add transaction, set timestamp)
3. UI changes (T-006: display freshness)
4. Infrastructure (T-007 through T-009: rate limiting, cache invalidation, batch size)

## Key Files

| File | Changes |
|------|---------|
| `prisma/schema.prisma` | Add metricsRefreshedAt column |
| `src/lib/cron/enrichment.ts` | Major refactor: remove >0 guards, per-skill transactions, rate limiting, batch size config, cache invalidation |
| `src/lib/popularity-fetcher.ts` | Remove >0 guard in live enrichment path |
| `src/lib/types.ts` | Add metricsRefreshedAt to SkillData |
| `src/lib/data.ts` | Map metricsRefreshedAt in mapDbSkillToSkillData |
| `src/app/skills/[name]/page.tsx` | Display "Metrics updated X ago" |
| `scripts/build-worker-entry.ts` | Thread KV env to enrichment for cache invalidation |

## Key Decisions

- Per-skill `$transaction` (not bulk) — one failure doesn't roll back all
- Inline trending formula in JS (replaces bulk `$executeRaw`)
- Backoff: 30s start, 120s max, cap total batch time
- Cloudflare Workers env pattern for KV access and batch size config

## Verification

1. Unit tests for enrichment with mocked fetchers
2. Test metric decrease: mock GitHub returning lower value
3. Test metricsRefreshedAt populated
4. Test rate-limit backoff behavior
5. `npx vitest run` (full suite)
