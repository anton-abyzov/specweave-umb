---
increment: 0814-studio-github-publish-phase0
title: "GitHub OAuth + Publish-to-GitHub in vskill studio (Phase 0)"
status: planned
generated: 2026-04-30
tasks_total: 24
ac_coverage: 39/39
---

# Tasks — GitHub OAuth + Publish-to-GitHub in vskill studio (Phase 0)

## Phase A — Foundation

### T-001: Register GitHub OAuth App (OPS precondition)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] pending
**EXTERNAL: Anton must complete** — Register a `vskill` GitHub OAuth App with Device Flow enabled. Embed the public Client ID in `repositories/anton-abyzov/vskill/src/config/github.ts` as `VSKILL_GITHUB_CLIENT_ID`. The PAT path (US-002) ships before this completes; Device Flow CTA is hidden via `isDeviceFlowEnabled()` until this task is done. No code is blocked by this task.
**Test Plan**: Given `VSKILL_GITHUB_CLIENT_ID` is set in the environment → When `isDeviceFlowEnabled()` is called → Then it returns `true`. Given env var is absent → When called → Then returns `false` and Device Flow button is absent from the modal.

---

### T-002: Create `src/config/github.ts` with feature flags
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-05 | **Status**: [ ] pending
Create `repositories/anton-abyzov/vskill/src/config/github.ts` (NEW, ~10 lines). Export `GITHUB_CLIENT_ID` read from `process.env.VSKILL_GITHUB_CLIENT_ID` (defaulting to `""`) and `isDeviceFlowEnabled()` returning `!!GITHUB_CLIENT_ID`. This gates the Device Flow CTA independently of the PAT path so the increment ships before OPS completes.
**Test Plan**: Given `VSKILL_GITHUB_CLIENT_ID` env var is absent → When `isDeviceFlowEnabled()` is called in the config module → Then it returns `false`. Given env var is `"Ov23liABC123"` → When called → Then it returns `true`.

---

### T-003: Extend `settings-store.ts` with `readJsonKey` / `writeJsonKey` helpers
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-04, AC-US2-04, AC-US2-06 | **Status**: [ ] pending
Extend `repositories/anton-abyzov/vskill/src/eval-server/settings-store.ts` (lines 1-80, +~30 lines, no API break). Add `readJsonKey<T>(provider): T | null` and `writeJsonKey(provider, blob: T)` helpers. Store a JSON blob as base64 in a dotenv line (`GITHUB_AUTH=<base64-json>`). Must use the existing atomic write + POSIX 0600 pattern already in the file. Also add `"github"` to `providers.ts` union + extended-providers list; do NOT add to `PROVIDERS` const (JSON blob, not single key). Auth record shape: `{ token, login, avatar, scopes: string[], issuedAt: string, source?: "pat" }`.
**Test Plan**: Given `writeJsonKey("github", record)` is called with a test record → When `readJsonKey("github")` is called → Then it returns the same record with all fields intact. Given the written file contents are read directly → Then the token byte sequence does not appear in plain text (base64 only). Given a filesystem permission check runs on the written file → Then the mode is 0600 (owner read-write only).

---

### T-004: Stub `github-routes.ts` and wire into `eval-server.ts`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-08 | **Status**: [ ] pending
Create `repositories/anton-abyzov/vskill/src/eval-server/github-routes.ts` as a stub that registers one working endpoint (`GET /api/github/auth/me` returning `{signedIn:false}`) and applies the CSRF/loopback guard pattern from `git-routes.ts:91-108`. Register the routes in `eval-server.ts:103` (one new line: `registerGithubRoutes(router, root);` after `registerGitRoutes`). This validates the wiring before full implementation.
**Test Plan**: Given `eval-server` is started → When `GET /api/github/auth/me` is called from `localhost` → Then it returns `{signedIn:false}` with HTTP 200. Given the same request is made with a non-loopback `Origin` header → Then it returns 403. Given a request arrives with `remoteAddress` that is not `127.0.0.1` or `::1` → Then all `/api/github/*` routes return 403.

---

## Phase B — Auth Backend

