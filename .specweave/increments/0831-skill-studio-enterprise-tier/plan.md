---
increment: 0831-skill-studio-enterprise-tier
title: "Architecture plan — Skill Studio enterprise tier (GitHub OAuth + smart folder picker + private repo support + 50-skill free tier)"
status: planned
created: 2026-05-07
spec: ./spec.md
---

# Architecture Plan: Skill Studio enterprise tier

## Architecture overview

This increment splits cleanly across two repos. **vskill** (the Tauri desktop shell + browser studio runtime) gets the identity layer, project-scope detection, the connected-repo widget, the skill-counter + paywall, and the tier-aware UI gates. **vskill-platform** (Next.js 15 on Cloudflare Workers) gets the `/api/v1/billing/quota` authoritative-tier endpoint and a server-rendered `/pricing` page with a waitlist sink. The two halves communicate over HTTPS using an OAuth bearer token the desktop holds in the OS keychain — no client secret ever touches the binary because GitHub's Device Authorization Grant (RFC 8628) carries the public `client_id` only, and GitHub returns a long-lived user-token directly to the desktop after the user authorizes the device code at `github.com/login/device`. This token is the single trust anchor: vskill-platform validates it by calling GitHub's `/user` endpoint and matches `githubId` against the existing `User` table from increment 0826.

The free-tier ceiling is a **server-authoritative count, locally cached for offline use**. The desktop computes its own count by walking opened project roots + `~/.claude/skills/` and posts it to `/api/v1/billing/quota` for reconciliation; the server returns the canonical `{ tier, skillCount, skillLimit, gracePeriodDaysRemaining, serverNow }` shape and that response is cached in `~/.vskill/settings.json::quota` with a `cachedAt` timestamp. While the cache is fresh (<7 days) the desktop enforces the limit from cache; older than 7 days the studio degrades to a "reconnect to refresh subscription" prompt. Private-repo support is a **separate code path** layered on top: the OAuth user-token can read the user's own private repos, but for cross-org / fine-grained access we lean on the existing GitHub App (the `Tenant` model already maps `installation_id → org`). Free tier never installs the App; Pro tier is offered the App-install CTA from the connected-repo widget.

```mermaid
sequenceDiagram
    participant U as User
    participant D as Skill Studio (Tauri)
    participant K as OS Keychain (keyring)
    participant GH as github.com
    participant P as vskill-platform

    U->>D: Click "Sign in with GitHub"
    D->>GH: POST /login/device/code (client_id only)
    GH-->>D: { user_code, device_code, verification_uri, interval, expires_in }
    D-->>U: Show user_code "AB12-CD34" + "Open GitHub"
    U->>D: Click "Open GitHub"
    D->>GH: shell.open(verification_uri)
    Note over U,GH: User pastes user_code, approves device in browser
    loop poll every <interval> until granted/expired
        D->>GH: POST /login/oauth/access_token (device_code, grant_type)
        GH-->>D: pending | slow_down | denied | expired | { access_token }
    end
    D->>K: keyring.set("vskill", "github.access_token", token)
    D->>P: GET /api/v1/billing/quota (Authorization Bearer token)
    P->>GH: GET /user (token validation)
    GH-->>P: { id, login, avatar_url }
    P->>P: lookup User.tier and compute skillLimit
    P-->>D: { tier:free, skillCount, skillLimit:50, gracePeriodDaysRemaining:7, serverNow }
    D-->>U: Sidebar shows avatar + Free badge; status-bar shows 47/50
```

## Component map

### vskill (desktop shell + studio runtime)

**Project**: vskill (for every module in this section)

