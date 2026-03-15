---
increment: 0002-auth-gateway-logging
title: Auth Gateway Logging Improvements
status: ready_for_review
priority: P1
type: feature
created: 2026-03-13T00:00:00.000Z
---

# Auth Gateway Logging Improvements

## Problem Statement

The Auth Gateway (Colibri.Identity.Keycloak) has inconsistent console logging across its 10 API endpoints. Well-logged endpoints (login, registration, check-email, refresh, introspect) follow a structured `[requestId] OPERATION | Key: value` pattern, but 3 endpoints have significant gaps (forgot-password, verify, student-id), the brand resolver middleware is completely silent, and the global error handler outputs unstructured context. This makes production debugging difficult when issues occur in those under-logged code paths.

## Goals

- Bring forgot-password, verify, and student-id endpoints to the same logging standard as login/registration
- Add fallback-path logging to brand resolver middleware
- Improve global error handler with structured, correlation-friendly output
- Zero new dependencies -- keep existing `console.log` pattern

## User Stories

### US-001: Structured Logging for Forgot Password Endpoint
**Project**: Colibri.Identity.Keycloak
**As a** DevOps engineer investigating password reset failures
**I want** the forgot-password endpoint to log request lifecycle with requestId correlation
**So that** I can trace a single forgot-password request end-to-end in CloudWatch

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a POST to `/api/forgot-password`, when the request is received, then a log line is emitted: `[{requestId}] FORGOT_PASSWORD | Email: {email} | Brand: {brandName}`
- [x] **AC-US1-02**: Given a POST with missing email, when validation fails, then a log line is emitted: `[{requestId}] ERROR: Missing email`
- [x] **AC-US1-03**: Given a successful password reset email trigger, when the response is sent, then a log line is emitted: `[{requestId}] FORGOT_PASSWORD SUCCESS | UserId: {userId}`
- [x] **AC-US1-04**: Given an error during the forgot-password flow, when the catch block executes, then the existing error log includes the `[{requestId}]` prefix
- [x] **AC-US1-05**: Given the requestId is generated via `Date.now()`, when assigned, then it is declared at the top of the handler before any other logic

### US-002: Structured Logging for Verify Endpoint
**Project**: Colibri.Identity.Keycloak
**As a** DevOps engineer debugging token verification issues
**I want** the verify endpoint to log request start and missing-token errors
**So that** I can see when verify requests arrive and why they fail early

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a POST to `/api/verify`, when the request is received, then a log line is emitted: `[{requestId}] VERIFY REQUEST | Source: {body|header}`
- [x] **AC-US2-02**: Given no token in body or Authorization header, when validation fails, then a log line is emitted: `[{requestId}] ERROR: Missing token`
- [x] **AC-US2-03**: Given an invalid token format (no issuer), when decoded payload lacks `iss`, then a log line is emitted: `[{requestId}] ERROR: Invalid token format`

### US-003: Structured Logging for Student ID Endpoint
**Project**: Colibri.Identity.Keycloak
**As a** DevOps engineer debugging student ID lookup failures
**I want** the student-id endpoint to log its full request lifecycle with requestId
**So that** I can correlate student ID lookups with upstream service calls

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a GET to `/api/users/:sub/student-id`, when the request is received, then a log line is emitted: `[{requestId}] GET_STUDENT_ID | Sub: {sub}`
- [x] **AC-US3-02**: Given a successful student ID lookup, when the response is sent, then a log line is emitted: `[{requestId}] GET_STUDENT_ID SUCCESS | StudentId: {studentId}`
- [x] **AC-US3-03**: Given no student ID found for the sub, when 404 is returned, then a log line is emitted: `[{requestId}] GET_STUDENT_ID NOT_FOUND | Sub: {sub}`
- [x] **AC-US3-04**: Given an error during student ID lookup, when the catch block executes, then a log line is emitted: `[{requestId}] GET_STUDENT_ID ERROR | Sub: {sub} | Message: {error.message}`

