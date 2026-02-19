---
increment: 0237-security-hardening
title: Security Hardening for verified-skill.com
type: feature
priority: P1
status: completed
created: 2026-02-18T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Security Hardening for verified-skill.com

## Overview

Address 12 security issues found during grill review of increment 0225. Three are CRITICAL (exploitable now), seven are HIGH (defense-in-depth), and two are MEDIUM. Covers both the vskill CLI and vskill-platform repos.

## User Stories

### US-001: Cryptographically Secure Submission IDs (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** submission IDs generated with cryptographically secure randomness
**So that** IDs cannot be predicted or enumerated by attackers

**Acceptance Criteria**:
- [x] **AC-US1-01**: `createSubmission()` uses `crypto.randomUUID()` instead of `Math.random()`
- [x] **AC-US1-02**: Generated IDs follow the format `sub_{uuid}`

---

### US-002: Admin Route Authentication (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** all admin API routes to require proper authentication and role verification
**So that** unauthenticated users cannot access admin functionality

**Acceptance Criteria**:
- [x] **AC-US2-01**: GET `/api/v1/admin/submissions` requires `requireRole('REVIEWER')`
- [x] **AC-US2-02**: GET `/api/v1/admin/submissions/[id]` requires `requireRole('REVIEWER')`
- [x] **AC-US2-03**: PATCH `/api/v1/admin/submissions/[id]` requires authentication
- [x] **AC-US2-04**: Unauthenticated requests receive 401; unauthorized receive 403

---

### US-003: CLI Tilde Expansion (P1)
**Project**: vskill

**As a** CLI user
**I want** `~` in file paths to resolve to my home directory
**So that** global installs work correctly instead of creating literal `~` directories

**Acceptance Criteria**:
- [x] **AC-US3-01**: `~` is resolved via `os.homedir()` in global install paths
- [x] **AC-US3-02**: New `resolveTilde()` utility exists in `src/utils/paths.ts`

---

### US-004: Rate Limiting (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** rate limiting on login and submission endpoints
**So that** brute-force and abuse attacks are mitigated

**Acceptance Criteria**:
- [x] **AC-US4-01**: Admin login limited to 5 requests per IP per 15 minutes
- [x] **AC-US4-02**: Submission creation limited to 10 requests per IP per hour
- [x] **AC-US4-03**: Rate-limited responses return HTTP 429 with `Retry-After` header
- [x] **AC-US4-04**: Reusable `checkRateLimit()` utility using Cloudflare KV counters

---

### US-005: JWT Audience Claims (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** JWT tokens to include audience claims distinguishing admin from user tokens
**So that** a stolen user token cannot be used to access admin endpoints

**Acceptance Criteria**:
- [x] **AC-US5-01**: Admin tokens include `aud: 'admin'`, user tokens include `aud: 'user'`
- [x] **AC-US5-02**: Token verification functions validate the `aud` claim
- [x] **AC-US5-03**: Tokens with wrong audience are rejected with 403

---

### US-006: Admin Refresh Token Rotation (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** admin refresh tokens to be rotated on use (matching the user token pattern)
**So that** stolen refresh tokens have limited reuse potential

**Acceptance Criteria**:
- [x] **AC-US6-01**: POST `/api/v1/auth/refresh` deletes old token and creates new token atomically
- [x] **AC-US6-02**: Token rotation uses Prisma `$transaction` for atomicity

---

### US-007: Hashed Refresh Tokens (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** refresh tokens stored as hashes in the database
**So that** a database breach does not expose usable refresh tokens

**Acceptance Criteria**:
- [x] **AC-US7-01**: Refresh tokens stored as SHA-256 hex hashes
- [x] **AC-US7-02**: `hashToken()` utility exists in `src/lib/auth.ts`
- [x] **AC-US7-03**: All token create/lookup paths use hashed values

---

### US-008: CLI Input Validation (P1)
**Project**: vskill

**As a** CLI user
**I want** owner/repo names and skill paths validated against injection
**So that** malicious input cannot cause path traversal or command injection

**Acceptance Criteria**:
- [x] **AC-US8-01**: owner/repo segments validated against `^[\w.-]+$`
- [x] **AC-US8-02**: `--skill` flag validated; path traversal patterns (e.g. `../`) rejected

---

### US-009: Remove Legacy Admin Login (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the legacy admin login route with hardcoded credentials removed
**So that** the `admin123` backdoor is eliminated

**Acceptance Criteria**:
- [x] **AC-US9-01**: Legacy `/api/v1/admin/login/route.ts` is deleted
- [x] **AC-US9-02**: Admin UI (`src/app/admin/page.tsx`) uses `/api/v1/auth/login` instead of `/api/v1/admin/login`
- [x] **AC-US9-03**: `getJwtSecret()` throws if secret is less than 32 characters

---

### US-010: KV Race Condition Mitigation (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** KV submission store operations to handle concurrent writes safely
**So that** simultaneous updates do not silently overwrite each other

**Acceptance Criteria**:
- [x] **AC-US10-01**: `StoredSubmission` type includes a `version` field
- [x] **AC-US10-02**: Read-modify-write operations use version check with retry (up to 3 attempts)

## Functional Requirements

### FR-001: All security fixes must not break existing functionality
Existing tests must continue to pass after each change.

### FR-002: JWT audience enforcement with grace period
Deploy with 1-week grace period accepting tokens both with and without `aud` claim, then enforce.

### FR-003: Hashed token deployment invalidates existing sessions
All existing refresh tokens become invalid on deployment. Users must re-login.

## Success Criteria

- Zero CRITICAL security findings on re-grill
- All existing unit and integration tests pass
- Both repos build successfully
- Rate limiting verified with manual curl tests

## Out of Scope

- Full penetration testing engagement
- WAF / CDN-level DDoS protection
- Content Security Policy headers
- Dependency audit / supply chain security

## Dependencies

- Increment 0225 (completed) — all platform code must be deployed first
- Cloudflare KV namespace for rate limiting (already provisioned)
