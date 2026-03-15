---
increment: 0002-auth-gateway-logging
type: plan
created: 2026-03-13
---

# Plan: Auth Gateway Logging Improvements

## Overview

Fill logging gaps in 3 under-logged endpoints, 1 middleware, and the global error handler. All changes follow the existing `[requestId] OPERATION | Key: value` pattern using `console.log` / `console.error`. No new dependencies, no architectural changes.

## Implementation Strategy

**Approach**: Direct inline additions to existing handler functions. Each endpoint handler already has a try/catch structure; logging lines are inserted at entry, success, and error points.

### Why no abstraction layer

A shared `logRequest(requestId, operation, data)` helper was considered and rejected:
- Only 5 call sites across 2 files
- The existing well-logged endpoints (login, registration, etc.) use raw `console.log` -- introducing a helper for only the new endpoints creates inconsistency
- Zero benefit at this scale; adds indirection for anyone reading the code

## File Changes

### 1. `auth-gateway.js` -- Forgot Password Handler (~line 931)

**What**: Add `requestId = Date.now()` at handler entry. Add log lines for: request received, missing email validation, success, and prefix existing error logs with requestId.

**Pattern**:
```
[{requestId}] FORGOT_PASSWORD | Email: {email} | Brand: {brandName}
[{requestId}] ERROR: Missing email
[{requestId}] FORGOT_PASSWORD SUCCESS | UserId: {userId}
[{requestId}] FORGOT_PASSWORD ERROR | ...
```

**Satisfies**: AC-US1-01 through AC-US1-05

### 2. `auth-gateway.js` -- Verify Handler (~line 1159)

**What**: Add `requestId = Date.now()` at handler entry. Log request start with token source (body vs header), missing token error, and invalid format error.

**Pattern**:
```
[{requestId}] VERIFY REQUEST | Source: {body|header}
[{requestId}] ERROR: Missing token
[{requestId}] ERROR: Invalid token format
```

**Satisfies**: AC-US2-01 through AC-US2-03

### 3. `auth-gateway.js` -- Student ID Handler (~line 302)

**What**: Add `requestId = Date.now()` at handler entry. Log full lifecycle: request received, success with studentId, not-found, and error.

**Pattern**:
```
[{requestId}] GET_STUDENT_ID | Sub: {sub}
[{requestId}] GET_STUDENT_ID SUCCESS | StudentId: {studentId}
[{requestId}] GET_STUDENT_ID NOT_FOUND | Sub: {sub}
[{requestId}] GET_STUDENT_ID ERROR | Sub: {sub} | Message: {error.message}
```

**Satisfies**: AC-US3-01 through AC-US3-04

### 4. `auth-gateway.js` -- Global Error Handler (~line 1597)

**What**: Replace unstructured `console.error('Global error handler:', err)` with a structured summary line plus the full error object on a second line. Both use `console.error`.

**Pattern**:
```
GLOBAL_ERROR | Method: {req.method} | Path: {req.path} | Status: {status} | Error: {err.message}
// followed by: console.error(err)  -- preserves stack trace
```

**Note**: No requestId available at this level (error handler receives (err, req, res, next), and requestId is handler-scoped). This matches the spec -- US-005 does not require requestId.

**Satisfies**: AC-US5-01 through AC-US5-03

### 5. `middleware/brand-resolver.js` -- Fallback Logging

**What**: Add a single `console.log` when brand resolution falls back to default. No logging on the happy path (avoids noise).

**Pattern**:
```
BRAND_RESOLVER FALLBACK | Host: {host} | BrandId: {brandId} | Default: {defaultBrand}
```

**Note**: No requestId -- middleware runs before handlers assign one. Spec confirms this: "Brand resolver has no access to requestId; use operation-level prefix only."

**Satisfies**: AC-US4-01, AC-US4-02

## Edge Cases (from spec)

| Case | Handling |
|------|----------|
| Brand resolver with no hostname and no brandId | Log fallback with empty/undefined host -- no special handling needed |
| Forgot-password with valid email but user not found | Log before returning 404 (add console.log alongside existing OTel span) |
| Verify with token in both body and header | Log `Source: body` (body takes precedence per existing code logic) |
| Student-id with empty/missing sub | Log the sub param as-is (Express delivers whatever matched `:sub`) |

## Security Constraints

- Email: already logged in well-logged endpoints -- consistent
- Never log: full tokens, passwords, client secrets
- Only log identifiers: email, sub, userId, brandName, studentId

## Testing Approach

Manual verification via local Docker run:
1. Start the auth gateway locally
2. Hit each of the 3 endpoints with valid/invalid payloads
3. Verify log output in console matches spec patterns
4. Trigger a forced error to verify global error handler output
5. Send a request with unknown brand host to verify fallback log

No automated tests -- this project has no existing test infrastructure, and adding unit tests for console.log output is out of scope.

## Task Sequencing

Tasks are independent (different code locations in the same files), but should be implemented in this order to minimize edit conflicts within the file:

1. **T-001**: Student ID logging (earliest in file, ~line 302)
2. **T-002**: Forgot Password logging (~line 931)
3. **T-003**: Verify logging (~line 1159)
4. **T-004**: Global error handler (~line 1597)
5. **T-005**: Brand resolver middleware (separate file)

All 5 tasks can be done in a single pass through the codebase.

## Domain Skill Delegation

No domain skills needed. This is a focused logging enhancement with no frontend, no new backend services, and no architectural decisions. Direct implementation via `/sw:do` is appropriate.
