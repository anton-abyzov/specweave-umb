# Plan: 0341 Search Performance & Reliability

## Approach
Fix frontend race conditions and backend performance in parallel-safe changes.

## File Changes
1. `src/app/components/SearchPalette.tsx` — AbortController, debounce, loading fix
2. `src/lib/search.ts` — lean payload, SQL consolidation, ILIKE fallback, timeout
3. `src/lib/search.test.ts` — updated tests
4. `src/app/components/__tests__/SearchPalette.test.tsx` — updated tests

## Risks
- Prisma.sql composition with dynamic WHERE — well-documented, safe
- ILIKE with leading wildcard is O(n) — only runs on empty tsvector results (rare)
- KV cache has old 18-field entries — frontend ignores extras, TTL 300s auto-expires
