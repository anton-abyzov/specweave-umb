---
increment: 0814-studio-github-publish-phase0
title: "GitHub OAuth + Publish-to-GitHub in vskill studio (Phase 0)"
generated: 2026-04-30
source: auto-generated
version: "1.0"
status: pending
---

# Quality Contract — GitHub OAuth + Publish-to-GitHub in vskill studio (Phase 0)

## Functional Correctness (per AC)

### R-001: Device Flow start returns user_code without device_code [blocking]
- **Source**: AC-US1-01, AC-US1-04
- **Evaluator**: sw:grill
- **Verify**: `POST /api/github/auth/device-start` response contains `user_code`, `verification_uri`, `sessionId` but does NOT contain `device_code` in any field.
- **Threshold**: Response body scan finds no `device_code` key; `user_code` is 6 characters.
- **Result**: [ ] PENDING

### R-002: Device Flow modal shows correct UX elements [blocking]
- **Source**: AC-US1-02
- **Evaluator**: sw:grill
- **Verify**: `GitHubAuthModal` in Waiting state renders the 6-char code in monospace, an "Open github.com/login/device" button, a countdown timer, and a polling spinner.
- **Threshold**: All 4 UI elements present in rendered component; countdown starts from `expires_in` seconds.
- **Result**: [ ] PENDING

### R-003: Device Flow poll handles slow_down and expiry correctly [blocking]
- **Source**: AC-US1-03
- **Evaluator**: sw:grill
- **Verify**: `pollDeviceFlow` increases interval by 5 on `slow_down`; stops polling at device code expiry; does not poll more frequently than 5s.
- **Threshold**: Vitest unit tests for all three behaviors pass.
- **Result**: [ ] PENDING

### R-004: Access token never reaches the browser [blocking]
- **Source**: AC-US1-04, AC-US1-08
- **Evaluator**: sw:grill
- **Verify**: No `/api/github/*` response body or header contains the GitHub access token. Browser receives only `{login, avatar, expiresAt}`. Playwright network intercept test asserts this.
- **Threshold**: E2E network intercept scan of all `/api/github/*` responses finds zero token matches.
- **Result**: [ ] PENDING

### R-005: Auth state survives page reload [blocking]
- **Source**: AC-US1-05, AC-US6-05
- **Evaluator**: sw:grill
- **Verify**: After sign-in, a browser page reload fetches `GET /api/github/auth/me` and rehydrates the top bar with avatar/login without a flash of the signed-out state.
- **Threshold**: E2E test asserts avatar is visible within 500ms of page load without a prior signed-out button flash.
- **Result**: [ ] PENDING

### R-006: Cancel aborts poller and writes nothing to settings-store [blocking]
- **Source**: AC-US1-06
- **Evaluator**: sw:grill
- **Verify**: Clicking cancel during Device Flow `Waiting` state stops all polling and leaves settings-store with no `github` entry.
- **Threshold**: After cancel, `GET /api/github/auth/me` returns `{signedIn:false}`.
- **Result**: [ ] PENDING

### R-007: Denied auth shows error state with Try Again [blocking]
- **Source**: AC-US1-07
- **Evaluator**: sw:grill
- **Verify**: When poll returns `{status:"denied"}`, modal shows error state with a "Try again" button that resets to Idle.
- **Threshold**: Vitest + component test asserts error state render and button presence.
- **Result**: [ ] PENDING

### R-008: CSRF/loopback guard rejects cross-origin requests [blocking]
- **Source**: AC-US1-08
- **Evaluator**: sw:grill
- **Verify**: All `/api/github/*` routes return 403 for requests with non-loopback `Origin` headers or non-loopback `remoteAddress`. Pattern mirrors `git-routes.ts:91-108`.
- **Threshold**: Integration test covering all 7 routes; each returns 403 on cross-origin probe.
- **Result**: [ ] PENDING

### R-009: PAT modal toggle and UI availability [blocking]
- **Source**: AC-US2-01, AC-US2-05
- **Evaluator**: sw:grill
- **Verify**: "Use a Personal Access Token instead" link toggles PAT form. When `isDeviceFlowEnabled()` is false, PAT form is the primary view. PAT path is always available regardless of `VSKILL_GITHUB_CLIENT_ID`.
- **Threshold**: Component renders PAT input when Device Flow disabled; toggle works when enabled.
- **Result**: [ ] PENDING

