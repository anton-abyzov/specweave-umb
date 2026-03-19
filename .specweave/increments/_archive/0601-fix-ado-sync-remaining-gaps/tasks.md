# Tasks: Fix Remaining ADO Sync Gaps

## Phase 1: P0 Fix

### T-001: Remove ADO auto-mapping block in sync-progress.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] Completed
**Test Plan**:
- Given sync-progress runs with unmapped ADO stories
- When the ADO section executes
- Then unmapped stories are NOT auto-mapped to the Feature ID
- And a warning is logged

**Files**: `src/cli/commands/sync-progress.ts` (lines 397-416)

---

## Phase 2: P1 Fixes

### T-002: Add title filter to AdoWorkItemFilter and searchWorkItemByTitle method
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] Completed
**Test Plan**:
- Given AdoClient.searchWorkItemByTitle("title", ["Feature"]) is called
- When WIQL query executes with title filter
- Then returns first matching work item or null

**Files**: `src/integrations/ado/ado-client.ts`

---

### T-003: Use Layer 3 dedup in createAdoIssues before Feature creation
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04 | **Status**: [x] Completed
**Test Plan**:
- Given an increment's Feature already exists in ADO (matching title + specweave tag)
- When createAdoIssues runs
- Then it reuses the existing Feature instead of creating a duplicate

**Files**: `src/sync/external-issue-auto-creator.ts` (before line 861)

---

### T-004: Fix updateIssue missing response.ok check
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] Completed
**Test Plan**:
- Given updateIssue is called and ADO API returns 400
- When the response is processed
- Then an Error is thrown

**Files**: `src/sync/providers/ado.ts` (lines 194-201)

---

### T-005: Add unit tests for all changes
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-02, AC-US3-02 | **Status**: [x] Completed
**Files**: `tests/unit/integrations/ado/ado-client.test.ts`, `tests/unit/sync/providers/ado-provider.test.ts`
