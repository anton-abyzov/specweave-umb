# Plan — 0343

## Implementation Order

1. Rewrite `src/lib/stats-compute.ts` — replace raw SQL, parallelize, add fallbacks
2. Update `src/lib/cron/stats-refresh.ts` — BigInt-safe serialization
3. Update `src/lib/__tests__/stats-compute.test.ts` — new mock structure + fallback tests
4. Update `src/lib/cron/__tests__/stats-refresh.test.ts` — BigInt test
5. Create `tests/e2e/smoke.spec.ts` — production smoke tests
6. Update `package.json` — add `test:e2e:smoke` script
7. Run tests, deploy, verify

## Key Decisions

- Replace `$queryRaw` with Prisma `groupBy`/`aggregate` to avoid BigInt and raw SQL issues
- Keep `DISTINCT ON` as raw SQL with safe fallback (Prisma has no equivalent)
- All queries in single `Promise.all` for maximum parallelism
- Minimal fallback ensures homepage never shows 0 skills even if DB is slow