| Module | Path | Responsibility |
|---|---|---|
| `auth::device_flow` | `src-tauri/src/auth/device_flow.rs` (new) | RFC 8628 client: POST device-code, poll token, surface state machine to UI via Tauri commands. Talks **directly to github.com** — no platform proxy. |
| `auth::token_store` | `src-tauri/src/auth/token_store.rs` (new) | Wrapper over `keyring` crate (macOS Keychain, Win Credential Manager, libsecret). Single API: `set/get/delete("github.access_token")`. |
| `auth::github_client` | `src-tauri/src/auth/github_client.rs` (new) | Thin HTTP client for `/user`, `/repos/{owner}/{repo}` (visibility check), `/applications/{client_id}/token` DELETE for revoke. Adds `Authorization: Bearer` header. |
| `project::folder_picker` | `src-tauri/src/project/folder_picker.rs` (new) | Wraps `tauri-plugin-dialog::open({directory:true})`, normalizes path, classifies as `home_root` / `personal_scope` / `project_root` / `invalid`. |
| `project::repo_detect` | `src-tauri/src/project/repo_detect.rs` (new) | Reads `.git/config` for `[remote "origin"]` URL, extracts `owner/repo` for `github.com` URLs, runs `git status` + `git rev-list` for sync state. Shells out to `git` (already a hard dep). |
| `quota::cache` | `src-tauri/src/quota/cache.rs` (new) | Reads/writes `settings.quota` block (extends `Settings` with `QuotaCache { tier, skill_count, skill_limit, cached_at, server_now, clock_skew_ms }`). |
| `quota::sync` | `src-tauri/src/quota/sync.rs` (new) | Periodic timer task: polls `/api/v1/billing/quota` on launch + every 1h while online + after sign-in/out. Emits `quota://updated` Tauri event. |
| `Settings::quota` (extension) | `src-tauri/src/preferences/settings.rs` | Add `pub quota: QuotaCache` field, `pub recents: RecentsCache` (last 5 picked folders). Schema stays v1 with backfill defaults — unknown-key-preservation handles forward-compat. |
| `commands::auth_*` | `src-tauri/src/commands.rs` | Add Tauri commands: `auth_start_device_flow`, `auth_poll_token`, `auth_sign_out`, `auth_get_user`. |
| `commands::project_*` | `src-tauri/src/commands.rs` | Add: `project_pick_folder`, `project_get_repo_state`, `project_recents`. |
| `commands::quota_*` | `src-tauri/src/commands.rs` | Add: `quota_get`, `quota_force_sync`, `quota_can_create_skill`. |
| **UI: SignInPanel** | `src/eval-ui/src/components/SignInPanel.tsx` (new) | Device-flow UX: shows user_code + copy button + "Open GitHub" button + polling spinner + error/retry. |
| **UI: UserMenu** | `src/eval-ui/src/components/UserMenu.tsx` (new) | Avatar dropdown in sidebar header; shows login + tier badge + "Sign out". |
| **UI: ConnectedRepoWidget** | `src/eval-ui/src/components/ConnectedRepoWidget.tsx` (replaces `SidebarGitHubIndicator.tsx`) | Repo name + branch + lock/check badges + sync state. Subscribes to `repo://updated` events. |
| **UI: FolderPickerDialog** | `src/eval-ui/src/components/FolderPickerDialog.tsx` (new) | Triggers Tauri `project_pick_folder`, handles home-dir warning modal, recents list. |
| **UI: SkillCountBadge** | extends `src/eval-ui/src/components/StatusBar.tsx` | Adds `47/50` counter with warn-color at 45-50, `Unlimited` for Pro. |
| **UI: PaywallModal** | `src/eval-ui/src/components/PaywallModal.tsx` (new) | Hard-block on 51st create. "Upgrade" → `shell.open` pricing URL. |
| **UI: TierGate** | `src/eval-ui/src/components/TierGate.tsx` (new) | Generic inline gate component consuming `tierFeatures` lookup. Used by ConnectedRepoWidget for private repos. |
| **UI: tierFeatures** | `src/eval-ui/src/lib/tier-features.ts` (new) | Single-source-of-truth lookup: `{ "private-repos": ["pro","enterprise"], "github-app": ["pro","enterprise"] }`. |
| **UI: AuthContext** | `src/eval-ui/src/AuthContext.tsx` (new) | React context providing `{ user, tier, skillCount, skillLimit, isOnline, lastSyncAt }`. Subscribes to `auth://*` and `quota://updated`. |

