# 0352 — Fix Certification Tier Display

## Problem

The Prisma schema defines three `CertificationTier` values (`SCANNED`, `VERIFIED`, `CERTIFIED`) but the TypeScript type only exposes two. The data layer silently maps `SCANNED → VERIFIED`, erasing the distinction between skills that passed only Tier 1 automated scan vs Tier 2 LLM verification. Additionally, `certTier` never upgrades from SCANNED after Tier 2 passes, security report resolution does not trigger trust recalculation, and users have no explanation for the dual badge system (cert + trust).

## User Stories

### US-001: Display SCANNED certification tier distinctly

As a user browsing skills, I want to see which skills have only been auto-scanned (Tier 1) versus fully verified (Tier 2), so I can make informed trust decisions.

**Acceptance Criteria:**
- [x] AC-US1-01: `CertificationTier` type in `types.ts` includes `"SCANNED"` as a valid value
- [x] AC-US1-02: `mapDbSkillToSkillData` preserves `SCANNED` from database (no mapping to VERIFIED)
- [x] AC-US1-03: `TierBadge` renders a distinct gray shield icon with "SCANNED" text
- [x] AC-US1-04: Badge API returns gray badge with "scanned" label for SCANNED tier
- [x] AC-US1-05: Skills list page filter includes "Scanned" option

### US-002: Upgrade certTier on Tier 2 pass

As a platform operator, I want skills to auto-upgrade from SCANNED to VERIFIED when Tier 2 completes with PASS verdict.

**Acceptance Criteria:**
- [ ] AC-US2-01: When Tier 2 scan returns PASS for a SCANNED skill, `certTier` updates to VERIFIED
- [ ] AC-US2-02: Only PASS verdict triggers upgrade; CONCERNS and FAIL do not

### US-003: Trigger trust recalc on report resolution

As a platform operator, I want trust scores recalculated on all report resolutions, not just auto-blocking.

**Acceptance Criteria:**
- [ ] AC-US3-01: Report status change to RESOLVED/DISMISSED triggers `updateSkillTrust` for affected skill
- [ ] AC-US3-02: Trust recalc runs regardless of auto-block status

### US-004: Clarify cert vs trust badges

As a user viewing a skill, I want tooltips explaining what each badge represents.

**Acceptance Criteria:**
- [ ] AC-US4-01: TierBadge has `title` attribute explaining certification tiers
- [ ] AC-US4-02: TrustBadge has `title` attribute explaining trust score

## Out of Scope

- Trust score formula changes (handled in 0353/0354)
- Trending score fixes (handled in 0353)
- Data freshness indicators (handled in 0354)