### R-010: PAT validation calls correct endpoint and validates scopes [blocking]
- **Source**: AC-US2-02, AC-US2-03
- **Evaluator**: sw:grill
- **Verify**: `POST /api/github/auth/pat` calls `GET /user` with the token, reads `X-OAuth-Scopes`, rejects with `{error:"missing_scopes", required:["repo"]}` if `repo` is absent.
- **Threshold**: Vitest tests for valid-scopes, missing-repo-scope, and human-readable UI error message all pass.
- **Result**: [ ] PENDING

### R-011: PAT persisted with same shape as Device Flow token [blocking]
- **Source**: AC-US2-04
- **Evaluator**: sw:grill
- **Verify**: On valid PAT, `settings-store.readJsonKey("github")` returns a record with `source:"pat"` and all standard fields. Subsequent publish flows are indistinguishable from Device-Flow tokens.
- **Threshold**: Vitest round-trip test passes; publish integration test works with a PAT-sourced token.
- **Result**: [ ] PENDING

### R-012: PAT input uses type="password" and token never logged [blocking]
- **Source**: AC-US2-06
- **Evaluator**: sw:grill
- **Verify**: PAT textarea has `type="password"`. Redacting logger test snapshot asserts the token byte sequence is absent from all log output.
- **Threshold**: Vitest snapshot test passes; DOM check confirms `type="password"`.
- **Result**: [ ] PENDING

### R-013: "Publish to GitHub" tab added to PublishDrawer [blocking]
- **Source**: AC-US3-01
- **Evaluator**: sw:grill
- **Verify**: `PublishDrawer` renders two tabs — "Commit & Push" (default) and "Publish to GitHub". Existing tab behavior is byte-for-byte unchanged.
- **Threshold**: Pre-existing Vitest + Playwright suite passes with zero modifications; new tab renders `GitHubPublishPanel`.
- **Result**: [ ] PENDING

### R-014: New-repo form prefills from skill metadata [blocking]
- **Source**: AC-US3-02
- **Evaluator**: sw:grill
- **Verify**: Repo name input prefills from skill folder name; description defaults from `SKILL.md` description frontmatter; visibility toggle defaults to public.
- **Threshold**: Component test asserts all three prefills with a fixture skill.
- **Result**: [ ] PENDING

### R-015: Publish creates repo, uploads files, sets topics in correct order [blocking]
- **Source**: AC-US3-03
- **Evaluator**: sw:grill
- **Verify**: `POST /api/github/publish` mode="create" runs: `POST /user/repos` → `PUT /repos/.../contents/...` per file (sequential) → `PATCH /repos/.../topics` with `["claude-skill","claude-code-skill"]`.
- **Threshold**: Integration test captures Octokit calls in correct order; topics include both required values.
- **Result**: [ ] PENDING

### R-016: Per-file progress indicator shown during upload [blocking]
- **Source**: AC-US3-04
- **Evaluator**: sw:grill
- **Verify**: UI shows `N/total filename` progress during upload. Octokit throttling pauses surface "rate limited, retrying in Ns" message rather than silent hang.
- **Threshold**: E2E test asserts progress indicator fires for each file; unit test asserts throttle message appears on `onRateLimit` callback.
- **Result**: [ ] PENDING

### R-017: Success panel shows repo URL and CTA buttons [blocking]
- **Source**: AC-US3-05
- **Evaluator**: sw:grill
- **Verify**: On success, panel shows the repo URL as a clickable link, "Open on GitHub" button, and "Submit to verified-skill.com" button.
- **Threshold**: E2E test and component test both assert all three elements present after publish.
- **Result**: [ ] PENDING

### R-018: Name-taken 422 handled with inline suggestion [blocking]
- **Source**: AC-US3-06
- **Evaluator**: sw:grill
- **Verify**: When `POST /user/repos` returns 422, UI shows "name taken" inline next to the field with an auto-suggested variant the user can accept in one click. No partial state is persisted.
- **Threshold**: Component test asserts inline error and suggestion button; integration test asserts `{error:"NAME_TAKEN", suggested:"<name>-2"}` response shape.
- **Result**: [ ] PENDING

### R-019: No `child_process` / `spawn` / `exec` in github-publish.ts [blocking]
- **Source**: AC-US3-07
- **Evaluator**: sw:grill
- **Verify**: Static import analysis of `github-publish.ts` finds no `child_process`, `spawn`, or `exec` references. Existing `git-routes.ts:291` shell-out flow is untouched.
- **Threshold**: Vitest assertion test passes; `grep -r "child_process\|spawn\|exec" github-publish.ts` returns empty.
- **Result**: [ ] PENDING

