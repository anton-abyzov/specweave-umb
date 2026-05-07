---
increment: 0831-skill-studio-enterprise-tier
title: "Skill Studio enterprise tier — tasks"
status: planned
created: 2026-05-07
test_mode: TDD
---

# Tasks: Skill Studio enterprise tier

<!-- AC coverage map: every AC-ID from spec.md is covered by at least one task below. -->

---

## Phase 1 — Backend foundation (vskill-platform, P0)

### T-001: Prisma migration — User tier + quota fields + PricingWaitlist model
**User Story**: US-006, US-009 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US9-02
**Status**: [ ] Not Started
**Plan component**: `User.tier`, `User.lastReportedSkillCount`, `User.quotaSyncedAt`, `PricingWaitlist` (plan.md §2 — vskill-platform table)
**ADR**: ADR-0831-04

**Test Plan**:
- Given the vskill-platform Prisma schema at `repositories/anton-abyzov/vskill-platform/prisma/schema.prisma`
- When migration `0831_user_tier` is applied via `npx prisma migrate dev`
- Then: (AC-US6-01) `User` table has column `tier UserTier @default(FREE)` with enum `FREE | PRO | ENTERPRISE`; (AC-US6-02) `skillLimit` is computable as `50` for FREE and `null` for PRO/ENTERPRISE; (AC-US6-03) `User` has `lastReportedSkillCount Int?` and `quotaSyncedAt DateTime?`; (AC-US9-02) `PricingWaitlist` model exists with `@@unique([email, tier])` constraint.

**TDD cycle**:
- RED: write Vitest integration test asserting the new fields + enum exist via `prisma.$queryRaw` and `PricingWaitlist` upsert on a test DB
- GREEN: write and apply the Prisma migration
- REFACTOR: verify `npx prisma generate` produces typed accessors, clean up test fixtures

---

### T-002: `verifyGithubToken` helper + `requireUserOrGithubBearer` middleware
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-04
**Status**: [ ] Not Started
**Plan component**: `auth::verifyGithubToken` at `src/lib/auth-github.ts`; `requireUserOrGithubBearer` extension to `src/lib/auth.ts` (plan.md §2)
**ADR**: ADR-0831-04, Risk R-5

**Test Plan**:
- Given a valid GitHub OAuth Bearer token `gho_valid` and a stubbed `https://api.github.com/user` response
- When `verifyGithubToken(request)` is called
- Then: (AC-US6-01) returns `{ githubId, login, avatarUrl }`; (AC-US6-04) with missing token returns `null`; KV cache key `gh-token:${sha256(token)}` is written with 300s TTL; second call with same token hits KV and skips GitHub API call.

**TDD cycle**:
- RED: unit tests for `verifyGithubToken` with mocked KV + fetch
- GREEN: implement `src/lib/auth-github.ts` with KV caching + `requireUserOrGithubBearer` in `src/lib/auth.ts`
- REFACTOR: extract SHA-256 key helper; ensure Bearer header is stripped from any logging

---

### T-003: `GET /api/v1/billing/quota` endpoint
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-04, AC-US6-05, AC-US6-06
**Status**: [ ] Not Started
**Plan component**: `src/app/api/v1/billing/quota/route.ts` (GET) (plan.md §2)

**Test Plan**:
- Given `src/app/api/v1/billing/quota/route.ts` with `requireUserOrGithubBearer`
- When `GET /api/v1/billing/quota` is called with each auth state:
  - (AC-US6-04) no auth → 401
  - (AC-US6-04) invalid token → 401
  - (AC-US6-01) free-tier Bearer → `{ tier:"free", skillCount:N, skillLimit:50, gracePeriodDaysRemaining:7, serverNow: <ISO> }`
  - (AC-US6-02) pro-tier Bearer → `skillLimit: null`
  - (AC-US6-01) enterprise Bearer → `tier:"enterprise"`, `skillLimit: null`
- Then (AC-US6-05) all four states are covered by integration tests; (AC-US6-06) `serverNow` is present in every 200 response.

**TDD cycle**:
- RED: integration tests for all four auth states using a test DB + mocked GitHub `/user`
- GREEN: implement GET handler; compute `skillCount` from `Skill` table where `userId = user.id`
- REFACTOR: extract `computeSkillLimit(tier)` helper; add OpenAPI JSDoc block

---

### T-004: `POST /api/v1/billing/quota` telemetry endpoint
**User Story**: US-006 | **Satisfies ACs**: AC-US6-03, AC-US6-04, AC-US6-05
**Status**: [ ] Not Started
**Plan component**: same `route.ts` file, POST method (plan.md §2)

**Test Plan**:
- Given an authenticated free-tier user with `lastReportedSkillCount = null`
- When `POST /api/v1/billing/quota` with body `{ skillCount: 23 }` is called
- Then: (AC-US6-03) `User.lastReportedSkillCount` is set to `23` and `User.quotaSyncedAt` is updated; (AC-US6-04) 401 on missing auth; (AC-US6-04) 429 with `Retry-After` header after 6 calls in 60s from same user; (AC-US6-05) integration test covers rate-limit path.

**TDD cycle**:
- RED: POST tests including rate-limit path using Cloudflare KV rate-counter stub
- GREEN: implement POST handler; upsert `lastReportedSkillCount` + `quotaSyncedAt`; wire rate-limiter (6/min/user via KV counter)
- REFACTOR: consolidate rate-limit logic with any existing rate-limiter pattern in the codebase

---

