# Implementation Plan: Local Studio /studio/find page — discovery UI with as-you-type search and pagination

## Overview

A new top-level Studio route at `/studio/find` (separate from `SkillListPage` which represents installed skills) that surfaces remote registry results inline with trust/publisher/threat signals. As-you-type performance is the central design constraint: 200ms debounce, AbortController for stale-request cancellation, client-side LRU cache, ETag/304 reuse from sibling [0716](../0716-studio-search-api-and-telemetry/), and skeleton states within 100ms.

## Component tree

```
src/app/studio/find/                          [new route]
├── page.tsx                                   # server component, reads ?q&offset
├── FindClient.tsx                             # client island: query state, fetch loop
├── components/
│   ├── SearchBar.tsx                          # input + debounce 200ms + min-length 2
│   ├── ResultCount.tsx                        # "Showing N of M results"
│   ├── ResultGrid.tsx                         # maps results -> ResultCard
│   ├── ResultCard.tsx
│   │   ├── TrustBadge.tsx                     # VERIFIED / CERTIFIED / unknown
│   │   ├── PublisherChip.tsx                  # publisher.name + verified check; deep-link
│   │   ├── ThreatBanner.tsx                   # rendered when isBlocked
│   │   ├── StatsRow.tsx                       # stars / installs / version
│   │   └── InstallButton.tsx                  # clipboard + toast + telemetry
│   ├── LoadMore.tsx                           # button, disabled when offset+len >= total
│   ├── SkeletonGrid.tsx                       # appears <100ms after debounce settle
│   ├── EmptyState.tsx
│   ├── ErrorState.tsx                         # preserves prior results, shows Retry
│   └── SubmitDeepLink.tsx                     # stub component owned here, behavior wired by 0718
└── hooks/
    └── useStudioSearch.ts                     # debounce + AbortController + LRU + ETag
```

## Key data flow — useStudioSearch hook

```ts
function useStudioSearch() {
  const [q, setQ] = useState(initialFromUrl);
  const [offset, setOffset] = useState(0);
  const [list, setList] = useState<Result[]>([]);
  const [total, setTotal] = useState(0);
  const [state, setState] = useState<'idle'|'loading'|'error'>('idle');
  const lru = useRef(new ClientLRU<Result[]>(50));
  const etag = useRef<Map<string, string>>(new Map());
  const aborter = useRef<AbortController | null>(null);
  const debounceTimer = useRef<number | null>(null);

  // Effect on q change:
  useEffect(() => {
    if (q.trim().length < 2) { setList([]); setTotal(0); setState('idle'); return; }
    if (debounceTimer.current) clearTimeout(debounceTimer.current);

    debounceTimer.current = window.setTimeout(async () => {
      const key = `${q.trim()}|${offset}`;
      const cached = lru.current.get(key);
      if (cached) {
        setList(cached.results);
        setTotal(cached.total);
        setState('idle');
        replaceUrl(q.trim(), offset);
        return;
      }
      aborter.current?.abort();
      const ac = new AbortController();
      aborter.current = ac;
      setState('loading');
      try {
        const headers: HeadersInit = {};
        const prevEtag = etag.current.get(key);
        if (prevEtag) headers['If-None-Match'] = prevEtag;
        const r = await fetch(`/api/v1/studio/search?q=${encodeURIComponent(q.trim())}&limit=20&offset=${offset}`, { signal: ac.signal, headers });
        if (r.status === 304) {
          // etag hit — use cached payload (LRU will already have a recent value)
          // (a defensive code path: if not in LRU, fall back to a fresh call without if-none-match)
          // ...
          return;
        }
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const body = await r.json();
        const newEtag = r.headers.get('ETag');
        if (newEtag) etag.current.set(key, newEtag);
        lru.current.set(key, body);
        setList(prev => offset === 0 ? body.results : [...prev, ...body.results]);
        setTotal(body.total);
        setState('idle');
        replaceUrl(q.trim(), offset);
      } catch (e: any) {
        if (e.name === 'AbortError') return; // superseded
        setState('error');
      }
    }, 200);

    return () => { if (debounceTimer.current) clearTimeout(debounceTimer.current); };
  }, [q, offset]);

  return { q, setQ, offset, setOffset, list, total, state, retry: () => setState('idle') };
}
```

