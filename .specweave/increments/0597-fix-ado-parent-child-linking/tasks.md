# Tasks: Fix ADO Sync Parent-Child Linking Bug

## Phase 1: Fix Error Handling

### T-001: Make linkWorkItems() throw on failure, handle 409 idempotently
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] Completed
**Test Plan**:
- Given `linkWorkItems()` is called and ADO API returns 500
- When the response is processed
- Then an Error is thrown with status code and message
- Given `linkWorkItems()` is called and ADO API returns 409
- When the response is processed
- Then the method returns successfully without throwing

**Files**: `src/integrations/ado/ado-client.ts` (lines 628-633)

---

### T-002: Add unit tests for linkWorkItems in ado-client
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] Completed
**Test Plan**:
- Given createWorkItem is called with parentId
- When the work item is created successfully
- Then a second PATCH call is made with Hierarchy-Reverse link
- Given createWorkItem is called without parentId
- When the work item is created
- Then only one fetch call is made (no linking)
- Given linkWorkItems fails with 500
- When createWorkItem is called with parentId
- Then createWorkItem throws an error
- Given linkWorkItems returns 409
- When createWorkItem is called with parentId
- Then createWorkItem succeeds

**Files**: `tests/unit/integrations/ado/ado-client.test.ts`

---

## Phase 2: Fix Metadata

### T-003: Remove dangerous metadata fallback in ExternalIssueAutoCreator
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] Completed
**Test Plan**:
- Given a story has no entry in storyItemMap
- When updateMetadataWithAdoWorkItem runs
- Then the story is skipped in metadata (NOT filled with Feature ID)
- And a warning is logged

**Files**: `src/sync/external-issue-auto-creator.ts` (lines 1244-1251)

---

## Phase 3: ADO Provider Tests

### T-004: Add parent-child linking tests for ADO provider
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] Completed
**Test Plan**:
- Given feature has externalRef with id "1448"
- When createIssue is called
- Then the request body includes a `/relations/-` operation with `System.LinkTypes.Hierarchy-Reverse`
- Given feature has no externalRef
- When createIssue is called
- Then no `/relations/-` operation is in the request body
- Given feature has externalRef
- When createIssue builds the parent URL
- Then the URL matches `https://dev.azure.com/{org}/{project}/_apis/wit/workItems/{id}`

**Files**: `tests/unit/sync/providers/ado-provider.test.ts`
