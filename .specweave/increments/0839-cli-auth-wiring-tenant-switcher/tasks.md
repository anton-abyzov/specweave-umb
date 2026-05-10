# 0839 — Tasks

## Phase 1 — Platform endpoints (additive, ship first)

### T-001: Implement `POST /api/v1/auth/github/exchange-for-vsk-token`
**User Story**: US-005 | **AC**: AC-US5-01, AC-US5-02 | **Status**: [x] completed
**Test Plan**:
- Given a valid `gho_*` token, When POST is called, Then a new `ApiToken` row is created with `prefix="vsk_"`, `tokenHash=sha256(plaintext)`, `tokenPrefix=<first 12>`, `scopes=["read","write"]`, expiry 90d → response includes plaintext `vsk_*` ONCE.
- Given an invalid `gho_*` token (GitHub returns 401), When POST is called, Then the route returns 401 and creates no DB row.
- Given GitHub /user returns 5xx, When POST is called, Then the route returns 503 (not 5xx).
- Path: `vskill-platform/src/app/api/v1/auth/github/exchange-for-vsk-token/route.ts` + `.test.ts`

### T-002: Implement `GET /api/v1/account/tenants`
**User Story**: US-003, US-004 | **AC**: AC-US3-01, AC-US4-02 | **Status**: [x] completed
**Test Plan**:
- Given an authenticated user with N=0 tenants, When GET is called, Then response is `{ tenants: [] }` with status 200.
- Given N=1 tenant, When GET is called, Then response includes `[{ tenantId, slug, name, role, installationId }]`.
- Given N=3 tenants, When GET is called, Then all three are returned with role from `OrgMember.role`.
- Given no Authorization header, When GET is called, Then 401 is returned.
- Path: `vskill-platform/src/app/api/v1/account/tenants/route.ts` + `.test.ts`

## Phase 2 — CLI auth core

### T-003: Add `vsk_*` keychain helpers
**User Story**: US-005 | **AC**: AC-US5-03, AC-US5-06 | **Status**: [x] completed
**Test Plan**:
- Given a `vsk_*` token, When `setVskillToken()` is called, Then `keytar.setPassword("vskill-token", ...)` is invoked.
- Given a stored token, When `getVskillToken()` is called, Then plaintext is returned.
- Given no stored token, When `getVskillToken()` is called, Then `null` is returned.
- Given a stored token, When `deleteVskillToken()` is called, Then keytar entry is removed.
- Path: `vskill/src/lib/keychain.ts` (modify) + new tests in same `__tests__` folder

### T-004: Add `~/.vskill/config.json` active-tenant helper
**User Story**: US-002, US-003 | **AC**: AC-US3-02, AC-US3-06 | **Status**: [x] completed
**Test Plan**:
- Given an empty config, When `setActiveTenant("acme")` is called, Then `{ currentTenant: "acme" }` is written.
- Given an existing config with unknown keys (`{ foo: "bar", currentTenant: "old" }`), When `setActiveTenant("new")` is called, Then `foo: "bar"` is preserved AND `currentTenant: "new"`.
- Given concurrent writes, When two callers race, Then atomic rename guarantees no partial file.
- Path: `vskill/src/lib/active-tenant.ts` + `.test.ts`

### T-005: Wire Bearer interceptor + tenant header in `client.ts`
**User Story**: US-001, US-002 | **AC**: AC-US1-01, AC-US1-02, AC-US1-06, AC-US2-06, AC-US5-04 | **Status**: [x] completed
**Test Plan**:
- Given a `vsk_*` token in keychain, When any client method is called, Then `Authorization: Bearer vsk_*` is sent.
- Given only a `gho_*` token, When called, Then `Authorization: Bearer gho_*` is sent (fallback).
- Given no token, When called, Then no Authorization header is sent.
- Given an active tenant, When called, Then `X-Vskill-Tenant: <slug>` is sent.
- Given multiple sequential calls in one process, When token is read, Then keychain is hit at most once (caching).
- Path: `vskill/src/api/client.ts` (modify) + `.test.ts` (new)

### T-006: Update `auth login` to call exchange + store both tokens
**User Story**: US-005 | **AC**: AC-US5-03, AC-US5-05 | **Status**: [x] completed
**Test Plan**:
- Given device flow returns `gho_*`, When login completes, Then `exchange-for-vsk-token` is called with the `gho_*` token.
- Given exchange returns 200, When login finishes, Then BOTH `vskill-github` (gho_) and `vskill-token` (vsk_) keychain entries exist.
- Given exchange returns 5xx, When login finishes, Then ONLY `vskill-github` is stored AND CLI prints "Logged in (legacy mode...)" — exit 0.
- Path: `vskill/src/commands/auth.ts` (modify)

### T-007: Update `auth logout` to clear both tokens + revoke
**User Story**: US-005 | **AC**: AC-US5-06 | **Status**: [x] completed
**Test Plan**:
- Given both tokens stored, When `auth logout` runs, Then both keychain entries are deleted AND `DELETE /api/v1/auth/sign-out-all` is called.
- Given the revoke call fails, When logout runs, Then keychain is still cleared AND CLI exit code is 0.
- Path: `vskill/src/commands/auth.ts` (modify)

## Phase 3 — CLI tenant commands