### T-005: Implement `github-oauth.ts` — Device Flow start and poll
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-06, AC-US1-07 | **Status**: [ ] pending
Create `repositories/anton-abyzov/vskill/src/eval-server/github-oauth.ts`. Implement `startDeviceFlow` (calls `POST github.com/login/device/code` with `application/x-www-form-urlencoded`, scopes `repo read:user`) and `pollDeviceFlow` (calls `POST github.com/login/oauth/access_token`, handles `authorization_pending`, `slow_down` with +5s interval, `access_denied`, `expired_token`, and success). On success, calls `GET /user` via `@octokit/rest` to fetch `login` and `avatar_url`. Injectable `deps.fetch` test seam. The `device_code` must never leave the module boundary.
Public surface (types only — see plan.md §3.1 for signatures): `startDeviceFlow`, `pollDeviceFlow`, `validatePat`, `revokeToken`.
**Test Plan**: Given a mock `fetch` stub returning `authorization_pending` twice then an `access_token` → When `pollDeviceFlow` is called in a loop → Then it eventually returns `{status:"ok", record}` with correct `login` and `avatar`. Given a mock returning `slow_down` → When polled → Then the returned `suggestedInterval` equals the original interval + 5. Given a mock returning `access_denied` → When polled → Then the result is `{status:"denied"}`. Given the `expires_in` seconds have elapsed → When polled past expiry → Then the result is `{status:"expired"}`.

---

### T-006: Implement `github-oauth.ts` — PAT validation and token revocation
**User Story**: US-002, US-006 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-06, AC-US6-03 | **Status**: [ ] pending
Add `validatePat` and `revokeToken` to `github-oauth.ts`. `validatePat` calls `GET https://api.github.com/user` with `Authorization: token <pat>`, reads the `X-OAuth-Scopes` response header, and rejects with `{error:"missing_scopes", required:["repo"]}` if `repo` is absent. On success returns `AuthRecord` with `source:"pat"`. `revokeToken` calls `DELETE /applications/{client_id}/token` (Device Flow tokens only); failure is logged but not thrown. Add a Vitest snapshot of a sample log line containing a real `GITHUB_AUTH` value to assert the token byte sequence is absent after the redacting logger processes it.
**Test Plan**: Given a PAT with `X-OAuth-Scopes: repo,read:user` → When `validatePat` is called → Then it returns a valid `AuthRecord` with all fields populated. Given a PAT with `X-OAuth-Scopes: public_repo` → When called → Then it throws `{error:"missing_scopes", required:["repo"]}`. Given a publish error containing the token is logged → When the logger output is inspected → Then the token character sequence is absent from the log line.

---

### T-007: Wire all auth endpoints in `github-routes.ts`
**User Story**: US-001, US-002, US-006 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-05, AC-US1-06, AC-US1-07, AC-US1-08, AC-US2-01, AC-US2-02, AC-US2-03, AC-US6-03 | **Status**: [ ] pending
Expand `github-routes.ts` to implement all 6 auth endpoints (all guarded by the CSRF/loopback pattern):
- `POST /api/github/auth/device-start`: calls `startDeviceFlow`, stores `{deviceCode, startedAt}` in a module-level `Map<sessionId, ...>`, returns `{user_code, verification_uri, expires_in, sessionId}` (device_code stays server-side, never in the response).
- `POST /api/github/auth/device-poll`: accepts `{sessionId}`, calls `pollDeviceFlow`, on success calls `writeJsonKey("github", record)` and clears the session map entry, returns `{status, login?, avatar?}`.
- `GET /api/github/auth/me`: calls `readJsonKey("github")`, returns `{signedIn, login?, avatar?, scopes?, source?}`.
- `POST /api/github/auth/logout`: calls `deleteKey("github")`, best-effort calls `revokeToken`, returns 204 `{ok:true}`.
- `POST /api/github/auth/pat`: calls `validatePat`, on success calls `writeJsonKey`, returns `{login, avatar}`.
**Test Plan**: Given a loopback request to `POST /api/github/auth/device-start` → When called → Then the response body contains `{user_code, sessionId}` and does NOT contain `device_code`. Given `POST /api/github/auth/logout` is called with an active session → When it completes → Then `GET /api/github/auth/me` subsequently returns `{signedIn:false}`. Given any `/api/github/auth/*` route receives a non-loopback `Origin` header → When handled → Then all routes return 403.