## Design decisions (skeptic-tested)

| Decision | Choice | Why |
|---|---|---|
| Tab vs route | **Separate route** `/studio/find` | SkillListPage = installed (local); /studio/find = registry (remote). Different concept. |
| Debounce window | **200ms** | Faster feels jittery; slower feels laggy. Industry typeahead floor. |
| Pagination pattern | **LoadMore button** (NOT infinite scroll) | Predictable, keyboard-accessible, clear "no more results" signal, avoids fetch-on-scroll thrash. |
| Install action | **Clipboard + toast** (NOT server shell-out, NOT direct fs) | Server can't reach `~/.claude/`; direct fs would duplicate 0670. Clipboard is correct + safe. |
| Deep-link behavior | `replaceState` per query (NOT pushState) | Avoid history pollution per keystroke. Each navigation event should be a navigation, not a typing artifact. |
| Cache key | `${q}|${offset}` | Limits cardinality (no `limit` since we always use 20). |
| Min query length | **2 chars** | 1 char queries return huge result sets and aren't actionable. |
| Skeleton vs spinner | **Skeleton cards** | Layout stability — no jump when results land. |

## Mock harness for parallel build (FR-001)

Until 0716 deploys, MSW handlers serve fixture data:

```ts
// vskill-platform/src/test-fixtures/studio-search.handlers.ts
export const studioSearchHandlers = [
  rest.get('/api/v1/studio/search', (req, res, ctx) => {
    const q = req.url.searchParams.get('q') || '';
    const offset = parseInt(req.url.searchParams.get('offset') || '0', 10);
    const limit = Math.min(parseInt(req.url.searchParams.get('limit') || '20', 10), 30);
    const fixture = require('./studio-search.json');
    const filtered = fixture.results.filter((r: any) => r.name.toLowerCase().includes(q.toLowerCase()));
    return res(
      ctx.status(200),
      ctx.set('ETag', `"mock-${q}-${offset}"`),
      ctx.json({ results: filtered.slice(offset, offset + limit), total: filtered.length, offset })
    );
  }),
  rest.post('/api/v1/studio/telemetry/install-copy', (_req, res, ctx) => res(ctx.status(204))),
  rest.post('/api/v1/studio/telemetry/submit-click', (_req, res, ctx) => res(ctx.status(204))),
];
```

`studio-search.json` fixture covers: verified+certified, verified-only, unknown publisher, blocked (isBlocked=true with threatType+severity), and a >40-result set for LoadMore tests.

## Test strategy

| Layer | Target | Tool |
|---|---|---|
| Unit | `ClientLRU`, `useStudioSearch` debounce/abort/cache | Vitest + React Testing Library + MSW |
| Component | Each card sub-component renders all signal states | Vitest + RTL |
| Integration | Full FindClient with MSW handlers | Vitest + RTL + MSW |
| E2E | Playwright golden path + LoadMore + blocked-skill flow + clipboard assertion | Playwright |
| Perf | Playwright trace asserting AC-US1-09 (<250ms perceived on cache hit) | Playwright |

## Coordination with siblings

- **Mock fixtures** delivered by sibling 0716 (T-010) at `.specweave/docs/contracts/studio-search-api-v1.md`. We import the response shape from there to keep MSW + types in sync.
- **Live integration task** (T-final) flips `MSW_ENABLED=false` and runs the Playwright suite against the live dev Worker.
- **SubmitDeepLink stub** lives here; sibling 0718 imports the component and binds its `onClick` + `repoUrl` props.

## ADR stubs

- **ADR-XXXa**: `/studio/find` is a separate route, not a tab on SkillListPage. Different concept (installed vs registry).
- **ADR-XXXb**: 200ms debounce is the as-you-type floor; AbortController is mandatory for stale-request cancellation.
- **ADR-XXXc**: LoadMore over infinite scroll for accessibility + predictability.
- **ADR-XXXd**: Install via clipboard, not server-side execution. Daemon deferred to V2.

## Risk register (linked from spec.md)

See spec.md "Risk register" — duplicated for plan-mode review.