### T-005: Pricing page `/pricing` + waitlist endpoint + nav link
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-03, AC-US9-04, AC-US9-05
**Status**: [ ] Not Started
**Plan component**: `src/app/pricing/page.tsx`, `src/app/api/v1/waitlist/route.ts`, `src/app/account/subscription/page.tsx`, `SiteNav.tsx` (plan.md §2)

**Test Plan**:
- Given a request to `GET /pricing` with JavaScript disabled (Playwright `javaScriptEnabled: false`)
- When the page is rendered server-side
- Then: (AC-US9-01) three columns Free/Pro/Enterprise with feature rows are present in the HTML; (AC-US9-03) `<title>`, `<meta name="description">`, and OG `<meta property="og:image">` tags are present; (AC-US9-04) page renders without JS errors; (AC-US9-05) `<a href="/account/subscription">` exists; (AC-US9-02) `POST /api/v1/waitlist` with `{ email, tier }` returns 200 and upserts `PricingWaitlist`; nav contains "Pricing" link.

**TDD cycle**:
- RED: Playwright test asserting 3-column structure + SSR; Vitest unit test for waitlist POST
- GREEN: implement `page.tsx` as Next.js `export default async function Page()` with no client JS; implement `route.ts` (waitlist); add placeholder `/account/subscription`; add nav link
- REFACTOR: verify page passes Core Web Vitals in Playwright; ensure "Notify me" form degrades gracefully without JS

---

## Phase 2 — Auth layer (vskill desktop, P0)

### T-006: Add `keyring` crate + `auth::token_store` module
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-04, AC-US2-02
**Status**: [ ] Not Started
**Plan component**: `src-tauri/src/auth/token_store.rs` (plan.md §2); ADR-0831-01

**Test Plan**:
- Given `keyring = "3"` added to `src-tauri/Cargo.toml`
- When `TokenStore::set("github.access_token", "gho_test")` is called followed by `TokenStore::get("github.access_token")` and then `TokenStore::delete("github.access_token")`
- Then: (AC-US1-04) `get` returns `Ok(Some("gho_test"))`; `delete` returns `Ok(())`; subsequent `get` returns `Ok(None)`; (AC-US2-02) token cannot be found after delete; macOS Keychain Access.app shows entry under service `vskill` for the set operation.

**TDD cycle**:
- RED: Rust `#[cfg(test)]` tests for set/get/delete round-trip; test that value is not present in memory after `zeroize` (use `secrecy` or `zeroize` crate)
- GREEN: implement `token_store.rs` wrapping `keyring::Entry`; key namespace `"vskill"` / `"github.access_token"`
- REFACTOR: add `#[derive(ZeroizeOnDrop)]` on any in-memory token wrapper; confirm `cargo test` passes on macOS

---

### T-007: `auth::device_flow` state machine
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-06
**Status**: [ ] Not Started
**Plan component**: `src-tauri/src/auth/device_flow.rs` (plan.md §2); ADR-0831-02, Risk R-6

**Test Plan**:
- Given a mocked `github.com` server returning `{ user_code:"AB12-CD34", device_code, interval:5, expires_in:900 }` from the device-code endpoint
- When the device-flow state machine runs
- Then: (AC-US1-02) state transitions `Idle → Requesting → Waiting(user_code)` before any browser is opened; (AC-US1-03) polling fires at `interval` seconds; state transitions to `Granted` on token response, `Denied` on `access_denied`, `Expired` on `expired_token`; (AC-US1-06) `NetworkError` state is reached on HTTP failure and exposes an error message string; all transitions are observable via returned `DeviceFlowState` enum values.

**TDD cycle**:
- RED: Rust unit tests for each state transition using `mockito` or an in-process HTTP stub
- GREEN: implement `device_flow.rs` with `tokio::time::sleep` honoring `interval` + `slow_down` (increase interval by 5s per `slow_down` response)
- REFACTOR: ensure `device_code` is zeroed from memory after `Granted`; verify state machine handles `expires_in` countdown correctly

---

### T-008: `auth::github_client` — `get_user`, `get_repo`, `revoke_token`
**User Story**: US-001, US-002, US-004 | **Satisfies ACs**: AC-US1-05, AC-US2-02, AC-US4-02
**Status**: [ ] Not Started
**Plan component**: `src-tauri/src/auth/github_client.rs` (plan.md §2)

**Test Plan**:
- Given a mocked GitHub API with a valid Bearer token
- When `github_client::get_user(token)` is called
- Then: (AC-US1-05) returns `{ login, avatar_url, id }`; (AC-US2-02) `revoke_token(token, client_id, client_secret)` calls `DELETE /applications/{client_id}/token` and returns `Ok(())`; (AC-US4-02) `get_repo(owner, repo, token)` returns `{ private: bool, default_branch: String }`; all calls add `Authorization: Bearer {token}` and strip it from log output.

**TDD cycle**:
- RED: Rust unit tests for each client method with mocked HTTP responses (200, 401, 404, 422)
- GREEN: implement `github_client.rs` using `reqwest` (already in Cargo deps); add `zeroize` on token before drop
- REFACTOR: consolidate base-URL constant; add `User-Agent: vskill-desktop` header required by GitHub API

---

### T-009: Tauri IPC commands — auth (`auth_start_device_flow`, `auth_poll_token`, `auth_get_user`, `auth_sign_out`)
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04, AC-US1-06, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [ ] Not Started
**Plan component**: `commands::auth_*` in `src-tauri/src/commands.rs` (plan.md §2)