### R-020: Binary files round-trip byte-for-byte [blocking]
- **Source**: AC-US3-08
- **Evaluator**: sw:grill
- **Verify**: A fixture PNG uploaded via Contents API base64 encoding, then base64-decoded from the captured request body, matches the original bytes exactly.
- **Threshold**: Integration test with fixture PNG passes byte equality assertion.
- **Result**: [ ] PENDING

### R-021: Update mode auto-detects existing remote [blocking]
- **Source**: AC-US4-01
- **Evaluator**: sw:grill
- **Verify**: When skill folder has an existing GitHub remote or prior publish record, `GitHubPublishPanel` defaults to update-existing mode showing the repo `owner/name`.
- **Threshold**: Component test with a mocked prior-publish state asserts update mode is active.
- **Result**: [ ] PENDING

### R-022: Update mode shows repo picker for manual selection [blocking]
- **Source**: AC-US4-02
- **Evaluator**: sw:grill
- **Verify**: Update mode populates a repo picker from `GET /api/github/repos?topic=claude-skill&match=<skillName>` as fallback when auto-detection misses.
- **Threshold**: Integration test asserts the repos endpoint filters by both topic and skill name.
- **Result**: [ ] PENDING

### R-023: Update uses GET-then-PUT with SHA; skips identical content [blocking]
- **Source**: AC-US4-03
- **Evaluator**: sw:grill
- **Verify**: Each file in update mode does a GET for current SHA before PUT. Files with identical content are skipped (no PUT issued, counted as `skipped`).
- **Threshold**: Vitest tests for no-change-skip, existing-file-update, and new-file-no-sha all pass.
- **Result**: [ ] PENDING

### R-024: Commit message field applies to all file PUTs [blocking]
- **Source**: AC-US4-04
- **Evaluator**: sw:grill
- **Verify**: Single commit message field in the UI; every `PUT /repos/.../contents/...` request body contains the exact message value.
- **Threshold**: Integration test captures all PUT bodies and asserts message field matches.
- **Result**: [ ] PENDING

### R-025: 409 SHA mismatch retried once; second 409 surfaces error [blocking]
- **Source**: AC-US4-05
- **Evaluator**: sw:grill
- **Verify**: On 409, a fresh GET is issued and PUT retried. On second 409, error `{code:"CONFLICT", path}` is surfaced to the UI.
- **Threshold**: Vitest test for conflict retry and double-conflict paths both pass.
- **Result**: [ ] PENDING

### R-026: Resume publish after network drop [blocking]
- **Source**: AC-US4-06
- **Evaluator**: sw:grill
- **Verify**: After a simulated network drop mid-publish, "Resume publish" button re-diffs local vs remote and uploads only files not yet committed.
- **Threshold**: Component test with 2-of-5 partial upload state asserts exactly 3 PUTs on resume.
- **Result**: [ ] PENDING

### R-027: US-004 integration test scenarios all pass [blocking]
- **Source**: AC-US4-07
- **Evaluator**: sw:grill
- **Verify**: All four Vitest scenarios pass: (a) update with no remote changes, (b) one conflicted file, (c) new file + modified file, (d) resume after network drop.
- **Threshold**: `npx vitest run` exits 0 with all four scenarios green.
- **Result**: [ ] PENDING

### R-028: "Submit to verified-skill.com" button present after publish [blocking]
- **Source**: AC-US5-01
- **Evaluator**: sw:grill
- **Verify**: After both create and update publish success, the success panel renders the "Submit to verified-skill.com" button.
- **Threshold**: E2E and component tests assert button is present after both modes.
- **Result**: [ ] PENDING

### R-029: CTA opens correct URL with pre-filled params [blocking]
- **Source**: AC-US5-02, AC-US5-04
- **Evaluator**: sw:grill
- **Verify**: Clicking "Submit to verified-skill.com" calls `window.open("https://verified-skill.com/submit?repoUrl=<encoded>&skillPath=<encoded>")`. If `skillPath` is absent from the publish response, the param is omitted entirely.
- **Threshold**: Component test inspects the `window.open` call; both with and without `skillPath` cases pass.
- **Result**: [ ] PENDING

### R-030: URL params are correctly URI-encoded for special characters [blocking]
- **Source**: AC-US5-03
- **Evaluator**: sw:grill
- **Verify**: Repo names with hyphens, spaces, and other special characters are correctly URI-encoded in the `submitUrl`. Vitest unit test for special-char round-trip passes.
- **Threshold**: `encodeURIComponent` used; test with `owner/repo with-dashes` produces clean URL.
- **Result**: [ ] PENDING

