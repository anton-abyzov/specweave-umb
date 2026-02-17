---
increment: 0223-fix-dashboard-cost-display
title: "Fix dashboard cost display for subscription plans"
type: bug
priority: P1
status: completed
created: 2026-02-16
started: 2026-02-17
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Fix dashboard cost display for subscription plans

## Overview

Dashboard shows API-equivalent costs as Total Cost which is misleading for subscription users. The billing context config and frontend relabeling are already in place, but: (1) test expectations are stale after pricing constant updates for Opus and Haiku models, (2) the `isMaxPlan` field is dead code — computed server-side but never consumed by the frontend, and (3) billing config access uses unsafe `as any` casting.

## User Stories

### US-001: Fix stale test expectations after pricing update (P1)
**Project**: specweave

**As a** developer maintaining the dashboard
**I want** tests to match the current Anthropic pricing constants
**So that** the test suite passes and validates cost calculations correctly

**Acceptance Criteria**:
- [x] **AC-US1-01**: Opus cost test expectations match current pricing (input: $5/MTok, output: $25/MTok, cacheWrite: $6.25/MTok, cacheRead: $0.50/MTok)
- [x] **AC-US1-02**: Haiku cost test expectations match current pricing (input: $1/MTok, output: $5/MTok)
- [x] **AC-US1-03**: All 10 cost-aggregator tests pass (3 dead isMaxPlan tests removed)

---

### US-002: Remove dead isMaxPlan field (P2)
**Project**: specweave

**As a** developer reading the codebase
**I want** unused fields removed from API payloads
**So that** the interface is clean and not misleading

**Acceptance Criteria**:
- [x] **AC-US2-01**: `isMaxPlan` removed from `CostsSummaryPayload` interface in cost-aggregator.ts
- [x] **AC-US2-02**: `isMaxPlan` removed from `CostsData` interface in CostsPage.tsx
- [x] **AC-US2-03**: `isMaxPlan` computation removed from `getTokenSummaries()`
- [x] **AC-US2-04**: Tests updated to not assert on `isMaxPlan` (billingContext.planType covers the same semantics)

---

### US-003: Type-safe billing config access (P2)
**Project**: specweave

**As a** developer working on the dashboard server
**I want** billing config access to be properly typed
**So that** type errors are caught at compile time

**Acceptance Criteria**:
- [x] **AC-US3-01**: `(config as any)?.billing` replaced with typed access in dashboard-server.ts
- [x] **AC-US3-02**: No TypeScript errors introduced

## Functional Requirements

### FR-001: Test expectations reflect current pricing
Update all cost calculation test expectations to use the pricing constants defined in cost-aggregator.ts PRICING map.

### FR-002: Remove dead isMaxPlan field
Remove `isMaxPlan` from server payload, client interface, and all test assertions. `billingContext.planType` is the canonical way to detect subscription plans.

### FR-003: Typed billing config
Add a `billing` property to the config type or use a narrowing pattern to avoid `as any`.

## Success Criteria

- All 10 cost-aggregator tests pass (3 isMaxPlan tests removed as dead code, 3 stale expectations fixed)
- No TypeScript compilation errors
- `isMaxPlan` grep returns 0 results in src/

## Out of Scope

- Changing actual pricing values (they're already correct per Anthropic Feb 2026 rates)
- Changing frontend relabeling logic (already working correctly)
- Adding new billing features

## Dependencies

None — self-contained bug fix.