---

## Phase B — Auth Frontend

### T-008: Implement `GitHubAuthModal.tsx` — Device Flow UI
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-05, AC-US1-06, AC-US1-07 | **Status**: [ ] pending
Create `repositories/anton-abyzov/vskill/src/eval-ui/src/components/GitHubAuthModal.tsx`. State machine: `Idle → Starting → Waiting → Success/Denied/Expired/Error`. The `Waiting` state shows: the 6-character `user_code` in large monospace, an "Open github.com/login/device" button (`window.open(verification_uri)`), a 15-minute countdown (from `expires_in`), and a polling spinner. Polls `device-poll` every 5s; adjusts to `suggestedInterval` on `slow_down`. On success calls `onAuthenticated(login, avatar)` and closes. Cancel button is always visible in `Waiting` — aborts the poller and writes nothing to settings-store. `Error` and `Denied` states show a "Try again" button resetting to `Idle`. When `isDeviceFlowEnabled()` is false, hides Device Flow entirely (modal opens directly to PAT tab).
Props: `{ open, onClose, onAuthenticated(login: string, avatar: string): void }`.
**Test Plan**: Given `open=true` and Device Flow is enabled → When the modal renders → Then it shows a "Sign in with GitHub" button. Given the poller receives `{status:"ok", login:"user", avatar:"url"}` → When the response arrives → Then `onAuthenticated("user", "url")` is called. Given the user clicks cancel during `Waiting` state → When checked → Then `GET /api/github/auth/me` still returns `{signedIn:false}`. Given the poller receives `{status:"denied"}` → When displayed → Then an error state with "Try again" button is shown.

---

### T-009: Implement `GitHubAuthModal.tsx` — PAT fallback tab
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06 | **Status**: [ ] pending
Add PAT fallback to `GitHubAuthModal.tsx`. A "Use a Personal Access Token instead" link below the Device Flow UI (or as the primary view when `isDeviceFlowEnabled()` is false) reveals a `type="password"` textarea + "Sign in with token" button. On submit calls `POST /api/github/auth/pat`. Surfaces a human-readable error for `{error:"missing_scopes"}` (e.g. "Token needs the `repo` scope"). On success calls `onAuthenticated(login, avatar)`. The PAT value must never appear in any console log output.
**Test Plan**: Given `isDeviceFlowEnabled()` returns `false` → When the modal opens → Then the PAT input is immediately visible with no toggle required. Given a PAT with missing `repo` scope is submitted → When the response is `{error:"missing_scopes"}` → Then a human-readable message listing the missing scope is displayed. Given a valid PAT is submitted and the server returns `{login, avatar}` → When the response arrives → Then `onAuthenticated` is called.

---

### T-010: Top-bar GitHub avatar / sign-in indicator
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05 | **Status**: [ ] pending
Modify the Studio top bar component. On mount (and after page reload) call `GET /api/github/auth/me`. When `signedIn:true`, render a 20px circle avatar with the `login` adjacent. When `signedIn:false`, render a "Sign in with GitHub" button that opens `<GitHubAuthModal/>`. Clicking the avatar opens a small dropdown showing: login, auth source (`Device Flow` or `Personal Access Token`), and a "Sign out" item. "Sign out" calls `POST /api/github/auth/logout` and reverts the top bar to signed-out state immediately (optimistic). If any publish call returns 401, show a "Session expired — sign in again" modal, preserve pending publish state in component memory, and revert the top bar to signed-out.
**Test Plan**: Given a signed-in session exists in settings-store → When the Studio page loads → Then the top bar shows the avatar and login without a prior flash of the signed-out button. Given "Sign out" is clicked → When logout completes → Then the top bar shows "Sign in with GitHub" and `GET /api/github/auth/me` returns `{signedIn:false}`. Given a publish call returns 401 → When the error is received → Then the "session expired" modal appears and the top bar reverts to signed-out state.

---

