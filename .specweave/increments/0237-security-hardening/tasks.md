# Tasks: Security Hardening for verified-skill.com

---
total_tasks: 13
completed_tasks: 13
---

## Wave 1: Critical Quick Wins (parallel)

### T-001: Cryptographically Secure Submission IDs
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed

**Description**: Replace `Math.random().toString(36).slice(2, 8)` with `crypto.randomUUID()` in `submission-store.ts:61`. Change ID format from `sub_{timestamp}_{random6}` to `sub_{uuid}`.

**Files**: `vskill-platform/src/lib/submission-store.ts:61`

**Implementation Details**:
- Replace `const id = \`sub_${Date.now()}_${Math.random().toString(36).slice(2, 8)}\`` with `const id = \`sub_${crypto.randomUUID()}\``
- Update `StoredSubmission` interface JSDoc if any references old format
- `crypto.randomUUID()` is available in Cloudflare Workers runtime

**Test Plan**:
- **File**: `vskill-platform/src/lib/__tests__/submission-store.test.ts`
- **Tests**:
  - **TC-001**: Submission ID format
    - Given a new submission is created
    - When `createSubmission()` is called
    - Then the returned ID matches pattern `sub_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}`
  - **TC-002**: ID uniqueness
    - Given two submissions are created
    - When both IDs are compared
    - Then they are different

**Dependencies**: None

---

### T-002: Admin Submissions List Auth Guard
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04 | **Status**: [x] completed

**Description**: Add `requireRole('REVIEWER')` guard to GET `/api/v1/admin/submissions`. Currently returns mock data without any authentication check.

**Files**: `vskill-platform/src/app/api/v1/admin/submissions/route.ts`

**Implementation Details**:
- Import `requireRole` from `@/lib/admin-auth` (or existing auth middleware)
- Call `requireRole(request, 'REVIEWER')` at start of GET handler
- Return 401 if no token, 403 if wrong role
- Keep existing mock data logic after auth check passes

**Test Plan**:
- **File**: `vskill-platform/src/app/api/v1/admin/submissions/__tests__/route.test.ts`
- **Tests**:
  - **TC-003**: Unauthenticated request returns 401
    - Given no Authorization header or auth cookie
    - When GET `/api/v1/admin/submissions` is called
    - Then response status is 401
  - **TC-004**: Wrong role returns 403
    - Given a valid token with role `USER` (not REVIEWER)
    - When GET `/api/v1/admin/submissions` is called
    - Then response status is 403
  - **TC-005**: Valid REVIEWER token returns submissions
    - Given a valid token with role `REVIEWER`
    - When GET `/api/v1/admin/submissions` is called
    - Then response status is 200 and body contains submissions array

**Dependencies**: None

---

### T-003: Admin Submission Detail Auth Guards
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed

**Description**: Add auth guards to GET and PATCH `/api/v1/admin/submissions/[id]`. Both handlers currently have no authentication.

**Files**: `vskill-platform/src/app/api/v1/admin/submissions/[id]/route.ts`

**Implementation Details**:
- Add `requireRole(request, 'REVIEWER')` to GET handler (line ~141)
- Add auth check to PATCH handler (line ~158)
- Return 401/403 as appropriate

**Test Plan**:
- **File**: `vskill-platform/src/app/api/v1/admin/submissions/[id]/__tests__/route.test.ts`
- **Tests**:
  - **TC-006**: GET without auth returns 401
    - Given no auth token
    - When GET `/api/v1/admin/submissions/sub_123` is called
    - Then response status is 401
  - **TC-007**: PATCH without auth returns 401
    - Given no auth token
    - When PATCH `/api/v1/admin/submissions/sub_123` with `{"action":"approve"}` is called
    - Then response status is 401
  - **TC-008**: GET with valid REVIEWER token returns 200
    - Given a valid REVIEWER token
    - When GET `/api/v1/admin/submissions/sub_123` is called
    - Then response status is 200

**Dependencies**: None

---

### T-004: CLI Tilde Expansion
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed

**Description**: Create `resolveTilde()` utility and apply it to global install paths in the CLI. Currently `agent.globalSkillsDir` may contain `~` which doesn't get expanded by the filesystem APIs.

**Files**: `vskill/src/utils/paths.ts` (new), `vskill/src/commands/add.ts:214`

**Implementation Details**:
- Create `src/utils/paths.ts` with `resolveTilde(p: string): string`
- If path starts with `~`, replace with `os.homedir()`
- Apply `resolveTilde()` to `agent.globalSkillsDir` in `add.ts:214` and line ~352
- Also apply in any other global path references

