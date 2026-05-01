---
increment: 0814-studio-github-publish-phase0
title: "GitHub OAuth + Publish-to-GitHub in vskill studio (Phase 0)"
type: feature
priority: P1
status: planned
created: 2026-04-30
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: GitHub OAuth + Publish-to-GitHub in vskill studio (Phase 0)

## Overview

Make `vskill studio` self-sufficient for the dominant publishing case — *"I just authored a skill, give me a GitHub repo and publish it"* — without leaving the Studio UI and without shelling out to the local `git` binary. Phase 0 lands entirely inside the existing eval-server + React bundle (no Tauri/Electron shell yet). It is the prerequisite that makes a future desktop wrapper meaningful: a desktop wrapper around a non-self-sufficient Studio adds nothing.

After this increment a user running `vskill studio` can:

1. **Sign in with GitHub** via Device Flow (browser pops `github.com/login/device`, user pastes a 6-character code, token returns to the eval-server) — with a Personal Access Token (PAT) fallback for air-gapped users and to unblock shipping while OAuth App registration completes.
2. **Create a brand-new GitHub repo** for a skill from inside Studio (no local `git init`, no manual repo creation on github.com).
3. **Push files to GitHub** via the REST Contents API (no shell to `git`).
4. **Optionally hand off to verified-skill.com** for marketplace indexing — one-click opens the existing submission form with `repoUrl` pre-filled.

The existing `git push`-based publish flow at `git-routes.ts:291` stays untouched — this is a parallel, additive path. The architecture (server-held token, REST-only) is portable as-is to a future Tauri sidecar — zero throwaway when Phase 1 ships.

## Goal

Reduce the time-to-publish for a brand-new skill from "open shell, init git, create remote on github.com, paste repo URL into verified-skill.com submit form" (multiple minutes, multiple context switches) to **"click Sign in with GitHub → click Publish → done"** (under 60 seconds, never leaving Studio).

## User Stories

### US-001: Sign in with GitHub via Device Flow (P1)
**Project**: vskill

**As a** Studio user authoring a skill
**I want** to sign in with my GitHub account from inside Studio using Device Flow
**So that** I can publish skills to my GitHub without managing OAuth callbacks, client secrets, or PATs

