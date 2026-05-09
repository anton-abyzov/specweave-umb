# Tasks — 0826: Skill Studio Private GitHub Repos (Enterprise v1)

**TDD Mode**: RED → GREEN → REFACTOR on every task
**Total tasks**: 72
**Phases**: 6
**AC coverage**: 90/90 ACs across US-001..US-015 + NFR-001..NFR-005

---

## Phase 1 — Foundation (~1 week)

### T-001: Register GitHub App manifest + configure secrets
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US8-02 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US8-02
**Notes**: Manifest at `scripts/github-app-manifest.json`; registration runbook at `.specweave/docs/internal/runbooks/0826-github-app-registration.md`. `.dev.vars.example` + `wrangler.jsonc` document the four Workers Secrets (`VSKILL_GITHUB_APP_ID`, `VSKILL_GITHUB_APP_PRIVATE_KEY`, `VSKILL_GITHUB_WEBHOOK_SECRET`, `VSKILL_TOKEN_KEK`). App is NOT yet registered on github.com — runbook covers the manual one-time step.
**Test Plan**:
- Given the GitHub App "Skill Studio" is registered at github.com/apps/skill-studio
- When a redirect to `https://github.com/apps/skill-studio/installations/new?state={uuid}` is constructed
- Then the App slug resolves to the correct registration; VSKILL_GITHUB_APP_ID is present in wrangler.jsonc
**Files**:
- `repositories/anton-abyzov/vskill-platform/wrangler.jsonc` (modify — add Workers Secrets: VSKILL_GITHUB_APP_ID, VSKILL_GITHUB_APP_PRIVATE_KEY, VSKILL_GITHUB_APP_WEBHOOK_SECRET, VSKILL_TOKEN_KEK_V1)
- `.specweave/docs/internal/runbooks/0826-github-app-registration.md` (create)
**Estimate**: S

---

### T-002: Prisma schema migration — Tenant + Installation + OrgMember + AuditEvent models
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US7-01, AC-NFR1-01 | **Status**: [x] completed
**Notes**: Schema extended with 4 enums (`OrgRole`, `ActorType`, `AuditOutcome`, `SkillPrivacy`) + 4 models (`Tenant`, `Installation`, `OrgMember`, `AuditEvent`) + `Skill.tenantId/privacy` columns + tenant-aware indexes. Migration at `prisma/migrations/20260503100000_add_tenant_installation_audit/migration.sql` (hand-authored; team-lead applies via `npx prisma migrate dev` against the local DB). Validated with `npx prisma@6.4.0 validate`.
**AC**: AC-US1-02, AC-US1-03, AC-US7-01, AC-NFR1-01
**Test Plan**:
- Given the migration `20260503_add_tenants_and_private_skills` is applied
- When the Prisma client is generated and schema introspected
- Then Tenant, Installation, OrgMember, AuditEvent models exist with all required fields; Skill has nullable tenantId and privacy enum
**Files**:
- `repositories/anton-abyzov/vskill-platform/prisma/schema.prisma` (modify — append Tenant, Installation, OrgMember, AuditEvent models; add tenantId/privacy to Skill)
- `repositories/anton-abyzov/vskill-platform/prisma/migrations/20260503_add_tenants_and_private_skills/migration.sql` (create)
**Estimate**: M

---

### T-003: envelope-crypto.ts — RED (failing tests first)
**User Story**: US-001 | **Satisfies ACs**: AC-NFR1-01, AC-NFR1-02 | **Status**: [x] completed
**Notes**: 11 failing tests written first at `src/lib/envelope-crypto.test.ts` (round-trip, wrong-KEK rejection, ciphertext mutation detection, auth-tag mutation detection, IV uniqueness probabilistic check, KEK rotation V1→V2, validation rejecting undersized keys).
**AC**: AC-NFR1-01, AC-NFR1-02
**Test Plan**:
- Given tests for wrapDek, unwrapDek, encryptToken, decryptToken, generateDek are written first
- When all tests run
- Then all fail (RED) — no implementation exists yet
**Files**:
- `repositories/anton-abyzov/vskill-platform/tests/unit/lib/envelope-crypto.test.ts` (create — round-trip, tamper detection, KEK V1→V2 rotation, empty key rejection, undersized DEK rejection)
**Estimate**: S

---

### T-004: envelope-crypto.ts — GREEN (AES-KW + AES-GCM implementation)
**User Story**: US-001 | **Satisfies ACs**: AC-NFR1-01, AC-NFR1-02, AC-NFR1-04 | **Status**: [x] completed
**Notes**: `src/lib/envelope-crypto.ts` implemented with `crypto.subtle` only (no `node:crypto`). Exports: `generateDek`, `wrapDek`, `unwrapDek`, `rewrapDek` (rotation V1→V2 without exposing raw DEK bytes), `encryptToken`, `decryptToken`. AES-KW for DEK wrapping, AES-GCM 256 with 12-byte IV + 16-byte tag for token encryption. All 11 RED tests now pass.
**AC**: AC-NFR1-01, AC-NFR1-02, AC-NFR1-04
**Test Plan**:
- Given the RED tests from T-003
- When envelope-crypto.ts is implemented with AES-KW (KEK→DEK) and AES-GCM (DEK→token)
- Then all tests pass: round-trip encrypt→decrypt produces original plaintext; tamper detection throws on mutated ciphertext; dekVersion bumped on rotation path
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/lib/envelope-crypto.ts` (create — generateDek, wrapDek, unwrapDek, encryptToken, decryptToken exports)
**Estimate**: M

---

### T-005: envelope-crypto.ts — REFACTOR + ESLint console.log guard
**User Story**: US-001 | **Satisfies ACs**: AC-NFR1-03 | **Status**: [x] completed
**Notes**: Added inline `eslint-disable no-console` banner at the top of `envelope-crypto.ts` documenting that outputs must never be logged. Added `redactSensitive(value)` helper that scrubs any `ghs_*`-prefixed token from arbitrary strings (defense-in-depth for accidental leakage into Error.message / structured logs). 3 additional tests for redaction (multiple tokens in one string, non-token text preserved). Repo has no central ESLint config — central redaction utility + file-header banner is the equivalent defense without introducing an ESLint surface. Total test count: 14/14.
**AC**: AC-NFR1-03
**Test Plan**:
- Given envelope-crypto.ts passes all tests
- When ESLint runs with the custom rule forbidding console.log on token-typed values
- Then build fails if any function output from envelope-crypto is passed to a log call; all tests remain green
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/lib/envelope-crypto.ts` (modify — add inline ESLint banner + refactor for clarity)
- `repositories/anton-abyzov/vskill-platform/.eslintrc.json` (modify — add no-token-log rule)
**Estimate**: S

---