### US-004: Brand Resolver Middleware Logging
**Project**: Colibri.Identity.Keycloak
**As a** DevOps engineer troubleshooting brand resolution issues
**I want** the brand resolver middleware to log when it falls back to the default brand
**So that** I can detect misconfigured or unknown brand domains

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given a request where brand resolution falls back to default, when `resolvedBrand` is null before default assignment, then a log line is emitted: `BRAND_RESOLVER FALLBACK | Host: {host} | BrandId: {brandId} | Default: {defaultBrand}`
- [x] **AC-US4-02**: Given a request where brand resolves successfully via host or brandId, when the brand is found, then no log line is emitted (to avoid noise on the happy path)

### US-005: Structured Global Error Handler
**Project**: Colibri.Identity.Keycloak
**As a** DevOps engineer investigating uncaught Express errors
**I want** the global error handler to output structured context
**So that** I can quickly identify the failing endpoint and error type in logs

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given an unhandled error reaches the global error handler, when the handler executes, then a log line is emitted: `GLOBAL_ERROR | Method: {req.method} | Path: {req.path} | Status: {status} | Error: {err.message}`
- [x] **AC-US5-02**: Given the existing `console.error('Global error handler:', err)` call, when replaced, then the full error object is still logged on a separate line for stack trace visibility
- [x] **AC-US5-03**: Given the global error handler logs, when the structured line is emitted, then it uses `console.error` (not `console.log`)

## Out of Scope

- Changes to already well-logged endpoints (login, registration, check-email, refresh, introspect, reset-password, logout, userinfo)
- New logging libraries or dependencies (winston, pino, etc.)
- OpenTelemetry span changes (separate concern, already instrumented)
- Log level configuration or environment-based filtering
- Request body sanitization beyond what already exists
- Centralized logging middleware (each handler owns its logs)

## Non-Functional Requirements

- **Performance**: Logging additions must not add measurable latency (console.log is synchronous but negligible at current request volume)
- **Security**: Never log full tokens, passwords, or client secrets -- only identifiers (email, sub, userId, brandName)
- **Compatibility**: Must work with existing CloudWatch log ingestion (plain text, no JSON structured logging)

## Edge Cases

- Brand resolver receives request with no hostname and no brandId: should log fallback with empty host
- Forgot-password with valid email but user not found in Keycloak: should log before returning 404 (already has OTel span, add console log)
- Verify endpoint receives token in both body and Authorization header: log which source was used (body takes precedence per existing code)
- Student-id endpoint called with empty/missing sub parameter: Express still routes it, log the sub as-is

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Logging PII (email) in production | 0.3 | 7 | 2.1 | Email already logged in well-logged endpoints; consistent with existing pattern |
| Brand resolver logging on every request creates noise | 0.4 | 3 | 1.2 | Only log on fallback path, not happy path |
| Forgetting requestId on a new code path in the future | 0.5 | 2 | 1.0 | Document the logging convention in code comments |

## Technical Notes

### Existing Pattern (Reference: login endpoint)
```
const requestId = Date.now();
console.log(`[${requestId}] OPERATION | Key: value`);
console.log(`[${requestId}] SUCCESS/ERROR | Key: value`);
```

### Files to Modify
- `auth-gateway.js` -- forgot-password (~line 931), verify (~line 1159), student-id (~line 302), global error handler (~line 1597)
- `middleware/brand-resolver.js` -- add fallback logging

### Constraints
- `requestId = Date.now()` -- keep this pattern, do not switch to UUID or crypto
- Brand resolver has no access to requestId (middleware runs before handler); use operation-level prefix only

## Success Metrics

- All 5 logging gaps documented in this spec are closed
- Every `/api/forgot-password`, `/api/verify`, and `/api/users/:sub/student-id` request produces at minimum a start log and an outcome log (success/error/not-found)
- Brand resolver fallback events are visible in CloudWatch
- Global error handler output includes method, path, and status in a single parseable line
