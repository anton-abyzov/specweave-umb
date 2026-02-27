# 0345 — Auth Architecture Rework Tasks

### T-001: Enrich JWT payload with avatarUrl and isAdmin
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-03 | **Status**: [x] completed
**Test**: Given a user logs in via GitHub OAuth → When tokens are signed → Then JWT contains `avatarUrl` and `isAdmin` claims

- Update `UserTokenPayload` interface in `auth.ts`
- Update `signUserAccessToken()` and `signUserRefreshToken()` to accept/include new fields
- Update OAuth callback to pass `avatarUrl` + `isAdmin` to signing
- Export `getJwtSecret()` from `auth.ts`

### T-002: Create server-side auth helper
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given a valid JWT in cookies → When `getServerAuth()` is called in Server Component → Then returns user object without DB call

- Create `src/lib/server-auth.ts` with `getServerAuth()` function
- Uses `cookies()` from `next/headers` + `jwtVerify` from `jose`
- Returns `{ id, githubUsername, avatarUrl, isAdmin }` or `null`
- Graceful error handling (returns null on any failure)

### T-003: Root layout passes auth to AuthProvider
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given user visits any page → When layout renders → Then AuthProvider receives server-resolved user

- Make root layout `async`
- Call `getServerAuth()` and pass result as `initialUser` prop to AuthProvider

### T-004: AuthProvider accepts initialUser and adds silent refresh
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test**: Given server provides initialUser → When AuthProvider mounts → Then no `/me` fetch occurs AND auth state is immediately available

- Accept `initialUser` prop
- Skip `/me` fetch when `initialUser` is provided
- When `initialUser === null`, attempt silent refresh via `/api/v1/auth/user/refresh`
- If refresh succeeds, fetch `/me` to populate user

### T-005: Optimize /me endpoint for JWT-first response
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given enriched JWT → When GET /me → Then response from JWT claims only (no DB query)

- Check if JWT has `avatarUrl` field — if yes, return claims directly
- If missing (old token), fall back to DB lookup

### T-006: Refresh endpoint carries enriched claims
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test**: Given old token without avatarUrl → When refresh → Then new token includes avatarUrl from DB lookup

- Import shared `getJwtSecret()` from `auth.ts` (remove local duplicate)
- Extract `avatarUrl`/`isAdmin` from old token claims
- If missing, do one-time DB lookup to self-heal
- Pass enriched payload to new token signing

### T-007: Fix blocklist seeding race condition
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given two concurrent blocklist requests → When both hit empty table → Then no 500 errors

- Replace upsert loop with `createMany({ skipDuplicates: true })`
- Add KV seeding flag check before DB call
- Set flag after successful seed

### T-008: Consolidate auth UI
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed
**Test**: Given unauthenticated user → When viewing any page → Then sees consistent "Login with GitHub" with icon

- UserNav: show "Login with GitHub" with GitHub icon
- Submit page: remove "Checking authentication..." flash (use server auth)
- Handle null avatarUrl gracefully

### T-009: Run tests and build
**User Story**: ALL | **Satisfies ACs**: ALL | **Status**: [x] completed
**Test**: Given all changes → When `npm test` and `npm run build` → Then both pass

- Run test suite
- Fix any broken tests
- Verify build succeeds
