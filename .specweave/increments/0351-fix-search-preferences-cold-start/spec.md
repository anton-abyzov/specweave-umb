---
increment: 0351-fix-search-preferences-cold-start
title: "Fix intermittent search failures and preferences 500 on cold starts"
type: bug
priority: P1
status: planned
created: 2026-02-24
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Fix intermittent search failures and preferences 500 on cold starts

## Overview

Neon Postgres cold starts (~8s) cause intermittent 500 errors on the search Postgres fallback and all preferences routes. The search route already has a bare retry loop but lacks a delay between attempts, so the second attempt hits the same cold connection. The preferences routes (GET/PATCH) have no retry at all.

This increment introduces a minimal shared `withRetry` utility used exclusively by these two route files, adds a 500ms delay between the initial attempt and the single retry, and adds generic structured logging (attempt count, error message, route path -- no PII).

## User Stories

### US-001: Retry utility for Neon cold-start resilience (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** a shared retry-with-backoff utility for DB-dependent routes
**So that** Neon cold starts are handled transparently without surfacing 500s to users

**Acceptance Criteria**:
- [ ] **AC-US1-01**: A `withRetry<T>(fn, opts?)` utility exists in `src/lib/retry.ts` accepting `maxAttempts` (default 2) and `delayMs` (default 500)
- [ ] **AC-US1-02**: The utility retries only on thrown errors (not on successful empty results)
- [ ] **AC-US1-03**: The utility waits `delayMs` between attempts using a simple fixed delay (no exponential backoff)
- [ ] **AC-US1-04**: After exhausting all attempts the utility re-throws the last error to the caller
- [ ] **AC-US1-05**: Unit tests cover success-on-first, success-on-retry, and failure-after-exhaustion scenarios with >=80% coverage

---

### US-002: Search route uses retry with delay (P1)
**Project**: vskill-platform

**As a** user searching for skills
**I want** the search Postgres fallback to retry with a delay on cold-start failures
**So that** I get results instead of a 500 error when Neon is waking up

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `GET /api/v1/skills/search` Postgres fallback path uses `withRetry` with 2 attempts and 500ms delay
- [ ] **AC-US2-02**: The existing inline for-loop retry in the search route is replaced by the `withRetry` call
- [ ] **AC-US2-03**: Edge-first KV path is unchanged -- empty KV results still fall through to Postgres (not a retry target)
- [ ] **AC-US2-04**: On retry, a `console.warn` log includes attempt number, error message, and route path `/api/v1/skills/search` -- no query params or user identifiers
- [ ] **AC-US2-05**: Existing search route tests still pass; new test covers retry-then-success scenario

---

### US-003: Preferences routes use retry for cold-start resilience (P1)
**Project**: vskill-platform

**As a** logged-in user
**I want** the preferences GET and PATCH endpoints to retry on cold-start DB failures
**So that** I can load and save my preferences reliably

**Acceptance Criteria**:
- [ ] **AC-US3-01**: `GET /api/v1/user/preferences` wraps its Prisma query in `withRetry` (2 attempts, 500ms delay)
- [ ] **AC-US3-02**: `PATCH /api/v1/user/preferences` wraps the entire read-merge-write block (findUnique + update) in a single `withRetry` call
- [ ] **AC-US3-03**: Auth validation and body parsing remain outside the retry boundary (not retried)
- [ ] **AC-US3-04**: On retry, a `console.warn` log includes attempt number, error message, and route path -- no user IDs or request body contents
- [ ] **AC-US3-05**: Existing preferences tests still pass; new tests cover retry-on-cold-start for both GET and PATCH

## Functional Requirements

### FR-001: withRetry utility
- Location: `src/lib/retry.ts`
- Signature: `async function withRetry<T>(fn: () => Promise<T>, opts?: { maxAttempts?: number; delayMs?: number; onRetry?: (attempt: number, error: unknown) => void }): Promise<T>`
- Default: 2 attempts total (1 initial + 1 retry), 500ms fixed delay
- The optional `onRetry` callback enables callers to log with route-specific context

### FR-002: Search route integration
- Replace the inline `for (let attempt = 0; attempt < 2; ...)` loop with `withRetry(searchSkills(...), { onRetry: ... })`
- Edge path and KV behavior untouched

### FR-003: Preferences route integration
- GET: wrap `prisma.user.findUnique` call in `withRetry`
- PATCH: wrap the entire `findUnique` + merge + `update` sequence in a single `withRetry` call (idempotent merge makes this safe)

## Success Criteria

- Zero increase in p99 latency for happy-path requests (no retry triggered)
- Worst-case latency with retry: ~16.5s (8s timeout + 500ms delay + 8s timeout) -- acceptable for cold start recovery
- Elimination of cold-start 500s on search and preferences routes in production logs

## Out of Scope

- Refactoring `scanner.ts` retry logic (has its own GitHub-specific retry, different concern)
- Exponential backoff or jitter (not needed for 2-attempt fixed delay)
- Circuit breaker patterns
- Retry on other API routes beyond search and preferences
- KV empty-result handling changes (current fall-through to Postgres is correct behavior)

## Dependencies

- Existing `src/lib/db.ts` timeout infrastructure (8s per-query timeout via Prisma `$extends`)
