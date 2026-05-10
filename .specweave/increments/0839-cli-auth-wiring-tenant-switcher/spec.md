---
status: completed
---
# 0839 — CLI Auth Wiring + Tenant Switcher

## Problem

Increment 0834 shipped a substantial auth foundation: User → OrgMember → Tenant → Installation → ApiToken model, GitHub OAuth + Device Flow + JWT, account cabinet UI. But the auth foundation is **invisible to the CLI's hot path**:

1. **CLI commands are anonymous.** `vskill add`, `install`, `list`, `marketplace` all hit the registry without ever reading the keychain Bearer token. Researcher (researcher-vskill-auth-current, 2026-05-09) confirmed zero occurrences of `Authorization` or `getGitHubToken` in `src/api/client.ts` or these four commands.
2. **No tenant picker in Studio.** When a user belongs to N>1 GitHub orgs that have the App installed, `ConnectGitHubCard` only handles the empty-state — there's no UI to pick which tenant to operate against.
3. **No CLI tenant switcher.** Even with the keychain wired up, there's no `vskill orgs` / `vskill whoami` to discover or switch tenants from the terminal.
4. **No `vsk_` token at login.** Login stores only the raw `gho_` GitHub OAuth token. The platform's `requireUserOrGithubBearer` (vskill-platform/src/lib/auth/bearer.ts:223) already supports both, but the CLI never asks for the entitlement-aware `vsk_` token, leaving the door closed for per-token revocation, scope-limited tokens, and entitlement gating in 0840.

This increment closes those four gaps so 0834 actually shows up in the developer experience.

## Out of Scope

- **Stripe entitlement check on install** — deferred to 0840
- **`publish --private` / submit private flag** — deferred to 0840
- **Enterprise SSO (SAML, SCIM)** — separate roadmap
- **Token rotation / refresh flows** — token TTL is set at mint; rotation is a future increment
- **Studio Tauri-app native keychain bridge** — Studio uses HTTP via the eval-server proxy; reading `~/.vskill/config.json` for tenant selection is sufficient

## User Stories

### US-001 — vskill CLI sends Bearer on registry calls
**As a** logged-in CLI user
**I want** `vskill add`, `install`, `list`, `marketplace` to authenticate automatically
**So that** I can see and install skills published to my private tenant

**Acceptance Criteria**
- [x] AC-US1-01: `src/api/client.ts` adds an Authorization header `Bearer ${token}` on every outbound request when a token is present in the keychain.
- [x] AC-US1-02: When no token is present in the keychain, requests proceed anonymously (preserves current OSS / public-skills flow). No prompt, no error.
- [x] AC-US1-03: `vskill add <skill>`, `vskill list`, `vskill marketplace`, and `vskill add --interactive` (wizard) all flow through `client.ts` and inherit the Bearer interceptor without per-command changes. Verified by grep: zero new direct `fetch(` calls in those commands.
- [x] AC-US1-04: When the registry returns 401 (token invalid/expired), the CLI prints `Authentication failed. Run \`vskill auth login\` to re-authenticate.` and exits non-zero. Token is NOT auto-deleted (user might be on a flaky network).
- [x] AC-US1-05: When the registry returns 403 (token valid but no entitlement for this skill), the CLI prints the upstream error message verbatim plus an upgrade URL if present in the response body.
- [x] AC-US1-06: Token is read from keychain ONCE per command invocation and cached for the duration of the process — keychain is not hit per request.

### US-002 — CLI install resolver tries tenant-scoped lookups
**As a** CLI user installing a private skill
**I want** the resolver to try the public registry, then each tenant I'm a member of, and fail with a clear message if not found
**So that** I don't have to know which tenant owns a skill before I install it

