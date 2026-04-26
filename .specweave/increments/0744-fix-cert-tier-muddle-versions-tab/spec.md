---
increment: 0744-fix-cert-tier-muddle-versions-tab
title: Fix CERTIFIED/VERIFIED cert-tier muddle on Versions tab
type: bug
priority: P2
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix CERTIFIED/VERIFIED cert-tier muddle on Versions tab

## Overview

The Skill Studio Versions tab shows two cert-tier badges, **CERTIFIED** and **VERIFIED**, that look like grades but actually encode different things:

- **CERTIFIED** = "publisher is in the trusted vendor list, scanning bypassed"
- **VERIFIED** = "publisher is non-vendor and the skill passed automated/LLM security scans"

Concrete reproduction: `anton-abyzov/obsidian-brain` shows `1.0.0–1.0.5 = CERTIFIED, 1.0.6 = VERIFIED` for the same skill from the same author. That mismatch is impossible under the documented model — it's a real bug, not a UI quirk.

Three problems, one increment:

1. **Bug**: `src/lib/skill-update/scanner.ts:184` hardcodes `certTier: 'VERIFIED'` on the auto-poll path, ignoring vendor status. The submission/publish path (`src/lib/submission/publish.ts:218`) correctly calls `deriveCertTier(scan, { isVendor })`. Vendor-org skills get the wrong tier when the auto-poll detects a new commit.
2. **UX**: The per-version certTier chip on the Versions tab is informationally empty — same publisher → same chip on every row. Useful per-version data (`certMethod`, `certScore`) isn't shown.
3. **Naming**: The labels are anti-intuitive. "CERTIFIED" sounds higher-trust than "VERIFIED" but actually means "we trusted the publisher and skipped scanning"; "VERIFIED" actually means "we ran security scans." Most users would assume the opposite.

## User Stories

### US-001: Vendor-org skills are CERTIFIED everywhere (P1)
**Project**: vskill-platform

**As a** vskill-platform operator
**I want** vendor-org skills to receive the CERTIFIED tier on every code path that creates a SkillVersion row
**So that** the Versions tab and the skill header don't disagree about whether a skill is from a trusted vendor

**Acceptance Criteria**:
- [x] **AC-US1-01**: When the auto-poll scanner creates a SkillVersion row for a skill whose author is in `VENDOR_ORGS` (e.g. `anton-abyzov`, `anthropics`, `openai`), the row is persisted with `certTier='CERTIFIED'` and `certMethod='VENDOR_AUTO'`.
- [x] **AC-US1-02**: When the auto-poll scanner creates a SkillVersion row for a non-vendor author, the row is persisted with `certTier='VERIFIED'` and `certMethod='AUTOMATED_SCAN'`.
- [x] **AC-US1-03**: Existing SkillVersion rows that are stale (vendor author + `certTier='VERIFIED'`) are corrected by an idempotent admin endpoint `POST /api/v1/admin/recompute-version-cert-tiers`.
- [x] **AC-US1-04**: The admin endpoint requires `SUPER_ADMIN` role OR `X-Internal-Key` header (returns 401 otherwise) and returns `{ ok: true, updated: <count>, skills: [{name, version, before, after}] }`.

---

### US-002: Versions tab shows per-version data that actually differs (P2)
**Project**: vskill-platform

**As a** skill consumer browsing version history
**I want** the Versions tab to show data that varies between versions (scan method, score)
**So that** the version list tells me something useful about each release instead of repeating the publisher tier on every row

**Acceptance Criteria**:
- [x] **AC-US2-01**: The Versions tab no longer renders a per-row chip whose text is the raw `certTier` value (`VERIFIED`/`CERTIFIED`).
- [x] **AC-US2-02**: Each row shows the human-readable `certMethod` mapping: `VENDOR_AUTO` → "Trusted Publisher", `LLM_JUDGE` → "LLM-judged scan", `AUTOMATED_SCAN` → "Automated scan".
- [x] **AC-US2-03**: Each row shows `certScore` as `<n>/100` when non-null; the score cell is omitted entirely when null (no "/100" with empty number).
- [x] **AC-US2-04**: The `getSkillVersions()` data fetcher returns `certMethod` alongside the existing `certTier` and `certScore` fields.

---

### US-003: TierBadge labels are renamed to be honest about meaning (P2)
**Project**: vskill-platform

**As a** skill consumer or publisher
**I want** the cert-tier badge text to reflect what the badge actually means
**So that** I'm not misled into thinking "CERTIFIED" is a higher verification level than "VERIFIED"

