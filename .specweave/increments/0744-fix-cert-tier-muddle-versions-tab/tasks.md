# Tasks: Fix CERTIFIED/VERIFIED cert-tier muddle on Versions tab

> Strict TDD per `.specweave/config.json`. Each task is RED → GREEN → REFACTOR.
> All paths relative to `repositories/anton-abyzov/vskill-platform/`.

## Phase 1 — Scanner derivation bug fix

### T-001: Scanner vendor-author auto-poll path → CERTIFIED
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US4-01 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** a scanner detects a new git SHA for a skill whose `author` is in `VENDOR_ORGS` (e.g. `anton-abyzov`)
- **When** the scanner enters the `db.$transaction` block at `src/lib/skill-update/scanner.ts` ~L174 and writes a SkillVersion row
- **Then** the row's `extraData.certTier` is `"CERTIFIED"` AND `extraData.certMethod` is `"VENDOR_AUTO"`
- **Test file**: `src/lib/skill-update/__tests__/scanner.test.ts` — new test "vendor-org skill gets CERTIFIED+VENDOR_AUTO via auto-poll path"
- **RED**: test fails with current hardcoded `"VERIFIED"`/`"AUTOMATED_SCAN"` values

### T-002: Scanner non-vendor auto-poll path → VERIFIED
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US4-01 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** a scanner detects a new git SHA for a skill whose `author` is NOT in `VENDOR_ORGS` (e.g. `random-user`)
- **When** the scanner writes a SkillVersion row
- **Then** the row's `extraData.certTier` is `"VERIFIED"` AND `extraData.certMethod` is `"AUTOMATED_SCAN"`
- **Test file**: same as T-001 — new test "non-vendor skill gets VERIFIED+AUTOMATED_SCAN via auto-poll path"
- **RED**: passes accidentally today (because hardcode happens to match), but RED-then-GREEN cycle still required to lock the contract

### T-003: Implement deriveCertTier integration in scanner.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** the failing tests from T-001/T-002
- **When** scanner.ts imports `deriveCertTier` and `isVendorOrg`, and replaces the hardcoded extraData with `deriveCertTier(null, { isVendor: isVendorOrg(skill.author) })`
- **Then** both T-001 and T-002 tests pass; integration test (`scanner.integration.test.ts`) confirms persisted rows carry derived values
- **Files modified**: `src/lib/skill-update/scanner.ts`

### T-004: Update existing scanner tests pinning old hardcoded value
**User Story**: US-001 | **Satisfies ACs**: AC-US4-05 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** any existing test in scanner.test.ts asserts `extraData.certTier === "VERIFIED"` for a vendor-author fixture
- **When** the test fixture is for a vendor author
- **Then** the assertion is updated to `"CERTIFIED"` to match new derivation
- **Files modified**: `src/lib/skill-update/__tests__/scanner.test.ts` (only if existing tests need updates)

## Phase 2 — Per-version UI data exposure

### T-005: getSkillVersions returns certMethod
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** a SkillVersion row exists in the DB with `certMethod='LLM_JUDGE'`
- **When** `getSkillVersions(owner, repo, skill)` is called from `src/lib/data.ts`
- **Then** the returned object includes `certMethod: 'LLM_JUDGE'`
- **Test file**: `src/lib/__tests__/data.test.ts` (or extend existing)
- **Files modified**: `src/lib/data.ts` (add `certMethod: true` to SELECT around L656-668)

### T-006: VersionCard renders certMethod label
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** a VersionCard receives `certMethod='VENDOR_AUTO'`
- **When** the component renders
- **Then** the rendered output contains "Trusted Publisher" AND does NOT contain the literal strings "VERIFIED" or "CERTIFIED"
- **And** for `certMethod='LLM_JUDGE'` → "LLM-judged scan"; for `certMethod='AUTOMATED_SCAN'` → "Automated scan"
- **Test file**: `src/app/skills/[owner]/[repo]/[skill]/versions/__tests__/page.test.tsx` (new)
- **Files modified**: `src/app/skills/[owner]/[repo]/[skill]/versions/page.tsx`

### T-007: VersionCard renders certScore conditionally
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** a VersionCard receives `certScore=87`
- **When** the component renders
- **Then** the rendered output contains "87/100"
- **And** when `certScore=null`, the rendered output contains NO substring matching `/\d*\/100/`
- **Test file**: same as T-006

## Phase 3 — TierBadge label rename