### T-011: `api.ts` client extensions — auth methods
**User Story**: US-001, US-002, US-006 | **Satisfies ACs**: AC-US1-01, AC-US2-01, AC-US6-02 | **Status**: [ ] pending
Extend `repositories/anton-abyzov/vskill/src/eval-ui/src/api.ts` (around lines 1092-1113, +~30 lines) with typed auth client methods:
`api.githubAuth.startDevice()`, `api.githubAuth.pollDevice(sessionId)`, `api.githubAuth.me()`, `api.githubAuth.logout()`, `api.githubAuth.pat(token)`.
All methods use the existing fetch wrapper. No Octokit types leak into the browser bundle.
**Test Plan**: Given `api.githubAuth.me()` is called against a mock server returning `{signedIn:true, login:"testuser"}` → When the method resolves → Then it returns the full typed response including `login`. Given `api.githubAuth.startDevice()` is called → When the outbound request is inspected → Then it is `POST /api/github/auth/device-start` and the response type has `user_code` and `sessionId` fields.

---

## Phase C — Publish Backend

### T-012: Install `@octokit/rest` + `@octokit/plugin-throttling` dependencies
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04 | **Status**: [ ] pending
Add to `repositories/anton-abyzov/vskill/package.json` (server-side only): `@octokit/rest@^21` and `@octokit/plugin-throttling@^9`. Configure throttling with `onRateLimit` and `onSecondaryRateLimit` callbacks capped at 2 retries. Verify `npm run build` passes. Assert Octokit does NOT appear in the eval-ui browser bundle (check bundle manifest or add a build assertion — the browser bundle must not grow from this dep).
**Test Plan**: Given the vskill package installs with the new deps → When `npm run build` runs → Then it exits 0 with no TypeScript errors. Given the browser bundle is analyzed after build → When the bundle chunks are inspected → Then `@octokit/rest` does not appear in any eval-ui browser chunk.

---

### T-013: Implement `github-publish.ts` — `createRepo` and `setTopics`
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-06, AC-US3-07 | **Status**: [ ] pending
Create `repositories/anton-abyzov/vskill/src/eval-server/github-publish.ts`. Implement `createRepo` (calls `POST /user/repos` via Octokit, returns `{owner, repo, htmlUrl, defaultBranch}`) and `setTopics` (calls `PATCH /repos/{owner}/{repo}/topics` with `["claude-skill", "claude-code-skill"]` to match the discovery convention in `vskill-platform/src/lib/scanner.ts:200-265`). Handle 422 from `createRepo` by throwing `{code:"NAME_TAKEN"}` so the route layer can auto-suggest a variant name (e.g. `<name>-2`). A Vitest test asserts this file does NOT import `child_process` and does NOT reference `spawn` or `exec`.
**Test Plan**: Given an Octokit instance with a mock `request.hook` → When `createRepo` is called with `{name:"my-skill", private:false}` → Then the captured request is `POST /user/repos` with the expected body shape. Given the mock returns HTTP 422 → When `createRepo` is called → Then it throws `{code:"NAME_TAKEN"}`. Given `setTopics` is called → When the captured request is inspected → Then the `names` array contains both `"claude-skill"` and `"claude-code-skill"`. Given a static import analysis of `github-publish.ts` runs → Then neither `child_process`, `spawn`, nor `exec` appear anywhere in the source.

---

### T-014: Implement `github-publish.ts` — `uploadFiles` (create mode)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-07, AC-US3-08 | **Status**: [ ] pending
Implement `uploadFiles` for `mode:"create"` in `github-publish.ts`. Iterates files sequentially (Octokit throttling plugin handles rate limits), calls `PUT /repos/{owner}/{repo}/contents/{path}` with `{message, content: base64, branch}` for each file, calls `onProgress(e)` after each. Binary files (PNG, etc.) must round-trip via base64 byte-for-byte. Returns `{uploaded, skipped}`. The `skipIdentical` check is not needed in create mode (no remote files exist yet).
**Test Plan**: Given a fixture skill directory with 3 text files and 1 PNG → When `uploadFiles` is called in `create` mode → Then 4 Octokit `PUT /repos/.../contents/...` requests are captured in order, each with base64-encoded content. Given the fixture PNG is base64-encoded, sent, and then decoded from the mock-captured body → When compared to the original bytes → Then they match exactly. Given 4 files → When `onProgress` fires → Then it fires 4 times with `index` incrementing from 0 to 3.

