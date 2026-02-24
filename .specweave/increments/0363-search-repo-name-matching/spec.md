# 0363 — Search: match by repository name, supplement partial edge results

## Problem
Searching "spec" in SearchPalette returns only 2 skills (sync-docs, spec-generator) instead of all skills from the specweave repository. Root cause: edge search shards by first letter of skill name, so skills in other shards are invisible; route returns partial edge results immediately without consulting Postgres.

## User Stories

### US-001: Search by repository name
**As a** user searching for skills from a specific repository,
**I want** the search to match against the repository name,
**So that** I can find all skills from a given repository.

**Acceptance Criteria**:
- [x] AC-US1-01: Searching "spec" returns skills from the specweave repository regardless of skill name
- [x] AC-US1-02: `repoUrl` is included in the Postgres search vector (weight D)
- [x] AC-US1-03: URL is tokenized properly (non-alphanumeric chars → spaces) before indexing

### US-002: Supplement partial edge results with Postgres
**As a** user expecting a full page of results,
**I want** the system to supplement partial edge results with Postgres,
**So that** I get up to `limit` results even when the edge shard has few matches.

**Acceptance Criteria**:
- [x] AC-US2-01: When edge returns < limit results, Postgres is also queried
- [x] AC-US2-02: Results are merged (edge first) and deduplicated by skill name
- [x] AC-US2-03: When edge returns >= limit results, Postgres is NOT queried (fast path preserved)
- [x] AC-US2-04: `X-Search-Source` header reflects source: "edge", "edge+postgres", or "postgres"
