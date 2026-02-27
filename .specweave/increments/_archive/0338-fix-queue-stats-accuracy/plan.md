# Plan — 0338 Fix Queue Stats Accuracy

## Approach
Switch stats from stale KV index to Prisma DB (source of truth) with KV caching. Fix frontend perf issues.

## Files to modify
1. `src/app/api/v1/submissions/stats/route.ts` — rewrite to DB + KV cache
2. `src/app/api/v1/submissions/route.ts` — add DB count for total
3. `src/app/hooks/useAdminStatus.ts` — add isAuthenticated field
4. `src/app/queue/page.tsx` — remove dup auth, conditional polling, debounce
5. `src/app/api/v1/submissions/stats/__tests__/route.test.ts` — rewrite mocks
6. `src/app/hooks/__tests__/useAdminStatus.test.tsx` — add isAuthenticated assertions
