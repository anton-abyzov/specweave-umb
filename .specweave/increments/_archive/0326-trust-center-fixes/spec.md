---
increment: 0326-trust-center-fixes
title: >-
  Trust Center fixes: real tier stats, blocklist retry, reports modal,
  auto-refresh
type: feature
priority: P1
status: completed
created: 2026-02-22T00:00:00.000Z
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Trust Center fixes: real tier stats, blocklist retry, reports modal, auto-refresh

## Overview

The Trust Center page (`/trust`) has four issues to fix:

1. **Trust tier distribution shows wrong counts** -- the stats API iterates `getSkills()` results and reads `trustTier`, but `mapDbSkillToSkillData()` never sets `trustTier` for Prisma skills, so all DB skills default to T1. The fix must compute a merged count: seed skills use their existing `trustTier`, Prisma skills derive trust tier from `certTier` (SCANNED->T2, VERIFIED->T3, CERTIFIED->T4), seed-only skills not in DB count as T1 (unscanned), and active blocklist entries contribute to T0.
2. **Blocklist tab has no retry/error UX** -- when `GET /api/v1/blocklist` fails, the tab shows a static error with no way to recover. Add a retry button that restarts a full 3-attempt exponential backoff cycle (fresh start, not resume).
3. **Reports tab wastes a full tab** -- move Reports out of the tab bar into a header-level "Report a Skill" button that opens a full-page overlay modal (centered card on dimmed backdrop), matching the block dialog pattern in VerifiedSkillsTab. Dismiss on outside click AND X close button (top-right).
4. **No freshness indicator** -- add a "last updated" relative-time label (e.g., "updated 45s ago") below the tier distribution cards, right-aligned, in small muted text with a small circular refresh icon button next to it.

## User Stories

### US-001: Accurate Trust Tier Distribution (P1)
**Project**: vskill-platform

**As a** Trust Center visitor
**I want** tier distribution cards to show correct counts from both seed and database skills
**So that** I can trust the security posture metrics displayed on the page

**Acceptance Criteria**:
- [x] **AC-US1-01**: Stats API computes `totalSkills` as merged count of seed skills + Prisma-only skills (no double counting of skills that exist in both)
- [x] **AC-US1-02**: Seed-only skills (not in Prisma) without a `trustTier` value count as T1 (Unscanned)
- [x] **AC-US1-03**: Prisma skills with `certTier=SCANNED` map to T2 (Scanned)
- [x] **AC-US1-04**: Prisma skills with `certTier=VERIFIED` map to T3 (Verified)
- [x] **AC-US1-05**: Prisma skills with `certTier=CERTIFIED` map to T4 (Certified)
- [x] **AC-US1-06**: Active blocklist entries (from `blocklistEntry` table where `isActive=true`) contribute to T0 count
- [x] **AC-US1-07**: Seed skills that already have `trustTier` set (e.g., "T4") use their existing value, not re-derive from certTier
- [x] **AC-US1-08**: The five tier cards (T0-T4) display updated counts immediately after API returns

---

### US-002: Blocklist Loading Retry with Exponential Backoff (P1)
**Project**: vskill-platform

**As a** Trust Center visitor
**I want** to retry loading the blocklist when it fails
**So that** temporary network or server errors don't leave me on a dead-end error screen

**Acceptance Criteria**:
- [x] **AC-US2-01**: When `GET /api/v1/blocklist` fails, BlockedSkillsTab shows an error message with a visible "Retry" button
- [x] **AC-US2-02**: Clicking Retry starts a fresh 3-attempt exponential backoff cycle (delays: ~1s, ~2s, ~4s with jitter)
- [x] **AC-US2-03**: During retry attempts, a loading/spinner state is shown (Retry button disabled or replaced with progress indicator)
- [x] **AC-US2-04**: If all 3 attempts fail, the error message reappears with the Retry button enabled again for another fresh cycle
- [x] **AC-US2-05**: If any attempt succeeds, the blocklist data renders normally and retry state resets

---

