# Tasks: Fix dashboard cost display for subscription plans

## Task Notation

- `[T###]`: Task ID
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (default)

## Phase 1: Fix test expectations

### T-001: Update Opus cost test expectations

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03 | **Status**: [x] Completed

**Description**: Update test expectations for Opus model to match current pricing (input: $5, output: $25, cacheWrite: $6.25, cacheRead: $0.50).

**Files**: `tests/unit/dashboard/cost-aggregator.test.ts`

**Implementation Details**:
- Fix "should compute non-zero totalCost even for subscription plans": expected 0.525 → 0.175
- Fix "should calculate Opus costs correctly with all token types": expected 10.50 → 3.50, savings 13.50 → 4.50
- Update inline comments to show correct arithmetic

**Test Plan**:
- **TC-001**: Opus subscription cost test passes
  - Given Opus session with 10000 input + 5000 output tokens
  - When getTokenSummaries called with subscription billing
  - Then totalCost = (10000×5 + 5000×25) / 1M = 0.175
- **TC-002**: Opus all-token-types test passes
  - Given Opus session with 100K input, 50K output, 200K cacheWrite, 1M cacheRead
  - When getTokenSummaries called
  - Then totalCost = 3.50, totalSavings = 4.50

**Dependencies**: None
**Model**: haiku

---

### T-002: Update Haiku cost test expectations

**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] Completed

**Description**: Update test expectations for Haiku model to match current pricing (input: $1, output: $5).

**Files**: `tests/unit/dashboard/cost-aggregator.test.ts`

**Implementation Details**:
- Fix "should calculate Haiku costs correctly": expected 0.28 → 0.35
- Update inline comment to show correct arithmetic

**Test Plan**:
- **TC-003**: Haiku cost test passes
  - Given Haiku session with 100K input + 50K output tokens
  - When getTokenSummaries called
  - Then totalCost = (100000×1 + 50000×5) / 1M = 0.35

**Dependencies**: None
**Model**: haiku

---

## Phase 2: Remove dead isMaxPlan

### T-003: Remove isMaxPlan from server-side code

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] Completed

**Description**: Remove `isMaxPlan` from `CostsSummaryPayload` interface and `getTokenSummaries()` result.

**Files**: `src/dashboard/server/data/cost-aggregator.ts`

**Implementation Details**:
- Remove `isMaxPlan: boolean` from `CostsSummaryPayload` interface (line 30)
- Remove `isMaxPlan: planType === 'subscription'` from result object (line 129)

**Test Plan**:
- **TC-004**: CostsSummaryPayload no longer has isMaxPlan
  - Given cost-aggregator compiled
  - When result inspected
  - Then isMaxPlan property does not exist

**Dependencies**: None
**Model**: haiku

---

### T-004: Remove isMaxPlan from client-side interface

**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] Completed

**Description**: Remove `isMaxPlan?: boolean` from `CostsData` interface in CostsPage.tsx.

**Files**: `src/dashboard/client/src/pages/CostsPage.tsx`

**Implementation Details**:
- Remove `isMaxPlan?: boolean` from `CostsData` interface (line 15)

**Test Plan**:
- **TC-005**: CostsData interface compiles without isMaxPlan
  - Given CostsPage.tsx compiled
  - When interface used
  - Then no TypeScript errors

**Dependencies**: T-003
**Model**: haiku

---

### T-005: Update tests to remove isMaxPlan assertions

**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] Completed

**Description**: Remove all `isMaxPlan` assertions from cost-aggregator tests. The `billingContext.planType` checks already cover the same semantics.

**Files**: `tests/unit/dashboard/cost-aggregator.test.ts`

**Implementation Details**:
- Remove entire "isMaxPlan config-driven detection" describe block (lines 85-115)
- The billingContext tests already verify the same information

**Test Plan**:
- **TC-006**: All remaining tests pass without isMaxPlan assertions
  - Given isMaxPlan tests removed
  - When test suite runs
  - Then all tests pass

**Dependencies**: T-003
**Model**: haiku

---

## Phase 3: Type billing config

### T-006: Add typed billing config access in dashboard-server.ts

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] Completed

**Description**: Replace `(config as any)?.billing` with properly typed access.

**Files**: `src/dashboard/server/dashboard-server.ts`

**Implementation Details**:
- Add BillingConfig type to the config object or use type narrowing
- Replace both `(config as any)?.billing` usages (lines ~315 and ~354)

**Test Plan**:
- **TC-007**: No TypeScript errors after typing change
  - Given typed billing config access
  - When project compiled
  - Then no type errors

**Dependencies**: None
**Model**: sonnet

---

## Phase 4: Validation

### T-007: Run full test suite and verify

**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] Completed

**Description**: Run all cost-aggregator tests, verify 0 failures.

**Dependencies**: T-001, T-002, T-003, T-004, T-005, T-006
**Model**: haiku
