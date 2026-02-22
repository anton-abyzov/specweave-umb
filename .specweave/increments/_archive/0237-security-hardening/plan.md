# Implementation Plan: Security Hardening for verified-skill.com

## Overview

Security hardening increment addressing 12 findings from the grill review of increment 0225. Changes span two repos (vskill CLI, vskill-platform) and are organized into 4 execution waves based on severity and dependencies.

## Architecture

### Components

- **Rate Limiter** (`src/lib/rate-limit.ts`): New KV-based sliding-window rate limiter with configurable limits per key prefix
- **Auth Hardening** (`src/lib/auth.ts`): JWT audience claims, token hashing, secret validation
- **Admin Auth Guards**: `requireRole('REVIEWER')` applied to all admin API routes
- **CLI Validation** (`src/utils/validation.ts`, `src/utils/paths.ts`): Input sanitization and tilde resolution
- **KV Versioning** (`src/lib/submission-store.ts`): Optimistic concurrency control for KV writes

### Data Model Changes

- `StoredSubmission`: Add `version: number` field for optimistic concurrency
- `AdminRefreshToken` / `UserRefreshToken`: Store SHA-256 hash instead of raw token
- Submission IDs: Change from `sub_<Math.random>` to `sub_<crypto.randomUUID()>`

### API Contracts

- `GET /api/v1/admin/submissions`: Add `requireRole('REVIEWER')` guard → 401/403 on failure
- `GET /api/v1/admin/submissions/[id]`: Add `requireRole('REVIEWER')` guard
- `PATCH /api/v1/admin/submissions/[id]`: Add auth guard
- `POST /api/v1/auth/login`: Apply rate limit (5/IP/15min) → 429 with `Retry-After`
- `POST /api/v1/submissions`: Apply rate limit (10/IP/hour) → 429 with `Retry-After`
- `DELETE /api/v1/admin/login`: Route removed entirely

## Technology Stack

- **Language/Framework**: TypeScript, Next.js 15 (Cloudflare Workers), Node.js CLI
- **Libraries**: `jose` (JWT), `bcryptjs` (password hashing), Web Crypto API (SHA-256, randomUUID)
- **Infrastructure**: Cloudflare KV (rate limit counters, submission store)

**Architecture Decisions**:
- **KV-based rate limiting over external service**: Cloudflare KV is already provisioned and co-located with the Workers runtime. No additional latency or cost.
- **SHA-256 for token hashing over bcrypt**: Refresh tokens are already high-entropy random strings. SHA-256 is sufficient and much faster than bcrypt for this use case.
- **Optimistic concurrency over distributed locks**: KV doesn't support locks natively. Version-check-and-retry (up to 3 attempts) is the pragmatic solution.
- **Grace period for JWT audience**: Breaking change for existing tokens. Accept tokens both with and without `aud` for 1 week, then enforce via config flag.

## Implementation Phases

### Wave 1: Critical Quick Wins (parallel)
- T-001: Replace `Math.random()` with `crypto.randomUUID()` in submission IDs
- T-002: Add `requireRole('REVIEWER')` to GET `/admin/submissions`
- T-003: Add auth guards to GET/PATCH `/admin/submissions/[id]`
- T-004: Create `resolveTilde()` utility and apply in CLI

### Wave 2: High Priority (parallel, T-005 first)
- T-005: Build KV-based rate limiter utility
- T-006: Apply rate limit to admin login (5/IP/15min)
- T-007: Apply rate limit to submissions (10/IP/hour)
- T-008: Add JWT audience claims to all sign/verify functions
- T-011: CLI input validation for owner/repo/skill

### Wave 3: Sequential (dependencies on earlier waves)
- T-012: Remove legacy admin login route, fix admin UI, add secret validation
- T-009: Implement admin refresh token rotation (depends on T-008)
- T-010: Hash refresh tokens in DB (depends on T-009)

### Wave 4: Final
- T-013: Add version field and retry logic to KV submission store

## Testing Strategy

- **TDD mode**: RED → GREEN → REFACTOR for all tasks
- **Unit tests**: Each utility function gets dedicated tests (`checkRateLimit`, `hashToken`, `resolveTilde`, `validateRepoSegment`)
- **Integration tests**: Auth guard tests verify 401/403 responses
- **Existing tests**: Must continue passing after each change
- **Manual verification**: curl tests for rate limiting, admin auth, submission ID format

## Technical Challenges

### Challenge 1: JWT Audience Breaking Change
**Solution**: Grace period — accept tokens with and without `aud` claim for 1 week. Config flag to enforce.
**Risk**: During grace period, old tokens without audience still work. Acceptable for 1-week window.

### Challenge 2: Hashed Tokens Invalidate Existing Sessions
**Solution**: Deploy hash change as final step. All users must re-login. No migration needed — old tokens simply won't match.
**Risk**: Brief disruption for active users. Mitigated by deploying during low-traffic window.

### Challenge 3: KV Eventual Consistency
**Solution**: Optimistic concurrency with version field. Read → check version → write with incremented version → retry on conflict (up to 3 attempts).
**Risk**: Very high contention could exhaust retries. Unlikely given current traffic levels.

## Critical Files

| File | Changes |
|---|---|
| `vskill-platform/src/lib/auth.ts` | `aud` claims, `hashToken()`, secret validation |
| `vskill-platform/src/lib/submission-store.ts` | crypto IDs, KV versioning |
| `vskill-platform/src/lib/rate-limit.ts` | New: KV-based rate limiter |
| `vskill-platform/src/app/api/v1/admin/submissions/route.ts` | Add auth guard |
| `vskill-platform/src/app/api/v1/admin/submissions/[id]/route.ts` | Add auth guard |
| `vskill-platform/src/app/api/v1/admin/login/route.ts` | DELETE |
| `vskill-platform/src/app/admin/page.tsx` | Fix login URL |
| `vskill-platform/src/app/api/v1/auth/refresh/route.ts` | Token rotation |
| `vskill/src/utils/paths.ts` | New: `resolveTilde()` |
| `vskill/src/utils/validation.ts` | New: input validators |
| `vskill/src/commands/add.ts` | Apply tilde + validation |