**Test Plan**:
- Given T-006 (TokenStore) and T-007 (DeviceFlow) are GREEN
- When each IPC command is invoked from the TypeScript bridge
- Then: (AC-US1-01) `auth_start_device_flow` returns `{ user_code, verification_uri }`; (AC-US1-03) `auth_poll_token` returns current `DeviceFlowState` as a serialized enum variant; (AC-US1-04) on `Granted`, `token_store.set` is called — Keychain entry verified; (AC-US1-06) `auth_poll_token` on `NetworkError` returns an error payload with `message` field; (AC-US2-01) `auth_sign_out` removes keychain entry; (AC-US2-02) `auth_sign_out` calls `github_client::revoke_token`; (AC-US2-04) if revocation fails, sign-out still removes local token and returns `{ localOnly: true }`; (AC-US2-03) `auth_sign_out` emits `auth://signed-out` Tauri event; (AC-US2-05) tier reverts to `free` in AuthContext after event.

**TDD cycle**:
- RED: Tauri command handler unit tests using `tauri::test` harness for each IPC
- GREEN: wire commands in `commands.rs`, register in `main.rs` `invoke_handler` (or `generate_handler!`)
- REFACTOR: group all auth commands under `#[tauri::command]` module; confirm no token leaks in `serde` serialization output

---

### T-010: `AuthContext` + `useDesktopBridge` auth hooks (TypeScript)
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-05, AC-US2-03, AC-US2-05
**Status**: [ ] Not Started
**Plan component**: `src/eval-ui/src/AuthContext.tsx` (new); `useDesktopBridge.ts` extension (plan.md §2)

**Test Plan**:
- Given T-009 IPC commands are wired and a mocked `@tauri-apps/api/core::invoke` bridge
- When `AuthContext` mounts
- Then: (AC-US1-05) calls `auth_get_user`; on success sets `{ user: { login, avatarUrl }, tier: "free"|"pro", skillCount, skillLimit }`; (AC-US2-03) on `auth://signed-out` Tauri event, resets state to `{ user: null, tier: "free" }`; (AC-US2-05) after sign-out all tier-gated checks return `false`; context value is stable across re-renders (memoized).

**TDD cycle**:
- RED: Vitest tests using `@testing-library/react` + mock `invoke` and `listen` from `@tauri-apps/api`
- GREEN: implement `AuthContext.tsx` with `createContext`, `useEffect` for startup `auth_get_user`, `listen("auth://signed-out", ...)` cleanup
- REFACTOR: extract `useTauriEvent(event, handler)` utility to avoid repeated `listen`/`unlisten` boilerplate

---

### T-011: `SignInPanel` + `UserMenu` UI components
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-06, AC-US2-01, AC-US2-04
**Status**: [ ] Not Started
**Plan component**: `SignInPanel.tsx`, `UserMenu.tsx` wired into `Sidebar.tsx` header (plan.md §2)

**Test Plan**:
- Given `AuthContext` providing `{ user: null }` (signed-out state)
- When `<SignInPanel>` renders
- Then: (AC-US1-01) user code `"AB12-CD34"` is displayed in a `<code>` element with `aria-label="Authorization code"`; copy-to-clipboard button is present; (AC-US1-02) "Open GitHub" button calls `shell.open("https://github.com/login/device")`; (AC-US1-06) when `DeviceFlowState.NetworkError`, inline error message and "Try again" button appear; when `AuthContext` provides `{ user: { login:"devon", avatarUrl:"..." } }`, `<UserMenu>` renders avatar + login + tier badge; (AC-US2-01) "Sign out" option is present; (AC-US2-04) after sign-out with `localOnly: true`, toast "Local sign-out complete; remote revocation will retry on next launch" appears.

**TDD cycle**:
- RED: Vitest + RTL component tests; Playwright smoke for copy-to-clipboard
- GREEN: implement both components; plug `<UserMenu>` into `Sidebar.tsx` header slot (above the existing folder section)
- REFACTOR: verify WAI-ARIA dialog pattern for sign-in panel; check keyboard navigation in Playwright

---

## Phase 3 — Smart folder picker (vskill desktop, P0)

### T-012: `project::folder_picker::classify` — four-way path classifier
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-06
**Status**: [ ] Not Started
**Plan component**: `src-tauri/src/project/folder_picker.rs` (plan.md §2); ADR-0831-03

**Test Plan**:
- Given the ordered ruleset from ADR-0831-03
- When `classify(path)` is called with each test case
- Then returns the correct `FolderClass` variant:
  - `os.homedir()` → `HomeRoot` (AC-US3-01)
  - `~/.claude/skills/` → `PersonalScope` (AC-US3-03)
  - `~/.claude/agents/` → `PersonalScope` (AC-US3-03)
  - `~/projects/my-app` with `.git/` → `ProjectRoot` (AC-US3-04)
  - `~/projects/my-app` with `package.json` → `ProjectRoot`
  - `~/projects/my-app` with `.specweave/` → `ProjectRoot`
  - Empty dir under `~` → `ProjectRoot` (weak, no signal, no warning)
  - Non-existent path → `Invalid` (AC-US3-06)
  - Path to a file, not dir → `Invalid` (AC-US3-06)

**TDD cycle**:
- RED: 9 Rust unit tests for the above cases using `tempdir` + conditional home-dir mock
- GREEN: implement `folder_picker.rs` using `std::path`, `dirs::home_dir()`
- REFACTOR: ensure classifier is pure (no I/O side effects for unit testability); I/O (exists check, is_dir check) injected via trait for mocking

---

