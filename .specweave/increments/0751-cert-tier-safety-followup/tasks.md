# Tasks: Cert-tier safety follow-up

> Strict TDD per `.specweave/config.json`. Each task is RED → GREEN → REFACTOR.
> All paths relative to `repositories/anton-abyzov/vskill-platform/`.

## Phase 1 — Bulk Skill backfill endpoint

### T-001: AC tests for new endpoint
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01..04, AC-US5-01 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** vendor-org `Skill` rows with `certTier='VERIFIED'` exist
- **When** `POST /api/v1/admin/recompute-skill-cert-tiers` is called with valid `X-Internal-Key`
- **Then** response is `200` with `{ ok: true, updated: <n>, sample: [...] }`; DB rows updated to CERTIFIED+VENDOR_AUTO+T4+100
- **And** non-vendor + VERIFIED rows untouched
- **And** vendor + already-CERTIFIED rows untouched (idempotency)
- **And** request without `X-Internal-Key` → 401
- **Test file**: `src/app/api/v1/admin/recompute-skill-cert-tiers/__tests__/route.test.ts` (NEW)

### T-002: Implement bulk endpoint
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01..04 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** failing tests from T-001
- **When** route handler implemented at `src/app/api/v1/admin/recompute-skill-cert-tiers/route.ts` using single `db.skill.updateMany()` + sample `findMany`
- **Then** all T-001 tests pass

## Phase 2 — Fix blocklist unblock bug

### T-003: Vendor unblock returns CERTIFIED + VENDOR_AUTO
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-04 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** a blocked skill whose author is in `VENDOR_ORGS` (e.g. `anton-abyzov`)
- **When** `POST /api/v1/admin/blocklist/[id]/unblock` is called with valid auth
- **Then** the `Skill.update` call uses `{ certTier: 'CERTIFIED', certMethod: 'VENDOR_AUTO' }`
- **And** the search-shard upsert payload includes `certTier: 'CERTIFIED'`
- **Test file**: `src/app/api/v1/admin/blocklist/[id]/unblock/__tests__/route.test.ts` (NEW or EXTEND)

### T-004: Non-vendor unblock returns VERIFIED + AUTOMATED_SCAN
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** a blocked skill whose author is NOT in `VENDOR_ORGS`
- **When** the unblock route is called
- **Then** the `Skill.update` uses `{ certTier: 'VERIFIED', certMethod: 'AUTOMATED_SCAN' }` (current behavior preserved)

### T-005: Implement deriveCertTier integration in unblock route
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** failing tests from T-003/T-004
- **When** `unblock/route.ts` imports `deriveCertTier` + `isVendorOrg`, computes `{certTier, certMethod}` once at top of `if (skill)` block, uses both fields in DB update + search shard payload
- **Then** T-003 and T-004 pass

### T-005b: Same fix in rebuild-index KV-recovery upsert
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** the architecture invariant test (US-004) walks `src/` for `certTier:` literals
- **And** `rebuild-index/route.ts` previously hardcoded `VERIFIED + AUTOMATED_SCAN` in its KV-recovery upsert (`create` block)
- **When** `rebuild-index/route.ts` is updated to call `deriveCertTier(null, { isVendor: isVendorOrg(skillAuthor) })` and pass the derived `{certTier, certMethod}` into `db.skill.upsert.create`
- **Then** vendor-org skills (e.g. `anton-abyzov/specweave/pm`) re-mint with `CERTIFIED + VENDOR_AUTO`, non-vendor skills re-mint with `VERIFIED + AUTOMATED_SCAN`, and the architecture test passes (no allowlist entry needed for this file)
- **Test file**: extend `src/app/api/v1/admin/rebuild-index/__tests__/route.test.ts` with a "0751 AC-US2-05" describe block (3 tests: vendor, non-vendor, fallback)

## Phase 3 — Structured logging

### T-006: Per-row structured log emitted
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** a vendor-author SkillVersion row with certTier='VERIFIED'
- **When** `POST /api/v1/admin/recompute-version-cert-tiers` is called and the row is updated
- **Then** `console.log` is called with a JSON-serialized payload containing `event: "recompute-version-cert-tier"`, `skillId`, `name`, `version`, `before.{certTier,certMethod}`, `after.{certTier,certMethod}`, `ts`
- **Test file**: extend `src/app/api/v1/admin/recompute-version-cert-tiers/__tests__/route.test.ts`

### T-007: Final summary log emitted
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** the endpoint completes processing N rows
- **When** the final response is constructed
- **Then** `console.log` was called once with `event: "recompute-version-cert-tier-summary"`, `updated: N`, `failed: M`, `ts`

### T-008: Log emission is defensive
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** `console.log` mocked to throw
- **When** the endpoint processes rows
- **Then** the batch completes anyway; response shape unchanged

### T-009: Implement structured logging
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01..03 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** failing tests from T-006/T-007/T-008
- **When** `recompute-version-cert-tiers/route.ts` adds the per-row + summary `console.log` calls (wrapped in try/catch)
- **Then** all 3 pass

## Phase 4 — Architecture invariant test

### T-010: Architecture test passes for current allowlist
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** the codebase after Phase 2 lands (blocklist/unblock no longer hardcodes)
- **When** `cert-tier-derivation.test.ts` runs against `src/`
- **Then** test passes — no violations
- **Test file**: `src/lib/__tests__/architecture/cert-tier-derivation.test.ts` (NEW)

### T-011: Architecture test catches a deliberate violation
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-05 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** a temporary file `src/__tests__/_violation-fixture.ts` containing `data: { certTier: "VERIFIED" }`  -- OR --  inline assertion using a fixture string fed to the same regex
- **When** the test runs
- **Then** the violation is detected and the file path appears in the error message
- **Cleanup**: remove fixture after assertion

### T-012: Implement the architecture test
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01..05 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** failing tests from T-010/T-011
- **When** the test file is implemented (walks src/, regex match, allowlist filter, error message includes file paths)
- **Then** T-010 passes (current state is clean) and T-011's regex assertion confirms catch behavior

## Phase 5 — Verification + deploy + prod backfill

### T-013: Full vitest suite no new failures
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** all Phase 1–4 changes landed
- **When** `npx vitest run` is executed
- **Then** failure count = baseline (~144 from 0744 audit); no NEW failures

### T-014: Closure pipeline (sw-closer)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** all tests pass
- **When** sw-closer runs code-review → simplify → grill → judge-llm → PM gates
- **Then** all gates pass (or findings are fixed in fix-loop)

### T-015: Deploy + run new endpoint against prod
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** code is committed + pushed
- **When** `npm run deploy` completes and `POST /api/v1/admin/recompute-skill-cert-tiers` is called with valid auth
- **Then** response shows `updated > 0`; idempotent re-run returns `updated: 0`
- **And** `GET /api/v1/skills/anton-abyzov/specweave/pm` shows `certTier: 'CERTIFIED'`
- **And** full audit response saved to `logs/backfill-skill-2026-04-26.md` (force-add via `git add -f`)
