---
increment: 0326-trust-center-fixes
title: "Trust Center fixes: real tier stats, blocklist retry, reports modal, auto-refresh"
type: feature
status: planned
created: 2026-02-22
test_mode: TDD
coverage_target: 80
by_user_story:
  US-001: [T-001, T-002, T-003]
  US-002: [T-004, T-005]
  US-003: [T-006, T-007]
  US-004: [T-008, T-009]
---

# Tasks: Trust Center fixes

## Phase 1: Backend Fix (US-001)

## User Story: US-001 - Accurate Trust Tier Distribution (P1)

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07, AC-US1-08
**Tasks**: 3 total, 0 completed

### T-001: Write tests for getTrustStats rewrite

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07
**Status**: [x] completed

**Test Plan**:
- **Given** an array of skills with mixed sources (seed with trustTier, Prisma with certTier only) and a blocklist count
- **When** getTrustStats is called
- **Then** T0 = blocklist count, T2/T3/T4 derived from certTier, T1 = remainder, seed trustTier values honored

**Test Cases**:
1. **Unit**: `src/app/api/v1/stats/__tests__/trust-stats.test.ts`
   - TC-001: seed skill with trustTier "T4" counts as T4 (not re-derived)
   - TC-002: Prisma skill with certTier SCANNED maps to T2
   - TC-003: Prisma skill with certTier VERIFIED maps to T3
   - TC-004: Prisma skill with certTier CERTIFIED maps to T4
   - TC-005: skill with no trustTier and no certTier counts as T1
   - TC-006: blocklist count of 5 sets T0=5 (additive, separate from skills)
   - TC-007: deduplication -- skill in both seed and Prisma counted once
   - TC-008: empty skills array + blocklist=0 returns all zeros
   - **Coverage Target**: 90%

**Implementation**:
1. Create test file at `src/app/api/v1/stats/__tests__/trust-stats.test.ts`
2. Write RED tests for the exported `getTrustStats` function signature
3. Run tests to confirm they fail (TDD RED phase)

**Dependencies**: None
**Model**: opus

---

### T-002: Rewrite getTrustStats in stats route

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07
**Status**: [x] completed

**Test Plan**:
- **Given** the RED tests from T-001 exist
- **When** getTrustStats is rewritten with certTier mapping + blocklist count
- **Then** all T-001 tests pass (TDD GREEN phase)

**Implementation**:
1. In `src/app/api/v1/stats/route.ts`, rewrite `getTrustStats()` to accept `(skills, blocklistCount)`
2. For each skill: if `trustTier` is valid (T0-T4), use it; else derive from `certTier` (SCANNED->T2, VERIFIED->T3, CERTIFIED->T4); else T1
3. Add `blocklistCount` to `counts.T0`
4. Export `getTrustStats` for testability
5. Run tests to confirm GREEN

**Dependencies**: T-001
**Model**: opus

---

### T-003: Wire blocklist count into stats API GET handler

**User Story**: US-001
**Satisfies ACs**: AC-US1-06, AC-US1-08
**Status**: [x] completed

**Test Plan**:
- **Given** the stats API GET handler
- **When** a request is made to GET /api/v1/stats
- **Then** blocklist count is queried via `getDb().blocklistEntry.count({ where: { isActive: true } })` and passed to getTrustStats

**Implementation**:
1. In the GET handler, import `getDb` and add `blocklistEntry.count` to the `Promise.all`
2. Pass blocklist count to `getTrustStats(allSkills, blocklistCount)`
3. Wrap blocklist query in try/catch with fallback to 0
4. Run full test suite to confirm

**Dependencies**: T-002
**Model**: opus

---

## Phase 2: Frontend Fixes (US-002, US-003, US-004)

## User Story: US-002 - Blocklist Loading Retry with Exponential Backoff (P1)

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 2 total, 0 completed

### T-004: Write tests for blocklist retry behavior

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** BlockedSkillsTab is rendered and fetch fails
- **When** the component mounts / user clicks Retry
- **Then** retry cycle executes with exponential delays, Retry button appears on exhaustion

**Test Cases**:
1. **Component**: `src/app/trust/__tests__/BlockedSkillsTab.retry.test.tsx`
   - TC-009: error state shows "Retry" button after fetch failure
   - TC-010: clicking Retry starts 3-attempt cycle (mock fetch fails 2x, succeeds 3rd)
   - TC-011: during retry, loading state shown (Retry button not visible)
   - TC-012: all 3 attempts fail -> error + Retry button reappears
   - TC-013: successful fetch clears error and renders blocklist data
   - TC-014: exponential delays follow ~1s, ~2s pattern (use vi.useFakeTimers)
   - **Coverage Target**: 85%

**Implementation**:
1. Create test file with mock fetch and fake timers
2. Write RED tests for retry button visibility, retry cycle, and exponential delays
3. Run tests to confirm they fail

**Dependencies**: None (parallel with T-001)
**Model**: opus

---

### T-005: Implement retry logic in BlockedSkillsTab

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** RED tests from T-004
- **When** fetchWithRetry is implemented in BlockedSkillsTab
- **Then** all T-004 tests pass

**Implementation**:
1. In `src/app/trust/BlockedSkillsTab.tsx`, replace `fetchBlocklist` with `fetchWithRetry(attempts=3, delay=0)`
2. Add inline `sleep(ms)` helper
3. Implement exponential backoff: delay 0 -> 1000 -> 2000 with +/-20% jitter
4. Add "Retry" button in error state: `onClick={() => fetchWithRetry(3, 0)}`
5. During retry, set `loading=true` to show spinner / hide error
6. Run tests to confirm GREEN

