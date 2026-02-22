# Architecture Plan: Search Performance & Scalability for 70k+ Skills

## Overview

Replace the ILIKE-based search in `data.ts` with Postgres full-text search (tsvector + GIN index), add a KV query cache layer, and upgrade the SearchPalette UX. The architecture touches three layers: database schema, backend service, and frontend component.

## Architecture Decisions

### ADR-1: tsvector GENERATED ALWAYS AS vs. Trigger-Based Update

**Decision**: Use `GENERATED ALWAYS AS ... STORED` column on the `Skill` table.

**Why**:
- Postgres auto-maintains the vector on INSERT/UPDATE -- zero application code needed
- Simpler than triggers (no `CREATE FUNCTION`, no `CREATE TRIGGER`)
- Prisma can't read generated columns via `findMany`, but we only read `search_vector` via `$queryRaw` anyway
- Trade-off: slightly larger row size, but negligible at 70k rows

**Rejected alternatives**:
- Trigger-based: more complex to maintain, no benefit for this use case
- Application-level: would require updating vector on every write path

### ADR-2: Raw SQL via $queryRaw vs. Prisma Full-Text Search

**Decision**: Use `$queryRaw` with `Prisma.sql` tagged templates.

**Why**:
- Prisma's built-in full-text search doesn't support `ts_rank_cd` with custom weights or `ts_headline`
- `Prisma.sql` provides parameterized queries (SQL injection safe)
- Keeps the search module self-contained -- no changes to Prisma client generation
- Pattern already used in the codebase (Prisma + Neon adapter supports raw queries)

### ADR-3: KV Cache Strategy -- Query-Level, Passive TTL

**Decision**: Cache entire search responses in KV keyed by `search:{normalizedQuery}:{category}:{page}`, TTL 300s.

**Why**:
- Query-level caching is simple and effective for the Cmd+K use case (many users search same terms)
- 300s TTL means newly published skills appear within 5 minutes -- acceptable latency
- No active invalidation needed (no publish hooks, no cache busting logic)
- New KV binding `SEARCH_CACHE_KV` isolates search cache from other namespaces

**Rejected alternatives**:
- Result-level caching: complex invalidation, marginal benefit
- No caching: unnecessary DB load for popular queries

### ADR-4: Migration Strategy -- Zero-Downtime Multi-Step

**Decision**: Three-step migration: (1) add nullable column + backfill, (2) alter to GENERATED, (3) CREATE INDEX CONCURRENTLY.

**Why**:
- `CREATE INDEX CONCURRENTLY` does not lock the table for writes
- Adding the column as nullable first avoids table rewrite on large tables
- Backfill can run in batches (1000 rows at a time) to avoid long transactions
- Prisma's `db execute` can run raw SQL for steps that Prisma migrations don't support natively

**Note**: Prisma migrations don't support `CONCURRENTLY` directly. The GIN index creation will be a raw SQL migration file.

## Component Design

### 1. Database Layer

```
Skill table
├── search_vector: tsvector (GENERATED ALWAYS AS ... STORED)
│   ├── A-weight: name (1.0)
│   ├── B-weight: displayName (0.4)
│   ├── C-weight: description (0.2)
│   └── D-weight: author || array_to_string(labels, ' ') (0.1)
└── idx_skill_search_vector: GIN index
```

**Migration files** (in `prisma/migrations/`):
1. `YYYYMMDDHHMMSS_add_search_vector/migration.sql` -- adds nullable tsvector column, backfills, alters to GENERATED
2. GIN index via `CREATE INDEX CONCURRENTLY` (raw SQL, not Prisma-managed)

**Seed data upsert**: A script/migration that upserts the 118 seed skills from `seed-data.ts` into the `Skill` table so they get `search_vector` values. Runs as part of the migration or as a separate seed step.

### 2. Search Service (`src/lib/search.ts`)

```typescript
// New module -- extracted from data.ts search concerns

interface SearchOptions {
  query: string;
  category?: string;
  page?: number;      // 1-based, default 1
  limit?: number;     // default 10, max 50
}

interface SearchResult {
  name: string;
  displayName: string;
  description: string;
  author: string;
  repoUrl: string;
  category: string;
  certTier: string;
  githubStars: number;
  highlight: string;    // ts_headline output
  rank: number;         // ts_rank_cd score
}

interface SearchResponse {
  results: SearchResult[];
  pagination: {
    page: number;
    limit: number;
    hasMore: boolean;
  };
}

export async function searchSkills(options: SearchOptions): Promise<SearchResponse>
```

**Data flow**:
```
searchSkills(options)
  → normalize query (lowercase, trim)
  → build cache key: "search:{query}:{category}:{page}"
  → check SEARCH_CACHE_KV
  → if hit: return cached SearchResponse
  → if miss:
      → getDb() → $queryRaw with:
          - plainto_tsquery('english', $query)
          - WHERE search_vector @@ tsquery
          - AND category = $category (if provided)
          - ORDER BY ts_rank_cd(search_vector, tsquery, '{1.0, 0.4, 0.2, 0.1}') DESC
          - ts_headline('english', description, tsquery) AS highlight
          - LIMIT $limit + 1  (fetch one extra to determine hasMore)
          - OFFSET ($page - 1) * $limit
      → map raw results to SearchResult[]
      → build SearchResponse (trim extra row, set hasMore)
      → put in SEARCH_CACHE_KV with expirationTtl: 300
      → return SearchResponse
```