### R-031: Skipping verified-skill.com CTA has no effect on publish state [blocking]
- **Source**: AC-US5-05
- **Evaluator**: sw:grill
- **Verify**: Not clicking "Submit to verified-skill.com" does not change the publish state, skill files, or any stored metadata.
- **Threshold**: Component test asserts no state mutations occur when the CTA is never clicked.
- **Result**: [ ] PENDING

### R-032: Top bar shows avatar when signed in, sign-in button when not [blocking]
- **Source**: AC-US6-01
- **Evaluator**: sw:grill
- **Verify**: Top bar conditionally renders based on `GET /api/github/auth/me` result. Avatar + login shown when `signedIn:true`; "Sign in with GitHub" button shown when `signedIn:false`.
- **Threshold**: Component tests for both states pass; E2E test asserts avatar appears after sign-in.
- **Result**: [ ] PENDING

### R-033: Avatar dropdown shows login, auth source, and sign-out [blocking]
- **Source**: AC-US6-02
- **Evaluator**: sw:grill
- **Verify**: Clicking avatar opens dropdown with: login, auth source label (`Device Flow` or `Personal Access Token`), and "Sign out" item.
- **Threshold**: Component test asserts all three dropdown items present for both auth source values.
- **Result**: [ ] PENDING

### R-034: Sign-out removes token, revokes if possible, reverts UI [blocking]
- **Source**: AC-US6-03
- **Evaluator**: sw:grill
- **Verify**: "Sign out" calls `POST /api/github/auth/logout` which deletes the `github` settings-store entry, best-effort calls token revocation, returns 204. UI immediately reverts to signed-out state.
- **Threshold**: Integration test asserts storage cleared; E2E test asserts top bar reverts. Revocation failure is logged but not surfaced as UI error.
- **Result**: [ ] PENDING

### R-035: 401 mid-session shows re-auth modal without losing publish state [blocking]
- **Source**: AC-US6-04
- **Evaluator**: sw:grill
- **Verify**: If a publish call returns 401, a "session expired" modal appears, the pending publish is paused (state preserved in component), and the top bar reverts to signed-out.
- **Threshold**: Component test with mocked 401 mid-publish asserts modal presence and preserved form state.
- **Result**: [ ] PENDING

---

## Infrastructure Criteria

### R-036: Line coverage ≥ 90% on new server files [blocking]
- **Source**: plan.md §8 coverage targets
- **Evaluator**: sw:grill
- **Verify**: `npx vitest run --coverage` reports ≥ 90% line coverage on `github-oauth.ts`, `github-publish.ts`, and `github-routes.ts`.
- **Threshold**: Coverage report shows ≥ 90% for all three files.
- **Result**: [ ] PENDING

### R-037: E2E spec passes in CI [blocking]
- **Source**: spec.md Success Metrics
- **Evaluator**: sw:grill
- **Verify**: `npx playwright test e2e/github-publish.spec.ts` boots Studio, mocks Device Flow + GitHub REST, and asserts repo creation + file upload calls; exits 0.
- **Threshold**: Playwright exits 0; all test steps pass.
- **Result**: [ ] PENDING

### R-038: Existing "Commit & Push" test suite unaffected [blocking]
- **Source**: spec.md Success Metrics ("Existing git push flow unaffected")
- **Evaluator**: sw:grill
- **Verify**: All pre-existing Vitest and Playwright tests for `PublishDrawer.tsx` and `git-routes.ts` pass without modification after the increment lands.
- **Threshold**: `npx vitest run` and `npx playwright test` exit 0 with zero pre-existing test failures.
- **Result**: [ ] PENDING

### R-039: Octokit does not appear in browser bundle [blocking]
- **Source**: plan.md §4.2
- **Evaluator**: sw:grill
- **Verify**: `@octokit/rest` and `@octokit/plugin-throttling` are server-side only. The eval-ui browser bundle does not include any Octokit code.
- **Threshold**: Bundle manifest / chunk analysis shows no Octokit imports in browser chunks.
- **Result**: [ ] PENDING

### R-040: Token storage uses POSIX 0600 permissions and base64 encoding [blocking]
- **Source**: AC-US1-04, ADR 0814-02
- **Evaluator**: sw:grill
- **Verify**: `~/.vskill/keys.env` is written with mode 0600. The `GITHUB_AUTH` value is base64-encoded JSON; the raw token does not appear in plain text anywhere in the file.
- **Threshold**: Vitest filesystem test asserts file mode 0600 and absence of token plain text.
- **Result**: [ ] PENDING
