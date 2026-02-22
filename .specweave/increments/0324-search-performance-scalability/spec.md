---
increment: 0324-search-performance-scalability
title: Search Performance & Scalability for 70k+ Skills
status: completed
priority: P1
type: feature
created: 2026-02-22T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Search Performance & Scalability for 70k+ Skills

## Problem Statement

The current search implementation (Prisma ILIKE `contains` with in-memory filtering/sorting/pagination) will not scale to 70k+ skills being ingested via 0319 discovery scale-up. The Cmd+K palette and `/api/v1/skills/search` API are limited to 8 results with no pagination, no loading states, and 200ms debounce. At 70k+ rows, ILIKE scans become prohibitively slow, violating the P99 < 200ms latency target.

## Goals

- Replace ILIKE search with Postgres full-text search (tsvector + GIN index)
- Achieve P99 search latency < 200ms for 70k+ skills
- Add query-level KV caching for repeat searches
- Upgrade SearchPalette UX: pagination, loading skeletons, highlighting, empty states
- Zero-downtime migration path for the new column and index

## User Stories

### US-001: Full-Text Search Column and Index
**Project**: vskill-platform
**As a** platform operator
**I want** a stored tsvector column with a GIN index on the Skill table
**So that** text search queries execute in milliseconds instead of sequential scans

**Acceptance Criteria**:
- [x] **AC-US1-01**: Prisma migration adds `search_vector` column as `tsvector GENERATED ALWAYS AS (setweight(to_tsvector('english', coalesce(name, '')), 'A') || setweight(to_tsvector('english', coalesce("displayName", '')), 'B') || setweight(to_tsvector('english', coalesce(description, '')), 'C') || setweight(to_tsvector('english', coalesce(author, '')), 'D')) STORED`
- [x] **AC-US1-02**: GIN index created on `search_vector` using `CREATE INDEX CONCURRENTLY`
- [x] **AC-US1-03**: Migration is zero-downtime: column added as nullable first, backfilled, then altered to GENERATED
- [x] **AC-US1-04**: Labels array is concatenated into the D-weight vector alongside author
- [x] **AC-US1-05**: Existing seed data (118 skills) is upserted into Postgres so full-text search covers them

### US-002: Search Service Module
**Project**: vskill-platform
**As a** developer
**I want** search logic extracted into a dedicated `src/lib/search.ts` module
**So that** search concerns are separated from listing logic in `data.ts`

**Acceptance Criteria**:
- [x] **AC-US2-01**: `src/lib/search.ts` exports `searchSkills(query, options)` function using `$queryRaw` with `Prisma.sql` tagged templates
- [x] **AC-US2-02**: Search uses `plainto_tsquery('english', $query)` against the `search_vector` column
- [x] **AC-US2-03**: Results ranked by `ts_rank_cd(search_vector, query)` with weight defaults A=1.0, B=0.4, C=0.2, D=0.1
- [x] **AC-US2-04**: `ts_headline('english', description, query)` returns a highlight snippet per result
- [x] **AC-US2-05**: Supports `category` filter, `page`/`limit` pagination parameters

### US-003: KV Query Cache Layer
**Project**: vskill-platform
**As a** platform operator
**I want** search results cached in Cloudflare KV per query+category+page combination
**So that** repeated searches are served from cache without hitting Postgres

**Acceptance Criteria**:
- [x] **AC-US3-01**: Cache key format: `search:{query}:{category}:{page}` stored in KV
- [x] **AC-US3-02**: TTL is 300 seconds (5 minutes); stale entries expire naturally on new publishes
- [x] **AC-US3-03**: Cache miss triggers Postgres query; result is written to KV before returning
- [x] **AC-US3-04**: `searchSkills()` checks KV first, falls back to Postgres on miss
- [x] **AC-US3-05**: Cache is transparent -- API response shape is identical whether cached or fresh

### US-004: Search API Upgrade
**Project**: vskill-platform
**As a** developer consuming the search API
**I want** `/api/v1/skills/search` to return paginated, ranked, highlighted results
**So that** the API supports the full-text search capabilities

**Acceptance Criteria**:
- [x] **AC-US4-01**: API delegates to `searchSkills()` from `src/lib/search.ts` instead of Prisma ILIKE
- [x] **AC-US4-02**: Response includes `results[]` with existing fields plus `highlight` (string from ts_headline)
- [x] **AC-US4-03**: Response includes `pagination: { page, limit, hasMore }` metadata
- [x] **AC-US4-04**: Default limit is 10 results per page; max 50
- [x] **AC-US4-05**: Minimum query length is 2 characters; shorter queries return 400

### US-005: SearchPalette UX Improvements
**Project**: vskill-platform
**As a** developer using the Cmd+K search palette
**I want** loading skeletons, highlighted matches, pagination, and empty states
**So that** the search experience feels fast, informative, and complete

**Acceptance Criteria**:
- [x] **AC-US5-01**: Debounce reduced from 200ms to 150ms with minimum 2-character query threshold
- [x] **AC-US5-02**: 4 shimmer skeleton rows displayed while search request is in-flight
- [x] **AC-US5-03**: Result text shows highlighted matches from the `highlight` field returned by API
- [x] **AC-US5-04**: "Load more" button at bottom of results fetches next page (not infinite scroll)
- [x] **AC-US5-05**: Empty state shows "No results" message with a "Browse by category" link

## Out of Scope

- ILIKE fallback search path (DB tuning is the fix, not dual code paths)
- Separate prefix/autocomplete index (full-text search covers this initially)
- Infinite scroll in the palette (Load more button chosen for simplicity)
- Rate limiting beyond Cloudflare built-in protections
- Real-time cache invalidation on publish (TTL expiry is acceptable)
- Changes to `data.ts` listing/browse logic (only search is migrated)

## Technical Notes

### Dependencies
- Postgres `pg_trgm` or built-in `tsvector` (no extension needed for tsvector)
- Prisma `$queryRaw` for raw SQL (no Prisma full-text search client support needed)
- Cloudflare KV (existing `SEARCH_CACHE` or new binding)
- 0319 scale-up must be in progress (seeds the 70k+ skills)

### Constraints
- P99 search latency < 200ms at 70k+ rows
- Zero-downtime migration (no table locks during GIN index creation)
- SearchPalette overlay is fixed-height (no layout shifts)

### Key Decisions (from interview)
- tsvector GENERATED ALWAYS AS on Skill table (simplest, auto-updates)
- $queryRaw with Prisma.sql tagged templates (type-safe raw SQL)
- Query-level KV caching with 300s TTL (no active invalidation)
- "Load more" button over infinite scroll
- No ILIKE fallback -- fix the DB, not the code

## Success Metrics

- P99 search latency < 200ms for 70k+ skills (measured via API timing)
- KV cache hit rate > 60% for repeat queries within 5-minute window
- Search palette usable with zero layout shift during loading
- All 70k+ skills searchable with relevance-ranked results
