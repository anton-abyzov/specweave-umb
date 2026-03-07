# Tasks: Unify skill page badges

## Task Notation

- `[T###]`: Task ID
- `[ ]`: Not started
- `[x]`: Completed

## Phase 1: TDD Red

### T-001: Write failing test for badge unification
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test Plan**:
- **File**: `src/app/skills/__tests__/skill-detail-badges.test.tsx`
- **TC-001**: Given the skill detail page renders, When checking the badge row, Then TierBadge text ("VERIFIED"/"CERTIFIED") should NOT appear as a standalone cert badge
- **TC-002**: Given the skill detail page renders with trustTier="T3", When checking the badge row, Then TrustBadge with "T3 VERIFIED" should be visible

**Dependencies**: None

## Phase 2: TDD Green

### T-002: Remove TierBadge from skill detail page
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given skill detail page → When rendered → Then only TrustBadge appears in badge row

**Implementation**:
1. Remove TierBadge import
2. Remove TierBadge `<span>` wrapper (lines 177-179)
3. Keep TrustBadge rendering

**Dependencies**: T-001

## Phase 3: Verify

### T-003: Run full test suite
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given all changes applied → When running `npx vitest run` → Then all tests pass

**Dependencies**: T-002
