# Tasks — 0361 Auth Hardening

### T-001: Shorten access token lifetime
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given auth.ts → When USER_ACCESS_TOKEN_EXPIRY checked → Then equals '15m'
- Change `USER_ACCESS_TOKEN_EXPIRY` from `'24h'` to `'15m'` in `auth.ts`
- Change `ACCESS_MAX_AGE` from `86400` to `900` in `auth-cookies.ts`

### T-002: Add expiry metadata cookie
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test**: Given setAuthCookies called → When response inspected → Then vskill_token_exp cookie is non-HttpOnly with Unix timestamp
- Add `vskill_token_exp` cookie in `setAuthCookies` (non-HttpOnly, Secure, 900s maxAge)
- Clear it in `clearAuthCookies`
- Update `auth-cookies.test.ts`

### T-003: Add PKCE helpers
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test**: Given generateCodeVerifier → When called → Then returns 43-char base64url string; Given generateCodeChallenge → When called with verifier → Then returns SHA-256 base64url hash
- Add `generateCodeVerifier()` and `generateCodeChallenge()` to `oauth-state.ts`
- Add unit tests

### T-004: Wire PKCE into OAuth flow
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Test**: Given OAuth initiation → When redirect built → Then code_challenge param present; Given callback → When token exchanged → Then code_verifier sent
- Update `buildAuthorizationUrl` to accept `codeChallenge`
- Update `exchangeCodeForToken` to accept `codeVerifier`
- Update `/auth/github/route.ts` to generate PKCE pair + store verifier cookie
- Update `/auth/github/callback/route.ts` to read verifier + pass to exchange + clear cookie

### T-005: Refresh endpoint returns user data
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test**: Given POST /auth/user/refresh → When successful → Then response body contains user object
- Add `user` field to refresh response JSON

### T-006: Proactive silent refresh in AuthProvider
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given user authenticated → When 12min pass → Then refresh fires before expiry; Given tab re-focused → When token near expiry → Then refresh fires
- Rewrite `AuthProvider.tsx` with refresh timer + visibility handler
- Read `vskill_token_exp` cookie for scheduling
- Use refresh response body instead of separate /auth/me call

### T-007: Create authFetch interceptor
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed
**Test**: Given 401 response → When authFetch called → Then refreshes and retries once; Given 200 response → Then passes through
- Create `src/lib/auth-fetch.ts`
- Add unit tests

### T-008: Migrate components to authFetch
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04 | **Status**: [x] completed
**Test**: Given authenticated component → When API call made → Then uses authFetch
- Migrate: ThemeToggle, submit/page, report/page, report/my-reports/page, ReportProblemModal
- Skip: AuthProvider, UserNav logout, admin pages

### T-009: Tests pass + build + deploy
**User Story**: All | **Status**: [x] completed
**Test**: Given all changes → When vitest run → Then pass; When build → Then succeeds; When deployed → Then login works