**Test Plan**:
- **File**: `vskill/src/utils/__tests__/paths.test.ts`
- **Tests**:
  - **TC-009**: Resolves tilde to home directory
    - Given path `~/some/path`
    - When `resolveTilde()` is called
    - Then result is `{os.homedir()}/some/path`
  - **TC-010**: Passes through absolute paths unchanged
    - Given path `/usr/local/bin`
    - When `resolveTilde()` is called
    - Then result is `/usr/local/bin`
  - **TC-011**: Passes through relative paths unchanged
    - Given path `./local/dir`
    - When `resolveTilde()` is called
    - Then result is `./local/dir`

**Dependencies**: None

---

## Wave 2: High Priority (T-005 first, then parallel)

### T-005: Rate Limiting Utility
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04 | **Status**: [x] completed

**Description**: Build a reusable KV-based rate limiter utility using Cloudflare KV counters with sliding window approach.

**Files**: `vskill-platform/src/lib/rate-limit.ts` (new)

**Implementation Details**:
- Export `checkRateLimit(kv: KVNamespace, key: string, limit: number, windowSec: number): Promise<RateLimitResult>`
- `RateLimitResult`: `{ allowed: boolean; remaining: number; retryAfter: number | null }`
- Key format: `rl:{prefix}:{ip}:{windowId}` where windowId = `Math.floor(now / windowSec)`
- Read current counter from KV, increment, write back with TTL = windowSec
- If counter > limit, return `allowed: false` with `retryAfter` seconds

**Test Plan**:
- **File**: `vskill-platform/src/lib/__tests__/rate-limit.test.ts`
- **Tests**:
  - **TC-012**: Allows requests under limit
    - Given KV is empty for the key
    - When `checkRateLimit(kv, 'login:1.2.3.4', 5, 900)` is called
    - Then `allowed` is true and `remaining` is 4
  - **TC-013**: Blocks requests over limit
    - Given KV counter is already at 5 for the key
    - When `checkRateLimit(kv, 'login:1.2.3.4', 5, 900)` is called
    - Then `allowed` is false and `retryAfter` is > 0
  - **TC-014**: Resets after window expires
    - Given KV counter was at 5 in a previous window
    - When a new window starts and `checkRateLimit()` is called
    - Then `allowed` is true

**Dependencies**: None

---

### T-006: Rate Limit Admin Login
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-03 | **Status**: [x] completed

**Description**: Apply rate limiting to POST `/api/v1/auth/login` — 5 requests per IP per 15 minutes.

**Files**: `vskill-platform/src/app/api/v1/auth/login/route.ts`

**Implementation Details**:
- Import `checkRateLimit` from `@/lib/rate-limit`
- Extract client IP from `request.headers.get('cf-connecting-ip') || request.headers.get('x-forwarded-for')`
- Call `checkRateLimit(env.RATE_LIMIT_KV, \`login:${ip}\`, 5, 900)` at handler start
- If not allowed, return 429 with `Retry-After` header and JSON error body

**Test Plan**:
- **File**: `vskill-platform/src/app/api/v1/auth/login/__tests__/route.test.ts`
- **Tests**:
  - **TC-015**: Normal login passes through
    - Given rate limit not exceeded
    - When POST `/api/v1/auth/login` is called
    - Then request proceeds to auth logic (not blocked by rate limiter)
  - **TC-016**: Rate-limited login returns 429
    - Given 5 login attempts from same IP in 15 minutes
    - When 6th POST `/api/v1/auth/login` is called
    - Then response status is 429 with `Retry-After` header

**Dependencies**: T-005

---

### T-007: Rate Limit Submissions
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03 | **Status**: [x] completed

**Description**: Apply rate limiting to POST `/api/v1/submissions` — 10 requests per IP per hour.

**Files**: `vskill-platform/src/app/api/v1/submissions/route.ts`

**Implementation Details**:
- Import `checkRateLimit` from `@/lib/rate-limit`
- Extract client IP
- Call `checkRateLimit(env.RATE_LIMIT_KV, \`submit:${ip}\`, 10, 3600)` at handler start
- If not allowed, return 429 with `Retry-After` header

**Test Plan**:
- **File**: `vskill-platform/src/app/api/v1/submissions/__tests__/route.test.ts`
- **Tests**:
  - **TC-017**: Normal submission passes through
    - Given rate limit not exceeded
    - When POST `/api/v1/submissions` is called
    - Then request proceeds to submission logic
  - **TC-018**: Rate-limited submission returns 429
    - Given 10 submissions from same IP in 1 hour
    - When 11th POST `/api/v1/submissions` is called
    - Then response status is 429 with `Retry-After` header

**Dependencies**: T-005

---

### T-008: JWT Audience Claims
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [x] completed

**Description**: Add `.setAudience()` to all JWT sign functions and validate `aud` in all verify functions. Admin tokens get `aud: 'admin'`, user tokens get `aud: 'user'`.