### T-013: `project_pick_folder` IPC + `FolderPickerDialog` React component
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-05, AC-US3-06
**Status**: [ ] Not Started
**Plan component**: `commands::project_pick_folder` in `commands.rs`; `FolderPickerDialog.tsx` (plan.md §2)

**Test Plan**:
- Given T-012 classifier is GREEN and `tauri-plugin-dialog::open` is available
- When user clicks "Open project folder" then selects their home directory
- Then: (AC-US3-01) modal warning "This is your home directory…" appears; (AC-US3-02) "Pick again" button re-invokes the dialog; "Use home anyway" proceeds and sets `FolderClass::HomeRoot` in UI state; (AC-US3-05) last 5 picked folders (excluding home-re-warned ones after first confirmation) appear in "Recent" list sorted MRU; (AC-US3-06) if dialog is cancelled, no state change occurs; if a non-existent path is provided programmatically, an inline error message is shown.

**TDD cycle**:
- RED: Vitest component test for `FolderPickerDialog` with mocked `invoke("project_pick_folder", ...)` returning `HomeRoot`
- GREEN: implement IPC command returning `{ path, class: "home_root"|"personal_scope"|"project_root"|"invalid" }`; implement `FolderPickerDialog.tsx` handling all four class variants
- REFACTOR: ensure "Personal scope" label appears in the sidebar when `class === "personal_scope"` per AC-US3-03

---

### T-014: Persist recent folders to `settings.recents` + `project_recents` IPC
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05
**Status**: [ ] Not Started
**Plan component**: `Settings::recents` extension in `preferences/settings.rs`; `commands::project_recents` (plan.md §2)

**Test Plan**:
- Given settings.json is written after `project_pick_folder` is called
- When the Tauri app is restarted and `project_recents` IPC is invoked
- Then: (AC-US3-05) the last 5 picked folders are returned in MRU order; folders beyond 5 are evicted; home-dir picks that were confirmed with "Use home anyway" are stored with a `confirmed: true` flag so the warning does not re-fire on re-select.

**TDD cycle**:
- RED: Rust integration test serializing + deserializing `Settings` with `recents.projectFolders` populated
- GREEN: extend `Settings` struct with `recents: RecentsCache { project_folders: Vec<RecentFolder> }` (max 5, MRU); implement `project_recents` Tauri command
- REFACTOR: verify schema stays forward-compatible — unknown keys preserved on round-trip

---

## Phase 4 — Connected-repo widget (vskill desktop, P0)

### T-015: `project::repo_detect` — git remote + sync state detection
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-04, AC-US4-05, AC-US4-06
**Status**: [ ] Not Started
**Plan component**: `src-tauri/src/project/repo_detect.rs` (plan.md §2)

**Test Plan**:
- Given a temporary git repository with a `github.com` remote
- When `repo_detect::detect(path)` is called via `tokio::join!` on four git sub-commands
- Then: (AC-US4-01) returns `{ owner:"owner", repo:"repo", branch:"main" }`; (AC-US4-04) sync state is one of `UpToDate | AheadN(u32) | BehindN(u32) | Diverged(u32,u32) | UncommittedChanges | NoUpstream`; (AC-US4-05) a folder with a non-GitHub remote returns `ExternalGit { host }` variant; (AC-US4-05) a git folder with no remote returns `LocalOnly`; (AC-US4-06) a non-git folder returns `NotGit`.

**TDD cycle**:
- RED: Rust tests using `tempdir` + `std::process::Command` to init git repos with controlled state for each variant
- GREEN: implement `repo_detect.rs` running `git -C {path} remote get-url origin`, `branch --show-current`, `status --porcelain`, `rev-list --count --left-right HEAD...origin/{branch}` in parallel
- REFACTOR: extract git-invocation helper to avoid repeated `Command::new("git")` boilerplate; timeout each sub-command at 5s

---

### T-016: `ConnectedRepoWidget` React component (replaces `SidebarGitHubIndicator`)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06, AC-US4-07
**Status**: [ ] Not Started
**Plan component**: `ConnectedRepoWidget.tsx` (replaces `SidebarGitHubIndicator.tsx`) (plan.md §2, §Phase 3)

**Test Plan**:
- Given T-015 IPC providing each repo detect variant and T-008 `get_repo` returning `{ private: true }`
- When `<ConnectedRepoWidget>` renders for each state
- Then: (AC-US4-01) `github-public` state shows `owner/repo`, branch name, and a status icon; (AC-US4-02) private repo shows lock icon with `aria-label="Private repository"`; (AC-US4-03) public+verified shows green check with `aria-label="Public, verified"`; (AC-US4-04) sync state pill shows correct text; (AC-US4-05) `LocalOnly` renders "Local-only (no remote)"; (AC-US4-05) `ExternalGit` renders "External git ({host})"; (AC-US4-06) `NotGit` renders "Not a git project" with link to docs; (AC-US4-07) "Refresh" button calls `project_get_repo_state` IPC; FS watcher event `repo://updated` triggers re-render.

**TDD cycle**:
- RED: Vitest + RTL tests for each render state; Playwright e2e for manual refresh click
- GREEN: implement `ConnectedRepoWidget.tsx`; delete `SidebarGitHubIndicator.tsx`; wire `tauri-plugin-fs::watchImmediate` on `.git/HEAD` (debounced 500ms) via `useEffect`
- REFACTOR: ensure `aria-label` text alternatives pass axe-core scan in Playwright

---

## Phase 5 — Quota + paywall (vskill-platform + vskill desktop, P0)

