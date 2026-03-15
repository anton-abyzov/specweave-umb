---
total_tasks: 5
completed_tasks: 5
---

# Tasks: Auth Gateway Logging Improvements

Tasks are sequenced by file position (top-to-bottom through auth-gateway.js, then brand-resolver.js) to minimize line-number drift between edits.


## User Story: US-003 - Structured Logging for Student ID Endpoint

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 1 total, 1 completed

### T-001: Add requestId and lifecycle logging to student-id handler

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [x] completed
**File**: `repositories/mckissocklp/Colibri.Identity.Keycloak/auth-gateway.js` (~line 302)

**Test Plan**:
- **Given** the student-id handler is modified and the gateway is running locally
- **When** `GET /api/users/some-sub-value/student-id` is called with a valid token
- **Then** the console shows `[{timestamp}] GET_STUDENT_ID | Sub: some-sub-value`

- **Given** the upstream lookup returns a valid studentId
- **When** the handler sends a 200 response
- **Then** the console shows `[{timestamp}] GET_STUDENT_ID SUCCESS | StudentId: {returnedId}`

- **Given** the upstream lookup returns no studentId (404 path)
- **When** the handler sends a 404 response
- **Then** the console shows `[{timestamp}] GET_STUDENT_ID NOT_FOUND | Sub: some-sub-value`

- **Given** the upstream call throws an exception
- **When** the catch block executes
- **Then** the console shows `[{timestamp}] GET_STUDENT_ID ERROR | Sub: some-sub-value | Message: {error.message}`

- **Given** the sub param is empty or missing (Express still routes)
- **When** any path through the handler executes
- **Then** the log line includes `Sub: ` with whatever value Express resolved (empty string or undefined)

**Manual Verification**:
1. Start gateway locally (`node auth-gateway.js` or `docker compose up`)
2. `curl -H "Authorization: Bearer <token>" http://localhost:<port>/api/users/test-sub/student-id`
3. Grep: `docker logs <container> 2>&1 | grep GET_STUDENT_ID`
4. Confirm pattern: `[\d+] GET_STUDENT_ID | Sub: test-sub`
5. Force 404: use a sub with no associated student ID; check NOT_FOUND log line
6. Force error: point to unreachable upstream; check ERROR log line

**Implementation**:
1. Open `auth-gateway.js`, locate the `GET /api/users/:sub/student-id` handler (~line 302)
2. Add `const requestId = Date.now();` as the first line inside the handler function body
3. Immediately after, add: `console.log(\`[\${requestId}] GET_STUDENT_ID | Sub: \${req.params.sub}\`);`
4. Locate the success response path; before `res.json(...)` or `res.status(200)`, add: `console.log(\`[\${requestId}] GET_STUDENT_ID SUCCESS | StudentId: \${studentId}\`);`
5. Locate the not-found branch (where 404 is returned); add: `console.log(\`[\${requestId}] GET_STUDENT_ID NOT_FOUND | Sub: \${req.params.sub}\`);`
6. In the catch block, add: `console.log(\`[\${requestId}] GET_STUDENT_ID ERROR | Sub: \${req.params.sub} | Message: \${error.message}\`);`


## User Story: US-001 - Structured Logging for Forgot Password Endpoint

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 1 total, 1 completed

### T-002: Add requestId and lifecycle logging to forgot-password handler

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] completed
**File**: `repositories/mckissocklp/Colibri.Identity.Keycloak/auth-gateway.js` (~line 931)

**Test Plan**:
- **Given** the forgot-password handler is modified and the gateway is running
- **When** `POST /api/forgot-password` is called with `{ "email": "user@example.com" }`
- **Then** the console shows `[{timestamp}] FORGOT_PASSWORD | Email: user@example.com | Brand: {brandName}`

- **Given** the POST body is missing the `email` field
- **When** validation fires before any upstream call
- **Then** the console shows `[{timestamp}] ERROR: Missing email`

- **Given** the password reset email is triggered successfully and userId is available
- **When** the success response is sent
- **Then** the console shows `[{timestamp}] FORGOT_PASSWORD SUCCESS | UserId: {userId}`

