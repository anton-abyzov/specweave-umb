---
increment: 0836-skill-studio-hardening-pass
title: "Skill Studio Hardening Pass — 6 P0 Security Findings"
test_mode: TDD
coverage_target: 90
---

# Tasks: Skill Studio Hardening Pass

> **TDD enforcement**: Every task follows RED → GREEN → REFACTOR.
> Write the failing test first, confirm it fails, implement to pass, refactor.
> Mark `[x]` only after tests pass.
>
> **Project root**: `repositories/anton-abyzov/vskill/`

---

## US-001: Loopback-only eval-server bind

### T-001: Write failing bind test (RED)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04 | **Status**: [x]
**Test Plan**:
  Given a freshly started eval-server on port 0
  When the server address is inspected via `server.address()`
  Then `address.address` equals `'127.0.0.1'` and NOT `'0.0.0.0'` or `'::'`
  And a TCP connect attempt from a non-loopback host IP returns ECONNREFUSED
**Files**: `src/eval-server/__tests__/eval-server-bind.test.ts`
**AC**: AC-US1-01, AC-US1-02, AC-US1-04
**Effort**: ~30m

### T-002: Implement loopback bind + port-retry preservation (GREEN + REFACTOR)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x]
**Test Plan**:
  Given `server.listen(port)` (no host arg) is the current implementation
  When changed to `server.listen(port, '127.0.0.1', cb)`
  Then the bind test from T-001 passes
  And when EADDRINUSE fires during retry, the next attempt still uses '127.0.0.1'
  And the existing Studio-loads-in-WebView smoke test passes
**Files**: `src/eval-server/eval-server.ts`
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Effort**: ~30m

---

## US-002: X-Studio-Token gate replaces permissive localhost CORS

### T-003: Write failing token-gate tests (RED)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-08 | **Status**: [x]
**Test Plan**:
  Given router.ts with no X-Studio-Token gate yet
  When GET /api/health is called without X-Studio-Token header
  Then it returns 200 currently — this test will turn green only after T-005 makes it 401
  And a request with an incorrect same-length token returns 401
  And a request with correct token returns 200
  And OPTIONS preflight returns 204 regardless of token presence
  And GET /index.html (static) returns 200 regardless of token
  And a token with wrong length returns 401 without calling timingSafeEqual
**Files**: `src/eval-server/__tests__/router.test.ts`
**AC**: AC-US2-01, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-08
**Effort**: ~1h

### T-004: Implement getStudioToken() helper + startup banner in eval-server (GREEN)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-07, AC-US2-08 | **Status**: [x]
**Test Plan**:
  Given eval-server.ts has no token generation
  When `getStudioToken()` is added using `crypto.randomBytes(32).toString('base64url')`
  Then the returned value is 43 characters and base64url-safe
  And two calls in the same process return the same value
  And after `_resetStudioTokenForTests()`, the next call returns a different value
  And the CLI startup path (non-Tauri) prints `Studio token: <token>` to stdout after the port banner
  And the Tauri desktop path does NOT print the token to stdout
**Files**: `src/eval-server/eval-server.ts`
**AC**: AC-US2-01, AC-US2-07, AC-US2-08
**Effort**: ~45m