### T-017: `quota::cache` + Settings extension (`QuotaCache`)
**User Story**: US-010 | **Satisfies ACs**: AC-US10-01, AC-US10-02, AC-US10-03, AC-US10-04
**Status**: [ ] Not Started
**Plan component**: `src-tauri/src/quota/cache.rs`; `Settings::quota: QuotaCache` (plan.md §2); ADR-0831-04, ADR-0831-05

**Test Plan**:
- Given `settings.json` with a `quota` block containing `{ tier:"free", skillLimit:50, cachedAt:"2026-05-01T00:00:00Z", serverNow:"2026-05-01T00:00:01Z" }`
- When `QuotaCache::is_fresh()` is called at various `now()` values
- Then: (AC-US10-01) cache reads `tier`, `skillLimit`, `cachedAt`, `serverNow`; (AC-US10-02) 6 days after `serverNow` → `is_fresh() = true`; 8 days after `serverNow` → `is_fresh() = false`; (AC-US10-03) free-tier cache still enforces `skillLimit:50` when fresh; (AC-US10-04) after `QuotaCache::update(new_response)`, `cachedAt` is reset to current `serverNow`.

**TDD cycle**:
- RED: Rust unit tests with time injection (trait `fn now() -> DateTime<Utc>`) to avoid real-clock dependency
- GREEN: implement `quota/cache.rs`; extend `Settings` struct with `pub quota: Option<QuotaCache>`; write migration logic for `None` (first launch)
- REFACTOR: apply ADR-0831-05 `serverNow`-based clock; store `clockSkewMs` for drift detection

---

### T-018: `quota::sync` background task + `quota_force_sync` IPC
**User Story**: US-010 | **Satisfies ACs**: AC-US10-04, AC-US10-05, AC-US10-06
**Status**: [ ] Not Started
**Plan component**: `src-tauri/src/quota/sync.rs`; `commands::quota_force_sync` (plan.md §2)

**Test Plan**:
- Given T-003 quota endpoint is deployed and T-017 `QuotaCache` is implemented
- When `quota::sync::start()` is called on app launch with a valid keychain token
- Then: (AC-US10-05) sync fires immediately on launch, after sign-in/out, and on 1h timer; (AC-US10-06) on HTTP 5xx, a single non-intrusive toast is emitted and work continues; (AC-US10-04) successful sync calls `QuotaCache::update`; `quota://updated` Tauri event is emitted; `quota_force_sync` IPC with `?fresh=1` busts the platform-side KV and returns an updated cache within 5s (hard timeout per plan non-functional requirements).

**TDD cycle**:
- RED: Rust async tests using a mocked HTTP server (3 attempts x exponential backoff) and a fake timer
- GREEN: implement `quota/sync.rs` with `tokio::time::interval(Duration::from_secs(3600))`; wire `quota_force_sync` command
- REFACTOR: verify 3-retry exponential backoff (1s/4s/16s); confirm 5s hard timeout on `quota_force_sync`

---

### T-019: `SkillCountBadge` in StatusBar + `quota_can_create_skill` IPC
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-06, AC-US5-07
**Status**: [ ] Not Started
**Plan component**: `StatusBar.tsx` extension + `commands::quota_can_create_skill` (plan.md §2)

**Test Plan**:
- Given `AuthContext` providing `{ tier:"free", skillCount:47, skillLimit:50 }`
- When `<SkillCountBadge>` renders
- Then: (AC-US5-01) displays "47/50" in status bar; Pro user context (`skillLimit: null`) displays "Unlimited"; (AC-US5-02) at counts 45-50 badge color is warning yellow with `title="Approaching free-tier limit"`; (AC-US5-06) `quota_can_create_skill` IPC counts skills across all opened project roots + `~/.claude/skills/` deduplicated by `name@version`; (AC-US5-07) count is computed locally and reconciled with last-cached quota response (no per-create API call).

**TDD cycle**:
- RED: Vitest tests for badge rendering at count 44 (normal), 47 (warning), 51 (should not be shown — paywall fires first); Rust unit test for `quota_can_create_skill` skill-counting logic across multiple roots
- GREEN: extend `StatusBar.tsx`; implement `quota_can_create_skill` Rust command walking `~/.claude/skills/` + each open project root, deduplicating on `name@version`
- REFACTOR: extract skill-counting logic into `quota::count` module for testability

---

### T-020: `PaywallModal` component + 51st-skill create intercept
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03, AC-US5-04, AC-US5-05
**Status**: [ ] Not Started
**Plan component**: `PaywallModal.tsx`; intercept in skill-create IPC path (plan.md §2 + §Phase 4)

**Test Plan**:
- Given `AuthContext` providing `{ tier:"free", skillCount:50, skillLimit:50 }` and a mocked `quota_can_create_skill` returning `blocked: true`
- When the user attempts to create a new skill
- Then: (AC-US5-04) skill file is NOT written and skill registry is NOT updated; (AC-US5-03) `<PaywallModal>` appears with "You've reached the 50-skill free tier…" copy; "Upgrade" button calls `shell.open("https://verified-skill.com/pricing")`; "Maybe later" closes the modal; (AC-US5-05) existing skills above limit remain visible and editable (no delete/hide); modal has WAI-ARIA `role="dialog"` with focus trap and ESC key closes.

**TDD cycle**:
- RED: Vitest + RTL tests for PaywallModal rendering and keyboard interaction; integration test asserting skill-create IPC returns `{ blocked: true }` without side effects when at limit
- GREEN: implement `PaywallModal.tsx`; wrap existing skill-create IPC handler to call `quota_can_create_skill` before any FS write
- REFACTOR: verify focus trap with axe-core; confirm `shell.open` URL uses `tierFeatures` canonical pricing URL constant

