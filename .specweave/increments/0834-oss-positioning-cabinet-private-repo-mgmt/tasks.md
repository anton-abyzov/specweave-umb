# Tasks — 0834 OSS positioning + Account cabinet + Private-repo mgmt parity

**Total**: 32 tasks across 5 agents.
**Status**: 32/32 completed.

## Phase 1 — Upstream (Database + shared types)

### T-001: Prisma schema additions (ConnectedRepo, ApiToken, AccountExport, User extensions)
**Owner**: database-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US5-01, AC-US8-01, AC-US11-02, AC-US10-02, AC-US4-01
**Test**: `npx prisma validate` passes; `npx prisma migrate diff --from-empty --to-schema-datasource prisma/schema.prisma` shows expected SQL; vitest schema test asserts `User.bio`, `User.publicProfile`, `User.notificationPrefs`, `User.deletedAt` exist.

### T-002: Generate migration `0834_account_cabinet`
**Owner**: database-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US5-01, AC-US8-01, AC-US11-02
**Test**: Migration applies on fresh DB without errors; rollback (down migration) restores prior shape.

### T-003: Shared TypeScript types (account.ts in src/lib/types/account.ts)
**Owner**: database-agent (it's the contract producer)
**Status**: [x] completed
**Satisfies ACs**: AC-US4-05, AC-US5-01, AC-US8-02, AC-US10-01, AC-US11-02
**Test**: `tsc --noEmit` passes; types match Prisma model output.

## Phase 2 — Backend API endpoints (vskill-platform)

### T-004: GET/PATCH /api/v1/account/profile
**Owner**: backend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-05
**Test**: Vitest covers (a) unauth → 401, (b) GET returns profile shape, (c) PATCH validates inputs (displayName max 80 chars, bio max 280), (d) PATCH persists.

### T-005: GET /api/v1/account/repos + KV cache
**Owner**: backend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US5-01, AC-US5-03
**Test**: Vitest covers list shape, status computation (all 4 colours), 60s KV cache hit, cache invalidation on connect/disconnect.

### T-006: POST /api/v1/account/repos/{id}/resync
**Owner**: backend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US5-04
**Test**: Vitest covers 202 response, scan-job enqueue, KV cache drop, rate limit 60/min.

### T-007: DELETE /api/v1/account/repos/{id} (soft-disconnect)
**Owner**: backend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-06
**Test**: Vitest covers idempotency (404 → 204), audit log entry, NO call to GitHub uninstall API (mock it; assert not-called).

### T-008: GET /api/v1/account/repos/connect (pre-flight render) + state cookie
**Owner**: backend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US7-01, AC-US7-04
**Test**: Vitest covers SSR copy (verbatim "what we'll see / what we'll never do"), CSRF state cookie set, redirect URL signed.

### T-009: GET /api/v1/account/repos/github/callback
**Owner**: backend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US7-05, AC-US7-07
**Test**: Vitest covers state mismatch → 403, valid state → fetches installation, persists ConnectedRepo rows, redirects to /account/repos.

### T-010: GET/POST /api/v1/account/tokens (list + create)
**Owner**: backend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US8-02, AC-US8-04, AC-US8-07
**Test**: Vitest covers (a) plaintext returned ONCE on POST, (b) list never returns hash/plaintext, (c) hash format vsk_+12char prefix, (d) Bearer auth using created token works on a sample protected endpoint.

### T-011: DELETE /api/v1/account/tokens/{id} (revoke)
**Owner**: backend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US8-02, AC-US8-06
**Test**: Vitest covers revoke marks revokedAt; subsequent Bearer use returns 401; idempotent on already-revoked.

### T-012: Extend requireUserOrGithubBearer to accept vsk_-prefixed tokens
**Owner**: backend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US8-04
**Test**: Vitest covers (a) cookie still works, (b) ghp_ Bearer still works, (c) vsk_ Bearer hash-lookup works, (d) revoked vsk_ → 401, (e) expired vsk_ → 401.

### T-013: GET /api/v1/account/skills/summary
**Owner**: backend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-04
**Test**: Vitest covers public/private counts, recent-activity ordering, 60s KV cache.

### T-014: GET/PATCH /api/v1/account/notifications
**Owner**: backend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US10-01, AC-US10-02, AC-US10-03
**Test**: Vitest covers default prefs (security alerts always-on, others off), PATCH refuses to set securityAlerts=false, persist roundtrip.

### T-015: POST /api/v1/account/sign-out-all + /export + /delete (re-auth gated)
**Owner**: backend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US11-02, AC-US11-03
**Test**: Vitest covers (a) re-auth gate <5min, (b) sign-out-all revokes sessions+tokens, (c) export enqueues job, (d) delete sets deletedAt + cascade-disconnects repos + revokes tokens, (e) hard-delete cron purges >30d.

## Phase 3 — Web UI (vskill-platform pages)

### T-016: /pricing pivot v2 — OSS-first copy + email fix + JSON-LD update
**Owner**: platform-frontend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US2-02
**Test**: Vitest SSR test asserts every AC bullet (license badge present, Pro lead-bullet text, Enterprise mailto matches anton.abyzov@easychamp.com with subject, meta description text, JSON-LD softwareLicense field, OSS hero strip).

### T-017: Email substitution sweep (vskill-platform)
**Owner**: platform-frontend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-04, AC-US2-05
**Test**: `grep -rn "@verified-skill\.com" src/ public/ | grep -v ".test.\|fixtures/" | wc -l` returns 0. README updates pass markdown lint.

### T-018: /account/* layout + sidebar + UserMenu top-nav avatar
**Owner**: platform-frontend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06, AC-US3-07
**Test**: Vitest covers cookie gate (anonymous → 302 to /auth/login?return=/account), sidebar order, active-tab styling, mobile breakpoint behavior. Playwright e2e covers click-through navigation.

### T-019: ProfileTab + Plan & billing tab
**Owner**: platform-frontend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Test**: Vitest covers form validation, save flow, plan card rendering for all 3 tiers, billing history empty state.

### T-020: Connected repos table + summary chip + connect-CTA
**Owner**: platform-frontend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-04b, AC-US5-07
**Test**: Vitest snapshot for all 4 status colors; mobile (<640px) snapshot becomes card-list; empty state CTA opens pre-flight page.

### T-021: Pre-flight permissions page
**Owner**: platform-frontend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-06
**Test**: Vitest covers verbatim copy match (3 do-rows + 3 don't-rows), Continue CTA URL with state token, Cancel routing.

### T-022: Disconnect modal + integration with table kebab
**Owner**: platform-frontend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US6-01, AC-US6-03, AC-US6-04, AC-US6-05
**Test**: Vitest covers modal copy, success path (row removed + toast), failure path (modal stays open + error banner), summary chip recalculation.

### T-023: TokensTab — generate + revoke modals
**Owner**: platform-frontend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US8-03, AC-US8-05, AC-US8-06
**Test**: Vitest covers generate modal flow (form → token plaintext shown → copy-to-clipboard works → row appears with prefix only), revoke confirmation modal, empty state.

### T-024: SkillsTab + NotificationsTab + DangerZone
**Owner**: platform-frontend-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US9-01..03, AC-US10-01..03, AC-US11-01
**Test**: Vitest covers stat tile rendering, recent-activity list, notification checkbox states (security-alerts disabled-checked), Danger Zone modals (typed-handle confirmation for delete-account).

## Phase 4 — Shared eval-ui components (vskill repo)

### T-025: Extract account/* components into src/eval-ui/src/components/account/
**Owner**: desktop-ui-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US12-05, AC-US5-05
**Test**: Vitest covers each component renders with mock props; web-side (T-018..T-024) imports the same components and tests still pass.

### T-026: useAccount hook + platform-base-url context
**Owner**: desktop-ui-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US12-06, AC-US5-06
**Test**: Vitest covers hook fetches from injected baseUrl; React Query cache + invalidation behavior.

### T-027: Desktop sidebar — Account entry + AccountShell
**Owner**: desktop-ui-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US12-01, AC-US12-04
**Test**: Vitest covers sidebar entry rendering, AccountShell stub-router state, offline-banner display when fetch fails.

### T-028: npx vskill studio — Account entry in sidebar (parity with desktop)
**Owner**: desktop-ui-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US12-02, AC-US12-03
**Test**: Vitest covers same component imports, fetch with cookie auth path.

### T-029: Tauri Bearer auth integration (read keyring → context provider)
**Owner**: desktop-ui-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US12-03
**Test**: Cargo test for IPC `account_get_token` returns from keyring; Vitest covers token-context provider.

## Phase 5 — Email sweep (vskill repo) + tests

### T-030: Email substitution sweep (vskill repo)
**Owner**: desktop-ui-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-04, AC-US2-05
**Test**: `grep -rn "@verified-skill\.com" repositories/anton-abyzov/vskill/{src,README.md} | grep -v ".test.\|fixtures/" | wc -l` returns 0.

### T-031: E2E Playwright — /account flows (cookie gate, profile edit, connect→list→resync→disconnect, generate-token→revoke)
**Owner**: testing-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US13-04
**Test**: e2e/account-flow.spec.ts + e2e/connect-disconnect.spec.ts run green.

### T-032: E2E Playwright — desktop+npx-studio account parity
**Owner**: testing-agent
**Status**: [x] completed
**Satisfies ACs**: AC-US13-05, AC-US13-06
**Test**: e2e/desktop/account-parity.spec.ts runs green; verifies same component renders identically across web + desktop + npx-studio against mocked API.