### T-008: Implement `vskill orgs list/use/current`
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-05 | **Status**: [x] completed
**Test Plan**:
- Given user has 2 tenants and `currentTenant: "acme"`, When `orgs list` runs, Then output includes both rows AND `acme` is marked `*`.
- Given a known slug, When `orgs use contoso` runs, Then config is updated to `currentTenant: "contoso"` and exit 0.
- Given an unknown slug, When `orgs use bogus` runs, Then exit non-zero with "Unknown tenant: bogus".
- Given `currentTenant` is unset, When `orgs current` runs, Then output is `(none)` and exit 0.
- Given user is not logged in, When `orgs list` runs, Then exit 0 with "Not logged in" message (anonymous-safe).
- Path: `vskill/src/commands/orgs.ts` + `.test.ts`

### T-009: Implement `vskill whoami`
**User Story**: US-003 | **AC**: AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Test Plan**:
- Given logged in with active tenant, When `whoami` runs, Then output shows email + token-prefix + active tenant + tenant list.
- Given logged in without active tenant, When `whoami` runs, Then "Active tenant: (none)" is shown.
- Given not logged in, When `whoami` runs, Then "Not logged in. Run \`vskill auth login\`." is shown AND exit non-zero.
- Path: `vskill/src/commands/whoami.ts` + `.test.ts`

### T-010: Update `add` command for tenant resolution
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test Plan**:
- Given user has 1 tenant, When `add private-skill` runs, Then resolution tries public → tenant_1, succeeds, no prompt.
- Given user has 3 tenants and skill exists in 2 of them with no `--tenant`, When `add` runs, Then exit non-zero with "found in multiple tenants" message.
- Given `--tenant acme`, When `add` runs, Then ONLY public + acme tenant are queried.
- Given platform returns 402 with `upgradeUrl`, When `add` runs, Then CLI prints the upgrade URL AND exits non-zero.
- Given platform returns 401, When `add` runs, Then CLI prints "Run \`vskill auth login\`" AND exits non-zero, AND keychain is NOT cleared.
- Path: `vskill/src/commands/add.ts` (modify)

## Phase 4 — Studio tenant switcher

### T-011: Add `/__internal/active-tenant` handler in eval-server
**User Story**: US-004 | **AC**: AC-US4-03 | **Status**: [x] completed
**Test Plan**:
- Given GET on `/__internal/active-tenant`, When handler runs, Then it returns `{ currentTenant: "..." }` from config.json.
- Given POST `{ currentTenant: "acme" }`, When handler runs, Then config.json is updated AND 200 is returned.
- Given POST with invalid JSON, When handler runs, Then 400 is returned.
- Path: `vskill/src/eval-server.ts` (modify) + integration test in existing eval-server test file

### T-012: Implement `<TenantPicker />` component
**User Story**: US-004 | **AC**: AC-US4-01, AC-US4-02, AC-US4-04, AC-US4-05, AC-US4-06 | **Status**: [x] completed
**Test Plan**:
- Given N=0 tenants, When mounted, Then renders the existing "Connect GitHub" CTA (delegates to ConnectGitHubCard empty state).
- Given N=1 tenant, When mounted, Then renders a static label `Tenant: <name>` with no dropdown.
- Given N=3 tenants, When mounted, Then renders a dropdown with all three; clicking one calls POST `/__internal/active-tenant`.
- Given a tenant is active, When tenant-scoped API calls are made elsewhere in the UI, Then the `X-Vskill-Tenant` header is set via shared API client config.
- Path: `vskill/src/eval-ui/src/components/private/TenantPicker.tsx` + `.test.tsx`

### T-013: Integrate TenantPicker into ConnectGitHubCard
**User Story**: US-004 | **AC**: AC-US4-01, AC-US4-04 | **Status**: [x] completed
**Test Plan**:
- Given the user is logged out, When ConnectGitHubCard renders, Then existing OAuth CTA shows (no regression).
- Given the user is logged in with N≥1 tenants, When ConnectGitHubCard renders, Then `<TenantPicker />` replaces the single-org block.
- Given the user is logged in with N=0 tenants, When card renders, Then existing "Install GitHub App" CTA shows.
- Path: `vskill/src/eval-ui/src/components/private/ConnectGitHubCard.tsx` (modify)

## Phase 5 — End-to-end

### T-014: E2E test — full login → switch → install flow
**User Story**: US-001, US-002, US-003, US-005 | **AC**: spans AC-US1-03, AC-US2-01, AC-US3-02, AC-US5-03 | **Status**: [x] completed
**Test Plan**:
- Given a fresh test environment, When mocked `auth login` runs, Then both `gho_*` and `vsk_*` are stored in test keychain.
- Given two seeded test tenants, When `orgs use acme` runs, Then config.json reflects it.
- Given a private skill in tenant acme, When `add private-skill` runs, Then the install succeeds with status 200.
- Given a private skill in tenant contoso (no entitlement), When `add other-skill` runs, Then exit non-zero with the upgrade URL.
- Path: `vskill/e2e/0839-cli-auth-tenant-switcher.spec.ts`

### T-015: Documentation updates
**User Story**: All | **AC**: implicit (DX completeness) | **Status**: [x] completed
**Test Plan**:
- Given the README references `vskill auth`, When updated, Then `vskill orgs` and `vskill whoami` are documented in the same section.
- Given the docs site has a "Private skills" page, When updated, Then it explains tenant resolution priority (flag > env > config > N=1 auto-pick > error).
- Path: `vskill/README.md` (modify) + any relevant `.md` in `vskill/docs/` if present
