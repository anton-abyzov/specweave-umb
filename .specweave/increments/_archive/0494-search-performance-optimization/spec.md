---
increment: 0494-search-performance-optimization
title: Search Performance Optimization
type: feature
priority: P1
status: completed
created: 2026-03-11T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Search Performance Optimization

## Problem Statement

Search on verified-skill.com is perceived as slow. The current hybrid search (KV edge + Postgres) runs both sources sequentially, always queries Postgres even when edge has sufficient results, adds 3 DB queries for blocklist enrichment unconditionally, and uses conservative cache TTLs. The frontend offers no instant results on palette open, requiring users to wait for the full API roundtrip before seeing anything.

## Goals

- Reduce p95 search latency to < 200ms (from current 200-1000ms+)
- Eliminate unnecessary Postgres queries when edge KV returns sufficient results
- Show trending skills instantly when the search palette opens (zero-wait UX)
- Improve CDN and client cache hit rates with longer, smarter TTLs
- Add Server-Timing headers for production latency observability

## User Stories

### US-001: Edge-First Search with Conditional Postgres Fallback
**Project**: vskill-platform
**As a** user searching for skills
**I want** search results returned as fast as possible
**So that** I get near-instant results without waiting for unnecessary database queries

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given edge KV returns >= fetchLimit results, when a search query is executed, then Postgres is NOT called and results are returned from edge only
- [x] **AC-US1-02**: Given edge KV returns < fetchLimit results, when a search query is executed, then Postgres is called to fill gaps and results are merged as before
- [x] **AC-US1-03**: Given edge KV fails entirely, when a search query is executed, then Postgres is called as full fallback and the response includes results
- [x] **AC-US1-04**: The response `X-Search-Source` header accurately reflects which sources were used ("edge", "postgres", or "edge+postgres")

---

### US-002: Conditional Blocklist Enrichment
**Project**: vskill-platform
**As a** user searching for skills
**I want** search to skip unnecessary blocklist DB queries for edge-only responses
**So that** search latency is not inflated by DB round-trips when KV already excludes blocked skills

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given search results came exclusively from edge KV, when blocklist enrichment runs, then `getBlockedSkillNames()` is NOT called (KV index already excludes blocked skills)
- [x] **AC-US2-02**: Given search results include Postgres data, when blocklist enrichment runs, then all 3 blocklist queries execute as before (getBlockedSkillNames, searchBlocklistEntries, searchRejectedSubmissions)
- [x] **AC-US2-03**: Given edge-only results, when blocklist enrichment runs, then `searchBlocklistEntries` and `searchRejectedSubmissions` still execute to surface blocked/rejected entries in results

---

### US-003: Improved CDN and Client Cache Headers
**Project**: vskill-platform
**As a** user performing repeated or popular searches
**I want** search responses cached longer at the CDN edge and on my client
**So that** repeat queries are served instantly from cache

**Acceptance Criteria**:
- [x] **AC-US3-01**: The search endpoint returns `Cache-Control: public, max-age=10, s-maxage=60, stale-while-revalidate=300` (up from s-maxage=30, adding stale-while-revalidate)
- [x] **AC-US3-02**: The frontend SWR cache TTL is 60 seconds (up from 10 seconds)
- [x] **AC-US3-03**: Stale-while-revalidate allows the CDN to serve stale content for up to 300s while fetching fresh data in the background

---

### US-004: Server-Timing Latency Headers
**Project**: vskill-platform
**As a** platform operator
**I want** Server-Timing headers on search responses showing edge and postgres latency
**So that** I can measure actual performance improvement in production via browser DevTools and CDN analytics

**Acceptance Criteria**:
- [x] **AC-US4-01**: The search response includes a `Server-Timing` header with `edge;dur=X` showing edge KV search duration in milliseconds
- [x] **AC-US4-02**: When Postgres is called, the Server-Timing header includes `postgres;dur=X` showing Postgres query duration
- [x] **AC-US4-03**: When Postgres is skipped, the Server-Timing header includes `postgres;desc="skipped"` with dur=0
- [x] **AC-US4-04**: The Server-Timing header includes `enrichment;dur=X` showing blocklist enrichment duration

---

### US-005: Preload Trending Skills on Palette Open
**Project**: vskill-platform
**As a** user opening the search palette
**I want** to see popular/trending skills immediately before I start typing
**So that** I can discover and navigate to popular skills with zero wait time

**Acceptance Criteria**:
- [x] **AC-US5-01**: When the search palette opens and the query is empty, then 10 trending skills are displayed in the SKILLS group
- [x] **AC-US5-02**: Trending skills are fetched from the existing KV-backed home stats endpoint (`/api/v1/stats` or equivalent `getHomeStats()` data)
- [x] **AC-US5-03**: Trending skills are displayed identically to search results (same row layout, tier badges, star counts) with no special "trending" indicator
- [x] **AC-US5-04**: Once the user starts typing (>= 2 chars), the trending skills are replaced by actual search results
- [x] **AC-US5-05**: Trending skills data is cached on the client and does not re-fetch on every palette open (cache for the session or with a reasonable TTL)

---

### US-006: Client-Side Filter of Preloaded Trending Data
**Project**: vskill-platform
**As a** user typing the first 1-2 characters in the search palette
**I want** the trending skills to be filtered client-side instantly
**So that** I see relevant results immediately while the API debounce timer is pending

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given trending skills are loaded and query is 1 character, when the user types, then the trending list is filtered client-side by name/displayName prefix match
- [x] **AC-US6-02**: Given the query reaches 2+ characters, when the debounce fires and API results arrive, then API results replace the client-filtered trending list
- [x] **AC-US6-03**: The client-side filter is instantaneous (no loading skeleton shown for 1-char queries when trending data is available)
- [x] **AC-US6-04**: If trending data has not loaded yet, the 1-char query shows nothing (no error, standard empty state)

## Out of Scope

- Full-text search algorithm changes (ranking, scoring, stemming)
- Search index rebuild or re-sharding of KV data
- Real-time cache invalidation on skill publish events
- Postgres query optimization (index changes, query rewriting)
- Search analytics or tracking infrastructure
- Personalized or geo-based search results

## Technical Notes

### Dependencies
- Existing KV sharded search index (`SEARCH_CACHE_KV`)
- Existing home stats with `trendingSkills` in KV (`getHomeStats()` / `stats-compute.ts`)
- Cloudflare CDN for cache header behavior
- Neon Postgres for fallback search

### Constraints
- p95 latency target: < 200ms
- No new KV namespaces or DB tables required
- All changes confined to `route.ts`, `search.ts`, and `SearchPalette.tsx`
- Trending skills data shape (`TrendingSkillEntry`) must be mapped to `SearchResult` for display

### Architecture Decisions
- Edge-first with conditional Postgres: simplest change with highest impact (~80-90% of queries become edge-only at ~50ms)
- Reuse existing `trendingSkills` from home stats rather than creating a new trending endpoint
- Client-side filtering for 1-char queries bridges the debounce gap without API calls
- Server-Timing headers for observability over custom logging infrastructure

## Success Metrics

- p95 search latency < 200ms (measured via Server-Timing headers)
- 80%+ of search queries served from edge-only (no Postgres) based on X-Search-Source header
- Time-to-first-result on palette open: < 50ms (trending skills from client cache)
- CDN cache hit rate increase (measurable via Cloudflare analytics)