**Acceptance Criteria**:
- [ ] **AC-US1-01**: A "Sign in with GitHub" button appears in the Studio top bar when no GitHub session exists. Clicking it opens a `GitHubAuthModal` that calls `POST /api/github/auth/device-start` on the eval-server, which calls `POST github.com/login/device/code` with the registered OAuth Client ID and scopes `repo` + `read:user` (no `workflow`, no `admin:org`).
- [ ] **AC-US1-02**: The modal displays the 6-character `user_code` in large monospace, an "Open github.com/login/device" button (`window.open` with `verification_uri`), a 15-minute countdown derived from `expires_in`, and a polling spinner.
- [ ] **AC-US1-03**: The eval-server polls `POST github.com/login/oauth/access_token` every 5 seconds (GitHub's recommended minimum), respects `slow_down` responses with exponential backoff, and stops at the device-code expiry (max 15 minutes).
- [ ] **AC-US1-04**: On successful exchange, the access token, `login`, `avatar_url`, and computed `expiresAt` are persisted as a JSON blob under a new `github` provider key in `~/.vskill/keys.env` via the existing `settings-store.ts` (POSIX 0600). The token is never sent to the browser; the UI receives only `{login, avatar, expiresAt}` from `GET /api/github/auth/me`.
- [ ] **AC-US1-05**: After success, the modal closes, the top bar shows the GitHub avatar + login, and the Studio's auth state survives a page reload (eval-server reads the stored token on `/api/github/auth/me`).
- [ ] **AC-US1-06**: User can cancel the modal at any time; cancellation aborts the poller and writes nothing to settings-store.
- [ ] **AC-US1-07**: If the user denies the authorization on github.com, the modal shows an error state with a "Try again" button.
- [ ] **AC-US1-08**: All `/api/github/auth/*` routes enforce the existing CSRF / loopback-only origin guard pattern from `git-routes.ts:91-108` so a malicious skill running inside Studio cannot exfiltrate the token via cross-origin XHR.

---

### US-002: Sign in with GitHub via PAT (fallback) (P1)
**Project**: vskill

**As a** Studio user without OAuth App access (or before the OAuth App registration is live)
**I want** to paste a Personal Access Token to authenticate
**So that** I can publish to GitHub even if Device Flow is unavailable

**Acceptance Criteria**:
- [ ] **AC-US2-01**: The `GitHubAuthModal` exposes a "Use a Personal Access Token instead" link that toggles to a textarea + "Sign in with token" button.
- [ ] **AC-US2-02**: Submitting the PAT calls `POST /api/github/auth/pat` on the eval-server which validates the token by calling `GET https://api.github.com/user` with `Authorization: token <pat>` and inspecting the response.
- [ ] **AC-US2-03**: Token must include the `repo` scope. The eval-server reads the `X-OAuth-Scopes` response header on the validation call and rejects with `400 { error: "missing_scopes", required: ["repo"] }` if `repo` is absent. The UI surfaces a human-readable error listing the missing scopes.
- [ ] **AC-US2-04**: On valid PAT, the token + login + avatar are persisted under the same `github` provider entry in `settings-store.ts` (same shape as Device Flow, plus `source: "pat"`). Subsequent flows are indistinguishable from Device-Flow-acquired tokens.
- [ ] **AC-US2-05**: The PAT path is **always available**, independent of whether the GitHub OAuth Client ID is configured. If `src/config/github.ts` has no Client ID, the Device Flow button is hidden but the PAT entry remains, so Phase 0 can ship before OPS work completes.
- [ ] **AC-US2-06**: PAT input field uses `type="password"`, the value is never logged, and the eval-server's existing redacting logger covers `GITHUB_AUTH` (verified by a vitest snapshot of a sample log line).

---

### US-003: Create a new GitHub repo and publish a skill from Studio (P1)
**Project**: vskill

**As a** Studio user who just finished authoring a brand-new skill with no remote
**I want** to publish it to a new GitHub repo with one click from the Publish drawer
**So that** I do not need to leave Studio, open a terminal, or visit github.com to bootstrap the repo

**Acceptance Criteria**:
- [ ] **AC-US3-01**: `PublishDrawer.tsx:17,102` gains a new "Publish to GitHub" tab alongside the existing "Commit & Push" tab. Inside the tab, a `GitHubPublishPanel` renders a "New repo" mode by default when the skill has no detected GitHub remote.
- [ ] **AC-US3-02**: The "New repo" form prefills the repo name from the skill folder name, lets the user edit it, and offers a public/private toggle (default: public) plus an optional description field that defaults to the skill's `SKILL.md` `description` frontmatter.
- [ ] **AC-US3-03**: Clicking "Create & Publish" calls `POST /api/github/publish` on the eval-server with `{ mode: "create", skillPath, repoName, isPrivate, description }`. The server-side `github-publish.ts` runs three Octokit calls in order: `POST /user/repos` (create), `PUT /repos/{owner}/{repo}/contents/{path}` per file in the skill folder (base64 content via the Contents API — sequential to preserve commit ordering), then `PUT /repos/{owner}/{repo}/topics` adding `claude-skill` and `claude-code-skill` (matching the discovery convention in `vskill-platform/src/lib/scanner.ts:200-265`).
- [ ] **AC-US3-04**: The UI shows a per-file progress indicator during the upload loop and surfaces Octokit's throttling pauses ("rate limited, retrying in Ns") rather than failing silently.
- [ ] **AC-US3-05**: On success, the panel shows the new repo URL as a clickable link, an "Open on GitHub" button, and (per US-005) a "Submit to verified-skill.com" CTA. The response includes `{ repoUrl, htmlUrl, commitShas: [...] }`.
- [ ] **AC-US3-06**: If `POST /user/repos` returns 422 (name taken), the UI surfaces "name taken" inline next to the field with an auto-suggested variant (e.g. `<name>-2`) the user can accept with one click. No partial state is persisted.
- [ ] **AC-US3-07**: At no point does the new GitHub publish path invoke the `git` binary. A vitest unit test asserts `github-publish.ts` does not import `child_process` and does not reference `spawn`/`exec`. The existing `git-routes.ts:291` shell-out flow remains untouched and continues to work for users who prefer it.
- [ ] **AC-US3-08**: All file uploads use base64-encoded content; binary assets (images bundled with the skill) round-trip byte-for-byte (verified by an integration test that uploads a fixture PNG and re-fetches it).

---

### US-004: Update an existing GitHub-tracked skill from Studio (P1)
**Project**: vskill

**As a** Studio user iterating on a skill that is already on GitHub
**I want** to push my latest edits to the existing repo from the Publish drawer
**So that** I do not need to remember the repo URL, run `git status`, or context-switch to a terminal

**Acceptance Criteria**:
- [ ] **AC-US4-01**: When the skill folder contains evidence of an existing GitHub remote (or the user has previously published it via this path — tracked locally), the `GitHubPublishPanel` opens in "Update existing" mode by default and shows the target repo (`owner/name`), the change summary (changed files vs `HEAD`), and a "Publish update" button.
- [ ] **AC-US4-02**: "Update existing" mode also lists the signed-in user's repos that match the skill name and carry the `claude-skill` topic, so the user can pick a target if auto-detection misses.
- [ ] **AC-US4-03**: Clicking "Publish update" calls `POST /api/github/publish` with `{ mode: "update", owner, repo, files: [...] }`. For each file, the eval-server first calls `GET /repos/{owner}/{repo}/contents/{path}` to read the current `sha`, then `PUT /repos/{owner}/{repo}/contents/{path}` with the new base64 content + `sha` to create a server-side commit. New files (no existing SHA) are created without a `sha` field.
- [ ] **AC-US4-04**: A user-provided commit message (single-line, default `"Update from vskill studio"`) is sent as the `message` parameter on each `PUT`. The UI exposes a single message field that applies to all files in the publish (server creates one commit per file, all sharing the message).
- [ ] **AC-US4-05**: If a `PUT` returns 409 (SHA mismatch — concurrent update on github.com), the eval-server retries once with a fresh `GET` for that file's current SHA. A second 409 surfaces "remote changed, refresh and retry" in the UI without uploading partial state.
- [ ] **AC-US4-06**: If the network drops mid-publish, the UI offers a "Resume publish" button that re-diffs local vs remote (using the read-SHA-then-PUT pattern) and uploads only the files that have not yet been committed.
- [ ] **AC-US4-07**: Vitest integration tests cover: (a) update with no remote changes, (b) update where one file is genuinely conflicted, (c) update with one new file + one modified file, (d) resume after simulated network drop.

---

### US-005: Optional handoff to verified-skill.com after publish (P2)
**Project**: vskill

**As a** Studio user who just published a skill to GitHub
**I want** a one-click button that takes me to verified-skill.com's submit form with the repo URL pre-filled
**So that** I can list the skill on the marketplace without copy-pasting the repo URL

**Acceptance Criteria**:
- [ ] **AC-US5-01**: After a successful publish (both "create" and "update" modes), the success panel renders a "Submit to verified-skill.com" button next to the "Open on GitHub" button.
- [ ] **AC-US5-02**: Clicking the button opens `https://verified-skill.com/submit?repoUrl=<encoded>&skillPath=<encoded>` in a new browser tab via `window.open`. The Studio does **not** call `/api/v1/submissions` directly — that endpoint requires platform JWT cookies which are deferred to a separate increment.
- [ ] **AC-US5-03**: The submission URL parameters are URI-encoded; a vitest unit test verifies special-character repos (e.g. `owner/repo with-dashes`) round-trip cleanly.
- [ ] **AC-US5-04**: If the publish response includes a `skillPath` (sub-folder within the repo), it is forwarded as the `skillPath` query param so the verified-skill.com submit form scopes correctly. If absent, the param is omitted (not sent as empty string).
- [ ] **AC-US5-05**: The button is purely a navigation hint — closing it or never clicking it has no effect on the local publish state. Skipping verified-skill.com is a first-class outcome.

---

### US-006: Persistent signed-in state with sign-out (P2)
**Project**: vskill

**As a** Studio user
**I want** to see at a glance whether I am signed in to GitHub and to be able to sign out cleanly
**So that** I trust the auth state and can switch accounts when needed

**Acceptance Criteria**:
- [ ] **AC-US6-01**: When `GET /api/github/auth/me` returns a valid session, the Studio top bar shows the user's GitHub avatar (16-24px circle) with their `login` adjacent. When no session exists, the top bar shows the "Sign in with GitHub" button instead.
- [ ] **AC-US6-02**: Clicking the avatar opens a small dropdown with the login, the auth source (`Device Flow` or `Personal Access Token`), and a "Sign out" item.
- [ ] **AC-US6-03**: "Sign out" calls `POST /api/github/auth/logout` which (a) deletes the `github` entry from `settings-store.ts`, (b) best-effort calls `DELETE /applications/{client_id}/token` on github.com to revoke the token (Device-Flow tokens only — PATs cannot be revoked this way; failure is logged but not surfaced as an error), and (c) returns `204`. The UI immediately reverts the top bar to the signed-out state.
- [ ] **AC-US6-04**: If a publish call returns 401 mid-session (token expired or revoked), the UI shows a "session expired, sign in again" modal, the pending publish is paused (not lost), and the top bar reverts to the signed-out state.
- [ ] **AC-US6-05**: A page reload after sign-in reads the persisted token and rehydrates the top bar with the avatar/login (no "flash of signed-out" beyond the initial `me` round-trip).

## Success Metrics

- **Time-to-first-publish for a brand-new skill**: under 60 seconds from clicking "Publish to GitHub" to seeing the live repo URL, measured on a fixture skill of 5–10 files.
- **Zero shell-outs to `git` on the new path**: vitest assertion that `github-publish.ts` does not import `child_process`; manual smoke verifies the new flow works on a clean machine with no `git` installed.
- **Token never reaches the browser**: integration test asserts no `/api/github/*` response body or header contains the access token; only `{login, avatar, expiresAt}` are exposed to the UI.
- **Existing `git push` flow unaffected**: `PublishDrawer.tsx` "Commit & Push" tab passes its full vitest + Playwright suite unchanged after the increment lands.
- **PAT path ships independently**: the increment can be merged and demoed end-to-end with PAT-only auth before the GitHub OAuth App registration is complete.
- **End-to-end E2E**: `npx playwright test e2e/github-publish.spec.ts` boots Studio, mocks Device Flow + GitHub REST, and asserts repo creation + file upload calls; passes in CI.

## Out of Scope

The following are deferred to Phase 1 (Tauri shell) or later increments:

- **Tauri / Electron desktop shell** — separate increment. Phase 0 is the prerequisite; the Tauri wrapper consumes this REST/server-held-token architecture as-is.
- **OS keychain migration** (Tauri Stronghold / `keytar` / `security` / `cmdkey` / `secret-tool`) — happens with the Tauri shell where it is free and OS-native. Phase 0 reuses the existing `~/.vskill/keys.env` POSIX 0600 storage; the threat model on a single-user laptop where filesystem access already implies game-over makes this acceptable for now. Migration path documented in the ADR.
- **Auto-submit to verified-skill.com** — requires wiring the platform's JWT cookie auth into the eval-server (`/api/v1/submissions`); deferred to a separate increment. Phase 0 ships the one-click handoff with pre-filled URL only.
- **GitHub App** (vs OAuth App) — fine-grained per-repo permissions are only worth the operational cost once we have many users and trust concerns. OAuth App + Device Flow is the right Phase 0 choice.
- **Multi-account / org-account selection** — single signed-in account is enough for v1. Signing out and back in with a different account works (settings-store overwrites cleanly), but there is no in-UI account switcher.
- **Replacing the existing `git push` publish flow** — leaves `git push` users undisturbed; revisit only if the dual-path becomes a maintenance burden. The two paths are intentionally parallel.
- **Webhook-based "your skill was indexed" notification from verified-skill.com back to Studio** — scope creep; users can refresh the marketplace listing themselves.
- **Bulk publish of multiple skills in one click** — Phase 0 publishes one skill at a time, matching the existing PublishDrawer model.

## Dependencies

- **Operational precondition (PAT path: none. Device Flow path: required)**: Anton registers a `vskill` GitHub OAuth App with Device Flow toggled on and embeds the public Client ID in `repositories/anton-abyzov/vskill/src/config/github.ts`. Without it, the Device Flow button is hidden via feature flag but the PAT path remains fully functional, so the increment can ship and be demoed before OPS completes.
- `repositories/anton-abyzov/vskill/src/eval-server/eval-server.ts:103` — route registration site (`registerGitRoutes` adjacent insertion point for `registerGitHubRoutes`).
- `repositories/anton-abyzov/vskill/src/eval-server/git-routes.ts:91-108,291` — CSRF guard pattern to mirror; existing `git push` publish flow that stays untouched.
- `repositories/anton-abyzov/vskill/src/eval-server/settings-store.ts:1-80` — extended with a new `github` provider entry holding the JSON blob.
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/PublishDrawer.tsx:17,102` — host for the new "Publish to GitHub" tab.
- `repositories/anton-abyzov/vskill/src/eval-ui/src/api.ts:1092-1113` — extended with `api.githubAuth.{startDevice, pollDevice, pat, logout, me}` and `api.githubPublish({...})`.
- `repositories/anton-abyzov/vskill-platform/src/lib/scanner.ts:200-265` — discovery convention (`claude-skill` topic, `**/SKILL.md`, folder name = skill name) that `setTopics()` must satisfy.
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts:1-80` — referenced only as the destination of the optional handoff URL; not called directly from Studio in Phase 0.
- `@octokit/rest` (new dep, server-side only — does not ship to the browser bundle).