### US-003: Reports as Header Button + Overlay Modal (P2)
**Project**: vskill-platform

**As a** Trust Center visitor
**I want** the report form accessible from a header button instead of a dedicated tab
**So that** the tab bar stays focused on data views (Verified / Blocked) and reporting feels like a quick action

**Acceptance Criteria**:
- [x] **AC-US3-01**: The "Reports" tab is removed from the TABS array in page.tsx; only "Verified Skills" and "Blocked Skills" tabs remain
- [x] **AC-US3-02**: A "Report a Skill" button appears in the Trust Center header (right of the subtitle text), styled consistently with the page
- [x] **AC-US3-03**: Clicking the button opens a full-page overlay modal: dimmed backdrop (`rgba(0,0,0,0.5)`), centered card, matching the block dialog pattern in VerifiedSkillsTab
- [x] **AC-US3-04**: The modal contains the existing ReportsTab content (submission form + recent reports table)
- [x] **AC-US3-05**: Modal dismisses on clicking outside the card (backdrop click)
- [x] **AC-US3-06**: Modal has an X close button positioned top-right of the card
- [x] **AC-US3-07**: After successful report submission, the recent reports list in the modal updates without closing the modal

---

### US-004: Auto-Refresh with Relative Time Indicator (P2)
**Project**: vskill-platform

**As a** Trust Center visitor
**I want** to see when the tier distribution was last refreshed and manually trigger a refresh
**So that** I know the data is current without reloading the entire page

**Acceptance Criteria**:
- [x] **AC-US4-01**: A relative time label (e.g., "updated 45s ago", "updated 2m ago") appears below the tier distribution cards, right-aligned
- [x] **AC-US4-02**: The label uses small muted text styling (`fontSize: 0.75rem`, `color: var(--text-faint)`)
- [x] **AC-US4-03**: A small circular refresh icon button appears next to the relative time label
- [x] **AC-US4-04**: Clicking the refresh button re-fetches `GET /api/v1/stats` and updates the tier cards
- [x] **AC-US4-05**: The relative time label updates live (ticks every ~15 seconds) without page reload
- [x] **AC-US4-06**: During refresh fetch, the refresh button shows a spinning/disabled state

## Functional Requirements

### FR-001: Stats API Trust Tier Computation
The `GET /api/v1/stats` route must build trust tier counts from three data sources:
1. **Seed skills**: Use existing `trustTier` field if set; otherwise count as T1
2. **Prisma skills**: Derive trust tier from `certTier` enum -- SCANNED->T2, VERIFIED->T3, CERTIFIED->T4
3. **Blocklist**: Query `blocklistEntry.count({ where: { isActive: true } })` for T0 count

Deduplication: Prisma skills whose `name` matches a seed skill name must not be double-counted (seed data is canonical for its skills).

### FR-002: Exponential Backoff Implementation
Retry logic in BlockedSkillsTab uses 3 attempts with exponential delays:
- Attempt 1: immediate
- Attempt 2: ~1000ms (with +/-200ms jitter)
- Attempt 3: ~2000ms (with +/-400ms jitter)

The Retry button click always starts a fresh cycle (resets attempt counter to 0).

### FR-003: Modal Architecture
The report modal reuses the existing `ReportsTab` component, wrapped in a fixed-position overlay. The modal card width is constrained to `maxWidth: 640px` to accommodate the form and table comfortably.

## Success Criteria

- Trust tier cards show correct merged counts matching seed + DB + blocklist data
- Blocklist retry recovers from transient failures without page reload
- Reports tab removed from navigation; report flow accessible via header button + modal
- Last-updated indicator shows live relative time with manual refresh capability

## Out of Scope

- Auto-refresh polling on a timer (manual refresh only for now)
- Tier distribution bar chart or sparkline visualizations
- Admin-only stats or audit log of tier changes
- Mobile-specific responsive layout changes to the Trust Center

## Dependencies

- Prisma `blocklistEntry` table must be accessible from the stats route (already available via `getDb()`)
- Existing `ReportsTab` component must remain functionally intact (just re-mounted inside a modal)
