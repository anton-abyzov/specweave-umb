# Plan — 0773

## Files Touched

| File | Why |
|---|---|
| `repositories/anton-abyzov/vskill-platform/src/app/submit/page.tsx` | View Queue href becomes `/queue?filter=active&highlight=...` |
| `repositories/anton-abyzov/vskill-platform/src/app/queue/QueuePageClient.tsx` | Parse `?highlight=`, scroll + flash, strip param. Skip mount fetch + debounce-on-mount when `?q=` present |
| `repositories/anton-abyzov/vskill-platform/src/app/queue/SubmissionTable.tsx` | Add `data-row-id={sub.id}` to row for scroll selector |
| `repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/search/route.ts` | KV cache, drop `id`, AND `reason`, `take: limit*2` |
| `repositories/anton-abyzov/vskill-platform/src/app/queue/data.ts` | Skip list fetch when `params.q` present |
| `repositories/anton-abyzov/vskill-platform/src/app/queue/page.tsx` | Pass `q` to `getQueueInitialDataSSR` |
| `repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/search/__tests__/route.test.ts` | Update `take: 400` → `take: 200`, `take: 40` → `take: 20`. Add cache + reason + no-id tests |
| `repositories/anton-abyzov/vskill-platform/src/app/queue/__tests__/data.test.ts` | New: assert `q` skips list fetch (or extend if exists) |
| `repositories/anton-abyzov/vskill-platform/src/app/submit/__tests__/page.test.tsx` | New or extend: assert View Queue href format |
| `repositories/anton-abyzov/vskill-platform/src/app/queue/__tests__/QueuePageClient.highlight.test.tsx` | New: highlight scroll + flash + URL strip |

## Implementation Order (TDD-friendly)

1. **Search route changes** (pure backend, easy to test):
   - Drop `id` from OR
   - AND `reason` into `where`
   - Reduce `fetchLimit` to `limit*2`
   - Add KV read (cache hit fast path) + KV write (non-blocking, skipped for `state=active`)
   - Update + extend route.test.ts
2. **SSR data.ts** — gate list fetch on `!params.q`. Update `page.tsx` to forward `q`.
3. **QueuePageClient.tsx** — add `didMountRef` + `searchQuery` skip on mount + debounce gate
4. **SubmissionTable.tsx** — add `data-row-id` attribute to row
5. **QueuePageClient.tsx** — parse `?highlight=`, seed flashRef, scrollIntoView, fallback to `filter=all`, strip URL
6. **submit/page.tsx** — build href from `results.filter(r => r.id && !r.error).map(r => r.id)`

## Risks / Decisions

- **Cache invalidation on submission writes**: not implemented. 60s TTL is the staleness ceiling. Acceptable because search is read-mostly and a fresh submission shows up via SSE in the queue list (the search cache is for typed queries, not for the live queue list).
- **Reason filter**: this is a bug fix; tests must catch the regression.
- **Highlight overflow (>50 IDs)**: server-side cap; existing batch path already limits to 50 URLs.
- **WASM cold-start**: KV hit avoids Prisma WASM entirely on subsequent identical queries — biggest single win.

## Future Work (Recommended, Not in Scope)

- `CREATE EXTENSION pg_trgm; CREATE INDEX ... USING gin (skill_name gin_trgm_ops, repo_url gin_trgm_ops);` — turns ILIKE seq-scan into bounded GIN scan. Defer until cache hit rate < 60% or table > 25k rows.
- `COUNT(*) OVER()` single-roundtrip pattern via `db.$queryRaw` — saves one WASM roundtrip per cache miss.
- Bump client debounce 500ms → 650ms — minor.