---

### T-015: Implement `github-publish.ts` — `uploadFiles` (update mode + conflict handling)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06, AC-US4-07 | **Status**: [ ] pending
Extend `uploadFiles` for `mode:"update"`. Per file: (1) call `GET /repos/{owner}/{repo}/contents/{path}` to read the current SHA; (2) compare local base64 vs remote blob — skip if identical (prevents empty commits and is the resume-on-failure mechanism); (3) PUT with `sha` for existing files, PUT without `sha` for new files; (4) on 409 SHA mismatch, retry once with a fresh GET; (5) on second 409, throw `{code:"CONFLICT", path}`. Commit message from `args.commitMessage` applies to all PUTs.
**Test Plan**: Given a file with identical content to remote → When `uploadFiles` runs in update mode → Then no PUT is issued for that file and it counts as `skipped`. Given a file returns 409 on the first PUT → When the handler retries → Then a fresh GET is issued and the PUT is retried with the refreshed SHA. Given a second 409 occurs → When the error is thrown → Then it has `{code:"CONFLICT", path}`. Given a partial publish (2 of 3 files uploaded before network drop) → When `uploadFiles` is re-run in update mode → Then only the remaining unuploaded file receives a PUT.

---

### T-016: Wire `POST /api/github/publish` and repo-list helper in `github-routes.ts`
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-01, AC-US3-03, AC-US3-05, AC-US3-06, AC-US4-01, AC-US4-02, AC-US4-04, AC-US4-05, AC-US4-06, AC-US5-04 | **Status**: [ ] pending
Add two routes to `github-routes.ts`:
1. `POST /api/github/publish`: reads token from `readJsonKey("github")`, constructs Octokit with throttling, dispatches to `createRepo+uploadFiles+setTopics` (create mode) or `uploadFiles` (update mode). Returns `{ok, repoUrl, uploaded, skipped, submitUrl}` where `submitUrl="https://verified-skill.com/submit?repoUrl=<encoded>&skillPath=<encoded>"` (skillPath param omitted if absent from request, not sent as empty string). On `NAME_TAKEN` returns `{ok:false, error:"NAME_TAKEN", suggested:"<name>-2"}`. On `CONFLICT` surfaces the conflicted path.
2. `GET /api/github/repos?topic=claude-skill&match=<skillName>`: calls Octokit `GET /user/repos`, filters by topic `claude-skill` and name match, returns array for the "Update existing" dropdown.
**Test Plan**: Given a fully stubbed Octokit route test with `mode:"create"` and 3 files → When `POST /api/github/publish` is called → Then the response is `{ok:true, repoUrl, uploaded:3, submitUrl}` with `submitUrl` containing a properly URI-encoded `repoUrl`. Given `createRepo` returns `NAME_TAKEN` → When the route handles it → Then the response is `{ok:false, error:"NAME_TAKEN", suggested:"my-skill-2"}`. Given `skillPath` is absent from the request → When `submitUrl` is built → Then the `skillPath` param is omitted entirely (not `skillPath=`).

---

## Phase C — Publish Frontend