### vskill-platform (Next.js 15 on Cloudflare Workers)

**Project**: vskill-platform (for every module in this section)

| Module | Path | Responsibility |
|---|---|---|
| `/api/v1/billing/quota` (GET) | `src/app/api/v1/billing/quota/route.ts` (new) | Validates Bearer token via GitHub `/user`, looks up `User.tier`, computes `skillCount` from `Skill` table, returns canonical quota shape. |
| `/api/v1/billing/quota` (POST) | same file | Accepts `{ skillCount }` from desktop, upserts `User.lastReportedSkillCount` for telemetry & overage detection. |
| `auth::verifyGithubToken` | `src/lib/auth-github.ts` (new) | Helper: takes raw `Authorization: Bearer` value, calls `https://api.github.com/user`, returns `{ githubId, login, avatarUrl }` or `null`. Cached 5 min in KV by `sha256(token)` to avoid hitting GitHub on every request. |
| `requireUserOrGithubBearer` | `src/lib/auth.ts` (extension) | New helper: tries cookie-based `requireUser` first, falls back to Bearer-token validation. Used by quota route to support both browser and desktop. |
| `User.tier` field | `prisma/schema.prisma` | New nullable enum `UserTier { FREE PRO ENTERPRISE }` defaulting to `FREE`. Prisma migration `0831_user_tier`. |
| `User.lastReportedSkillCount` | `prisma/schema.prisma` | New nullable `Int` field. |
| `User.quotaSyncedAt` | `prisma/schema.prisma` | New nullable `DateTime` for server-side reconciliation tracking. |
| `/pricing` page | `src/app/pricing/page.tsx` (new) | Server-rendered three-column comparison (Free/Pro/Enterprise). No JS for the comparison; "Notify me" form is progressively-enhanced. |
| `/pricing` waitlist | `src/app/api/v1/waitlist/route.ts` (new) | POST `{ email, tier }` upserts to new `PricingWaitlist` Prisma model. Mirrors existing `VideoNotification` pattern. |
| `PricingWaitlist` model | `prisma/schema.prisma` | `{ id, email, tier (PRO/ENTERPRISE), createdAt, source, confirmed }` with `@@unique([email, tier])`. |
| `/account/subscription` page | `src/app/account/subscription/page.tsx` (new) | Placeholder route; renders "Available once billing launches" card. |
| nav link | `src/components/SiteNav.tsx` | Add "Pricing" entry between existing nav items. |

## Phase plan

### Phase 1 — Token store + device-flow auth (vskill)
Goal: user can sign in and the app remembers them across launches.

1. Add `keyring = "3"` to `Cargo.toml`. Implement `auth::token_store`. Smoke-test on macOS with a known string round-trip.
2. Implement `auth::device_flow` (POST `/login/device/code`, polling loop honoring `interval` + `slow_down`). State machine: `Idle → Requesting → Waiting(user_code) → Polling → {Granted, Denied, Expired, NetworkError}`.
3. Implement `auth::github_client::get_user()` and `revoke_token()`.
4. Wire Tauri commands. Build `SignInPanel.tsx` + `UserMenu.tsx`. Hook the avatar into `Sidebar.tsx`'s header.
5. On startup, attempt `token_store.get()` — if present, fetch `/user` and populate AuthContext.

**Exit criteria**: AC-US1-01..06, AC-US2-01..05 pass; token visible in macOS Keychain Access.app under service `vskill`.

### Phase 2 — Smart folder picker (vskill)
Goal: the picker correctly distinguishes personal-scope from project-scope and warns on `~`.