**Files**: `vskill-platform/src/lib/auth.ts`

**Implementation Details**:
- `signAccessToken()` (line 44): Add `.setAudience('admin')`
- `signRefreshToken()` (line 61): Add `.setAudience('admin')`
- `signUserAccessToken()`: Add `.setAudience('user')`
- `signUserRefreshToken()`: Add `.setAudience('user')`
- `verifyAccessToken()` (line 79): Add `audience: 'admin'` to jwtVerify options
- `verifyRefreshToken()`: Add `audience: 'admin'`
- `verifyUserAccessToken()`: Add `audience: 'user'`
- **Grace period**: Accept tokens without `aud` for backward compatibility (check `aud` only if present, log warning if missing). Add `ENFORCE_JWT_AUDIENCE` env var to switch to strict mode later.

**Test Plan**:
- **File**: `vskill-platform/src/lib/__tests__/auth.test.ts`
- **Tests**:
  - **TC-019**: Admin access token has aud='admin'
    - Given admin payload
    - When `signAccessToken()` is called and token decoded
    - Then `aud` claim is `'admin'`
  - **TC-020**: User access token has aud='user'
    - Given user payload
    - When `signUserAccessToken()` is called and token decoded
    - Then `aud` claim is `'user'`
  - **TC-021**: verifyAccessToken rejects user tokens (when enforced)
    - Given a token with `aud: 'user'`
    - When `verifyAccessToken()` is called with enforcement on
    - Then it throws an error
  - **TC-022**: Grace period accepts tokens without aud
    - Given a legacy token without `aud` claim
    - When `verifyAccessToken()` is called with enforcement off
    - Then it succeeds (with warning logged)

**Dependencies**: None

---

### T-011: CLI Input Validation
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02 | **Status**: [x] completed

**Description**: Add input validation for owner/repo segments and skill names in the CLI. Reject path traversal and injection patterns.

**Files**: `vskill/src/utils/validation.ts` (new), `vskill/src/commands/add.ts`, `vskill/src/commands/submit.ts`

**Implementation Details**:
- Create `src/utils/validation.ts`:
  - `validateRepoSegment(segment: string): boolean` — validates against `^[\w.-]+$`
  - `validateSkillName(name: string): boolean` — rejects `../`, `..\\`, null bytes
- Apply to `submit.ts:25` after splitting owner/repo
- Apply to `add.ts` for skill name argument
- Exit with clear error message on validation failure

**Test Plan**:
- **File**: `vskill/src/utils/__tests__/validation.test.ts`
- **Tests**:
  - **TC-023**: Valid owner/repo passes
    - Given segment `my-org`
    - When `validateRepoSegment()` is called
    - Then returns true
  - **TC-024**: Path traversal rejected
    - Given segment `../etc/passwd`
    - When `validateRepoSegment()` is called
    - Then returns false
  - **TC-025**: Null bytes rejected
    - Given segment `repo\x00name`
    - When `validateRepoSegment()` is called
    - Then returns false
  - **TC-026**: Valid skill name passes
    - Given name `my-skill`
    - When `validateSkillName()` is called
    - Then returns true
  - **TC-027**: Skill name with traversal rejected
    - Given name `../../malicious`
    - When `validateSkillName()` is called
    - Then returns false

**Dependencies**: None

---

## Wave 3: Sequential (dependencies)

### T-012: Remove Legacy Admin Login
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-03 | **Status**: [x] completed

**Description**: Delete the legacy admin login route (has hardcoded `admin123` password and fake base64 "JWT"), fix admin UI to use proper auth endpoint, and add JWT secret length validation.

**Files**:
- DELETE: `vskill-platform/src/app/api/v1/admin/login/route.ts`
- EDIT: `vskill-platform/src/app/admin/page.tsx:19`
- EDIT: `vskill-platform/src/lib/auth.ts` (getJwtSecret)

**Implementation Details**:
- Delete `src/app/api/v1/admin/login/route.ts` entirely
- In `src/app/admin/page.tsx:19`: Change `fetch("/api/v1/admin/login"` to `fetch("/api/v1/auth/login"`
- Update admin page to use proper auth cookie-based flow instead of localStorage tokens
- In `auth.ts` `getJwtSecret()`: Add validation that secret is >= 32 characters, throw if not

**Test Plan**:
- **File**: `vskill-platform/src/lib/__tests__/auth.test.ts`
- **Tests**:
  - **TC-028**: getJwtSecret throws on short secret
    - Given JWT_SECRET env var is "short"
    - When `getJwtSecret()` is called
    - Then it throws "JWT secret must be at least 32 characters"
  - **TC-029**: getJwtSecret accepts 32+ char secret
    - Given JWT_SECRET is a 32+ char string
    - When `getJwtSecret()` is called
    - Then it returns the secret as Uint8Array
  - **TC-030**: Legacy admin login route does not exist
    - Given the codebase after changes
    - When checking for `/api/v1/admin/login/route.ts`
    - Then the file does not exist

