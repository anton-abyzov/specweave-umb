# Implementation Plan: Fix dashboard cost display for subscription plans

## Overview

Three targeted fixes to the dashboard cost display subsystem: align test expectations with updated pricing constants, remove the dead `isMaxPlan` field, and add type safety for billing config access.

## Architecture

### Components Affected
- **cost-aggregator.ts**: Remove `isMaxPlan` from interface and computation
- **CostsPage.tsx**: Remove `isMaxPlan` from client-side interface
- **dashboard-server.ts**: Type the billing config access (lines 315, 354)
- **cost-aggregator.test.ts**: Fix 3 failing test expectations, remove `isMaxPlan` assertions

### Data Model Changes
- `CostsSummaryPayload`: Remove `isMaxPlan: boolean` field
- `CostsData` (client): Remove `isMaxPlan?: boolean` field
- No new fields added

## Technology Stack

- **Language/Framework**: TypeScript (Node.js server + React client)
- **Testing**: Vitest
- **No new dependencies**

## Implementation Phases

### Phase 1: Fix test expectations (P1)
Update Opus and Haiku cost expectations to match current PRICING constants.

### Phase 2: Remove isMaxPlan dead code (P2)
Remove from interfaces, computation, and tests. Frontend already uses `billingContext.planType`.

### Phase 3: Type billing config access (P2)
Replace `(config as any)?.billing` with typed access.

## Testing Strategy

Run existing test suite — all 13 tests must pass after changes.

## Technical Challenges

None — straightforward code cleanup and test alignment.
