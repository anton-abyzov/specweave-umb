---
id: US-002
feature: FS-363
title: Supplement partial edge results with Postgres
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1326
    url: https://github.com/anton-abyzov/specweave/issues/1326
---
# US-002: Supplement partial edge results with Postgres

**Feature**: [FS-363](./FEATURE.md)

**As a** user expecting a full page of results,
**I want** the system to supplement partial edge results with Postgres,
**So that** I get up to `limit` results even when the edge shard has few matches.

---

## Acceptance Criteria

- [x] **AC-US2-01**: When edge returns < limit results, Postgres is also queried
- [x] **AC-US2-02**: Results are merged (edge first) and deduplicated by skill name
- [x] **AC-US2-03**: When edge returns >= limit results, Postgres is NOT queried (fast path preserved)
- [x] **AC-US2-04**: `X-Search-Source` header reflects source: "edge", "edge+postgres", or "postgres"

---

## Implementation

**Increment**: [0363-search-repo-name-matching](../../../../../increments/0363-search-repo-name-matching/spec.md)

**Tasks**: See increment tasks.md for implementation details.

## Tasks

_Completed_