---

### T-021: Quota force-sync on 51st create — race condition resolution
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04, AC-US5-07
**Status**: [ ] Not Started
**Plan component**: quota force-sync in skill-create intercept (plan.md §Phase 4, Risk R-2)

**Test Plan**:
- Given a user at 50 skills locally but just upgraded to Pro (cache is stale)
- When the 51st skill create is attempted
- Then: (AC-US5-04) paywall is shown based on cached state; (AC-US5-07) a background `quota_force_sync` with `?fresh=1` is fired; if sync returns `tier:"pro"`, the paywall modal auto-dismisses and the create proceeds; if sync fails or times out (5s), the create remains blocked and the user sees the paywall; (AC-US5-04) in all failure paths, no partial skill file is written.

**TDD cycle**:
- RED: async integration test simulating stale cache + pro-upgrade race; test the 5s timeout path
- GREEN: implement the force-sync + conditional dismiss in the paywall controller; `?fresh=1` handled in platform quota route (bust KV cache)
- REFACTOR: use a `tokio::select!` for the 5s timeout vs sync response; confirm no skill write occurs in the timeout path

---

## Phase 6 — Tier-aware gates (vskill desktop, P0)

### T-022: `tierFeatures` lookup + `TierGate` component
**User Story**: US-008 | **Satisfies ACs**: AC-US8-02, AC-US8-03, AC-US8-04, AC-US8-05, AC-US8-06
**Status**: [ ] Not Started
**Plan component**: `src/eval-ui/src/lib/tier-features.ts`; `TierGate.tsx` (plan.md §2)

**Test Plan**:
- Given `tier-features.ts` exporting `{ "private-repos": ["pro","enterprise"], "github-app": ["pro","enterprise"] }`
- When `<TierGate feature="private-repos" />` renders with `AuthContext` providing `{ tier:"free" }`
- Then: (AC-US8-05) gate evaluates `tierFeatures["private-repos"].includes("free") === false` → renders locked slot; (AC-US8-03) all "Upgrade" buttons rendered by TierGate link to the same URL (single constant from `tier-features.ts`); (AC-US8-02) gate renders inline (no modal), not full-screen; (AC-US8-04) with `{ user: null }` (anonymous), TierGate renders "Sign in to continue" instead of the upgrade prompt; (AC-US8-06) upgrade CTA copy contains no countdown, urgency, or "act now" language (linting test via content snapshot).

**TDD cycle**:
- RED: Vitest tests for each tier/feature combination; snapshot test for CTA copy content
- GREEN: implement `tier-features.ts` with exported `PRICING_URL` constant; implement `TierGate.tsx` consuming `AuthContext`
- REFACTOR: run copy snapshot through a wordlist linter asserting absence of dark-pattern phrases ("act now", "limited time", "expire")

---

### T-023: Private-repo lock state in `ConnectedRepoWidget` + free-tier upgrade CTA
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02
**Status**: [ ] Not Started
**Plan component**: `ConnectedRepoWidget.tsx` extension; `TierGate` integration (plan.md §Phase 3 + §Phase 5)

**Test Plan**:
- Given `AuthContext` with `{ tier:"free" }` and `ConnectedRepoWidget` showing a private GitHub repo (`repo_detect` returns `private`)
- When the widget renders
- Then: (AC-US8-01) the locked state shows "Private repos are a Pro feature" and an inline "Upgrade" button (not a modal); (AC-US8-02) no full-screen modal appears — the gate is inline within the widget; clicking "Upgrade" opens `shell.open(PRICING_URL)` and does NOT trigger any confirmation dialog.

**TDD cycle**:
- RED: Vitest test for `ConnectedRepoWidget` in `tier:"free"` + `private:true` state
- GREEN: add `<TierGate feature="private-repos">` branch in `ConnectedRepoWidget` for the locked render state
- REFACTOR: verify the upgrade CTA is keyboard-reachable; confirm no modal side-effect

---

## Phase 7 — GitHub App install flow (vskill + platform, P1)

### T-024: GitHub App install CTA + Pro tier detection in `ConnectedRepoWidget`
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-05
**Status**: [ ] Not Started
**Plan component**: `ConnectedRepoWidget` + `commands::project_get_repo_state`; `tauri-plugin-shell` (plan.md §Phase 5)

**Test Plan**:
- Given `AuthContext` with `{ tier:"pro" }` and a folder whose remote is a private GitHub repo where the GitHub App is NOT installed (`get_repo` returns 404)
- When `ConnectedRepoWidget` renders the `private-needs-app` state
- Then: (AC-US7-01) CTA "Install GitHub App" is visible; (AC-US7-02) clicking CTA calls `shell.open("https://github.com/apps/verified-skill/installations/new?state=<state_token>")`; (AC-US7-05) free-tier user sees `<TierGate>` ("Private repos are a Pro feature") NOT the install CTA; Pro user sees install CTA NOT the tier gate.

**TDD cycle**:
- RED: Vitest tests for `ConnectedRepoWidget` in `pro` + `private-needs-app` state and `free` + `private` state
- GREEN: wire `private-needs-app` render branch with GitHub App install URL; reuse existing `installation/init` URL from platform (confirmed from Inherited Givens)
- REFACTOR: generate `state_token` (random UUID) per open; store it so the callback can validate it

---

### T-025: Installation callback + re-detect on `quota://updated`
**User Story**: US-007 | **Satisfies ACs**: AC-US7-03, AC-US7-04, AC-US7-06
**Status**: [ ] Not Started
**Plan component**: deep-link handler `vskill://installation-complete`; quota sync re-triggering repo state refresh (plan.md §Phase 5)