### T-005: Implement tokenGate middleware; delete LOCALHOST_ORIGIN_RE (GREEN + REFACTOR)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06 | **Status**: [x]
**Test Plan**:
  Given router.ts still contains LOCALHOST_ORIGIN_RE
  When `LOCALHOST_ORIGIN_RE` is deleted and `tokenGate(req, res)` is added to `Router.handle()`
  Then GET /api/* without X-Studio-Token → 401 with empty body
  And GET /api/* with correct X-Studio-Token → proxied response (200 or upstream code)
  And OPTIONS → 204 (gate bypassed)
  And static file paths → 200 (gate bypassed)
  And token length mismatch returns 401 without invoking `timingSafeEqual`
  And a 401 log line never contains the value of the supplied (wrong) token
  And all router tests from T-003 pass
**Files**: `src/eval-server/router.ts`
**AC**: AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06
**Effort**: ~2h

### T-006: Add Rust get_studio_token IPC (sidecar stdout capture + command registration)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x]
**Test Plan**:
  Given sidecar.rs pipes sidecar stdout but does not parse token lines
  When the stdout parser scans for `Studio token: <token>` and stashes the value in `SharedSidecar.studio_token: Option<String>`
  Then `get_studio_token` IPC returns `Some(token)` after sidecar has emitted the banner
  And returns `None` if called before the banner line arrives
  And the IPC is registered in `tauri::generate_handler!`
  And the token is not reachable via any public HTTP endpoint
**Files**: `src-tauri/src/sidecar.rs`, `src-tauri/src/commands.rs`, `src-tauri/src/lib.rs`
**AC**: AC-US2-02
**Effort**: ~1.5h

### T-007: Patch WebView fetch to inject X-Studio-Token header
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-05 | **Status**: [x]
**Test Plan**:
  Given useDesktopBridge.ts does not inject X-Studio-Token
  When the global `fetch` is patched inside an `if (isTauri())` guard
  Then any fetch to `/api/` or `window.location.origin + '/api/'` includes `X-Studio-Token: <token>`
  And non-Tauri (web platform build) fetch is unchanged
  And the token is fetched once via `invoke('get_studio_token')` and cached for the process lifetime
**Files**: `src/eval-ui/src/desktop/useDesktopBridge.ts`
**AC**: AC-US2-02, AC-US2-05
**Effort**: ~1h

---

## US-003: Remove account_get_token IPC; replace with account_get_user_summary

### T-008: Write failing tests for account_get_user_summary (RED)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-06 | **Status**: [x]
**Test Plan**:
  Given account/commands.rs has no `account_get_user_summary`
  When tests are written for: (a) signed-out returns defaults, (b) signed-in returns identity fields, (c) compile-guard that `account_get_token` symbol is absent
  Then tests (a) and (b) fail with "symbol not found" and test (c) passes now (it will invert after T-009)
**Files**: `src-tauri/src/account/tests.rs`
**AC**: AC-US3-01, AC-US3-02, AC-US3-06
**Effort**: ~45m

### T-009: Add account_get_user_summary; delete account_get_token (GREEN)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04, AC-US3-06 | **Status**: [x]
**Test Plan**:
  Given `account_get_token` exists in commands.rs and is registered in lib.rs
  When `account_get_token` function + handler registration are deleted
  And `AccountUserSummary` struct and `account_get_user_summary` fn are added
  Then signed-out returns `{signedIn:false, login:null, avatarUrl:null, tier:"free"}`
  And signed-in returns `{signedIn:true, login, avatarUrl, tier}` from identity cache (no keychain read)
  And `git grep -n "account_get_token" -- src-tauri/src/` returns zero matches
  And Rust tests from T-008 all pass
**Files**: `src-tauri/src/account/commands.rs`, `src-tauri/src/account/mod.rs`, `src-tauri/src/lib.rs`
**AC**: AC-US3-01, AC-US3-02, AC-US3-04, AC-US3-06
**Effort**: ~1.5h

### T-010: Migrate WebView callers from account_get_token to proxy paths
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04 | **Status**: [x]
**Test Plan**:
  Given AccountContext.tsx (or similar) calls account_get_token or reads gho_* bearer directly
  When callers are updated: display data from account_get_user_summary, HTTP via relative /api/v1/* proxy paths
  Then `git grep -n "account_get_token" -- src/` returns zero matches
  And no WebView source file contains a `gho_` literal or stores a bearer string
  And the WebView still shows correct login/avatar/tier after sign-in
**Files**: `src/eval-ui/src/account/AccountContext.tsx` (and any other WebView callers found by grep)
**AC**: AC-US3-03, AC-US3-04
**Effort**: ~1.5h

### T-011: Playwright E2E — assert gho_* absent from WebView DOM
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05 | **Status**: [x]
**Test Plan**:
  Given the app launches with a seeded fake PAT
  When the user is signed in and navigates between Studio tabs
  Then `page.evaluate(() => document.documentElement.outerHTML.match(/gho_[A-Za-z0-9]+/))` returns null
  And `page.evaluate(() => JSON.stringify(Object.entries(window))).match(/gho_[A-Za-z0-9]+/)` returns null
  And the assertion holds after each tab navigation
**Files**: `tests/e2e/webview-no-token-leak.spec.ts`
**AC**: AC-US3-05
**Effort**: ~1h

---

## US-004: Build-time client_id assertion

### T-012: Update build.rs + CI workflow with placeholder assertion and grep step
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-06 | **Status**: [x]
**Test Plan**:
  Given build.rs has no GITHUB_OAUTH_CLIENT_ID check
  When `cargo:rerun-if-env-changed=GITHUB_OAUTH_CLIENT_ID` is added
  And a `PROFILE == "release"` block panics when the env is unset or equals the placeholder
  Then `cargo build --release` without GITHUB_OAUTH_CLIENT_ID fails with the actionable message
  And `GITHUB_OAUTH_CLIENT_ID=Iv1.placeholder-replace-before-ship cargo build --release` fails
  And `cargo build` (debug, no env) succeeds
  And the CI workflow `desktop-release.yml` has a `Verify no placeholder client_id in release binary` step that runs `strings <binary> | grep -q 'Iv1.placeholder-replace-before-ship'` and exits 1 on match
**Files**: `src-tauri/build.rs`, `.github/workflows/desktop-release.yml`
**AC**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-06
**Effort**: ~1h

### T-013: Document GITHUB_OAUTH_CLIENT_ID + write OAuth client_id rotation runbook
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04, AC-US4-05 | **Status**: [x]
**Test Plan**:
  Given README.md does not mention GITHUB_OAUTH_CLIENT_ID
  When a section is added with: what the env var is, where to set it in CI secrets, what happens on missing value
  Then README.md contains GITHUB_OAUTH_CLIENT_ID with CI instruction
  And a runbook at `.specweave/docs/internal/specs/oauth-client-id-rotation.md` covers: register new OAuth App, update CI secret, verify build passes, retire old App
**Files**: `repositories/anton-abyzov/vskill/README.md`, `.specweave/docs/internal/specs/oauth-client-id-rotation.md`
**AC**: AC-US4-04, AC-US4-05
**Effort**: ~30m

---

## US-005: Token revocation on sign-out

### T-014: Write failing revocation tests with mockito (RED)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05, AC-US5-06 | **Status**: [x]
**Test Plan**:
  Given no `grant_revoke.rs` module exists
  When tests are written (in a `#[cfg(test)]` block at file bottom) for:
    (a) mockito returns 200 → outcome is `Revoked`
    (b) mockito returns 401 → outcome is `AlreadyInvalid`
    (c) mockito returns 500 → outcome is `Failed("http 500")`
    (d) mockito delays 6s → outcome is `Failed("timeout")`
    (e) sign_out with revocation failure still clears keychain (TokenStore::load() == None)
    (f) no gho_* token value appears in any log line during revocation
  Then all tests fail (module missing)
**Files**: `src-tauri/src/auth/grant_revoke.rs`
**AC**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05, AC-US5-06
**Effort**: ~1.5h

### T-015: Implement grant_revoke.rs + async sign_out with 5s-budget revocation (GREEN + REFACTOR)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05, AC-US5-06, AC-US5-07 | **Status**: [x]
**Test Plan**:
  Given sign_out only clears the keychain locally
  When `grant_revoke.rs` is created with `revoke_grant(token: &str, platform_url: Option<&str>) -> RevocationOutcome`
  And the platform URL is `https://verified-skill.com/api/v1/auth/github/grant` (DELETE, Bearer auth)
  And reqwest client has a 5s timeout
  And sign_out becomes async: read token → tokio::spawn revoke → ALWAYS clear keychain + identity cache
  And token is wrapped in `Zeroizing<String>` and never written to logs
  And `auth/mod.rs` exports `revoke_grant` and `RevocationOutcome`
  Then all mockito tests from T-014 pass
  And sign_out returns Ok(()) regardless of revocation outcome
**Files**: `src-tauri/src/auth/grant_revoke.rs`, `src-tauri/src/auth/mod.rs`, `src-tauri/src/commands.rs`
**AC**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05, AC-US5-06, AC-US5-07
**Effort**: ~3h

---

## US-006: Canonical keychain service consolidation

### T-016: Write failing keychain migration tests + Rust SERVICE_NAME lock test (RED)
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-07, AC-US6-08 | **Status**: [x]
**Test Plan**:
  Given no `keychain-migration.ts` module exists
  When 6 migration tests are written with injectable `{keyring, fs, now}` deps:
    (a) old slot only → token moved to canonical, old deleted, returns 'migrated'
    (b) both slots populated → canonical wins, old deleted, returns 'migrated'
    (c) both empty → no-op, done flag written, returns 'noop'
    (d) lock held by another process within TTL → second runner returns 'skipped'
    (e) stale lock (>5s) → stolen, migration runs
    (f) VSKILL_KEYCHAIN_MIGRATE=0 → returns 'skipped' immediately
  And a Rust `#[test] fn service_name_is_canonical_for_node_interop` is written in token_store.rs asserting SERVICE_NAME == "com.verifiedskill.desktop"
  Then all Node migration tests fail (module missing); Rust test passes (constant already correct)
**Files**: `src/lib/__tests__/keychain.test.ts`, `src-tauri/src/auth/token_store.rs`
**AC**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-07, AC-US6-08
**Effort**: ~1h

### T-017: Implement keychain-migration.ts + update keychain.ts constants (GREEN + REFACTOR)
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05, AC-US6-06, AC-US6-07, AC-US6-08 | **Status**: [x]
**Test Plan**:
  Given keychain.ts uses SERVICE_NAME='vskill-github' and key='github_token'
  When constants are updated to SERVICE_NAME='com.verifiedskill.desktop' and GITHUB_TOKEN_KEY='github-oauth-token'
  And `keychain-migration.ts` is created with: file-mutex at `~/.vskill/locks/keychain-migration.lock` (5s TTL), done-flag at `~/.vskill/keychain-migration.done`, read-old/write-canonical-if-empty/delete-old flow
  And migration is called once from `keychain.ts` on first `getGitHubToken()` via a per-process boolean gate
  And `VSKILL_KEYCHAIN_MIGRATE` env guard defaults on, with `// REMOVE AFTER vskill 1.1.x` comment
  And legacy fallback in `getGitHubToken` reads old slot if canonical empty, with `// TODO(0836-followup): remove` comment
  Then all 6 migration tests from T-016 pass
  And Rust SERVICE_NAME lock test still passes
  And existing keychain.test.ts assertions updated to use canonical service/key names
  And `vskill auth status` (CLI) shows same login as desktop sign-in on next invocation
**Files**: `src/lib/migration/keychain-migration.ts`, `src/lib/keychain.ts`, `src/lib/__tests__/keychain.test.ts`
**AC**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05, AC-US6-06, AC-US6-07, AC-US6-08
**Effort**: ~3h

---

## Final Verification

### T-018: Run full test suite + signed-build smoke + update CHANGELOG
**User Story**: US-001 through US-006 | **Satisfies ACs**: all | **Status**: [x]
**Test Plan**:
  Given all previous tasks are marked complete
  When `cargo test` runs in `src-tauri/`
  Then zero failures
  When `npx vitest run` runs in `repositories/anton-abyzov/vskill/`
  Then zero failures and ≥90% coverage on changed lines
  When `npx playwright test` runs
  Then webview-no-token-leak.spec.ts and all existing E2E specs pass
  When `cargo build --release` is attempted without GITHUB_OAUTH_CLIENT_ID
  Then build fails with the actionable panic message
  When `cargo build --release` runs with a real GITHUB_OAUTH_CLIENT_ID
  Then build succeeds and `strings <binary> | grep -q 'Iv1.placeholder-replace-before-ship'` exits 1 (string absent)
  And CHANGELOG.md has a Security section entry for vskill 1.0.18 covering all 6 P0 findings
**Files**: `CHANGELOG.md`
**AC**: AC-US1-01 through AC-US6-08 (regression sweep)
**Effort**: ~1h