1. Implement `project::folder_picker::classify(path)` returning the four-way enum. Rules: equals `os.homedir()` → `home_root`; under `~/.claude/` → `personal_scope`; contains `.git/` OR `package.json` OR `.specweave/` → `project_root`; else → `project_root` weak (no warning).
2. Implement `project::repo_detect` — shells out to `git -C <path> remote get-url origin`, `git -C <path> branch --show-current`, `git -C <path> status --porcelain`, `git -C <path> rev-list --count --left-right HEAD...origin/<branch>`. Calls run in parallel via `tokio::join!`.
3. Build `FolderPickerDialog.tsx` with the home-dir warning + recents list.
4. Persist `settings.recents.projectFolders` (max 5, MRU eviction).

**Exit criteria**: AC-US3-01..06 pass; recents survive restart.

### Phase 3 — Connected-repo widget (vskill)
Goal: sidebar shows live repo state with public/private badge.

1. Replace `SidebarGitHubIndicator.tsx` with `ConnectedRepoWidget.tsx`. Render states: `not-git`, `local-only`, `external-git`, `github-public`, `github-private-readable`, `github-private-locked`, `private-needs-app`.
2. For private-repo visibility: call `auth::github_client::get_repo(owner, repo)` — 200 = readable, 404 = either not-found OR private-and-no-access (treat as `private-needs-app`).
3. Public+verified-registry check: hit `https://verified-skill.com/api/v1/registry/check?repo=owner/repo`. If endpoint missing, fall back to neutral icon (this is P1 polish).
4. Debounced refresh on `tauri-plugin-fs::watchImmediate` over `.git/HEAD` and `.git/index`. Manual refresh button in widget.

**Exit criteria**: AC-US4-01..07 pass on a folder with a public repo, a private repo (signed in), and a non-git folder.

### Phase 4 — Quota endpoint + paywall (vskill-platform + vskill)
Goal: 50-skill cap enforced server-side, locally cached, with paywall modal.

1. **Platform**: Prisma migration adds `User.tier UserTier @default(FREE)`, `User.lastReportedSkillCount Int?`, `User.quotaSyncedAt DateTime?`.
2. **Platform**: implement `auth::verifyGithubToken` with KV cache (key = `gh-token:${sha256(token)}`, TTL 300s). Implement `requireUserOrGithubBearer`.
3. **Platform**: implement `/api/v1/billing/quota` GET + POST. POST is rate-limited to 6/min/user. Add OpenAPI doc + integration tests for all four states (anonymous → 401; free; pro; enterprise).
4. **Desktop**: implement `quota::cache` and `quota::sync` (timer + on-launch). Extend `Settings::quota`.
5. **Desktop**: extend `StatusBar.tsx` with skill counter; build `PaywallModal.tsx`; intercept `commands::create_skill` (or whatever the existing skill-creation path is) and call `quota_can_create_skill` first.
6. **Desktop**: 51st-create flow — when blocked, show paywall AND trigger a synchronous `quota_force_sync` (with `?fresh=1` to bust KV cache) in the background; if the sync returns Pro, dismiss paywall and proceed (handles the "user just upgraded" race).

**Exit criteria**: AC-US5-01..07, AC-US6-01..06, AC-US10-01..06 pass.

### Phase 5 — GitHub App install + pricing page (both repos)
Goal: Pro tier gets a path to install the App on private repos; pricing page lands.

1. **Desktop**: when `repo_detect` returns `private-needs-app` AND tier is Pro/Enterprise, render the "Install GitHub App" CTA in `ConnectedRepoWidget`. CTA opens `https://verified-skill.com/api/v1/auth/github/installation/init` in browser.
2. **Desktop**: register `tauri-plugin-deep-link` handler for `vskill://installation-complete?installation_id=...` so the studio re-detects the new installation without manual refresh.
3. **Desktop**: when free tier, render `<TierGate feature="private-repos" />` instead — inline "Upgrade" CTA opens `/pricing`.
4. **Platform**: build `/pricing` page (server-rendered, SEO meta, OG image), `PricingWaitlist` Prisma model, `/api/v1/waitlist` endpoint, `/account/subscription` placeholder, nav link.

**Exit criteria**: AC-US7-01..06, AC-US8-01..06, AC-US9-01..05 pass.

## ADRs (5 — to be written into `.specweave/docs/internal/architecture/adr/`)

