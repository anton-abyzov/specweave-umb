# Tasks — 0352 Fix Certification Tier Display

### T-001: Add SCANNED to CertificationTier type
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] pending
**Test**: Given types.ts → When CertificationTier is referenced → Then "SCANNED" is valid
- `src/lib/types.ts:9` — change `"VERIFIED" | "CERTIFIED"` to `"SCANNED" | "VERIFIED" | "CERTIFIED"`

### T-002: Stop mapping SCANNED to VERIFIED in data layer
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] pending
**Test**: Given Prisma skill with certTier=SCANNED → When mapDbSkillToSkillData runs → Then result.certTier === "SCANNED"
- `src/lib/data.ts:48-52` — change tierMap: `SCANNED: "SCANNED"`
- Update `buildWhereClause` filter logic for SCANNED
- Fix test in `src/lib/__tests__/data-db-first.test.ts:640`

### T-003: Add SCANNED rendering to TierBadge
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [ ] pending
**Test**: Given tier="SCANNED" → When TierBadge renders → Then gray shield icon with "SCANNED" text
- `src/app/components/TierBadge.tsx` — add ScannedIcon (gray #6B7280), handle 3 tiers

### T-004: Add SCANNED to badge API
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [ ] pending
**Test**: Given skill with certTier=SCANNED → When GET badge → Then gray SVG with "scanned"
- `src/app/api/v1/skills/[name]/badge/route.ts:5-13` — add SCANNED to TIER_COLORS (#6B7280) and TIER_LABELS ("scanned")

### T-005: Add SCANNED filter to skills list
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [ ] pending
**Test**: Given skills page → When rendered → Then tier filter includes "Scanned"
- `src/app/skills/page.tsx` — add to TIER_OPTIONS

### T-006: Auto-upgrade certTier on Tier 2 PASS
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [ ] pending
**Test**: Given SCANNED skill → When Tier 2 PASS stored → Then certTier updates to VERIFIED
- Find Tier 2 result handler; add upgrade logic for SCANNED → VERIFIED on PASS only

### T-007: Trigger trust recalc on all report resolutions
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [ ] pending
**Test**: Given report RESOLVED without auto-block → When PATCH runs → Then updateSkillTrust called
- `src/app/api/v1/admin/reports/[id]/route.ts` — move updateSkillTrust outside auto-block conditional

### T-008: Add tooltip explanations for badges
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [ ] pending
**Test**: Given skill detail page → When badges render → Then title attrs present
- `src/app/skills/[name]/page.tsx:199-201` — wrap badges with title attrs
