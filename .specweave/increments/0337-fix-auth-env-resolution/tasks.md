# Tasks

### T-001: Create resolveEnv() helper
**Status**: [x] completed
Create `src/lib/env-resolve.ts` with 3-tier CF env resolution.

### T-002: Update env.d.ts types
**Status**: [x] completed
Add JWT_SECRET and ADMIN_GITHUB_USERNAMES to CloudflareEnv interface.

### T-003: Fix auth.ts getJwtSecret() and isAdminUsername()
**Status**: [x] completed
Make async, use resolveEnv(), update all internal callers.

### T-004: Fix oauth-state.ts getSigningKey()
**Status**: [x] completed
Use resolveEnv() instead of process.env.JWT_SECRET.

### T-005: Fix refresh route duplicate getJwtSecret()
**Status**: [x] completed
Apply resolveEnv() fix inline or import from auth.ts.

### T-006: Update auth/me route for async isAdminUsername
**Status**: [x] completed
Add await to isAdminUsername() call.

### T-007: Update tests
**Status**: [x] completed
Mock env-resolve in auth, oauth-state tests. Add env-resolve tests.

### T-008: Build and deploy
**Status**: [x] completed
Run tests, build, deploy, verify production.
