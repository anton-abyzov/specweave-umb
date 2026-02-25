---
id: US-001
feature: FS-351
title: Fix KV context resolution in search
status: complete
priority: P0
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1324
    url: https://github.com/anton-abyzov/specweave/issues/1324
---
# US-001: Fix KV context resolution in search

**Feature**: [FS-351](./FEATURE.md)

user searching for skills
**I want** the edge KV search path to reliably resolve the Cloudflare context
**So that** search queries don't intermittently fall through to slow Postgres fallback

---

## Acceptance Criteria

- [x] **AC-US1-01**: `getKv()` in `src/lib/search.ts` calls `getCloudflareContext({ async: true })` consistent with all other call sites
- [x] **AC-US1-02**: No other behavioral changes to edge search or Postgres fallback paths

---

## Implementation

**Increment**: [0351-fix-search-preferences-cold-start](../../../../../increments/0351-fix-search-preferences-cold-start/spec.md)