### T-017: Implement `GitHubPublishPanel.tsx` — new-repo mode + post-publish handoff
**User Story**: US-003, US-005 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04, AC-US3-05, AC-US3-06, AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05 | **Status**: [ ] pending
Create `repositories/anton-abyzov/vskill/src/eval-ui/src/components/GitHubPublishPanel.tsx`. New-repo mode (default when skill has no detected GitHub remote): repo name input (prefilled from skill folder name), public/private toggle (default: public), optional description (prefilled from `SKILL.md` description frontmatter). "Create & Publish" button calls `api.githubPublish({mode:"create", ...})`. During upload shows per-file progress (`N/total filename`; "rate limited, retrying in Ns" when Octokit pauses). On success shows the repo URL as a clickable link, "Open on GitHub" (`window.open`), and "Submit to verified-skill.com" (`window.open("https://verified-skill.com/submit?repoUrl=<encoded>&skillPath=<encoded>")`). Skipping the CTA is a first-class outcome — no state is changed if it is never clicked. On `NAME_TAKEN`: inline error next to the field + auto-suggested variant with one-click accept. Sign-in gate: if `me.signedIn` is false, show "Sign in with GitHub" CTA that opens `<GitHubAuthModal/>`.
**Test Plan**: Given the panel renders with skill name `"my-skill"` → When the new-repo form mounts → Then the repo name input is prefilled with `"my-skill"`. Given publish succeeds with `submitUrl` containing a repo name with hyphens → When the "Submit to verified-skill.com" button's href is checked → Then the `repoUrl` query param is correctly URI-encoded (Vitest unit test verifies special-char safety). Given `NAME_TAKEN` is returned → When the error renders → Then the suggested name appears with a one-click accept button. Given the user never clicks "Submit to verified-skill.com" → When checked → Then the publish state is unchanged.

---

### T-018: Implement `GitHubPublishPanel.tsx` — update-existing mode
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-06 | **Status**: [ ] pending
Add update-existing mode to `GitHubPublishPanel.tsx`. Activated when the skill folder contains evidence of an existing GitHub remote or when the user has previously published via this path. Shows: target repo (`owner/name`), change summary (changed files vs remote), a single commit message field (default: `"Update from vskill studio"`) applied to all file PUTs, and "Publish update" button. Also shows a repo picker (populated from `GET /api/github/repos?topic=claude-skill&match=<skillName>`) as fallback for when auto-detection misses. "Resume publish" button appears after a simulated or real network-drop partial publish — re-diffs local vs remote and uploads only missing files.
**Test Plan**: Given a skill folder with a previously published GitHub remote → When the panel renders → Then it defaults to update-existing mode showing the repo `owner/name`. Given a commit message is entered and publish runs → When the Octokit PUT calls are captured → Then every PUT request body includes the exact message. Given 2 of 5 files were uploaded before a network drop → When "Resume publish" is clicked → Then exactly 3 PUT requests are issued (the remaining files only).

---

### T-019: Integrate `PublishDrawer.tsx` — add "Publish to GitHub" tab
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [ ] pending
Modify `repositories/anton-abyzov/vskill/src/eval-ui/src/components/PublishDrawer.tsx` (lines 17, 102, ~+15 lines). Wrap the existing UI in a two-tab container. Add a "Publish to GitHub" tab rendering `<GitHubPublishPanel skillPath={currentSkillPath} />` alongside the existing "Commit & Push" tab. The existing "Commit & Push" tab must remain the default and its behavior must be identical to pre-increment. This is purely additive — zero behavior change to the existing path.
**Test Plan**: Given `PublishDrawer` is rendered → When it mounts → Then both "Commit & Push" and "Publish to GitHub" tabs are visible and "Commit & Push" is active by default. Given the "Commit & Push" tab is selected and the existing git-push flow runs → When `npx vitest run` and `npx playwright test` are executed → Then all pre-existing tests pass without modification. Given the "Publish to GitHub" tab is selected → When rendered → Then `<GitHubPublishPanel/>` mounts.

---

### T-020: `api.ts` client extensions — publish methods
**User Story**: US-003, US-004, US-005 | **Satisfies ACs**: AC-US3-03, AC-US4-03, AC-US5-02 | **Status**: [ ] pending
Extend `repositories/anton-abyzov/vskill/src/eval-ui/src/api.ts` (around lines 1092-1113, +~30 lines) with:
`api.githubPublish(args: PublishArgs): Promise<PublishResult>` and `api.githubRepos(skillName: string): Promise<RepoListItem[]>`.
`PublishResult` shape: `{ok, repoUrl?, uploaded?, skipped?, submitUrl?, error?, suggested?}`. No Octokit types in the browser bundle.
**Test Plan**: Given `api.githubPublish({mode:"create", skillPath:"/tmp/skill", repoName:"test", isPrivate:false})` is called against a mock server → When the method resolves → Then it returns a typed `PublishResult` with `submitUrl` present. Given `api.githubRepos("my-skill")` is called → When the outbound request is inspected → Then the URL is `GET /api/github/repos?topic=claude-skill&match=my-skill`.