**Test Plan**:
- Given the user has completed GitHub App installation in browser and the platform has received the callback
- When the deep-link `vskill://installation-complete?installation_id=12345` fires in the Tauri app
- Then: (AC-US7-03) the app calls `project_get_repo_state` which re-runs `repo_detect` + `github_client::get_repo`; (AC-US7-04) if installation is confirmed, `ConnectedRepoWidget` transitions to "GitHub App connected" badge state; (AC-US7-06) on next quota sync after App uninstall on GitHub (detected via 404 on `get_repo` or missing installation in platform), widget reverts to `private-needs-app` state.

**TDD cycle**:
- RED: Tauri deep-link handler test simulating `installation-complete` event; Vitest test for `ConnectedRepoWidget` uninstall reversion
- GREEN: register deep-link handler in `main.rs`; emit `repo://refresh` on `installation-complete`; `ConnectedRepoWidget` listens and re-fetches
- REFACTOR: confirm `state_token` from T-024 is validated before trusting `installation_id`

---

### T-026: "Connect private repos" button in Preferences Account tab
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02
**Status**: [ ] Not Started
**Plan component**: new Account tab in `src/eval-ui/src/preferences/` (plan.md §Existing code references)

**Test Plan**:
- Given a Pro-tier signed-in user opening Preferences
- When the Account tab renders
- Then: (AC-US7-01) "Connect private repos" button is visible; (AC-US7-02) clicking it calls `shell.open(GITHUB_APP_INSTALL_URL)` — same URL as the widget CTA; free-tier users see the button disabled with tooltip "Available on Pro".

**TDD cycle**:
- RED: Vitest + RTL test for the Account tab in pro vs free state
- GREEN: add Account tab component to preferences; wire to existing `GITHUB_APP_INSTALL_URL` constant from T-024
- REFACTOR: ensure Preferences tab titles are i18n-safe (use `locales/` JSON key)

---

## Phase 8 — Polish + verification (P1)

### T-027: Unit tests — folder classifier edge cases (10 parameterized cases)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-06
**Status**: [ ] Not Started
**Plan component**: supplements T-012 with an exhaustive parameterized test suite (plan.md §Phase 2)

**Test Plan**:
- Given the `classify(path)` function from T-012
- When each of the following paths is passed
- Then the expected variant is returned (10 parameterized cases via `#[rstest]`):
  1. Exact `HOME` → `HomeRoot`
  2. `HOME/.claude/skills/` → `PersonalScope`
  3. `HOME/.claude/agents/skills/` → `PersonalScope`
  4. `HOME/.claude/` (parent) → `PersonalScope`
  5. `HOME/projects/my-app` with `.git/` → `ProjectRoot`
  6. `HOME/projects/my-app` with `package.json` → `ProjectRoot`
  7. `HOME/projects/my-app` with `.specweave/` → `ProjectRoot`
  8. Empty existing dir (no signals) → `ProjectRoot` (weak, no warning)
  9. Non-existent path → `Invalid`
  10. Path to a file → `Invalid`

**TDD cycle**:
- RED: write Rust `#[rstest]` parameterized tests for all 10 cases; this task IS the test (classifier was already implemented in T-012 — these confirm no regression and fill coverage gaps)
- GREEN: fix any edge case failures found; add missing `dirs` dependency if not already present
- REFACTOR: ensure each case has a descriptive `#[case]` name visible in `cargo test` output

---

### T-028: Integration tests — quota endpoint (all four auth states + rate-limit)
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-04, AC-US6-05, AC-US6-06
**Status**: [ ] Not Started
**Plan component**: supplements T-003/T-004 with a complete integration test suite (plan.md §Phase 4 exit criteria)

**Test Plan**:
- Given the quota route is deployed in a test Cloudflare Workers environment with a seeded test DB
- When `GET /api/v1/billing/quota` is called for each auth state
- Then (AC-US6-05):
  - Anonymous → 401 `{ error:"unauthorized" }`
  - Free-tier Bearer → `{ tier:"free", skillLimit:50, serverNow: <ISO> }`
  - Pro-tier Bearer → `{ tier:"pro", skillLimit:null, serverNow: <ISO> }`
  - Enterprise Bearer → `{ tier:"enterprise", skillLimit:null, serverNow: <ISO> }`
  - POST with `{ skillCount:23 }` → upserts `lastReportedSkillCount`; 7th POST within 60s → 429 + `Retry-After`.

**TDD cycle**:
- RED: Vitest integration tests using `@cloudflare/vitest-pool-workers` with test DB fixtures for each tier
- GREEN: verify T-003 + T-004 implementations pass all cases (fix if any gaps found)
- REFACTOR: extract test fixtures into `tests/fixtures/quota-users.ts` for reuse; confirm OpenAPI doc matches actual response shapes

---

### T-029: Offline grace-period boundary tests (7-day cache + reconnect prompt)
**User Story**: US-010 | **Satisfies ACs**: AC-US10-01, AC-US10-02, AC-US10-03, AC-US10-04, AC-US10-05, AC-US10-06
**Status**: [ ] Not Started
**Plan component**: quota cache + sync integration (plan.md §Phase 4 exit criteria + ADR-0831-05)