**Dependencies**: T-002, T-003 (admin routes must have auth before removing legacy login)

---

### T-009: Admin Refresh Token Rotation
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02 | **Status**: [x] completed

**Description**: Rewrite POST `/api/v1/auth/refresh` to delete old token and create new one atomically, matching the user refresh pattern.

**Files**: `vskill-platform/src/app/api/v1/auth/refresh/route.ts`

**Implementation Details**:
- Wrap token rotation in `prisma.$transaction()`
- Delete old refresh token from DB
- Create new refresh token with new expiry
- Return both new access and refresh tokens
- Set new auth cookies

**Test Plan**:
- **File**: `vskill-platform/src/app/api/v1/auth/refresh/__tests__/route.test.ts`
- **Tests**:
  - **TC-031**: Refresh rotates tokens
    - Given a valid refresh token in DB
    - When POST `/api/v1/auth/refresh` is called with the token
    - Then old token is deleted and new tokens are returned
  - **TC-032**: Used refresh token cannot be reused
    - Given a refresh token that was already rotated
    - When POST `/api/v1/auth/refresh` is called with the old token
    - Then response status is 401
  - **TC-033**: Rotation is atomic
    - Given a valid refresh token
    - When rotation is called and DB write fails
    - Then old token is NOT deleted (transaction rolled back)

**Dependencies**: T-008 (needs audience claims before rotating tokens)

---

### T-010: Hashed Refresh Tokens in Database
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03 | **Status**: [x] completed

**Description**: Store refresh tokens as SHA-256 hex hashes. Add `hashToken()` utility. Update all token create/lookup paths.

**Files**: `vskill-platform/src/lib/auth.ts`, `vskill-platform/src/app/api/v1/auth/refresh/route.ts`, `vskill-platform/src/app/api/v1/auth/login/route.ts`, `vskill-platform/src/app/api/v1/auth/github/callback/route.ts`

**Implementation Details**:
- Add `hashToken(token: string): string` using `crypto.createHash('sha256').update(token).digest('hex')`
- In login route: hash token before storing in `AdminRefreshToken.create()`
- In refresh route: hash incoming token before DB lookup
- In GitHub callback: hash token before storing in `UserRefreshToken.create()`
- No schema changes needed — `token` column stores hash instead of raw value

**Test Plan**:
- **File**: `vskill-platform/src/lib/__tests__/auth.test.ts`
- **Tests**:
  - **TC-034**: hashToken produces consistent SHA-256 hex
    - Given token string "test-token-123"
    - When `hashToken()` is called twice
    - Then both results are identical 64-char hex strings
  - **TC-035**: hashToken produces different hashes for different tokens
    - Given two different token strings
    - When `hashToken()` is called on each
    - Then results are different
  - **TC-036**: Token lookup uses hashed value
    - Given a refresh token stored via login route
    - When refresh endpoint receives the raw token
    - Then it hashes before DB lookup and finds the record

**Dependencies**: T-009 (rotation logic must be in place before adding hashing)

---

## Wave 4: Final

### T-013: KV Race Condition Mitigation
**User Story**: US-010 | **Satisfies ACs**: AC-US10-01, AC-US10-02 | **Status**: [x] completed

**Description**: Add `version` field to `StoredSubmission` and implement optimistic concurrency control with retry logic for KV write operations.

**Files**: `vskill-platform/src/lib/submission-store.ts`

**Implementation Details**:
- Add `version: number` to `StoredSubmission` interface (default: 1 for new submissions)
- In `updateSubmission()`: Read current version → increment → write with version check
- If KV write detects stale version (re-read and compare), retry up to 3 times
- Throw `ConflictError` if all retries exhausted
- New helper: `updateWithRetry(kv, id, updater, maxRetries=3)`

**Test Plan**:
- **File**: `vskill-platform/src/lib/__tests__/submission-store.test.ts`
- **Tests**:
  - **TC-037**: New submissions get version 1
    - Given a new submission is created
    - When stored in KV
    - Then `version` field is 1
  - **TC-038**: Successful update increments version
    - Given a submission at version 1
    - When `updateSubmission()` is called
    - Then stored version is 2
  - **TC-039**: Concurrent conflict triggers retry
    - Given submission at version 1
    - When two concurrent updates race (mock KV to return version 2 on first retry)
    - Then one succeeds after retry
  - **TC-040**: Exhausted retries throw ConflictError
    - Given submission that always conflicts (mock)
    - When `updateSubmission()` is called
    - Then `ConflictError` is thrown after 3 attempts

**Dependencies**: T-001 (new ID format should be in place first)