---

## Phase D — Tests

### T-021: Unit tests — Device Flow poller, settings-store, PAT validation
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US1-06, AC-US1-07, AC-US2-03, AC-US2-06 | **Status**: [ ] pending
Write Vitest unit tests in `repositories/anton-abyzov/vskill/src/eval-server/__tests__/github-oauth.test.ts`:
- Device Flow poller: all state transitions (`authorization_pending`, `slow_down` +5s, `access_denied`, `expired_token`, success).
- `validatePat`: valid scopes, missing `repo` scope (structured error), `X-OAuth-Scopes` header parsing.
- `settings-store` `readJsonKey`/`writeJsonKey` round-trip: all fields preserved; token byte sequence absent in the written file; file permissions are 0600.
- Redacting logger snapshot: log a sample error line containing a `GITHUB_AUTH` blob and assert the token characters are absent.
All stubs use injectable `deps.fetch` — no network calls.
**Test Plan**: Given `npx vitest run` is executed targeting the new test file → When all tests run → Then all pass with no network calls made. Given the logger snapshot assertion runs → When the snapshot is compared → Then the token string is absent and only `{login, avatar}` fields appear in the output.

---

### T-022: Unit + integration tests — `github-publish.ts` and routes
**User Story**: US-003, US-004, US-005 | **Satisfies ACs**: AC-US3-07, AC-US3-08, AC-US4-07, AC-US5-03 | **Status**: [ ] pending
Write Vitest tests in `repositories/anton-abyzov/vskill/src/eval-server/__tests__/github-publish.test.ts` and `github-routes.test.ts`:
- `github-publish.ts` unit (Octokit `request.hook` mocks): `createRepo`, `uploadFiles` create mode, `uploadFiles` update mode — (a) no-change skip, (b) conflict retry, (c) new file no-sha, (d) binary PNG byte equality.
- `github-routes.ts` integration (full `RouteRouter` against stubbed Octokit): all 7 routes happy + error paths, CSRF/loopback rejection, `NAME_TAKEN` response shape, `submitUrl` URI encoding with special-character repo names (AC-US5-03).
- Regression: static import assertion that `github-publish.ts` has no `child_process`, `spawn`, or `exec`.
- US-004 scenarios: (a) update with no remote changes, (b) one conflicted file, (c) new file + modified file, (d) resume after network drop.
**Test Plan**: Given `npx vitest run` is executed for all new test files → When tests complete → Then pass rate is 100% and line coverage on the three new server files exceeds 90%. Given the `submitUrl` encoding test runs with a repo name containing spaces and special characters → When the encoded URL is parsed → Then all characters round-trip correctly.

---

### T-023: E2E test — full publish flow with mocked GitHub
**User Story**: US-003, US-005, US-006 | **Satisfies ACs**: AC-US1-05, AC-US3-03, AC-US3-04, AC-US3-05, AC-US5-01, AC-US5-02, AC-US6-01, AC-US6-05 | **Status**: [ ] pending
Write `repositories/anton-abyzov/vskill/e2e/github-publish.spec.ts` (Playwright). Scenario:
1. Boot Studio with a fixture skill (5 text files).
2. Mock `POST /api/github/auth/device-start` → `{user_code:"ABCD-12", sessionId, verification_uri, expires_in:900}`.
3. Mock `POST /api/github/auth/device-poll` → return `{status:"pending"}` on poll 1, `{status:"ok", login:"testuser", avatar:"https://example.com/avatar.png"}` on poll 2.
4. Click "Sign in with GitHub" in top bar → verify modal shows `"ABCD-12"` → verify avatar + login appear in top bar after poll 2.
5. Open "Publish to GitHub" tab in PublishDrawer → verify "Create & Publish" form is present with prefilled name.
6. Mock `POST /api/github/publish` → `{ok:true, repoUrl:"https://github.com/testuser/my-skill", uploaded:5, submitUrl:"https://verified-skill.com/submit?repoUrl=..."}`.
7. Click "Create & Publish" → assert progress indicators fire → assert success panel shows the repo URL link and "Submit to verified-skill.com" button.
8. Assert via Playwright network intercept that no `/api/github/*` response body or header contains the mock access token value.
**Test Plan**: Given `npx playwright test e2e/github-publish.spec.ts` runs → When all 8 scenario steps execute → Then all assertions pass and the command exits 0. Given all network responses to `/api/github/*` are inspected → When scanned for the mock token value → Then the token does not appear in any response body or header.