**Acceptance Criteria**
- [x] AC-US2-01: `vskill add <skill>` resolution order: (1) public registry, (2) tenant-scoped registry for the active tenant from `~/.vskill/config.json`, (3) other tenants the user is a member of (parallel HEAD requests, first match wins).
- [x] AC-US2-02: A new `--tenant <slug>` flag overrides the active tenant for a single invocation. When set, only the public registry and that tenant are tried.
- [x] AC-US2-03: Auto-pick when N=1 tenant: if the user belongs to exactly one tenant and no `--tenant` flag is set, that tenant is used silently (no prompt).
- [x] AC-US2-04: Ambiguity handling for N>1 with no active tenant: if the skill is found in 2+ tenants and the user has no active tenant set, the CLI prints `Skill found in multiple tenants: acme, contoso. Re-run with --tenant <slug> or set an active tenant: vskill orgs use <slug>.` and exits non-zero.
- [x] AC-US2-05: 402 response handling: if the platform returns 402 Payment Required (skill exists in a tenant but user lacks entitlement), the CLI prints the response's `upgradeUrl` field if present, else `Upgrade required: <message>`. Non-zero exit.
- [x] AC-US2-06: Tenant-scoped requests include the header `X-Vskill-Tenant: <slug>` in addition to the Authorization header. Platform routes will already accept this (no platform changes needed in this increment).

### US-003 — `vskill orgs` and `vskill whoami` commands
**As a** CLI user
**I want** `vskill orgs list/use/current` and `vskill whoami` commands
**So that** I can discover, switch, and verify my tenant context from the terminal

**Acceptance Criteria**
- [x] AC-US3-01: `vskill orgs list` calls `GET /api/v1/account/tenants` (new endpoint, see plan.md) and prints a table: `slug | name | role | active`. Active tenant marked with `*`.
- [x] AC-US3-02: `vskill orgs use <slug>` validates the slug against the user's tenant list, then writes `currentTenant: "<slug>"` to `~/.vskill/config.json`. If slug is unknown, exits non-zero with `Unknown tenant: <slug>` followed by `Available: <slug1>, <slug2>` (when the user has tenants). [Amendment 2026-05-10 closure] The original spec text suggested `Run \`vskill orgs list\` to see options.`; the shipped UX surfaces the available slugs inline, which is strictly more helpful and semantically equivalent. Accepted as implemented.
- [x] AC-US3-03: `vskill orgs current` reads `~/.vskill/config.json` and prints the active tenant slug, or `(none)` if unset. Exit code 0 either way.
- [x] AC-US3-04: `vskill whoami` combines `vskill auth status` and `vskill orgs current` into a single multi-line block:
  ```
  Logged in as @<github-login>
  Token: vsk_* (vsk_xxxxxxxx…)   # or gho_* (gho_xxxxxxxx…) in legacy mode
    GitHub token: gho_* (gho_xxxxxxxx…)   # only printed when both are stored
  Active tenant: <slug>           # or "(none)"
  Tenants:
    * acme-corp — Acme Corp (admin)
      contoso — Contoso (member)
  ```
  If not logged in, prints `Not logged in. Run \`vskill auth login\`.` and exits non-zero.

  [Amendment 2026-05-10 closure] The original spec literal text was `Logged in as: anton.abyzov@gmail.com (gho_xxxx…) / Active tenant: ... / Tenants: ...`. The shipped output diverges in two ways:
  1. **No email** — the User row populated by the device-flow exchange route only captures `githubUsername` (no `email` column), so `Logged in as @<login>` is the strongest identity signal we can render. Capturing email would require an additional GitHub /user/emails round-trip and a schema migration; out of scope for this closure pass.
  2. **Multi-line layout** — easier to scan in a terminal than the slash-separated single-line form, and surfaces both stored tokens (vsk_ + gho_) which is a real diagnostic need that the original spec didn't account for.
  Both deviations are accepted as shipped.
- [x] AC-US3-05: Both `orgs` and `whoami` are anonymous-safe — they do NOT crash on missing keychain; they print `Not logged in` and exit (orgs: 0, whoami: 1).
- [x] AC-US3-06: `~/.vskill/config.json` schema is forward-compatible: unknown keys are preserved on writes (read → modify → write the merged object).

### US-004 — Studio tenant switcher
**As a** Studio user belonging to multiple tenants
**I want** a sidebar tenant picker
**So that** I can browse skills, evaluations, and settings for any tenant I'm a member of

