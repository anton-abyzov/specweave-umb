---
increment: 0351-fix-search-preferences-cold-start
title: "Fix intermittent search failures and preferences 500 on cold starts"
type: bug
priority: P1
status: in-progress
created: 2026-02-24
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Fix intermittent search failures and preferences 500 on cold starts

## Overview

Two bugs cause intermittent 500s on search and preferences endpoints:

1. **Search KV context bug**: `getKv()` in `search.ts` calls `getCloudflareContext()` without `{ async: true }`, unlike every other call site. This causes intermittent KV resolution failures, forcing unnecessary Postgres fallback that can then time out on Neon cold starts.

2. **Preferences no retry**: The preferences GET/PATCH routes have no retry logic for Neon cold starts, unlike the search route which already has a 2-attempt retry loop.

## User Stories

### US-001: Fix KV context resolution in search (P0)
**Project**: vskill-platform

**As a** user searching for skills
**I want** the edge KV search path to reliably resolve the Cloudflare context
**So that** search queries don't intermittently fall through to slow Postgres fallback

**Acceptance Criteria**:
- [x] **AC-US1-01**: `getKv()` in `src/lib/search.ts` calls `getCloudflareContext({ async: true })` consistent with all other call sites
- [x] **AC-US1-02**: No other behavioral changes to edge search or Postgres fallback paths

---

### US-002: Preferences cold-start retry (P1)
**Project**: vskill-platform

**As a** logged-in user
**I want** the preferences endpoints to retry on cold-start DB failures
**So that** I can load and save my preferences reliably

**Acceptance Criteria**:
- [x] **AC-US2-01**: `GET /api/v1/user/preferences` retries DB operations once on failure (2 attempts total), matching the search route pattern
- [x] **AC-US2-02**: `PATCH /api/v1/user/preferences` retries the entire read-merge-write block once on failure
- [x] **AC-US2-03**: Auth validation and body parsing remain outside the retry boundary
- [x] **AC-US2-04**: On retry, `console.warn` logs attempt failure with route path (no user IDs or body contents)
- [x] **AC-US2-05**: Existing preferences tests still pass

## Success Criteria

- Elimination of intermittent search 500s caused by KV context resolution failures
- Elimination of preferences 500s on cold isolate starts
- All existing tests pass

## Out of Scope

- New `withRetry` utility (inline retry matches existing search route pattern)
- Exponential backoff or circuit breakers
- Frontend SWR background revalidation abort (non-fatal, low impact)