- **Given** an error is thrown during the forgot-password flow
- **When** the catch block executes
- **Then** the existing error log now includes the `[{requestId}]` prefix

- **Given** the requestId assignment is the very first statement in the handler
- **When** reading the handler code
- **Then** `const requestId = Date.now();` appears before any `if`, destructuring, or upstream call

**Manual Verification**:
1. `curl -X POST http://localhost:<port>/api/forgot-password -H "Content-Type: application/json" -d '{"email":"test@example.com"}'`
2. Grep: `docker logs <container> 2>&1 | grep FORGOT_PASSWORD`
3. Confirm: `[\d+] FORGOT_PASSWORD | Email: test@example.com | Brand: <brand>`
4. Send request with no email body; confirm `ERROR: Missing email` log line appears
5. Force catch path (point to unreachable Keycloak); confirm prefixed error log

**Implementation**:
1. Open `auth-gateway.js`, locate the `POST /api/forgot-password` handler (~line 931)
2. Add `const requestId = Date.now();` as the very first statement in the handler body (before any destructuring of `req.body`)
3. After the requestId line, add: `console.log(\`[\${requestId}] FORGOT_PASSWORD | Email: \${email} | Brand: \${brandName}\`);`
4. Find the missing-email early-return branch; before `return res.status(400)`, add: `console.log(\`[\${requestId}] ERROR: Missing email\`);`
5. Find the success path (after `userId` is available); add: `console.log(\`[\${requestId}] FORGOT_PASSWORD SUCCESS | UserId: \${userId}\`);`
6. In the catch block, prepend `[${requestId}] ` to the existing error log message string


## User Story: US-002 - Structured Logging for Verify Endpoint

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 1 total, 1 completed

### T-003: Add requestId and start/error logging to verify handler

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed
**File**: `repositories/mckissocklp/Colibri.Identity.Keycloak/auth-gateway.js` (~line 1159)

**Test Plan**:
- **Given** the verify handler is modified and the gateway is running
- **When** `POST /api/verify` is called with a token in the request body
- **Then** the console shows `[{timestamp}] VERIFY REQUEST | Source: body`

- **Given** `POST /api/verify` is called with a token only in the `Authorization` header (no body token)
- **When** the handler reads from the header
- **Then** the console shows `[{timestamp}] VERIFY REQUEST | Source: header`

- **Given** neither body nor Authorization header contains a token
- **When** validation fails before any decode attempt
- **Then** the console shows `[{timestamp}] ERROR: Missing token`

- **Given** a token is present but decoding reveals no `iss` field in the payload
- **When** the invalid-format branch executes
- **Then** the console shows `[{timestamp}] ERROR: Invalid token format`

**Manual Verification**:
1. `curl -X POST http://localhost:<port>/api/verify -d '{"token":"<jwt>"}' -H "Content-Type: application/json"`
2. Grep: `docker logs <container> 2>&1 | grep "VERIFY REQUEST"`
3. Confirm: `[\d+] VERIFY REQUEST | Source: body`
4. Send with Authorization header only; confirm `Source: header`
5. Send with no token; confirm `ERROR: Missing token`
6. Send with malformed JWT (no `iss` in payload); confirm `ERROR: Invalid token format`

**Implementation**:
1. Open `auth-gateway.js`, locate the `POST /api/verify` handler (~line 1159)
2. Add `const requestId = Date.now();` as the first statement in the handler body
3. Identify where the code decides token source; set a local variable `const tokenSource = req.body.token ? 'body' : 'header';` (adjust to match existing conditional logic); then add: `console.log(\`[\${requestId}] VERIFY REQUEST | Source: \${tokenSource}\`);`
4. Find the missing-token early-return branch; before `return res.status(400)`, add: `console.log(\`[\${requestId}] ERROR: Missing token\`);`
5. Find the invalid-format branch (where `iss` is checked on decoded payload); add: `console.log(\`[\${requestId}] ERROR: Invalid token format\`);`


## User Story: US-005 - Structured Global Error Handler

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Tasks**: 1 total, 1 completed

### T-004: Replace unstructured global error handler log with structured output

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [x] completed
**File**: `repositories/mckissocklp/Colibri.Identity.Keycloak/auth-gateway.js` (~line 1597)

