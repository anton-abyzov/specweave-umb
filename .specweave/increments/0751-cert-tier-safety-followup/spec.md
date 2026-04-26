---
increment: 0751-cert-tier-safety-followup
title: "Cert-tier safety follow-up: bulk Skill backfill + bug fixes + invariant test"
type: bug
priority: P2
status: active
created: 2026-04-26
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Cert-tier safety follow-up to 0744

## Overview

0744 fixed the auto-poll scanner so vendor-org `SkillVersion` rows are correctly stamped `CERTIFIED`. Backfill ran successfully (39 rows fixed). The post-run audit ([logs/backfill-2026-04-26.md](../0744-fix-cert-tier-muddle-versions-tab/logs/backfill-2026-04-26.md)) surfaced four loose ends that this increment closes:

1. **Bulk Skill backfill is missing.** The existing `trusted-author-backfill` endpoint times out under load (per-row `updateSkillTrust()` does ~9 sub-queries each → DB circuit breaker opens after 10 timeouts). 151 vendor-org Skill records still sit at `certTier='VERIFIED'` in prod, so the header badge displays "Security-Scanned" instead of "Trusted Publisher".
2. **`blocklist/[id]/unblock` route hardcodes `certTier: "VERIFIED"`** at lines ~52 and ~67 — same bug class as the original scanner.ts hardcode. If a vendor-org skill is unblocked, it gets wrongly downgraded.
3. **No persistent audit trail for `recompute-version-cert-tiers`** — the response carries `before/after` but if the operator forgets to capture it (as happened during 0744), the data is gone.
4. **No guardrail prevents this bug class from recurring** — there's no architecture test that fails the build when a new file writes a hardcoded `certTier:` value to a Prisma `data` block.

## User Stories

### US-001: Bulk Skill backfill endpoint that doesn't time out (P1)
**Project**: vskill-platform

**As a** vskill-platform operator
**I want** a fast bulk endpoint to flip vendor-org `Skill.certTier` to `CERTIFIED` in a single SQL statement
**So that** I can correct ~151 stale rows in <2s instead of hitting the DB circuit breaker like `trusted-author-backfill` did

**Acceptance Criteria**:
- [x] **AC-US1-01**: `POST /api/v1/admin/recompute-skill-cert-tiers` exists, uses one `db.skill.updateMany()` call (no per-row trust recomputation), and updates vendor-org rows where `certTier != 'CERTIFIED'` OR `trustScore != 100` OR `isTainted = true` to `{ certTier: 'CERTIFIED', certMethod: 'VENDOR_AUTO', trustScore: 100, trustTier: 'T4', isTainted: false, taintedAt: null, taintReason: null }`.
- [x] **AC-US1-02**: Endpoint returns `{ ok: true, updated: <count>, sample: [...up to 20 affected rows for audit...] }`.
- [x] **AC-US1-03**: Endpoint is idempotent — immediate re-run returns `updated: 0`.
- [x] **AC-US1-04**: Endpoint requires `SUPER_ADMIN` role OR `X-Internal-Key` header; returns `401` otherwise.
- [x] **AC-US1-05**: After deploy, running the endpoint against prod fixes ~151 stale vendor Skill records; verification via `GET /api/v1/skills/anton-abyzov/specweave/pm` shows `certTier: 'CERTIFIED'`.

---

### US-002: Blocklist unblock respects vendor-org status (P1)
**Project**: vskill-platform

**As a** vskill-platform operator unblocking a previously-blocked skill
**I want** the unblock route to use `deriveCertTier()` instead of hardcoding `VERIFIED`
**So that** vendor-org skills that get unblocked don't get silently downgraded

**Acceptance Criteria**:
- [x] **AC-US2-01**: `src/app/api/v1/admin/blocklist/[id]/unblock/route.ts` no longer contains the literal `certTier: "VERIFIED"` write.
- [x] **AC-US2-02**: When unblocking a skill whose author is in `VENDOR_ORGS` (e.g. `anton-abyzov`), the `Skill.certTier` is set to `CERTIFIED` and `certMethod` to `VENDOR_AUTO`.
- [x] **AC-US2-03**: When unblocking a non-vendor skill, the `Skill.certTier` is set to `VERIFIED` and `certMethod` to `AUTOMATED_SCAN` (current behavior preserved).
- [x] **AC-US2-04**: The search-shard upsert payload (around line ~67) carries the same derived `certTier` value, not the hardcoded `"VERIFIED"`.
- [x] **AC-US2-05**: `src/app/api/v1/admin/rebuild-index/route.ts` (KV-recovery path that re-mints `Skill` rows when the search KV is empty) calls `deriveCertTier()` instead of hardcoding `"VERIFIED" + AUTOMATED_SCAN`, so vendor-org skills re-created from a rebuilt index keep `CERTIFIED + VENDOR_AUTO`. Same bug class as US-002, fixed in the same pass to prevent the architecture invariant test (US-004) from immediately surfacing it.

---

### US-003: Recompute-version-cert-tiers leaves a CF-tail audit trail (P2)
**Project**: vskill-platform

**As a** vskill-platform operator running the SkillVersion backfill
**I want** every per-row mutation to emit a structured log line in CF Worker logs
**So that** if I forget to capture the response, I can still reconstruct exactly which rows changed by tailing CF logs