**Acceptance Criteria**:
- [x] **AC-US3-01**: The shared `TierBadge` component renders display text "Trusted Publisher" when `tier === 'CERTIFIED'` and "Security-Scanned" when `tier === 'VERIFIED'`.
- [x] **AC-US3-02**: A shared helper `formatTierLabel(certTier)` is exported from `src/app/components/TierBadge.tsx` and consumed by inline mini-badge sites: `SearchPalette.tsx`, `TrendingSkills.tsx`, `FeatureSecurityVerified.tsx`, `VerifiedSkillsTab.tsx`, `PublisherSkillsList.tsx`, `studio/find/[owner]/[repo]/[skill]/page.tsx`.
- [x] **AC-US3-03**: The DB enum `CertificationTier { VERIFIED, CERTIFIED }` is unchanged — only display text changes. No Prisma migration is generated.
- [x] **AC-US3-04**: Icon and color theming continue to key off the enum value (CERTIFIED vs VERIFIED), not the display text.

---

### US-004: TDD coverage gates the fix (P1)
**Project**: vskill-platform

**As a** maintainer
**I want** every behavior change preceded by a failing test
**So that** regressions are caught and the fix is provably correct

**Acceptance Criteria**:
- [x] **AC-US4-01**: New unit tests in `src/lib/skill-update/__tests__/scanner.test.ts` cover the vendor and non-vendor auto-poll branches; tests fail without the scanner.ts change and pass after.
- [x] **AC-US4-02**: New render tests cover `TierBadge` label resolution for both enum values.
- [x] **AC-US4-03**: New render tests cover the Versions tab `certMethod` chip text mapping and `certScore` rendering.
- [x] **AC-US4-04**: New API tests cover the backfill endpoint: vendor+VERIFIED → updated, non-vendor+VERIFIED → untouched, vendor+already-CERTIFIED → untouched, unauthenticated → 401.
- [x] **AC-US4-05**: Full `npx vitest run` suite passes after all changes; existing tests that pinned the old hardcoded `certTier: 'VERIFIED'` are updated.

## Functional Requirements

### FR-001: Unified cert-tier derivation
All code paths that create or update SkillVersion.certTier MUST call `deriveCertTier(scan, { isVendor })` from `src/lib/submission/types.ts`. Hardcoded values are forbidden.

### FR-002: Per-version UI data
The Versions tab data fetcher MUST select `certMethod` from SkillVersion alongside the existing `certTier` and `certScore` fields. The UI MUST render `certMethod` and `certScore` per row instead of repeating the publisher's `certTier`.

### FR-003: Display label resolver
A single `formatTierLabel(certTier)` helper MUST be the source of truth for human-readable badge text. All TierBadge consumers (component and inline sites listed in AC-US3-02) MUST use it.

### FR-004: Backfill endpoint
`POST /api/v1/admin/recompute-version-cert-tiers` MUST be idempotent (re-runs are safe, filter excludes already-CERTIFIED rows) and require `SUPER_ADMIN` role OR `X-Internal-Key` header.

## Success Criteria

- After deploy + one backfill run, no SkillVersion row in the production DB has a vendor author paired with `certTier='VERIFIED'`.
- Versions tab for `anton-abyzov/obsidian-brain` shows consistent labels across all versions, with per-row `certMethod`/`certScore` cells.
- Skill header TierBadge shows "Trusted Publisher" for vendor-org skills and "Security-Scanned" for community skills.
- All existing E2E and unit tests continue to pass; new tests cover the bug fix and label resolver.

## Out of Scope

- DB enum rename (would require Prisma migration + data backfill — not worth it for a label change).
- Remotion video re-render (`scenes/VerifiedSkills.tsx` — pre-rendered assets, separate refresh cadence).
- Admin dashboard inline TierBadge rewrite (admin-only surface, low blast radius — defer unless requested).
- Search ranking weights tied to `certTier` (`search.ts`) — semantics unchanged at the enum level.
- Changes to `VENDOR_ORGS` membership or vendor-vetting policy.
- Resuming or modifying the parallel active increment 0670-skill-builder-universal.

## Dependencies

- `deriveCertTier()` at `src/lib/submission/types.ts:160` (existing, reused).
- `isVendorOrg()` at `src/lib/trust/trusted-orgs.ts:23` (existing, reused).
- `VENDOR_ORGS` set at `src/lib/trust/trusted-orgs.ts:13` (existing, reused).
- `requireAdmin`, `hasInternalAuth`, `jsonResponse`, `errorResponse` admin route plumbing (existing, mirrored from `trusted-author-backfill/route.ts`).
