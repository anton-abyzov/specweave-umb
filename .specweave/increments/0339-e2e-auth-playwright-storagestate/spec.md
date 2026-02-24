# Spec — 0339 E2E Auth Playwright storageState

## User Stories

### US-001: Reusable authenticated Playwright session
As a developer, I want a Playwright storageState setup that captures GitHub OAuth cookies once (with manual 2FA) and reuses them for all authenticated E2E tests, so I don't need to re-login every test run.

**Acceptance Criteria:**
- [x] AC-US1-01: `auth.setup.ts` navigates to `/api/v1/auth/github`, pauses for manual login, saves cookies to `.auth/user.json`
- [x] AC-US1-02: Setup checks existing `.auth/user.json` validity (hits `/api/v1/auth/me`) before prompting login
- [x] AC-US1-03: `playwright.config.ts` has 3 projects: setup, chromium (unauthenticated), authenticated (depends on setup, uses storageState)
- [x] AC-US1-04: `.auth/` is in `.gitignore`
- [x] AC-US1-05: `npm run test:e2e:auth` script runs setup project in headed mode

### US-002: Authenticated E2E tests
As a developer, I want E2E tests that verify authenticated user flows so regressions are caught automatically.

**Acceptance Criteria:**
- [x] AC-US2-01: `auth-me.spec.ts` verifies `/api/v1/auth/me` returns user profile (id, githubUsername, avatarUrl, isAdmin)
- [x] AC-US2-02: `submit-page.spec.ts` verifies submit page shows authenticated form (not login prompt)
- [x] AC-US2-03: `user-preferences.spec.ts` verifies GET/PATCH `/api/v1/user/preferences`
- [x] AC-US2-04: `problem-reports.spec.ts` verifies GET `/api/v1/problem-reports/mine`
- [x] AC-US2-05: Existing unauthenticated E2E tests remain unchanged and passing