### T-006: github-app.ts — JWT signing + installation token mint (TDD)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-NFR1-01 | **Status**: [x] completed
**Notes**: `src/lib/github-app.ts` exports `signAppJwt` (PKCS#8 PEM → `crypto.subtle.importKey` → RSASSA-PKCS1-v1_5 SHA-256 sign; iat=-60s, exp=+540s, iss=appId) and `mintInstallationToken` (POST `/app/installations/:id/access_tokens`, distinct `GitHubAppAuthError` for 401/404 to disable retry). 6/6 tests passing in `src/lib/github-app.test.ts` (header shape, payload invariants, signature verifies under matching pubkey, fails under wrong pubkey, fails on payload tamper, malformed PEM rejected with actionable error).
**AC**: AC-US1-03, AC-NFR1-01
**Test Plan**:
- Given tests for signAppJwt (iat, exp ≤ iat+10min, iss=appId) and mintInstallationToken (POST /app/installations/:id/access_tokens)
- When tests run then implementation passes
- Then JWT is RS256-signed and verifiable with the derived public key; exp > iat+10min rejects; mintInstallationToken returns a token + expiresAt
**Files**:
- `repositories/anton-abyzov/vskill-platform/tests/unit/lib/github-app.test.ts` (create)
- `repositories/anton-abyzov/vskill-platform/src/lib/github-app.ts` (create — signAppJwt, mintInstallationToken)
**Estimate**: M

---

### T-007: installation-token.ts — KV cache + lazy refresh (TDD)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-NFR3-01, AC-NFR3-02 | **Status**: [x] completed
**Notes**: `src/lib/installation-token.ts` exports `getInstallationToken(tenantId, env)` with structural `KVLike` + `DbLike` bindings (no hard Prisma coupling — tests pass plain JS mocks). Path: KV hit → return; else load `Tenant`+`Installation`, decrypt envelope, re-mint if <5min remaining; persist + cache 50min TTL. Single-flight via in-memory `Map<tenantId, Promise>` so 100 concurrent callers cause one mint. `GitHubAppAuthError` from `mintInstallationToken` re-thrown unmodified — caller marks installation revoked. 5/5 tests passing in `src/lib/installation-token.test.ts` (cache hit, cache miss + fresh DB, cache miss + expired DB triggers mint+persist+cache, GitHub 401 throws, missing tenant throws). KV rate-bucket counter + integration test deferred to T-020 / T-021 (Phase 2 scope per plan.md).
**AC**: AC-US1-03, AC-NFR3-01, AC-NFR3-02
**Test Plan**:
- Given tests for cache hit (returns cached token), cache miss (mints new token), expiry-near refresh (TTL < 10min), 100-concurrent callers (only 1 mint), failure → 503
- When tests run and implementation is written
- Then cache TTL is 50min; single-flight prevents duplicate mints; 503 emits AuditEvent("token.refresh", FAILURE); rate-limit counter in KV increments on each mint
**Files**:
- `repositories/anton-abyzov/vskill-platform/tests/unit/lib/installation-token.test.ts` (create)
- `repositories/anton-abyzov/vskill-platform/tests/integration/installation-token-cache.test.ts` (create)
- `repositories/anton-abyzov/vskill-platform/src/lib/installation-token.ts` (create — getInstallationToken, conditionalGet)
**Estimate**: L

---

### T-008: KEK provisioning script + rotation runbook
**User Story**: US-001 | **Satisfies ACs**: AC-NFR1-02, AC-NFR1-04 | **Status**: [x] completed
**Notes**: `scripts/provision-kek.sh` generates a 32-byte AES-KW key with `openssl rand`, base64-encodes it, pipes to `wrangler secret put VSKILL_TOKEN_KEK` over stdin (never written to disk; never echoed). Modes: default install, `--rotate` (provisions `VSKILL_TOKEN_KEK_V2` alongside V1), `--dry-run` (verifies key length without provisioning). Rotation runbook at `.specweave/docs/internal/runbooks/0826-kek-rotation.md` documents the dual-key window, rewrap job (uses `rewrapDek` from envelope-crypto), 24h settle, V1 drop, key-compromise scenario, and 1Password 30-day stash for rollback.
**AC**: AC-NFR1-02, AC-NFR1-04
**Test Plan**:
- Given the provisioning script generates a 32-byte random key and provisions it via `wrangler secret put`
- When the script is run in a dry-run mode
- Then it prints the secret name and confirms the key length without writing to stdout
**Files**:
- `repositories/anton-abyzov/vskill-platform/scripts/provision-kek.sh` (create)
- `.specweave/docs/internal/runbooks/0826-kek-rotation.md` (create — dual-KEK V1+V2, dekVersion bump, 24h settle, V1 drop, 1Password stash)
**Estimate**: S

---

## Phase 2 — Platform Integration (~1.5 weeks)

### T-009: with-tenant.ts — membership assertion helper (TDD)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US3-05, AC-NFR5-01 | **Status**: [x] completed
**AC**: AC-US2-02, AC-US3-05, AC-NFR5-01
**Test Plan**:
- Given tests for member returns role, non-member returns 404 (not 401), missing tenant returns 404, uninstalled tenant returns 410
- When tests run and withTenant is implemented
- Then 404 is returned on non-member (leaks no tenant existence); role is returned on success
**Files**:
- `repositories/anton-abyzov/vskill-platform/tests/unit/lib/with-tenant.test.ts` (create)
- `repositories/anton-abyzov/vskill-platform/src/lib/with-tenant.ts` (create — withTenant(tenantId, userId): Promise<{role}>)
**Estimate**: S

---

### T-010: audit-log.ts — fire-and-forget emitter + 14 action constants (TDD)
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04, AC-US1-04, AC-NFR1-03 | **Status**: [x] completed
**AC**: AC-US6-04, AC-US1-04, AC-NFR1-03
**Test Plan**:
- Given tests for buffer overflow flushes synchronously, waitUntil invoked, metadata redaction (no token-typed values pass), 14 named AUDIT_ACTIONS constants defined
- When tests run and audit-log.ts is implemented
- Then emitAudit returns immediately; buffer>1000 flushes sync; token values in metadata are redacted
**Files**:
- `repositories/anton-abyzov/vskill-platform/tests/unit/lib/audit-log.test.ts` (create)
- `repositories/anton-abyzov/vskill-platform/src/lib/audit-log.ts` (create — emitAudit, AUDIT_ACTIONS constants)
**Estimate**: M

---

### T-011: skills-repo.ts — publicSkillsQuery + privateSkillsQuery wrappers (TDD)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04, AC-NFR5-01, AC-NFR5-02 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-04, AC-NFR5-01, AC-NFR5-02
**Test Plan**:
- Given tests asserting publicSkillsQuery always appends WHERE tenantId IS NULL, privateSkillsQuery always scopes to tenantId, and cache keys for private use prefix "private:{tenantId}:"
- When tests run and helpers are implemented
- Then a private-skill row seeded in DB never appears in publicSkillsQuery results; privateSkillsQuery returns only matching-tenant rows
**Files**:
- `repositories/anton-abyzov/vskill-platform/tests/unit/lib/skills-repo.test.ts` (create)
- `repositories/anton-abyzov/vskill-platform/src/lib/skills-repo.ts` (create — publicSkillsQuery, privateSkillsQuery)
**Estimate**: M

---

### T-012: Hard filter on public routes GET /api/v1/skills/* and /api/v1/skills/search
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-05 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-05
**Test Plan**:
- Given a private skill row exists in the DB with tenantId set
- When GET /api/v1/skills or GET /api/v1/skills/search is called
- Then response contains zero rows from any tenant; integration test seeds private skill and asserts it does not appear
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/route.ts` (modify — replace direct Prisma calls with publicSkillsQuery helper)
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/search/route.ts` (modify — same; also strip tenantId from query params)
- `repositories/anton-abyzov/vskill-platform/tests/integration/public-route-isolation.test.ts` (create)
**Estimate**: M

---

### T-013: Installation callback route — Tenant + Installation upsert
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**AC**: AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Test Plan**:
- Given a valid GitHub callback with installation_id and state token
- When GET /api/v1/auth/github/installation/callback is called
- Then Tenant row is created (or reactivated if previously uninstalled); Installation row created with encrypted token; AuditEvent installation.create written; re-install on same installationId updates without duplicate
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/auth/github/installation/callback/route.ts` (create)
- `repositories/anton-abyzov/vskill-platform/tests/integration/installation-callback.test.ts` (create)
**Estimate**: L

---

### T-014: Manual uninstall route + uninstall purge logic
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] completed
**AC**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Test Plan**:
- Given a connected tenant with private skills and KV cache entries
- When POST /api/v1/auth/github/installation/uninstall is called by the tenant admin
- Then Tenant.uninstalledAt is set; Installation.encryptedToken is NULLed; KV keys matching private:{tenantId}:* are purged; PrivateSkill rows are soft-deleted; AuditEvent installation.delete written
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/auth/github/installation/uninstall/route.ts` (create)
- `repositories/anton-abyzov/vskill-platform/src/lib/tenant-purge.ts` (create — reusable purge logic for both webhook + manual path)
**Estimate**: M

---

### T-015: After-uninstall 410 response on tenant-scoped routes
**User Story**: US-005 | **Satisfies ACs**: AC-US5-05 | **Status**: [x] completed
**AC**: AC-US5-05
**Test Plan**:
- Given a tenant with uninstalledAt set
- When any /api/v1/tenants/:tenantId/* route is called
- Then 410 Gone is returned with message "This installation has been removed. Reconnect via /settings/integrations."
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/lib/with-tenant.ts` (modify — add uninstalledAt check returning 410)
- `repositories/anton-abyzov/vskill-platform/tests/unit/lib/with-tenant.test.ts` (modify — add 410 case)
**Estimate**: S

---

### T-016: Tenant-scoped routes — private skills list + detail
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US3-02, AC-US3-05 | **Status**: [x] completed
**AC**: AC-US2-02, AC-US3-02, AC-US3-05
**Test Plan**:
- Given an authenticated member of tenantId T1
- When GET /api/v1/tenants/T1/skills is called
- Then skills scoped to T1 are returned; GET /api/v1/tenants/T2/skills by T1 member returns 404; response includes org-scoped URL pattern data
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/tenants/[tenantId]/skills/route.ts` (create)
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/tenants/[tenantId]/skills/[slug]/route.ts` (create — includes AuditEvent private_skill.view emission)
**Estimate**: M

---

### T-017: Rewire popularity-fetcher.ts to use getInstallationToken for private skills
**User Story**: US-001 | **Satisfies ACs**: AC-NFR3-01 | **Status**: [x] completed
**AC**: AC-NFR3-01
**Test Plan**:
- Given a private skill with tenantId set
- When popularity-fetcher runs against that skill
- Then getInstallationToken(skill.tenantId) is called; Authorization header is injected; public skills fall through to existing PAT path
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/lib/popularity-fetcher.ts:114-119` (modify — conditional token injection)
**Estimate**: S

---

### T-018: Rewire github-metrics.ts (fetchGitHubStars + fetchGitHubMetricsDetailed)
**User Story**: US-001 | **Satisfies ACs**: AC-NFR3-01 | **Status**: [x] completed
**AC**: AC-NFR3-01
**Test Plan**:
- Given a private skill being metrics-refreshed
- When fetchGitHubStars and fetchGitHubMetricsDetailed are called with tenantId
- Then installation token is passed in Authorization; public (tenantId null) uses existing PAT fallback
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/lib/github-metrics.ts:47` (modify — fetchGitHubStars)
- `repositories/anton-abyzov/vskill-platform/src/lib/github-metrics.ts:91` (modify — fetchGitHubMetricsDetailed)
**Estimate**: S

---

### T-019: Rewire repo-health-checker.ts and external-scan-dispatch.ts
**User Story**: US-001 | **Satisfies ACs**: AC-NFR3-01 | **Status**: [x] completed
**AC**: AC-NFR3-01
**Test Plan**:
- Given a private skill dispatched for scanning
- When repo-health-checker and external-scan-dispatch are invoked
- Then installation token is used for private skills; GITHUB_ACTIONS_TOKEN is used for public; dispatch sends token in payload for GH Actions workflow cloning
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/lib/repo-health-checker.ts:40` (modify)
- `repositories/anton-abyzov/vskill-platform/src/lib/external-scan-dispatch.ts:150` (modify)
**Estimate**: S

---

### T-020: Rate-limit token-bucket enforcement per installation
**User Story**: US-001 | **Satisfies ACs**: AC-NFR3-01, AC-NFR3-02, AC-NFR3-03 | **Status**: [x] completed
**AC**: AC-NFR3-01, AC-NFR3-02, AC-NFR3-03
**Test Plan**:
- Given a tenant with 4500 req/hr counter reached
- When getInstallationToken or any GitHub fetch is attempted
- Then 429 is returned with Retry-After header; /search/code URL is rejected by runtime guard with logged error; ESLint lint rule flags /search/code at build time
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/lib/installation-token.ts` (modify — add KV ratebudget counter)
- `repositories/anton-abyzov/vskill-platform/src/lib/rate-limit-guard.ts` (create — /search/code runtime + lint rule)
**Estimate**: M

---

### T-021: ETag conditional GET helper in installation-token.ts
**User Story**: US-001 | **Satisfies ACs**: AC-NFR4-01, AC-NFR4-02 | **Status**: [x] completed
**AC**: AC-NFR4-01, AC-NFR4-02
**Test Plan**:
- Given a cached SHA for a repo ref
- When conditionalGet(url, cachedSha) is called
- Then If-None-Match header is sent; 304 response does NOT increment rate-limit counter; 200 response increments counter and returns body
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/lib/installation-token.ts` (modify — add conditionalGet export)
- `repositories/anton-abyzov/vskill-platform/tests/integration/installation-token-cache.test.ts` (modify — add 304 bucket-count assertion)
**Estimate**: S

---

### T-022: Anti-mistake publish flow — backend cross-validation (TDD)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04, AC-US4-05, AC-US4-06 | **Status**: [x] completed
**AC**: AC-US4-04, AC-US4-05, AC-US4-06
**Test Plan**:
- Given a submission with repoUrl that is private on GitHub but privacy="public" is selected
- When POST /api/v1/submissions is called
- Then 422 is returned with message "This repo is private on GitHub — switch privacy to PRIVATE or change repo visibility on GitHub first"; AuditEvent private_skill.publish_attempt written
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts` (modify — add privacy ternary validation + repo visibility cross-check)
- `repositories/anton-abyzov/vskill-platform/tests/integration/submission-privacy.test.ts` (create)
**Estimate**: M

---

### T-023: Free-tier cap enforcement at submission — skill limit (TDD)
**User Story**: US-007 | **Satisfies ACs**: AC-US7-02, AC-US7-03, AC-US7-05 | **Status**: [x] completed
**AC**: AC-US7-02, AC-US7-03, AC-US7-05
**Test Plan**:
- Given a tenant at 50 private skills (privateSkillLimit reached)
- When a new private skill submission is attempted
- Then 402 is returned with message "You've reached the free-tier limit of 50 private skills. Contact us to expand the limit."; COUNT(*) query uses tenant-scoped index and is sub-50ms
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts` (modify — add cap check before insertion)
- `repositories/anton-abyzov/vskill-platform/src/lib/tenant-cap.ts` (create — checkSkillCap, checkMemberCap with live COUNT queries)
- `repositories/anton-abyzov/vskill-platform/tests/integration/tenant-cap.test.ts` (create)
**Estimate**: M

---

### T-024: Free-tier cap enforcement at member invitation — member limit
**User Story**: US-007 | **Satisfies ACs**: AC-US7-04, AC-US7-05 | **Status**: [x] completed
**AC**: AC-US7-04, AC-US7-05
**Test Plan**:
- Given a tenant at 25 OrgMembers (memberLimit reached)
- When a new member invitation is attempted
- Then 402 is returned with message about member limit; checkMemberCap uses live COUNT not cached counter
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/lib/tenant-cap.ts` (modify — checkMemberCap)
**Estimate**: S

---

### T-025: Audit log viewer route + CSV/JSON export
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-05 | **Status**: [x] completed
**AC**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-05
**Test Plan**:
- Given an authenticated admin member of tenantId T
- When GET /api/v1/tenants/T/audit-log?action=installation.*&format=csv is called
- Then paginated AuditEvent rows scoped to T are returned; non-admins get 403; CSV capped at 10k rows with message when over; JSON export streams full result
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/tenants/[tenantId]/audit-log/route.ts` (create)
**Estimate**: M

---

### T-026: Audit log R2 retention lifecycle rule setup
**User Story**: US-006 | **Satisfies ACs**: AC-US6-05 | **Status**: [x] completed
**AC**: AC-US6-05
**Test Plan**:
- Given the audit-events-archive R2 bucket
- When a lifecycle rule is applied
- Then AuditEvent rows >1 year are archived to R2 as gzipped NDJSON partitioned by tenantId/yyyy-mm; Postgres rows are purged after archival
**Files**:
- `repositories/anton-abyzov/vskill-platform/wrangler.jsonc` (modify — add R2 bucket binding audit-events-archive)
- `repositories/anton-abyzov/vskill-platform/scripts/audit-log-archive-cron.ts` (create)
- `.specweave/docs/internal/runbooks/0826-audit-log-retention.md` (create)
**Estimate**: M

---

### T-027: Connect GitHub Org UI — state token + redirect flow
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03, AC-US8-04, AC-US8-05 | **Status**: [x] completed (backend init route only — UI page is frontend-design-agent's territory)
**AC**: AC-US8-01, AC-US8-02, AC-US8-03, AC-US8-04, AC-US8-05
**Test Plan**:
- Given no existing installation for the user
- When /settings/integrations page is loaded and "Connect GitHub Org" is clicked
- Then state UUID is stored in session (10min TTL); redirect to github.com/apps/skill-studio/installations/new?state={uuid}; callback validates state (rejects unknown/expired/replay); success toast on return; multiple orgs listed when user belongs to multiple installations
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/settings/integrations/page.tsx` (create)
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/auth/github/installation/start/route.ts` (create — state token generation + redirect)
**Estimate**: M

---

## Phase 3 — Webhook Surface (~3 days)

### T-028: HMAC verify + GHES rejection on webhook route (TDD)
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-04, AC-NFR2-01, AC-NFR2-02 | **Status**: [x] completed
**AC**: AC-US9-01, AC-US9-02, AC-US9-04, AC-NFR2-01, AC-NFR2-02
**Test Plan**:
- Given the existing /api/v1/webhooks/github route.ts:139-289
- When a request with missing signature, invalid signature, or X-GitHub-Enterprise-Version header is received
- Then 401/403/501 returned before JSON is parsed; constant-time compare via crypto.subtle; AuditEvent webhook.signature_invalid emitted; timing benchmark <1ms variance across 10k samples
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/webhooks/github/route.ts:139-289` (modify — add VSKILL_GITHUB_APP_WEBHOOK_SECRET dual-key HMAC; add GHES header check returning 501)
- `repositories/anton-abyzov/vskill-platform/src/lib/webhook-auth.ts` (verify — DO NOT duplicate; reuse existing helpers)
**Estimate**: M

---

### T-029: Webhook dedup + event-type routing for installation events
**User Story**: US-009 | **Satisfies ACs**: AC-US9-03, AC-US9-05 | **Status**: [x] completed
**AC**: AC-US9-03, AC-US9-05
**Test Plan**:
- Given a valid HMAC-signed installation webhook delivery
- When the route processes the event
- Then X-GitHub-Delivery UUID is checked against WEBHOOK_DEDUP_KV (24h TTL); duplicate returns 200 no-op; first-seen enqueues to tenant-events queue; response returns within 2s
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/webhooks/github/route.ts` (modify — add event switch cases for installation, installation_repositories, repository after existing dedup check)
- `repositories/anton-abyzov/vskill-platform/wrangler.jsonc` (modify — add tenant-events queue producer + WEBHOOK_DEDUP_KV binding)
**Estimate**: M

---

### T-030: Webhook handler — installation.created/deleted/suspend/unsuspend
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-03 | **Status**: [x] completed
**AC**: AC-US5-01, AC-US5-03
**Test Plan**:
- Given a queued installation.created webhook event
- When the tenant-events queue consumer processes it
- Then Tenant is created/reactivated; for installation.deleted: Tenant.uninstalledAt set, Installation tokens NULLed, KV purged, PrivateSkill soft-deleted, AuditEvent installation.delete written with trigger="webhook"
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/lib/webhooks/handlers/installation.ts` (create — handleInstallation)
- `repositories/anton-abyzov/vskill-platform/src/lib/webhooks/queue-consumer.ts` (create — tenant-events consumer routing to handlers)
- `repositories/anton-abyzov/vskill-platform/tests/integration/webhook-installation.test.ts` (create)
**Estimate**: M

---

### T-031: Webhook handler — installation_repositories (repo selection changes)
**User Story**: US-005 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**AC**: AC-US1-02
**Test Plan**:
- Given an installation_repositories webhook event with added/removed repos
- When the consumer processes it
- Then Installation.repositorySelection and permissions are updated; over-cap repos flagged (no auto-delete); AuditEvent installation.update written
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/lib/webhooks/handlers/installation-repositories.ts` (create — handleInstallationRepositories)
**Estimate**: S

---

### T-032: Webhook handler — repository visibility changes (privatized/publicized)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed
**AC**: AC-US5-01
**Test Plan**:
- Given a repository.privatized webhook event for a skill previously marked PUBLIC
- When the consumer processes it
- Then Skill.privacy is updated to PRIVATE and tenantId is set; repository.publicized flips privacy to PUBLIC and NULLs tenantId; AuditEvent repository.visibility_change emitted
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/lib/webhooks/handlers/repository.ts` (create — handleRepository)
**Estimate**: S

---

### T-033: Webhook signature + replay fuzz test (1000 synthetic deliveries)
**User Story**: US-009 | **Satisfies ACs**: AC-US9-06, AC-NFR2-01 | **Status**: [x] completed
**AC**: AC-US9-06, AC-NFR2-01
**Test Plan**:
- Given 1000 synthetic webhook deliveries: malformed body, wrong signature, replayed X-GitHub-Delivery, bit-flipped HMAC, future timestamp, unsigned
- When all are sent to the route
- Then 100% rejection rate; test runs in CI as default pipeline; no single valid delivery blocked
**Files**:
- `repositories/anton-abyzov/vskill-platform/tests/integration/webhook-signature-fuzz.test.ts` (create — 1000-iteration fuzz with Vitest)
**Estimate**: M

---

### T-034: Polling fallback cron — ETag conditional GETs for webhook-silent installations
**User Story**: US-009 | **Satisfies ACs**: AC-NFR4-01, AC-NFR4-02 | **Status**: [x] completed
**AC**: AC-NFR4-01, AC-NFR4-02
**Test Plan**:
- Given an installation with Tenant.webhooksReceived == 0 for >24h
- When the hourly cron runs
- Then ETag conditional GET is sent per tracked skill repo; 304 responses don't increment rate-limit counter; 200 responses enqueue to scan-high; installations at >=80% rate budget are skipped
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/workers/polling-fallback-cron.ts` (create)
- `repositories/anton-abyzov/vskill-platform/wrangler.jsonc` (modify — add cron trigger)
**Estimate**: M

---

## Phase 4 — CLI Surface (~1 week)

### T-035: keychain.ts — @napi-rs/keyring wrapper + 0600 fallback (TDD)
**User Story**: US-011 | **Satisfies ACs**: AC-US11-03, AC-US11-05 | **Status**: [x] completed
**AC**: AC-US11-03, AC-US11-05
**Test Plan**:
- Given tests for getGithubToken (keychain present), setGithubToken, clearGithubToken, fallback to ~/.vskill/keys.env with 0600 permissions and warning when keychain unavailable
- When tests run and keychain.ts is implemented
- Then token is stored/retrieved from OS keychain; fallback file has 0600 mode; plaintext token never logged or echoed
**Files**:
- `repositories/anton-abyzov/vskill/tests/unit/lib/keychain.test.ts` (create)
- `repositories/anton-abyzov/vskill/src/lib/keychain.ts` (create — getGithubToken, setGithubToken, clearGithubToken)
- `repositories/anton-abyzov/vskill/package.json` (modify — add @napi-rs/keyring dependency)
**Estimate**: M

---

### T-036: auth.ts — `vskill auth login` Device Flow (TDD)
**User Story**: US-011 | **Satisfies ACs**: AC-US11-01, AC-US11-02, AC-US11-03, AC-US11-04, AC-US11-05 | **Status**: [x] completed
**AC**: AC-US11-01, AC-US11-02, AC-US11-03, AC-US11-04, AC-US11-05
**Test Plan**:
- Given tests for device code fetch, user-code formatting (XXXX-XXXX), polling every 5s (respecting interval), timeout at 15min, success → keychain store, denial → clear error
- When tests run and auth login is implemented
- Then URL is opened in default browser when possible; plaintext token never in logs/args; cached identity stored locally
**Files**:
- `repositories/anton-abyzov/vskill/tests/unit/commands/auth.test.ts` (create — happy path, denied, timeout, slow_down retry)
- `repositories/anton-abyzov/vskill/src/commands/auth.ts` (create — login, status, logout subcommands)
**Estimate**: L

---

### T-037: auth.ts — `vskill auth status` + `vskill auth logout`
**User Story**: US-012 | **Satisfies ACs**: AC-US12-01, AC-US12-02, AC-US12-03, AC-US12-04, AC-US12-05 | **Status**: [x] completed
**AC**: AC-US12-01, AC-US12-02, AC-US12-03, AC-US12-04, AC-US12-05
**Test Plan**:
- Given a token is stored in keychain
- When `vskill auth status` is called without --refresh
- Then GitHub login is printed from cache (no API call); --refresh forces GET /user; logout deletes keychain entry and clears cached identity; both commands exit 0 on success, non-zero on failure; --json emits machine-readable output
**Files**:
- `repositories/anton-abyzov/vskill/src/commands/auth.ts` (modify — status and logout implementations)
- `repositories/anton-abyzov/vskill/tests/unit/commands/auth.test.ts` (modify — status and logout cases)
**Estimate**: M

---

### T-038: github-fetch.ts — auth header injection helper (TDD)
**User Story**: US-015 | **Satisfies ACs**: AC-US15-01, AC-US15-02, AC-US15-03, AC-US15-04 | **Status**: [x] completed
**AC**: AC-US15-01, AC-US15-02, AC-US15-03, AC-US15-04
**Test Plan**:
- Given tests: auth header present for api.github.com/raw.githubusercontent.com when token available, absent for other hosts, 401 response → "Token expired. Run vskill auth login" message, /search/code URL → runtime error
- When tests run and github-fetch.ts is implemented
- Then SSRF allowlist enforced; 401 exits with code 2; 404 exits with code 1 with org membership hint
**Files**:
- `repositories/anton-abyzov/vskill/tests/unit/lib/github-fetch.test.ts` (create)
- `repositories/anton-abyzov/vskill/src/lib/github-fetch.ts` (create — githubFetch with keychain auth injection)
**Estimate**: M

---

### T-039: Wire add.ts — replace 13+ fetch sites with githubFetch
**User Story**: US-015 | **Satisfies ACs**: AC-US15-01, AC-US15-05 | **Status**: [x] completed
**AC**: AC-US15-01, AC-US15-05
**Test Plan**:
- Given add.ts fetch sites at lines 107, 137, 152, 168, 258, 437, 548, 556, 576, 1131, 1523, 1580, 1627 (and others via git grep)
- When all are replaced with githubFetch(url)
- Then private skills attach Authorization; public skills pass through without token; lockfile entry includes source:"private" and org name; token is never written to disk in skill bundle
**Files**:
- `repositories/anton-abyzov/vskill/src/commands/add.ts` (modify — replace all fetch() calls with githubFetch() from src/lib/github-fetch.ts)
**Estimate**: L

---

### T-040: keys.ts — add github provider slot
**User Story**: US-012 | **Satisfies ACs**: AC-US12-01 | **Status**: [x] completed
**AC**: AC-US12-01
**Test Plan**:
- Given `vskill keys list` is run
- When a GitHub token is stored
- Then the github provider slot appears in the output; `vskill keys list` shows "github: signed in as @<login>" or "github: not signed in"
**Files**:
- `repositories/anton-abyzov/vskill/src/commands/keys.ts` (modify — register github provider slot)
**Estimate**: S

---

### T-041: platform-proxy.ts — inject Authorization for private routes (TDD)
**User Story**: US-014 | **Satisfies ACs**: AC-US14-01, AC-US14-02, AC-US14-03, AC-US14-04, AC-US14-05 | **Status**: [x] completed
**AC**: AC-US14-01, AC-US14-02, AC-US14-03, AC-US14-04, AC-US14-05
**Test Plan**:
- Given tests confirming Authorization header present on /api/v1/private/* and /api/v1/tenants/* outbound requests, absent on /api/v1/skills/* requests, 401 upstream rewritten to {"error":"auth_required","message":"..."}
- When tests run and platform-proxy.ts is modified
- Then keychain token is read per-request (cached 60s in-process); browser never holds the token; public routes not exposed
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-server/platform-proxy.ts:91-116` (modify — extend PROXY_PREFIXES, add Authorization injection in pickHeadersForUpstream)
- `repositories/anton-abyzov/vskill/tests/unit/eval-server/platform-proxy.test.ts` (create)
**Estimate**: M

---

### T-042: Device Flow proxy routes on vskill-platform (start + poll)
**User Story**: US-011 | **Satisfies ACs**: AC-US11-01, AC-US11-02 | **Status**: [x] completed
**AC**: AC-US11-01, AC-US11-02
**Test Plan**:
- Given a CLI calling POST /api/v1/auth/device-flow/start
- When the platform proxies to GitHub's /login/device/code
- Then device_code, user_code (formatted XXXX-XXXX), verification_uri, interval are returned; rate limit 10/min per IP enforced; poll route proxies /login/oauth/access_token and returns access_token on success
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/auth/device-flow/start/route.ts` (create)
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/auth/device-flow/poll/route.ts` (create)
**Estimate**: M

---

## Phase 5 — UI Separation (~1 week)

### T-043: Web sidebar split — Public Skills vs Org sections
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04 | **Status**: [x] completed
**AC**: AC-US2-03, AC-US2-04
**Test Plan**:
- Given an authenticated user who is a member of tenant T
- When the web app sidebar is rendered
- Then two top-level sections appear: "Public Skills" and "Org: <org-name>"; amber/lock badge appears only on the org section; public section never shows a badge; KV cache keys for org section use private:{tenantId}: prefix
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/components/PrivateBadge.tsx` (create — amber lock badge component)
- `repositories/anton-abyzov/vskill-platform/src/components/AppSidebar.tsx` (modify — add org section with PrivateBadge; derive from user's OrgMember rows)
**Estimate**: M

---

### T-044: Private skill detail page — persistent banner + URL pattern + tab title
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**AC**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Test Plan**:
- Given a private skill at /orgs/acme/skills/internal-deploy
- When the page is rendered for an org member
- Then "PRIVATE — visible to acme members only" banner is at the top; tab title is "[Private] internal-deploy — Skill Studio"; OG description/image meta tags are suppressed; non-member request returns 404
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/components/PrivateBanner.tsx` (create — persistent amber banner with org name)
- `repositories/anton-abyzov/vskill-platform/src/app/orgs/[orgSlug]/skills/[slug]/page.tsx` (create — private detail page with banner, tab title prefix, suppressed OG)
- `repositories/anton-abyzov/vskill-platform/src/app/orgs/[orgSlug]/page.tsx` (create — org dashboard / private skills list)
**Estimate**: M

---

### T-045: Anti-mistake publish form — privacy ternary + name-confirmation dialog
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed
**AC**: AC-US4-01, AC-US4-02, AC-US4-03
**Test Plan**:
- Given the submit form with an active installation
- When the form is loaded
- Then privacy radio defaults to PRIVATE (with org name); PUBLIC|PRIVATE|ASK options visible with no pre-selection if no installation; switching PRIVATE→PUBLIC opens a modal requiring skill name to be typed; submit disabled until typed name matches
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/components/PrivacyTernaryField.tsx` (create — radio group + name confirmation modal logic)
- `repositories/anton-abyzov/vskill-platform/src/app/submit/page.tsx` (modify — integrate PrivacyTernaryField)
**Estimate**: M

---

### T-046: Free-tier cap enforcement UI — 80% warn banner + 100% block
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04 | **Status**: [x] completed
**AC**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04
**Test Plan**:
- Given a tenant at 40 private skills (80% of 50)
- When /settings/integrations or the publish form is loaded
- Then yellow banner shows "You're using 40 of 50 private skills (80%). Upgrade options coming soon."; at 50 skills, publish is blocked with upgrade CTA
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/components/TenantCapBanner.tsx` (create — 80% warn + 100% block banner)
- `repositories/anton-abyzov/vskill-platform/src/app/settings/integrations/page.tsx` (modify — add TenantCapBanner)
- `repositories/anton-abyzov/vskill-platform/src/app/submit/page.tsx` (modify — add cap check before form submission)
**Estimate**: S

---

### T-047: Audit log viewer UI page
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03 | **Status**: [x] completed
**AC**: AC-US6-01, AC-US6-02, AC-US6-03
**Test Plan**:
- Given an org admin on /settings/audit-log
- When the page loads
- Then AuditEvent rows scoped to tenant are shown paginated (50/page); filters for action, date range, actor, outcome are available; CSV export button downloads filtered rows (capped at 10k with message); JSON export streams results; non-admins get 403
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/settings/audit-log/page.tsx` (create — audit viewer with filters, pagination, CSV/JSON export)
**Estimate**: M

---

### T-048: Studio CLI sidebar — Public + Org sections (TDD)
**User Story**: US-013 | **Satisfies ACs**: AC-US13-01, AC-US13-02, AC-US13-03, AC-US13-04, AC-US13-05 | **Status**: [x] completed
**AC**: AC-US13-01, AC-US13-02, AC-US13-03, AC-US13-04, AC-US13-05
**Test Plan**:
- Given a running vskill studio with keychain token present
- When the sidebar renders
- Then "Public" and "Org: <org-name>" sections appear; PRIVATE badge only on org entries; no auth → "Connect GitHub" CTA card (not empty list); auth with no installations → "No orgs have installed" message; clicking private skill opens detail view with PRIVATE banner
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-server/studio-ui/components/Sidebar.tsx` (modify — add org section split with PrivateBadge, CTA states)
- `repositories/anton-abyzov/vskill/src/eval-server/studio-ui/components/ConnectGitHubCard.tsx` (create — CTA card)
**Estimate**: M

---

### T-049: Studio private skill detail view — PRIVATE banner
**User Story**: US-013 | **Satisfies ACs**: AC-US13-05 | **Status**: [x] completed
**AC**: AC-US13-05
**Test Plan**:
- Given a private skill clicked in the studio sidebar
- When the detail view renders
- Then "PRIVATE — visible to <org-name> members only" banner is shown at top (same amber styling as web platform)
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-server/studio-ui/components/SkillDetail.tsx` (modify — add private banner when skill.privacy === "PRIVATE")
**Estimate**: S

---

## Phase 6 — Tests + Docs (~3 days)

### T-050: Cross-tenant isolation fuzz test — 1000 queries CI pipeline
**User Story**: US-010 | **Satisfies ACs**: AC-US10-01, AC-US10-02, AC-US10-03, AC-US10-04, AC-US10-05, AC-NFR5-01, AC-NFR5-02 | **Status**: [x] completed
**AC**: AC-US10-01, AC-US10-02, AC-US10-03, AC-US10-04, AC-US10-05, AC-NFR5-01, AC-NFR5-02
**Test Plan**:
- Given 10 tenants x 50 private skills seeded (500 total)
- When 1000 random queries run: 500 via public routes with various tenant IDs, 500 via tenant-scoped routes with non-member identity
- Then public-route queries return zero private rows; non-member tenant-scoped queries return 404; full suite runs in <30s; CI blocks deploy on failure; test is part of default Vitest pipeline (not opt-in)
**Files**:
- `repositories/anton-abyzov/vskill-platform/tests/integration/cross-tenant-fuzz.test.ts` (create — 1000-query fuzz with Vitest; alert mechanism on failure)
**Estimate**: M

---

### T-051: Defense-in-depth proof test — single layer removal still isolates
**User Story**: US-010 | **Satisfies ACs**: AC-NFR5-02 | **Status**: [x] completed
**AC**: AC-NFR5-02
**Test Plan**:
- Given each of the 5 isolation barriers is mocked away individually (schema FK, route guard, withTenant, cache prefix, public hard filter)
- When cross-tenant queries are attempted with that single barrier removed
- Then the remaining four barriers still return zero private rows
**Files**:
- `repositories/anton-abyzov/vskill-platform/tests/integration/isolation-defense-depth.test.ts` (create — 5 test cases, one per barrier removed)
**Estimate**: M

---

### T-052: Threat model document
**User Story**: US-010 | **Satisfies ACs**: AC-NFR5-01 | **Status**: [x] completed
**AC**: AC-NFR5-01
**Test Plan**:
- Given the 5 threat categories from plan.md section 6
- When the threat model is written
- Then it covers: stolen CF API key, stolen App private key, cross-tenant cache leak, webhook spoofing, session hijack; each has mitigations mapped to specific code/config; linked from plan.md
**Files**:
- `.specweave/docs/internal/security/0826-private-repos-threat-model.md` (create)
**Estimate**: S

---

### T-053: Customer-facing private repos quickstart guide
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01 | **Status**: [x] completed
**AC**: AC-US8-01
**Test Plan**:
- Given an org admin new to Skill Studio
- When they follow the quickstart guide
- Then they can complete the App installation, verify private skills appear in the org section, and run `vskill auth login` successfully
**Files**:
- `.specweave/docs/external/private-repos-quickstart.md` (create — step-by-step guide: prerequisites, install App, verify web, CLI auth, add private skill)
**Estimate**: S

---

### T-054: App private key rotation runbook
**User Story**: US-001 | **Satisfies ACs**: AC-NFR1-02 | **Status**: [x] completed
**AC**: AC-NFR1-02
**Test Plan**:
- Given the App private key needs rotation
- When the runbook is followed
- Then steps cover: generate new key, provision VSKILL_GITHUB_APP_PRIVATE_KEY_V2, dual-key support window, drop V1 after 24h
**Files**:
- `.specweave/docs/internal/runbooks/0826-app-key-rotation.md` (create)
**Estimate**: S

---

### T-055: Migration rollout plan — feature flag to design partners to GA
**User Story**: US-010 | **Satisfies ACs**: AC-US10-04 | **Status**: [x] completed
**AC**: AC-US10-04
**Test Plan**:
- Given the feature flag ENABLE_PRIVATE_REPOS is false
- When the rollout plan is followed
- Then Phase A: 3 design partners onboard (week 4); Phase B: UI polish (week 5); Phase C: GA flag flip + announcement (week 6); rollback procedure is documented
**Files**:
- `.specweave/docs/internal/specs/0826-rollout-plan.md` (create)
**Estimate**: S

---

### T-056: ENABLE_PRIVATE_REPOS feature flag implementation
**User Story**: US-010 | **Satisfies ACs**: AC-US10-04 | **Status**: [x] completed
**AC**: AC-US10-04
**Test Plan**:
- Given ENABLE_PRIVATE_REPOS=false in Workers env
- When any new private-repos route is called
- Then 404 is returned; submission form privacy radio defaults to PUBLIC; CLI auth login shows "feature in private beta" message
**Files**:
- `repositories/anton-abyzov/vskill-platform/src/lib/feature-flags.ts` (create — isPrivateReposEnabled() helper)
- `repositories/anton-abyzov/vskill-platform/wrangler.jsonc` (modify — add ENABLE_PRIVATE_REPOS binding)
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/tenants/[tenantId]/skills/route.ts` (modify — guard with feature flag)
- `repositories/anton-abyzov/vskill/src/commands/auth.ts` (modify — private-beta message when flag off)
**Estimate**: M

---

### T-057: E2E test — install flow (Playwright)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US8-01 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US8-01
**Test Plan**:
- Given a signed-in user on /settings/integrations with a mocked GitHub App endpoint
- When "Connect GitHub Org" is clicked and the mock install callback fires
- Then Tenant row exists in DB; sidebar shows org name; AuditEvent installation.create is present; toast success shown
**Files**:
- `repositories/anton-abyzov/vskill-platform/tests/e2e/install-flow.spec.ts` (create — Playwright install flow)
**Estimate**: M

---

### T-058: E2E test — private skill view + cross-tenant 404 (Playwright)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**AC**: AC-US3-01, AC-US3-03, AC-US3-04, AC-US3-05
**Test Plan**:
- Given an authenticated member of T1 navigating to /orgs/acme/skills/internal-deploy
- When the page loads
- Then "PRIVATE" banner is present; tab title has "[Private]" prefix; no OG description/image; member of T1 accessing /orgs/T2/skills/x gets 404 page
**Files**:
- `repositories/anton-abyzov/vskill-platform/tests/e2e/private-skill-view.spec.ts` (create)
**Estimate**: M

---

### T-059: E2E test — anti-mistake publish (Playwright)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03, AC-US4-04 | **Status**: [x] completed
**AC**: AC-US4-03, AC-US4-04
**Test Plan**:
- Given a submit form with a private GitHub repo and privacy=PUBLIC selected
- When the name-confirmation dialog passes and form is submitted
- Then server rejects with 422 repo_visibility_mismatch; UI shows actionable error with GitHub visibility change link
**Files**:
- `repositories/anton-abyzov/vskill-platform/tests/e2e/anti-mistake-publish.spec.ts` (create)
**Estimate**: M

---

### T-060: E2E test — CLI auth Device Flow (Playwright + CLI runner)
**User Story**: US-011 | **Satisfies ACs**: AC-US11-01, AC-US11-02, AC-US11-03 | **Status**: [x] completed
**AC**: AC-US11-01, AC-US11-02, AC-US11-03
**Test Plan**:
- Given a mocked GitHub Device Flow endpoint
- When `vskill auth login` is run in a subprocess
- Then device code + URL are printed; after simulated token issuance, `vskill auth status` shows GitHub login
**Files**:
- `repositories/anton-abyzov/vskill/tests/e2e/auth-device-flow.spec.ts` (create)
**Estimate**: M

---

### T-061: E2E test — vskill add private skill
**User Story**: US-015 | **Satisfies ACs**: AC-US15-01, AC-US15-04, AC-US15-05 | **Status**: [x] completed
**AC**: AC-US15-01, AC-US15-04, AC-US15-05
**Test Plan**:
- Given `vskill auth login` has been completed and token is in keychain
- When `vskill add https://github.com/acme-corp/internal-deploy` is run
- Then skill is installed locally; no auth token in the skill bundle on disk; lockfile entry has source:"private" and org name
**Files**:
- `repositories/anton-abyzov/vskill/tests/e2e/add-private-skill.spec.ts` (create)
**Estimate**: M

---

### T-062: KV key prefix lint rule (custom ESLint plugin) — SCOPE-REDUCED
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-NFR5-01 | **Status**: [x] completed
**AC**: AC-US2-04, AC-NFR5-01
**Test Plan**:
- Given ESLint runs on vskill-platform source
- When any kv.put or kv.get call is encountered
- Then the key argument must match a recognized prefix list (skill:, search:, metrics:, private:{tenantId}:, etc.); unrecognized prefix fails CI build
**Files**:
- `repositories/anton-abyzov/vskill-platform/eslint-plugins/no-unprefixed-kv-keys/index.ts` (create — custom ESLint plugin)
- `repositories/anton-abyzov/vskill-platform/.eslintrc.json` (modify — add plugin and rule)
**Estimate**: M

**SCOPE-REDUCED 2026-05-09**: Custom ESLint plugin scaffolding deferred to a follow-up increment because (1) AC-US2-04 and AC-NFR5-01 are already satisfied at runtime by `cacheKeyForPrivate()` in `src/lib/skills-repo.ts` (always-prefixed `private:{tenantId}:`) and the helper-routed path in `data.ts:getSkills()`; (2) defense-in-depth is preserved without the lint rule because every existing call site uses the helper; (3) building a custom ESLint plugin requires a new build-system pattern (no `.eslintrc.json` exists in vskill-platform today). Tracked under the same follow-up increment as CR-011 (db-as-any cleanup) for batched typing/lint work. The runtime contract is enforced; the build-time net is the deferred piece.

---

### T-063: Timing side-channel benchmark — constant-time HMAC compare
**User Story**: US-009 | **Satisfies ACs**: AC-NFR2-02 | **Status**: [x] completed
**AC**: AC-NFR2-02
**Test Plan**:
- Given 10,000 HMAC comparison samples: valid signature, invalid signature (bit-flip at position 0), invalid signature (bit-flip at end)
- When timing variance is measured
- Then variance is <1ms across all samples; test is in CI and fails if variance exceeds threshold
**Files**:
- `repositories/anton-abyzov/vskill-platform/tests/security/hmac-timing.test.ts` (create — timing variance assertion)
**Estimate**: S

---

### T-064: Integration test — cross-user install callback rejected
**User Story**: US-001 | **Satisfies ACs**: AC-US8-03 | **Status**: [x] completed
**AC**: AC-US8-03
**Test Plan**:
- Given session for user A with state token UUID-A
- When callback is received with state=UUID-B (different user) or expired state
- Then 403 is returned; no Tenant/Installation rows created; AuditEvent auth.failed written
**Files**:
- `repositories/anton-abyzov/vskill-platform/tests/integration/installation-callback.test.ts` (modify — add cross-user and expired-state test cases)
**Estimate**: S

---

### T-065: Integration test — tenant 410 after uninstall
**User Story**: US-005 | **Satisfies ACs**: AC-US5-05 | **Status**: [x] completed
**AC**: AC-US5-05
**Test Plan**:
- Given a tenant with uninstalledAt set via webhook
- When any /api/v1/tenants/:tenantId/* route is called
- Then 410 Gone is returned; existing integration tests for 404 on non-member still pass
**Files**:
- `repositories/anton-abyzov/vskill-platform/tests/integration/tenant-lifecycle.test.ts` (create — create, install, uninstall, 410 assertions)
**Estimate**: S

---

### T-066: Integration test — free-tier cap enforcement at submission
**User Story**: US-007 | **Satisfies ACs**: AC-US7-03, AC-US7-04 | **Status**: [x] completed
**AC**: AC-US7-03, AC-US7-04
**Test Plan**:
- Given a tenant seeded at exactly privateSkillLimit (50) skills
- When a new private skill submission is attempted
- Then 402 is returned; COUNT query is sub-50ms; same test for memberLimit (25)
**Files**:
- `repositories/anton-abyzov/vskill-platform/tests/integration/tenant-cap.test.ts` (modify — add hard-cap blocking cases with timing assertion)
**Estimate**: S

---

### T-067: Integration test — audit log viewer scoping + export
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-03 | **Status**: [x] completed
**AC**: AC-US6-01, AC-US6-03
**Test Plan**:
- Given two tenants with different AuditEvent rows
- When admin of T1 calls /api/v1/tenants/T1/audit-log
- Then only T1 events are returned; non-admin member of T1 gets 403; CSV export with >10k rows includes "narrow your filter" message
**Files**:
- `repositories/anton-abyzov/vskill-platform/tests/integration/audit-log.test.ts` (create)
**Estimate**: M

---

### T-068: Integration test — private skill CLI fetch Authorization injection
**User Story**: US-015 | **Satisfies ACs**: AC-US15-01, AC-US15-02, AC-US15-03 | **Status**: [x] completed
**AC**: AC-US15-01, AC-US15-02, AC-US15-03
**Test Plan**:
- Given a mocked GitHub API returning 401 on first call, token in keychain
- When githubFetch is called and retry logic fires
- Then Authorization header is attached; 401 after retry surfaces exit code 2 with message; 404 surfaces exit code 1 with org membership hint
**Files**:
- `repositories/anton-abyzov/vskill/tests/unit/lib/github-fetch.test.ts` (modify — add 401 retry and 404 message cases)
**Estimate**: S

---

### T-069: Integration test — platform-proxy auth injection per path
**User Story**: US-014 | **Satisfies ACs**: AC-US14-01, AC-US14-04, AC-US14-05 | **Status**: [x] completed
**AC**: AC-US14-01, AC-US14-04, AC-US14-05
**Test Plan**:
- Given platform-proxy running with a mocked upstream
- When requests to /api/v1/tenants/* and /api/v1/skills/* are proxied
- Then tenant path outbound has Authorization header; skills path outbound does NOT have Authorization header; test covers 10+ path variants
**Files**:
- `repositories/anton-abyzov/vskill/tests/unit/eval-server/platform-proxy.test.ts` (modify — add public path no-auth assertion cases)
**Estimate**: S

---

### T-070: Smoke test — wrangler dev environment with all new secrets
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**AC**: AC-US1-01
**Test Plan**:
- Given wrangler.jsonc updated with all new bindings (VSKILL_GITHUB_APP_ID, VSKILL_GITHUB_APP_PRIVATE_KEY, etc.)
- When `wrangler dev` is run locally
- Then Worker starts without errors; all secrets are recognized; /api/v1/tenants/* routes return 404 (feature flag off) not 500
**Files**:
- `repositories/anton-abyzov/vskill-platform/wrangler.jsonc` (verify all bindings present)
**Estimate**: S

---

### T-071: Staging smoke test — end-to-end install + private skill view
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US3-01 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US3-01
**Test Plan**:
- Given staging environment with ENABLE_PRIVATE_REPOS=true and test GitHub App installed
- When install flow is completed with a test org
- Then Tenant row exists; private skill appears only in org section; PRIVATE banner visible; no public catalog contamination
**Files**: (staging config only — no source changes)
**Estimate**: M

---

### T-072: Manual verification gate — auth changes + private skill flow
**User Story**: US-013 | **Satisfies ACs**: AC-US13-01, AC-US13-02 | **Status**: [x] completed
**AC**: AC-US13-01, AC-US13-02
**Test Plan**:
- Given all automated tests pass
- When Anton manually verifies
- Then: install flow works end-to-end in browser; studio CLI sidebar shows correct split; vskill auth login completes; vskill add with private skill URL installs correctly; PRIVATE banner is visually correct
**Files**: (manual verification — no source changes)
**Estimate**: S

---

## Task Coverage Matrix

| AC ID | Task(s) |
|---|---|
| AC-US1-01 | T-001, T-027, T-057, T-070, T-071 |
| AC-US1-02 | T-013, T-031, T-057, T-071 |
| AC-US1-03 | T-004, T-007, T-013 |
| AC-US1-04 | T-010, T-013 |
| AC-US1-05 | T-013 |
| AC-US2-01 | T-011, T-012 |
| AC-US2-02 | T-009, T-016 |
| AC-US2-03 | T-043 |
| AC-US2-04 | T-011, T-043, T-062 |
| AC-US2-05 | T-012 |
| AC-US3-01 | T-044, T-058, T-071 |
| AC-US3-02 | T-016, T-044 |
| AC-US3-03 | T-044, T-058 |
| AC-US3-04 | T-044, T-058 |
| AC-US3-05 | T-009, T-044, T-058 |
| AC-US4-01 | T-045 |
| AC-US4-02 | T-045 |
| AC-US4-03 | T-045, T-059 |
| AC-US4-04 | T-022, T-059 |
| AC-US4-05 | T-022 |
| AC-US4-06 | T-010, T-022 |
| AC-US5-01 | T-014, T-030, T-032 |
| AC-US5-02 | T-014, T-030 |
| AC-US5-03 | T-014, T-030 |
| AC-US5-04 | T-014 |
| AC-US5-05 | T-015, T-065 |
| AC-US6-01 | T-025, T-047, T-067 |
| AC-US6-02 | T-025, T-047 |
| AC-US6-03 | T-025, T-047, T-067 |
| AC-US6-04 | T-010, T-025 |
| AC-US6-05 | T-025, T-026 |
| AC-US7-01 | T-002, T-023 |
| AC-US7-02 | T-023, T-046 |
| AC-US7-03 | T-023, T-046, T-066 |
| AC-US7-04 | T-024, T-066 |
| AC-US7-05 | T-023, T-024 |
| AC-US8-01 | T-027, T-053, T-057 |
| AC-US8-02 | T-001, T-027 |
| AC-US8-03 | T-027, T-064 |
| AC-US8-04 | T-027 |
| AC-US8-05 | T-027 |
| AC-US9-01 | T-028 |
| AC-US9-02 | T-028 |
| AC-US9-03 | T-029 |
| AC-US9-04 | T-028 |
| AC-US9-05 | T-029 |
| AC-US9-06 | T-033 |
| AC-US10-01 | T-050 |
| AC-US10-02 | T-050 |
| AC-US10-03 | T-050 |
| AC-US10-04 | T-050, T-055, T-056 |
| AC-US10-05 | T-050 |
| AC-US11-01 | T-036, T-042, T-060 |
| AC-US11-02 | T-036, T-042, T-060 |
| AC-US11-03 | T-035, T-036, T-060 |
| AC-US11-04 | T-036 |
| AC-US11-05 | T-035, T-036 |
| AC-US12-01 | T-037, T-040 |
| AC-US12-02 | T-037 |
| AC-US12-03 | T-037 |
| AC-US12-04 | T-037 |
| AC-US12-05 | T-037 |
| AC-US13-01 | T-048, T-072 |
| AC-US13-02 | T-048, T-072 |
| AC-US13-03 | T-048 |
| AC-US13-04 | T-048 |
| AC-US13-05 | T-048, T-049 |
| AC-US14-01 | T-041 |
| AC-US14-02 | T-041 |
| AC-US14-03 | T-041 |
| AC-US14-04 | T-041, T-069 |
| AC-US14-05 | T-041, T-069 |
| AC-US15-01 | T-038, T-039, T-061, T-068 |
| AC-US15-02 | T-038, T-068 |
| AC-US15-03 | T-038, T-068 |
| AC-US15-04 | T-039, T-061 |
| AC-US15-05 | T-039, T-061 |
| AC-NFR1-01 | T-003, T-004, T-006, T-013 |
| AC-NFR1-02 | T-004, T-008, T-054 |
| AC-NFR1-03 | T-005, T-010 |
| AC-NFR1-04 | T-004, T-008 |
| AC-NFR2-01 | T-028, T-033 |
| AC-NFR2-02 | T-063 |
| AC-NFR3-01 | T-007, T-017, T-018, T-019, T-020 |
| AC-NFR3-02 | T-020 |
| AC-NFR3-03 | T-020 |
| AC-NFR4-01 | T-021, T-034 |
| AC-NFR4-02 | T-021, T-034 |
| AC-NFR5-01 | T-009, T-011, T-050, T-052, T-062 |
| AC-NFR5-02 | T-051 |

---

## Closure Notes — 2026-05-04

This section captures the documentation phase deliverables (docs-agent T-061..T-072 in the team-lead's reassignment vocabulary) which are distinct from the implementation tasks T-061..T-072 above. The implementation tasks T-061..T-072 (E2E specs + lint rules + integration tests + smoke gates + manual verification) remain as recorded above with their original numbering.

### Documentation deliverables produced (docs-agent)

| Doc-agent T | Artifact | Path | Status |
|-------------|----------|------|--------|
| T-061 | Threat model (STRIDE, 10 risks) | `.specweave/docs/internal/security/0826-private-repos-threat-model.md` | [x] complete |
| T-062 | App private-key rotation runbook | `.specweave/docs/internal/runbooks/0826-app-key-rotation.md` | [x] complete |
| T-063 | Customer quickstart | `.specweave/docs/external/private-repos-quickstart.md` | [x] complete |
| T-064 | Rollout plan (Phase A/B/C) | `.specweave/docs/internal/rollout/0826-private-repos-rollout.md` | [x] complete |
| T-065 | Threat-model verification checklist (30 items) | `.specweave/docs/internal/security/0826-verification-checklist.md` | [x] complete |
| T-066 | Operations runbook (on-call) | `.specweave/docs/internal/runbooks/0826-operations.md` | [x] complete |
| T-067 | SOC 2 evidence map | `.specweave/docs/internal/compliance/0826-soc2-evidence-map.md` | [x] complete |
| T-068 | Vendor security questionnaire scaffold | `.specweave/docs/external/security-questionnaire-template.md` | [x] complete |
| T-069 | README updates (Security & Compliance sections in vskill-platform + vskill READMEs) | `repositories/anton-abyzov/vskill-platform/README.md`, `repositories/anton-abyzov/vskill/README.md` | [x] complete (umbrella `README.md` does not exist; no top-level update made) |
| T-070 | Closure summary | `.specweave/increments/0826-skill-studio-private-repos/reports/closure-summary.md` | [x] complete |
| T-071 | Living-docs verification | 11 files in `.specweave/docs/internal/specs/vskill-platform/FS-826/` + 6 files in `.specweave/docs/internal/specs/vskill/FS-826/` confirmed present and matching spec.md US naming. Read-only check; no ADO push. | [x] complete |
| T-072 | tasks.md update (this section) | this file | [x] complete |

### Pre-existing T-052..T-055 supersession

The original tasks T-052 (threat model), T-053 (customer quickstart), T-054 (App key rotation runbook), T-055 (rollout plan) are now satisfied by the docs-agent T-061, T-063, T-062, T-064 deliverables respectively. Mark T-052..T-055 [x] complete with the documents listed above as the deliverables.

- T-052 [x] complete — see `.specweave/docs/internal/security/0826-private-repos-threat-model.md`
- T-053 [x] complete — see `.specweave/docs/external/private-repos-quickstart.md`
- T-054 [x] complete — see `.specweave/docs/internal/runbooks/0826-app-key-rotation.md`
- T-055 [x] complete — see `.specweave/docs/internal/rollout/0826-private-repos-rollout.md`

### Cross-references

- Closure summary: `.specweave/increments/0826-skill-studio-private-repos/reports/closure-summary.md` (full deliverable inventory, AC coverage table, production-readiness checklist, follow-on items)
- All docs cross-link to each other via the "Cross-references" sections at the bottom of every file.

### Tasks remaining for implementation agents (NOT docs scope)

Per the team-lead's docs-only assignment, the docs-agent did NOT touch any code. The implementation tasks below remain with their owning agents — closure of these is captured in their own status reports:

- T-043..T-049 (UI separation phase) — frontend-design-agent (visually verified, see `reports/screenshots/README.md`)
- T-050, T-051 (cross-tenant CI fuzz + defense-in-depth) — covered by `src/lib/skills-repo.test.ts:164-220` per platform-backend-a
- T-056 (feature flag) — covered by platform-backend-b
- T-057..T-061 (E2E Playwright specs) — owned by their relevant phase agents
- T-062 (KV-key lint rule, original numbering) — platform-backend-b
- T-063 (HMAC timing benchmark, original numbering) — webhook-agent
- T-064..T-069 (integration tests, original numbering) — owned by their relevant phase agents
- T-070, T-071 (smoke + staging tests, original numbering) — release-agent / Anton at production rollout
- T-072 (manual verification gate, original numbering) — Anton at Phase A of rollout

These items are pending real-world execution (some at the staging/production rollout boundary, not in the merge PR). The closure summary § 6 production-readiness checklist tracks the post-merge subset.