### T-008: formatTierLabel returns Trusted Publisher for CERTIFIED
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US4-02 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** the helper `formatTierLabel` from `src/app/components/TierBadge.tsx`
- **When** called with `'CERTIFIED'`
- **Then** returns `'Trusted Publisher'`
- **And** when called with `'VERIFIED'` → returns `'Security-Scanned'`
- **Test file**: `src/app/components/__tests__/TierBadge.test.tsx` (new)

### T-009: TierBadge component renders new labels
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-04 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** `<TierBadge tier="CERTIFIED" />` rendered
- **When** the DOM is queried
- **Then** the visible text is "Trusted Publisher" AND the icon for CERTIFIED is present (style/icon lookups still key off enum, not display text)
- **Test file**: same as T-008

### T-010: Replace raw certTier render in 6 inline sites
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** any of the 6 inline mini-badge sites (SearchPalette, TrendingSkills, FeatureSecurityVerified, VerifiedSkillsTab, PublisherSkillsList, studio/find page)
- **When** rendered with a vendor-tier skill prop
- **Then** the rendered output contains "Trusted Publisher" AND does NOT contain the raw "CERTIFIED" string
- **Test file**: spot-check render test for `TrendingSkills.tsx` (representative); other sites verified via grep that all `{certTier}` references are replaced
- **Files modified**: 6 component files listed in plan.md §5

### T-011: DB enum unchanged — no migration generated
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** the changes from T-008/T-009/T-010
- **When** `npx prisma migrate status` is run (or git diff on `prisma/migrations/`)
- **Then** no new migration file is created
- **Verification**: visual check that `prisma/schema.prisma` line 31-34 enum is untouched

## Phase 4 — Backfill admin endpoint

### T-012: Backfill endpoint updates vendor+VERIFIED rows
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US4-04 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** a SkillVersion row with vendor author (e.g. `anton-abyzov`) and `certTier='VERIFIED'` exists
- **When** `POST /api/v1/admin/recompute-version-cert-tiers` is called with valid `X-Internal-Key`
- **Then** the response is `200` with `{ ok: true, updated: 1, skills: [{ name, version, before: { certTier: 'VERIFIED', certMethod: ... }, after: { certTier: 'CERTIFIED', certMethod: 'VENDOR_AUTO' } }] }`
- **And** the DB row is updated to `certTier='CERTIFIED'`, `certMethod='VENDOR_AUTO'`
- **Test file**: `src/app/api/v1/admin/recompute-version-cert-tiers/__tests__/route.test.ts` (new)

### T-013: Backfill endpoint leaves non-vendor+VERIFIED rows untouched
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US4-04 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** a SkillVersion row with non-vendor author and `certTier='VERIFIED'` exists
- **When** the backfill endpoint is called
- **Then** the response shows `updated: 0` (or excludes this row from the list); the DB row is unchanged
- **Test file**: same as T-012

### T-014: Backfill is idempotent (vendor+CERTIFIED untouched)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US4-04 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** a SkillVersion row with vendor author and `certTier='CERTIFIED'` already
- **When** the backfill endpoint is called
- **Then** `updated: 0`; the DB row is unchanged
- **And** running the endpoint twice in succession returns `updated: 0` on the second call
- **Test file**: same as T-012

### T-015: Backfill requires auth (401 otherwise)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US4-04 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** the backfill endpoint
- **When** called without `X-Internal-Key` header AND without an admin session
- **Then** the response is `401 Unauthorized`
- **Test file**: same as T-012

### T-016: Implement backfill endpoint
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** the failing tests from T-012/T-013/T-014/T-015
- **When** the route handler is implemented at `src/app/api/v1/admin/recompute-version-cert-tiers/route.ts` mirroring trusted-author-backfill structure
- **Then** all 4 tests pass
- **Files created**: `src/app/api/v1/admin/recompute-version-cert-tiers/route.ts`

## Phase 5 — Verification

### T-017: Full vitest run green
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** all Phase 1-4 changes landed
- **When** `npx vitest run` is executed in `repositories/anton-abyzov/vskill-platform/`
- **Then** exit code is 0; no test failures
- **Note**: Update any pre-existing test that asserts the old hardcoded literals

### T-018: Playwright E2E suite green
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** all changes landed
- **When** `npx playwright test` is executed (if E2E tests exist locally)
- **Then** exit code is 0
- **Note**: If E2E suite asserts on "VERIFIED"/"CERTIFIED" text, update assertions to new labels

### T-019: Sync living docs + close
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** all tests pass
- **When** `specweave sync-living-docs 0744-fix-cert-tier-muddle-versions-tab` runs
- **Then** living docs are updated; ready for `/sw:done`
