# 0361 — Auth Hardening: Short-Lived Tokens + PKCE + Proactive Refresh

## Problem
Access tokens live 24 hours — too long. If leaked, attacker has a full day. OAuth flow lacks PKCE. Client only refreshes on page load, not proactively.

## Solution
Shorten access tokens to 15min with proactive silent refresh. Add PKCE to GitHub OAuth. Add global 401 retry interceptor.

## User Stories

### US-001: Short-Lived Access Tokens with Silent Refresh
**As a** user, **I want** my access tokens to expire quickly **so that** token theft has minimal impact.

- [ ] AC-US1-01: Access token lifetime is 15 minutes (was 24h)
- [ ] AC-US1-02: Access cookie maxAge is 900 seconds
- [ ] AC-US1-03: Non-HttpOnly `vskill_token_exp` cookie set with Unix timestamp of expiry
- [ ] AC-US1-04: `vskill_token_exp` cleared on logout

### US-002: Proactive Silent Refresh
**As a** user, **I want** my session to refresh seamlessly **so that** I never get logged out unexpectedly.

- [ ] AC-US2-01: AuthProvider schedules refresh 3min before token expiry
- [ ] AC-US2-02: Tab focus triggers expiry check and refresh if needed
- [ ] AC-US2-03: Concurrent refresh attempts are deduplicated via mutex
- [ ] AC-US2-04: Refresh response includes user data (eliminates /auth/me round-trip)

### US-003: PKCE for GitHub OAuth
**As a** security-conscious platform, **I want** PKCE on the OAuth flow **so that** authorization code interception is prevented.

- [ ] AC-US3-01: OAuth initiation generates code_verifier and code_challenge (S256)
- [ ] AC-US3-02: code_verifier stored in HttpOnly cookie (10min TTL)
- [ ] AC-US3-03: code_verifier passed to token exchange in callback
- [ ] AC-US3-04: PKCE cookie cleared after use
- [ ] AC-US3-05: Graceful fallback if PKCE cookie absent (backward compat)

### US-004: Global 401 Retry Interceptor
**As a** developer, **I want** a fetch wrapper that auto-retries on 401 **so that** expired tokens don't break API calls.

- [ ] AC-US4-01: `authFetch` retries once after successful refresh on 401
- [ ] AC-US4-02: Concurrent 401s deduplicate to single refresh request
- [ ] AC-US4-03: Non-401 responses pass through unchanged
- [ ] AC-US4-04: Authenticated client components migrated to use `authFetch`