**KV access pattern**: Uses `getCloudflareContext()` from `@opennextjs/cloudflare` for API route context, same as existing KV patterns in the codebase. Falls back to `getWorkerEnv()` for non-Next.js contexts.

### 3. Search API Route (`src/app/api/v1/skills/search/route.ts`)

**Changes**:
- Replace `getSkills({ search: q })` with `searchSkills({ query, category, page, limit })`
- Add `page` and `category` query params
- Add `highlight` field to response
- Add `pagination` object to response
- Return 400 for queries shorter than 2 characters
- Keep existing `Cache-Control` header

**Response shape**:
```json
{
  "results": [
    {
      "name": "skill-name",
      "displayName": "Skill Name",
      "description": "...",
      "author": "org",
      "repoUrl": "https://github.com/...",
      "category": "development",
      "certTier": "VERIFIED",
      "githubStars": 42,
      "highlight": "...matched <b>text</b> here..."
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "hasMore": true
  }
}
```

### 4. SearchPalette Component (`src/app/components/SearchPalette.tsx`)

**Changes**:
- Update `SearchResult` interface to include `highlight`, `displayName`, `githubStars`, `category`, pagination fields
- Reduce debounce from 200ms to 150ms
- Add 2-character minimum threshold (skip fetch for 0-1 chars)
- Add `isLoading` state for skeleton display
- Add 4 shimmer skeleton rows (fixed-height divs with CSS animation)
- Render `highlight` via `dangerouslySetInnerHTML` (ts_headline output is server-controlled, safe)
- Add "Load more" button that increments page state and appends results
- Add empty state with "No results" + "Browse by category" link
- Keep fixed-height overlay (maxHeight: 400 unchanged)

**State additions**:
```typescript
const [isLoading, setIsLoading] = useState(false);
const [page, setPage] = useState(1);
const [hasMore, setHasMore] = useState(false);
const [allResults, setAllResults] = useState<SearchResult[]>([]);
```

### 5. Infrastructure

**New KV namespace**: `SEARCH_CACHE_KV`
- Add to `wrangler.jsonc` `kv_namespaces` array
- Add to `CloudflareEnv` in `src/lib/env.d.ts`
- Create via `wrangler kv namespace create SEARCH_CACHE_KV`

## Dependency Graph

```
Migration (US-001)
  └──→ Search Service (US-002)
         ├──→ KV Cache Layer (US-003)
         └──→ Search API (US-004)
                └──→ SearchPalette UX (US-005)
```

US-001 must complete first (schema). US-002 depends on the column existing. US-003 is integrated into US-002 (same module). US-004 consumes US-002. US-005 consumes US-004.

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| GENERATED column not supported on Neon | Low | Neon runs standard Postgres 16+, GENERATED columns are supported since PG 12 |
| $queryRaw type safety gap | Medium | Define explicit TypeScript interfaces for raw query results; cast with `as` |
| GIN index build time on 70k rows | Low | `CONCURRENTLY` avoids locks; 70k rows = seconds, not minutes |
| ts_headline XSS in highlight | Low | Server-controlled output, no user HTML; but still render via dangerouslySetInnerHTML with awareness |
| KV cold start on new queries | Low | 300s TTL means popular queries stay warm; cold queries hit Postgres which should be <200ms with GIN |

## Files to Create/Modify

| File | Action | US |
|------|--------|-----|
| `prisma/migrations/YYYYMMDD_add_search_vector/migration.sql` | Create | US-001 |
| `prisma/schema.prisma` | No change (generated columns are invisible to Prisma schema) | US-001 |
| `src/lib/search.ts` | Create | US-002, US-003 |
| `src/lib/search.test.ts` | Create | US-002, US-003 |
| `wrangler.jsonc` | Add SEARCH_CACHE_KV binding | US-003 |
| `src/lib/env.d.ts` | Add SEARCH_CACHE_KV type | US-003 |
| `src/app/api/v1/skills/search/route.ts` | Modify | US-004 |
| `src/app/api/v1/skills/search/route.test.ts` | Create | US-004 |
| `src/app/components/SearchPalette.tsx` | Modify | US-005 |
| `src/app/components/SearchPalette.test.tsx` | Create | US-005 |
| `scripts/seed-skills-to-db.ts` or migration SQL | Create | US-001 (AC-US1-05) |

## Testing Strategy

- **Unit tests**: `search.ts` -- mock `getDb()` and KV, verify query construction, caching logic, pagination math
- **Unit tests**: `route.ts` -- mock `searchSkills()`, verify param validation, response shape, 400 on short queries
- **Component tests**: `SearchPalette.tsx` -- mock fetch, verify skeleton display, load more behavior, empty state
- **Integration**: Manual against Neon dev DB with 70k+ rows to verify P99 < 200ms
- **TDD mode**: RED (write failing test) -> GREEN (implement) -> REFACTOR for each US