**Acceptance Criteria**
- [x] AC-US4-01: A new `<TenantPicker />` component replaces the single-org `<ConnectGitHubCard />` empty state when the user has 1+ tenants. The component renders in the Studio sidebar.
- [x] AC-US4-02: TenantPicker fetches from `GET /api/v1/account/tenants` (same endpoint as CLI) on mount and on focus. Result cached for the session.
- [x] AC-US4-03: Selection persists via the studio runtime endpoint `POST /__internal/active-tenant` (eval-server.ts handler) which writes `currentTenant` to `~/.vskill/config.json` — the SAME file the CLI uses, so CLI and Studio stay in sync.
- [x] AC-US4-04: When N=0 (user has no tenants), the picker shows the existing "Connect GitHub" CTA (preserves the 0834 onboarding flow).
- [x] AC-US4-05: When N=1, the picker is collapsed into a static label `Tenant: acme-corp` (no dropdown — nothing to pick).
- [x] AC-US4-06: All Studio API calls that hit tenant-scoped endpoints include the `X-Vskill-Tenant: <slug>` header sourced from the active tenant. If no tenant is active and the endpoint requires one, the call fails fast with a UI banner `Select a tenant to continue`.

### US-005 — `vsk_` token exchange at login
**As a** CLI user
**I want** `vskill auth login` to also mint a `vsk_`-prefixed verified-skill API token
**So that** future entitlement checks, per-token revocation, and scope-limited automation are possible without re-authenticating

**Acceptance Criteria**
- [x] AC-US5-01: New endpoint `POST /api/v1/auth/github/exchange-for-vsk-token` accepts `{ githubToken: string }` (raw `gho_*`), verifies the token against the GitHub API (`GET /user`), upserts the User record, and mints a new `ApiToken` row with `prefix: "vsk_"`, `scopes: ["read", "write"]`, `tokenHash: sha256(plaintext)`, `tokenPrefix: <first 12 chars>`, and a 90-day expiry.
- [x] AC-US5-02: Response shape: `{ token: "vsk_...", expiresAt: "2026-08-07T...", scopes: ["read","write"], userId: "<cuid>" }`. Plaintext token is returned ONCE — only the hash is stored.
- [x] AC-US5-03: CLI `auth.ts:login()` calls this endpoint immediately after the device-flow returns `gho_*`. On success, both tokens are stored in the keychain under distinct service names: `vskill-github` (gho_, existing) and `vskill-token` (vsk_, new — already referenced in vskill-platform/src/lib/auth/bearer.ts:49).
- [x] AC-US5-04: After successful exchange, `client.ts` interceptor sends the `vsk_` token (preferred) over the `gho_` token. If `vsk_` is missing (legacy login or exchange failed), it falls back to `gho_`.
- [x] AC-US5-05: If `exchange-for-vsk-token` fails (network error, 5xx), login still succeeds with just the `gho_` token. CLI prints `Logged in (legacy mode — some features unavailable).` and continues. No hard failure.
- [x] AC-US5-06: `vskill auth logout` deletes BOTH tokens from the keychain and calls `DELETE /api/v1/auth/sign-out-all` to revoke the `vsk_` token server-side (revocation is best-effort; local logout always succeeds). [Amendment 2026-05-10 closure / F-G01 hotfix] The CLI was already wired to call `DELETE /api/v1/auth/sign-out-all`, but the platform route did not exist on the initial implementation pass — only the cookie-only `POST /api/v1/account/sign-out-all` (from 0834) was present, which the CLI cannot reach (no cookies). The closure-pass hotfix adds a Bearer-accepting `DELETE /api/v1/auth/sign-out-all` route that revokes ONLY the calling vsk_ token (token self-revocation does not require the destructive-op fresh-session gate; possession of the token IS the authorization). Idempotent on already-revoked tokens. 6/6 unit tests passing.

## Non-Functional Requirements

- **Backward compatibility:** every CLI command MUST continue to work for anonymous users hitting public skills. No regressions to the OSS flow.
- **Performance:** keychain read is cached per process; tenant list is cached per Studio session; no N+1 GitHub API calls during install.
- **Security:** `vsk_` token plaintext is returned ONCE at mint; only `tokenHash` is persisted. Token prefix `vsk_` is enforced server-side; `gho_` tokens never round-trip back to the CLI as `vsk_`.
- **Observability:** CLI logs (at `--verbose`) every Authorization header decision: `[auth] using vsk_ token (cached)`, `[auth] no token, anonymous`, `[auth] tenant: acme-corp (from config)`.
- **Test coverage:** unit ≥ 95% on `client.ts` interceptor and `orgs.ts`; integration ≥ 90% on the exchange endpoint and `/account/tenants`; one E2E covering full login → orgs use → install private skill.