---

## Phase D — Polish

### T-024: README "Publishing from Studio" + ADR references + optional CLI subcommand
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US2-05, AC-US3-07 | **Status**: [ ] pending
1. Add a "Publishing from Studio" section to `repositories/anton-abyzov/vskill/README.md` covering: PAT-only flow (works immediately without OAuth App setup), Device Flow flow (requires OPS task T-001), and pointers to `0814-01-device-flow-over-pkce-for-local-studio.md` and `0814-02-file-store-vs-keychain-phase0.md` in `.specweave/docs/internal/architecture/adr/`.
2. **Optional (defer if scope tight)**: implement `vskill auth login|logout|status` CLI subcommand in `repositories/anton-abyzov/vskill/src/index.ts:269-280` (~+50 lines). `login` calls `POST /api/github/auth/device-start` against the local eval-server and polls; `logout` calls `/auth/logout`; `status` calls `/auth/me` and prints login or "not signed in".
3. Re-run the full pre-existing "Commit & Push" Vitest + Playwright suite to verify zero regressions.
**Test Plan**: Given the README is reviewed → When the "Publishing from Studio" section is read → Then both the PAT flow and Device Flow are documented with correct route names and both ADR file names are referenced. Given the optional CLI subcommand is implemented and a session exists → When `vskill auth status` is run → Then it prints the current `login`. Given the pre-existing test suite is re-run → When `npx vitest run` and `npx playwright test` complete → Then all pre-existing tests pass.

---

## AC Coverage Matrix

| AC | Task(s) |
|----|---------|
| AC-US1-01 | T-001, T-002, T-007 |
| AC-US1-02 | T-005, T-008 |
| AC-US1-03 | T-005, T-021 |
| AC-US1-04 | T-003, T-005, T-021 |
| AC-US1-05 | T-007, T-008, T-023 |
| AC-US1-06 | T-005, T-008, T-021 |
| AC-US1-07 | T-005, T-008, T-021 |
| AC-US1-08 | T-004, T-007 |
| AC-US2-01 | T-009, T-011 |
| AC-US2-02 | T-006 |
| AC-US2-03 | T-006, T-009, T-021 |
| AC-US2-04 | T-003, T-006 |
| AC-US2-05 | T-002, T-009, T-024 |
| AC-US2-06 | T-006, T-009, T-021 |
| AC-US3-01 | T-016, T-017, T-019 |
| AC-US3-02 | T-017 |
| AC-US3-03 | T-013, T-014, T-016, T-020, T-023 |
| AC-US3-04 | T-014, T-017, T-023 |
| AC-US3-05 | T-016, T-017, T-023 |
| AC-US3-06 | T-013, T-016, T-017 |
| AC-US3-07 | T-013, T-022, T-024 |
| AC-US3-08 | T-014, T-022 |
| AC-US4-01 | T-016, T-018 |
| AC-US4-02 | T-016, T-018 |
| AC-US4-03 | T-015, T-016, T-020 |
| AC-US4-04 | T-015, T-016, T-018 |
| AC-US4-05 | T-015, T-016 |
| AC-US4-06 | T-015, T-016, T-018 |
| AC-US4-07 | T-015, T-022 |
| AC-US5-01 | T-017, T-023 |
| AC-US5-02 | T-017, T-020, T-023 |
| AC-US5-03 | T-017, T-022 |
| AC-US5-04 | T-016, T-017 |
| AC-US5-05 | T-017 |
| AC-US6-01 | T-010, T-023 |
| AC-US6-02 | T-010 |
| AC-US6-03 | T-006, T-007, T-010 |
| AC-US6-04 | T-010 |
| AC-US6-05 | T-010, T-023 |