### ADR-0831-01 — Token storage = `keyring` crate (vs `tauri-plugin-stronghold`, `tauri-plugin-store`)
We pick the `keyring` Rust crate (~100KB binary impact, direct Keychain/Cred-Manager/libsecret bindings, no schema/init dance) over `tauri-plugin-stronghold` (~4MB, encrypted vault file requires user-provided password to unlock — wrong UX for "remember me silently") and `tauri-plugin-store` (plaintext JSON — unfit for tokens). Our tokens are GitHub OAuth user-tokens (`gho_...`), which are sensitive enough to warrant OS-level keychain isolation but **not** so high-value that the per-app encrypted-vault overhead of Stronghold is justified. `keyring` is a thin, purpose-built abstraction; it's already in production for `cargo`, `rustup`, and `gh` itself. Cross-platform consistency: macOS Keychain, Windows Credential Manager, Linux Secret Service (libsecret) — all three covered by one crate.

### ADR-0831-02 — Free tier = OAuth-only; Pro tier = OAuth + opt-in GitHub App
For free-tier identity + own-private-repo reads, GitHub OAuth user-tokens are sufficient and have lower friction (one approval at `github.com/login/device`). For paid tier we layer the existing GitHub App on top — App installation tokens grant org-scoped, fine-grained, higher-rate-limit access that OAuth user-tokens cannot match. The two coexist: OAuth always carries identity; App install is an additive capability gated to Pro+. This avoids forcing a heavyweight App install on free users (who often won't have admin rights on their employer's org) while keeping the upgrade path obvious. Rejected alternative: GitHub App for everyone (too much friction for the free hobbyist persona; many users can't self-install on their org).

### ADR-0831-03 — Folder picker disambiguation rules
A path is classified by an ordered ruleset: (1) equals `os.homedir()` → `home_root` (warn modal); (2) under `~/.claude/` → `personal_scope` (no project-connect attempt, neutral label); (3) contains any of `.git/`, `package.json`, `.specweave/` → `project_root` (run repo_detect); (4) else → `project_root` with no strong signal but no warning either (covers e.g. an empty new-project folder). We deliberately don't treat presence-of-files as a hard requirement for project-root because a user opening a fresh empty dir to start a new skill set is a valid flow. Rejected alternative: ML-classify or content-walk the dir — overkill, slow, and the user knows their own intent better than we do; the warning modal at `~` gives them a chance to correct.

### ADR-0831-04 — Server-authoritative quota tracking with local cache (vs client-side trust)
The skill-count limit is enforced from the server's view of the user's account (sum of `Skill` rows owned by the user across all tenants they belong to), not from the desktop's count of files on disk. The desktop reports its local count via POST for telemetry and so we can detect overages caused by manual file copies, but the **enforcement** path is `/api/v1/billing/quota → User.tier → skillLimit lookup`. The desktop caches the latest response in `settings.quota` to keep working offline. This prevents three abuse vectors at once: (a) deleting `~/.vskill/settings.json` to reset the counter, (b) git-cloning skills onto disk to bypass the in-app create flow, (c) running an old desktop version that doesn't know about new limits. Rejected: pure-client trust (trivially bypassable) and per-create API call (latency on a hot path; offline-hostile).

### ADR-0831-05 — Offline grace period = 7 days based on `serverNow` from last sync
The cache freshness window is 7 days, computed as `(serverNow_at_last_sync) + 7d`, NOT `cachedAt + 7d`. The reason: a user with a wrong machine clock (common on Linux distros after a battery-drained laptop boots) would otherwise either lock themselves out or get free unlimited time. We trust the server's clock. The desktop stores both `serverNow` and the local `Date.now()` at sync time; the delta becomes the clock-skew estimate, applied to all subsequent `now()` checks within that grace window. After 7 days from `serverNow`, the studio shows a non-blocking "Reconnect to refresh subscription" banner; tier is enforced from the last-known cache (so a Pro user stays Pro, a free user stays free) for an additional 24h hard-stop window before the studio refuses to load skills (the practical impact: a Pro user at sea for 8 days still gets Pro for the first day after landfall, then must reconnect). Rejected alternatives: 30 days (too long — stale tier could mask cancellations), no grace (offline-hostile, breaks the travel persona).

## Risks

- **R-1 — Token theft via process inspection.** A local-machine attacker with `ptrace` or memory-dump capability on the running Tauri process can read the OAuth token in cleartext while the studio is running, even with `keyring` storing it at rest. **Mitigation**: token is only loaded into memory on demand and zeroed via `zeroize` crate after each HTTP call; rotation requires manual user sign-out + sign-in (GitHub OAuth tokens have no programmatic refresh). **Acceptance**: this matches the threat model of every desktop app on the user's machine — the right defense is OS-level (FileVault, etc.), not in-app.
- **R-2 — Race condition on quota check.** The 51st-skill paywall makes a synchronous quota sync call before blocking. If the user just upgraded but the sync's KV cache returns the stale "free" tier (5-min TTL on `gh-token:` cache), the user sees the paywall despite being Pro. **Mitigation**: the POST `/api/v1/billing/quota` call **busts** the user's KV entry on every successful POST, and the paywall's force-sync uses GET with a `?fresh=1` query param that the route handler interprets as "skip KV cache". Trade-off: rare extra GitHub API call (~1 per paywall trigger).
- **R-3 — GitHub API rate limits.** Free OAuth tokens get 5,000 req/hr/user. The connected-repo widget making `/repos/{owner}/{repo}` calls on every refresh + the platform validating tokens via `/user` could push enterprise users near limit. **Mitigation**: platform-side KV cache on `/user` (5-min TTL); desktop-side `/repos/...` calls only fire on folder-change or manual refresh, not on a timer. **Monitor**: log 403 responses with `X-RateLimit-Remaining: 0` to tail-end alerting.
- **R-4 — Stripe-not-yet-shipped paywall UX.** Users click "Upgrade" → land on a "Coming Soon — Notify me" page → may feel teased and bounce. **Mitigation**: pricing page copy is honest ("Pro launches Q3 2026 — get notified and lock in early-bird pricing"), the waitlist email is double-opt-in (mirror `VideoNotification.confirmed`), and the desktop paywall copy reads "Upgrade (joining waitlist)" not "Upgrade now" so expectations are set before the click. Acceptance: this is a known v1 cost — this increment ships the seam, not the checkout.
- **R-5 — JWT-vs-Bearer auth split between desktop and platform.** vskill-platform's existing browser-facing routes use cookie-based JWT (`vskill_access`); the desktop has no cookies and uses raw GitHub OAuth Bearer tokens. The `/api/v1/billing/quota` route must recognize both: (a) `Authorization: Bearer gho_...` from desktop → validate via GitHub `/user`; (b) `Cookie: vskill_access=...` from web → reuse existing `requireUser`. **Mitigation**: implement a new `requireUserOrGithubBearer(request)` helper in `lib/auth.ts` that tries both paths; document in OpenAPI which auth methods are accepted.
- **R-6 — Device-flow proxy gate (architectural escape hatch).** The existing `/api/v1/auth/github/device-flow/{code,token}` routes require `requireUser` (cookie auth) — they were built for the CLI-after-login flow. The desktop **cannot** use them on first sign-in (chicken-and-egg). **Decision**: the desktop bypasses the platform proxy entirely on first-time auth and talks **directly to `github.com/login/device/code`** + `github.com/login/oauth/access_token` with the public `client_id` baked into the binary. The platform proxy stays for the CLI's enterprise-egress use case but is not on the desktop's hot path. **Follow-up**: enterprise customers behind a strict egress firewall that blocks `github.com` directly will need a future "use platform proxy" toggle in advanced settings (deferred to a later increment).

## Non-functional requirements

- **Performance**: device-flow first poll → token-in-keychain in **<3s on a 50ms RTT connection** (excludes user-typing-code time at GitHub). Quota sync round-trip <500ms p95. ConnectedRepoWidget refresh <300ms p95 (mostly bound by `git status` exec).
- **Reliability**: 7-day offline grace per ADR-0831-05; every network call has exponential-backoff retry (3 attempts, 1s/4s/16s) before surfacing error. Paywall force-sync has a 5s hard timeout — on timeout, fall back to cached state.
- **Security**: tokens stored via `keyring` only — never in `settings.json`, never in logs, never in crash reports (`PrivacySettings` already exposes `crash_reporting_enabled`). Network calls strip `Authorization` header from any reqwest log middleware. Token in memory zeroed via `zeroize` after each use. CSRF-state cookie on GitHub App install init already in place (verified from existing code).
- **Accessibility**: paywall modal traps focus per WAI-ARIA dialog pattern, ESC closes, primary action is keyboard-reachable in tab order, `aria-describedby` on the modal points at the cap explanation. SignInPanel's user_code is a `<code>` with `aria-label="Authorization code"` for screen readers; copy-button has visible focus ring. ConnectedRepoWidget badges have `aria-label` text alternatives ("Private repository", "Public, verified").
- **Observability**: server logs `auth.github.bearer.{success, fail_404, fail_401}` counters per request to `/api/v1/billing/quota`. Desktop emits `quota.sync.{ok, network_error, timeout, auth_error}` to local log only (privacy-respecting — never phoned home).
- **Internationalization**: all new UI strings go through the existing `locales/` JSON files (already used by PreferencesApp). Pricing page is English-only in v1.

## Existing code references

- vskill-platform device-flow endpoints: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/auth/github/device-flow/{code,token}/route.ts` — currently gated by `requireUser`; **NOT used by desktop on first auth** per Risk R-6.
- vskill-platform GitHub App endpoints: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/auth/github/installation/{init,callback,uninstall}/route.ts` — desktop opens `init` URL via `tauri-plugin-shell` for the Pro-tier App-install flow (US-007).
- vskill desktop settings store: `repositories/anton-abyzov/vskill/src-tauri/src/preferences/settings.rs` — extend with `quota: QuotaCache` and `recents: RecentsCache` fields (additive, schema stays at v1, unknown-key-preservation handles forward-compat).
- vskill desktop preferences UI: `repositories/anton-abyzov/vskill/src/eval-ui/src/preferences/` — new auth tab can be added later but is **not in scope** for v1 (sign-in lives in the main sidebar's UserMenu, not in preferences).
- vskill existing GitHub indicator: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/SidebarGitHubIndicator.tsx` (85 LOC) — replaced wholesale by `ConnectedRepoWidget.tsx`.
- vskill main sidebar: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/Sidebar.tsx` (1502 LOC) — UserMenu + ConnectedRepoWidget plug into the existing header/section structure.
- vskill status bar: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/StatusBar.tsx` (221 LOC) — extended with SkillCountBadge.
- vskill-platform Prisma schema: `repositories/anton-abyzov/vskill-platform/prisma/schema.prisma` — extend `User` model; new `PricingWaitlist` model (mirror `VideoNotification` pattern).

## Out-of-band assumptions

1. **OAuth client_id is already provisioned for the desktop.** vskill-platform has `VSKILL_GITHUB_CLIENT_ID`; the desktop binary embeds the same `client_id` (it's public; safe to ship). If a separate "Skill Studio Desktop" OAuth App is preferred for telemetry separation, that's a configuration ask, not an architecture change.
2. **GitHub App slug `verified-skill` is correct** per the existing `installation/init` route. Confirmed.
3. **`User.tier` defaults to FREE** for all 0826-existing users. The migration sets the default; no backfill needed beyond the column default. Granted Pro upgrades happen via direct DB write by ops in v1 (Stripe wiring will replace this in the follow-up increment).
4. **The `tier_features` lookup is shipped in code, not a DB table.** Adding a feature requires a code change. This is intentional — feature flags belong in code review until the surface area justifies a runtime config layer (post-MVP).

---

**End of plan.md.**