**Dependencies**: T-004
**Model**: opus

---

## User Story: US-003 - Reports as Header Button + Overlay Modal (P2)

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06, AC-US3-07
**Tasks**: 2 total, 0 completed

### T-006: Write tests for reports modal behavior

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-05, AC-US3-06
**Status**: [x] completed

**Test Plan**:
- **Given** TrustCenterPage is rendered
- **When** user interacts with the Report a Skill button and modal
- **Then** modal opens/closes correctly, Reports tab is absent from tabs

**Test Cases**:
1. **Component**: `src/app/trust/__tests__/TrustCenterPage.modal.test.tsx`
   - TC-015: TABS array contains only "Verified Skills" and "Blocked Skills" (no "Reports")
   - TC-016: "Report a Skill" button is visible in header area
   - TC-017: clicking button opens overlay modal with dimmed backdrop
   - TC-018: clicking backdrop dismisses modal
   - TC-019: clicking X close button dismisses modal
   - TC-020: modal contains ReportsTab content (form visible)
   - **Coverage Target**: 85%

**Implementation**:
1. Create test file with render + user event testing
2. Write RED tests for tab removal, button presence, modal open/close
3. Run tests to confirm they fail

**Dependencies**: None (parallel with T-001, T-004)
**Model**: opus

---

### T-007: Implement reports modal in page.tsx

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06, AC-US3-07
**Status**: [x] completed

**Test Plan**:
- **Given** RED tests from T-006
- **When** page.tsx is updated to remove Reports tab and add modal
- **Then** all T-006 tests pass

**Implementation**:
1. In `src/app/trust/page.tsx`:
   - Remove `{ key: "reports", label: "Reports" }` from TABS
   - Remove `{activeTab === "reports" && <ReportsTab />}` from content
   - Add `const [reportModalOpen, setReportModalOpen] = useState(false)`
   - Add "Report a Skill" button in header (right of subtitle)
   - Add overlay modal (fixed position, dimmed backdrop, centered card maxWidth 640px)
   - Add X close button (absolute top-right), backdrop click to close
   - Render `<ReportsTab />` inside modal card
2. Run tests to confirm GREEN

**Dependencies**: T-006
**Model**: opus

---

## User Story: US-004 - Auto-Refresh with Relative Time Indicator (P2)

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06
**Tasks**: 2 total, 0 completed

### T-008: Write tests for refresh + relative time

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06
**Status**: [x] completed

**Test Plan**:
- **Given** TrustTierDistribution is rendered with mock stats data
- **When** time passes and user clicks refresh
- **Then** relative time label updates, refresh button re-fetches data

**Test Cases**:
1. **Component**: `src/app/trust/__tests__/TrustTierDistribution.refresh.test.tsx`
   - TC-021: relative time label appears below tier cards ("updated 0s ago" initially)
   - TC-022: label uses muted styling (fontSize 0.75rem)
   - TC-023: refresh icon button is present next to label
   - TC-024: clicking refresh triggers re-fetch of /api/v1/stats
   - TC-025: during refresh, button shows spinning/disabled state
   - TC-026: after 15s tick, label updates to "updated 15s ago" (vi.useFakeTimers)
   - TC-027: after 90s, label shows "updated 1m ago"
   - **Coverage Target**: 85%

**Implementation**:
1. Create test file with mock fetch and fake timers
2. Write RED tests for label presence, styling, refresh behavior, time ticking
3. Run tests to confirm they fail

**Dependencies**: None (parallel with T-001, T-004, T-006)
**Model**: opus

---

### T-009: Implement refresh + relative time in TrustTierDistribution

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06
**Status**: [x] completed

**Test Plan**:
- **Given** RED tests from T-008
- **When** TrustTierDistribution is extended with fetchedAt, relativeTime, refresh
- **Then** all T-008 tests pass

**Implementation**:
1. In `src/app/trust/TrustTierDistribution.tsx`:
   - Add `fetchedAt` state (Date.now() on successful fetch)
   - Add `relativeTime` state, ticked every 15s via setInterval
   - Add `refreshing` state for button disabled/spin
   - Add `formatRelativeTime(ms)` helper (seconds -> "Xs ago", minutes -> "Xm ago")
   - Add `refresh()` callback that re-fetches /api/v1/stats
   - Render: below tier cards, right-aligned flex row with muted label + circular refresh SVG button
   - Spin animation via inline keyframes or style during refreshing state
   - Clean up interval on unmount via useEffect return
2. Run tests to confirm GREEN

**Dependencies**: T-008
**Model**: opus

---

## Phase 3: Verification

### T-010: Run full test suite and verify all ACs

**User Story**: All
**Satisfies ACs**: All (AC-US1-01 through AC-US4-06)
**Status**: [x] completed

**Test Plan**:
- **Given** all implementation tasks complete
- **When** full test suite runs
- **Then** all 27 ACs verified, coverage >= 80%

**Implementation**:
1. Run `npx vitest run` in vskill-platform
2. Verify no regressions in existing tests
3. Check coverage meets 80% target for changed files
4. Mark all spec.md ACs as completed

**Dependencies**: T-003, T-005, T-007, T-009
**Model**: opus