**Test Plan**:
- **Given** the global error handler is updated and the gateway is running
- **When** an unhandled error propagates to the Express error handler
- **Then** the console (stderr) shows `GLOBAL_ERROR | Method: POST | Path: /api/some-path | Status: 500 | Error: <error message>`

- **Given** the structured summary line is emitted
- **When** checking the immediately following log entry
- **Then** the full error object (with stack trace) is also logged via `console.error(err)` on a separate line

- **Given** both log lines are emitted
- **When** checking which console method is used for each
- **Then** both use `console.error` (not `console.log`)

- **Given** the original `console.error('Global error handler:', err)` was the sole log call
- **When** the replacement is in place
- **Then** that original single-argument call is removed and replaced by the two new structured calls

**Manual Verification**:
1. Temporarily add a test route: `app.get('/api/test-error', () => { throw new Error('test forced error'); });` (remove after testing)
2. `curl http://localhost:<port>/api/test-error`
3. Grep: `docker logs <container> 2>&1 | grep GLOBAL_ERROR`
4. Confirm first line: `GLOBAL_ERROR | Method: GET | Path: /api/test-error | Status: 500 | Error: test forced error`
5. Confirm second line shows full error object with stack trace
6. Confirm both appear on stderr (not stdout)
7. Remove the temporary test route

**Implementation**:
1. Open `auth-gateway.js`, locate the global error handler function (~line 1597); it has the four-argument signature `(err, req, res, next)`
2. Confirm `status` variable is in scope (typically `const status = err.status || 500;`); add it if absent
3. Find the existing `console.error('Global error handler:', err)` call
4. Replace that single call with two lines:
   ```js
   console.error(`GLOBAL_ERROR | Method: ${req.method} | Path: ${req.path} | Status: ${status} | Error: ${err.message}`);
   console.error(err);
   ```


## User Story: US-004 - Brand Resolver Middleware Logging

**Linked ACs**: AC-US4-01, AC-US4-02
**Tasks**: 1 total, 1 completed

### T-005: Add fallback-path logging to brand resolver middleware

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed
**File**: `repositories/mckissocklp/Colibri.Identity.Keycloak/middleware/brand-resolver.js`

**Test Plan**:
- **Given** the brand resolver is updated and the gateway is running
- **When** a request arrives whose `Host` header does not match any configured brand and has no matching `brandId` param
- **Then** the console shows `BRAND_RESOLVER FALLBACK | Host: <host-value> | BrandId: <brandId-value> | Default: <defaultBrand>`

- **Given** a request arrives with a `Host` header that matches a configured brand directly
- **When** the brand resolves successfully (happy path)
- **Then** no `BRAND_RESOLVER` log line is emitted

- **Given** a request has no Host header and no brandId param
- **When** the fallback executes with undefined/empty values
- **Then** the log line still emits with empty or `undefined` for those fields (no crash)

**Manual Verification**:
1. Identify the default brand name from brand-resolver.js config or constants
2. Send a request with an unknown host: `curl -H "Host: unknown.example.com" http://localhost:<port>/api/verify -X POST -d '{}'`
3. Grep: `docker logs <container> 2>&1 | grep BRAND_RESOLVER`
4. Confirm: `BRAND_RESOLVER FALLBACK | Host: unknown.example.com | BrandId: undefined | Default: <defaultBrand>`
5. Send a request with a known brand host; confirm NO `BRAND_RESOLVER` line appears in logs
6. Send a request with no Host header; confirm fallback log emits without error

**Implementation**:
1. Open `middleware/brand-resolver.js`
2. Read the existing resolution logic to identify the variable names for: the request host (`host`), any brand identifier from query/body (`brandId`), the resolved brand before default fallback, and the default brand constant
3. Locate the point where `resolvedBrand` (or equivalent) is null/undefined and the code is about to assign the default
4. Immediately before the default-brand assignment, add:
   ```js
   console.log(`BRAND_RESOLVER FALLBACK | Host: ${host} | BrandId: ${brandId} | Default: ${defaultBrand}`);
   ```
5. Adjust variable names to match what the file actually uses
6. Do NOT add any log line on the happy path (where brand resolves without fallback)