**Test Plan**:
- Given a seeded `settings.json` with quota cache `serverNow = 7 days ago` (fresh boundary)
- When the app launches with the quota endpoint returning a network error (mocked)
- Then: (AC-US10-02) cache is considered fresh for exactly 7 days; at day 7+1s, `is_fresh()` returns false; (AC-US10-03) free-tier cap still enforced from stale cache; (AC-US10-06) single toast appears on sync failure ("Subscription refresh unavailable — working offline"); no second toast on subsequent failures in the same session; (AC-US10-05) on reconnect, a successful sync resets `cachedAt`.

**TDD cycle**:
- RED: Rust integration tests injecting controlled `serverNow` timestamps at day 6, day 7, and day 8 boundaries; mock HTTP returning 5xx for failure path
- GREEN: fix any edge cases in `quota::cache::is_fresh()` found by boundary tests; implement "single toast per session" deduplication in `quota::sync`
- REFACTOR: confirm clock-skew correction (`clockSkewMs` delta) is applied in all `is_fresh()` comparisons per ADR-0831-05

---

### T-030: E2E Playwright — auth flow + folder pick + 50-skill paywall
**User Story**: US-001, US-003, US-005 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US3-01, AC-US5-03, AC-US5-04
**Status**: [ ] Not Started
**Plan component**: `e2e/desktop/auth-flow.spec.ts` (plan.md §Phase 2 suggestion)

**Test Plan**:
- Given a running Tauri dev instance with stubbed IPC (device-flow, classifier, quota) injected via `VITE_TEST_STUBS=true`
- When the full sign-in → folder-pick → 50-skill-paywall flow is exercised
- Then:
  - (AC-US1-01) sign-in button opens `SignInPanel` showing an 8-character code
  - (AC-US1-02) "Open GitHub" triggers `shell.open` stub with `https://github.com/login/device`
  - (AC-US1-03) device-flow stub resolves to `Granted` after 1 poll interval; `SignInPanel` closes
  - (AC-US1-04) Keychain stub records `set("github.access_token", ...)` call
  - (AC-US3-01) opening home dir shows warning modal with correct text
  - (AC-US5-03) on 51st skill create attempt, `PaywallModal` appears with "Upgrade" CTA
  - (AC-US5-04) skill count does not increment after blocked create attempt
  - All assertions recorded as Playwright screenshots in `e2e/screenshots/auth-flow/`

**TDD cycle**:
- RED: write failing Playwright spec; all assertions fail until implementation is complete
- GREEN: spec passes with stubbed IPC; verify no real Keychain or GitHub API calls are made during CI
- REFACTOR: extract stub injection helper into `e2e/helpers/stub-ipc.ts`; add test to CI pipeline

---

## AC Coverage Summary

| AC-ID | Covered by |
|---|---|
| AC-US1-01 | T-009, T-011, T-030 |
| AC-US1-02 | T-007, T-011, T-030 |
| AC-US1-03 | T-007, T-009, T-030 |
| AC-US1-04 | T-006, T-009, T-030 |
| AC-US1-05 | T-008, T-010 |
| AC-US1-06 | T-007, T-009, T-011 |
| AC-US2-01 | T-009, T-011 |
| AC-US2-02 | T-006, T-008, T-009 |
| AC-US2-03 | T-009, T-010 |
| AC-US2-04 | T-009, T-011 |
| AC-US2-05 | T-009, T-010 |
| AC-US3-01 | T-012, T-013, T-027, T-030 |
| AC-US3-02 | T-012, T-013, T-027 |
| AC-US3-03 | T-012, T-013, T-027 |
| AC-US3-04 | T-012, T-013, T-027 |
| AC-US3-05 | T-013, T-014 |
| AC-US3-06 | T-012, T-013, T-027 |
| AC-US4-01 | T-015, T-016 |
| AC-US4-02 | T-008, T-016 |
| AC-US4-03 | T-016 |
| AC-US4-04 | T-015, T-016 |
| AC-US4-05 | T-015, T-016 |
| AC-US4-06 | T-015, T-016 |
| AC-US4-07 | T-016 |
| AC-US5-01 | T-019 |
| AC-US5-02 | T-019 |
| AC-US5-03 | T-020, T-030 |
| AC-US5-04 | T-020, T-021, T-030 |
| AC-US5-05 | T-020 |
| AC-US5-06 | T-019 |
| AC-US5-07 | T-019, T-021 |
| AC-US6-01 | T-001, T-003, T-028 |
| AC-US6-02 | T-001, T-003, T-028 |
| AC-US6-03 | T-001, T-004, T-028 |
| AC-US6-04 | T-002, T-003, T-004, T-028 |
| AC-US6-05 | T-003, T-004, T-028 |
| AC-US6-06 | T-003, T-028 |
| AC-US7-01 | T-024, T-026 |
| AC-US7-02 | T-024, T-026 |
| AC-US7-03 | T-025 |
| AC-US7-04 | T-025 |
| AC-US7-05 | T-023, T-024 |
| AC-US7-06 | T-025 |
| AC-US8-01 | T-022, T-023 |
| AC-US8-02 | T-022, T-023 |
| AC-US8-03 | T-022 |
| AC-US8-04 | T-022 |
| AC-US8-05 | T-022 |
| AC-US8-06 | T-022 |
| AC-US9-01 | T-005 |
| AC-US9-02 | T-001, T-005 |
| AC-US9-03 | T-005 |
| AC-US9-04 | T-005 |
| AC-US9-05 | T-005 |
| AC-US10-01 | T-017 |
| AC-US10-02 | T-017, T-029 |
| AC-US10-03 | T-017, T-029 |
| AC-US10-04 | T-017, T-018, T-029 |
| AC-US10-05 | T-018, T-029 |
| AC-US10-06 | T-018, T-029 |