**Acceptance Criteria**:
- [x] **AC-US3-01**: For each updated `SkillVersion` row, the route emits one structured `console.log(JSON.stringify({...}))` line containing `event: "recompute-version-cert-tier"`, `skillId`, `name`, `version`, `before.{certTier,certMethod}`, `after.{certTier,certMethod}`, `ts`.
- [x] **AC-US3-02**: After all rows process, the route emits one `event: "recompute-version-cert-tier-summary"` line with `updated`, `failed`, `ts`.
- [x] **AC-US3-03**: Log emission does not abort the batch on serialization failure (defensive try/catch around `console.log`).

---

### US-004: Architecture test prevents the bug class from recurring (P1)
**Project**: vskill-platform

**As a** maintainer
**I want** the build to fail when a new file writes a hardcoded `certTier: "VERIFIED"` or `certTier: "CERTIFIED"` to a Prisma `data` block outside the allowlist
**So that** future contributors can't silently reintroduce the scanner.ts / blocklist-unblock bug class

**Acceptance Criteria**:
- [x] **AC-US4-01**: New test file `src/lib/__tests__/architecture/cert-tier-derivation.test.ts` exists and walks all `.ts/.tsx` under `src/`.
- [x] **AC-US4-02**: Test fails when any non-allowlisted file matches `/certTier\s*:\s*['"]VERIFIED['"]|certTier\s*:\s*['"]CERTIFIED['"]/`.
- [x] **AC-US4-03**: Allowlist includes: `src/lib/submission/types.ts` (deriveCertTier itself), `src/lib/trust/trust-updater.ts` (parallel canonical derivation), the three vendor-only backfill routes (`trusted-author-backfill`, `recompute-version-cert-tiers`, `recompute-skill-cert-tiers`), the two read-only Prisma `where`-filter sites (`trust-backfill/route.ts` and `eval/reverify/route.ts` — these match the regex but never write), and all `__tests__/` + `*.test.ts` files.
- [x] **AC-US4-04**: Test passes against the current codebase after Phase 2's bug fix lands (i.e. the blocklist/unblock route stops being a violator).
- [x] **AC-US4-05**: When the test fails, the error message names the offending file path so the contributor knows where to look.

---

### US-005: TDD coverage and full-suite no-regression (P1)
**Project**: vskill-platform

**As a** maintainer
**I want** every behavior change preceded by a failing test, and the full vitest suite to show no NEW failures
**So that** the fix is provably correct and doesn't regress anything

**Acceptance Criteria**:
- [x] **AC-US5-01**: Each of W1–W4 follows RED → GREEN cycle (test fails before implementation, passes after).
- [x] **AC-US5-02**: New tests cover all ACs in US-001 through US-004.
- [x] **AC-US5-03**: Pre-existing failing tests count remains at the prior baseline (~144 from 0744's audit) — no NEW failures introduced.

## Functional Requirements

### FR-001: Single bulk update statement
The new `recompute-skill-cert-tiers` endpoint MUST use exactly one `prisma.skill.updateMany()` call for the mutation. Per-row updates or per-row trust recomputation are forbidden — that's what made `trusted-author-backfill` time out.

### FR-002: Centralized derivation
All non-test, non-allowlisted code paths that write `certTier: "VERIFIED"` or `certTier: "CERTIFIED"` to a Prisma `data` block MUST call `deriveCertTier()`. Enforced by the architecture test.

### FR-003: Structured logging
The `recompute-version-cert-tiers` endpoint MUST emit JSON-formatted `console.log` lines with the exact event names specified in AC-US3-01/02 so external log analyzers can filter on `event`.

### FR-004: Idempotency
Both backfill endpoints (`recompute-skill-cert-tiers` new, `recompute-version-cert-tiers` existing) MUST be idempotent — re-runs against an already-correct state return `updated: 0` and make no DB writes.

## Success Criteria

- After deploy + one run of the new endpoint against prod: zero vendor-org `Skill` records have `certTier='VERIFIED'`.
- Skill-detail header for a vendor-org skill (e.g. `anton-abyzov/specweave/pm`) reads "Trusted Publisher".
- The architecture test catches a deliberately-introduced violation (smoke test that the test actually works).
- No new pre-existing test failures; new tests for all ACs pass.

## Out of Scope

- Rewriting `trusted-author-backfill` (kept intact for non-vendor edge cases).
- DB enum rename or Prisma migration.
- Updating Hetzner VM env files (no key rotation).
- Other certTier-write paths beyond the ones identified — the architecture test will surface any others, which can be addressed in future increments.
- Resuming or modifying the parallel active increments 0670 / 0746 / 0747 / 0750.

## Dependencies

- `deriveCertTier()` at `src/lib/submission/types.ts:160` (existing, reused).
- `isVendorOrg()` and `VENDOR_ORGS` at `src/lib/trust/trusted-orgs.ts` (existing, reused).
- `requireAdmin`, `hasInternalAuth`, `jsonResponse`, `errorResponse` admin route plumbing (existing, mirrored from `recompute-version-cert-tiers`).
- Architecture test pattern from `src/lib/skill-update/__tests__/architecture.test.ts` (existing, mirrored).
