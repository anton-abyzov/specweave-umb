# 0336 — Worker DB Timeout Protection

## Problem
Production verified-skill.com crashes with Cloudflare Error 1101 when Neon PostgreSQL cold starts hang DB calls. `withDbTimeout()` exists but only covers 1 of 40+ DB call sites.

## Solution
Add Prisma `$extends` query interceptor with 8s timeout on all model operations. Explicitly wrap `$transaction`/`$queryRaw` with `withDbTimeout`.

## User Stories

### US-001: Worker stability under DB cold starts
As a visitor, I want the site to load even when the database is slow, so I don't see "Worker threw exception" errors.

**Acceptance Criteria:**
- [x] AC-US1-01: All Prisma model operations auto-timeout at 8s via `$extends`
- [x] AC-US1-02: `$transaction` and `$queryRaw` calls wrapped with explicit `withDbTimeout`
- [x] AC-US1-03: Timeout errors include model+operation label for debugging
- [x] AC-US1-04: Existing KV fallback in data.ts catches timeout errors gracefully
- [x] AC-US1-05: OAuth callback cleanup — remove redundant explicit wrapping
- [x] AC-US1-06: Tests verify timeout behavior
