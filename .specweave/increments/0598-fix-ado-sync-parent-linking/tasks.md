# Tasks: Fix ADO Sync Wrong Parent Links

## T-001: Write failing tests for findStoryByTitle() scoped query
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-03, AC-US1-04

**Test Plan**:
- Given `featureId="FS-591"` and `usId="US-001"`, When `findStoryByTitle(featureId, usId)` is called, Then the WIQL query CONTAINS clause is `'[FS-591][US-001]'`
- Given two features A and B both have `US-001`, When syncing feature A, Then only feature A's story is matched (WIQL scoped by feature prefix)
- Given no story exists under the current feature, When `findStoryByTitle()` is called with that feature's id, Then it returns `null`

**File**: `plugins/specweave/lib/integrations/ado/ado-spec-sync.test.ts`
**Dependencies**: None

---

## T-002: Fix findStoryByTitle() — add featureId param and scope WIQL
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02

**Implementation Details**:
- Signature: `findStoryByTitle(usId: string)` → `findStoryByTitle(featureId: string, usId: string)`
- Line 683: `CONTAINS '[${usId}]'` → `CONTAINS '[${featureId}][${usId}]'`
- Line 458 (caller in `syncUserStories()`): `findStoryByTitle(us.id)` → `findStoryByTitle(spec.metadata.id.toUpperCase(), us.id)`

**Test Plan**:
- Given T-001 failing tests, When the signature and WIQL are updated, Then all T-001 tests pass

**File**: `plugins/specweave/lib/integrations/ado/ado-spec-sync.ts`
**Dependencies**: T-001

---

## T-003: Update story title format to include feature prefix
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**AC**: AC-US1-01

**Implementation Details**:
- Line 454: `[${us.id}] ${us.title}` → `[${spec.metadata.id.toUpperCase()}][${us.id}] ${us.title}`

**Test Plan**:
- Given spec id `fs-591` and US `US-001 My Story`, When `syncUserStories()` builds the title, Then the resulting title is `[FS-591][US-001] My Story`

**File**: `plugins/specweave/lib/integrations/ado/ado-spec-sync.ts`
**Dependencies**: T-002

---

## T-004: Write failing tests for updateStory() parent re-linking
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05

**Test Plan**:
- Given `parentId` provided and story has no existing parent, When `updateStory()` runs, Then it GETs with `$expand=relations` then PATCHes to add parent link
- Given `parentId` provided and existing parent matches intended parent, When `updateStory()` runs, Then no parent relation PATCH is issued (no-op)
- Given `parentId` provided and existing parent differs from intended parent, When `updateStory()` runs, Then a single PATCH with `op:remove` at old relation index + `op:add` for new parent is issued
- Given `parentId` provided, When `updateStory()` runs, Then it never hits the silent catch block (AC-US2-05)

**File**: `plugins/specweave/lib/integrations/ado/ado-spec-sync.test.ts`
**Dependencies**: None

---

## T-005: Fix updateStory() — fetch-compare-swap parent link
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05

**Implementation Details**:
- When `updates.parentId` is set, fetch `GET /wit/workitems/{storyId}?$expand=relations&api-version=7.0`
- Find existing `System.LinkTypes.Hierarchy-Reverse` relation; extract parent work item ID from relation URL last path segment
- If no existing parent → add new parent link (preserve existing behavior)
- If existing parent === `updates.parentId` → skip (no-op, avoids 409)
- If existing parent !== `updates.parentId` → single PATCH with `[{ op:'remove', path:'/relations/{idx}' }, { op:'add', path:'/relations/-', value:{...} }]`
- Remove the silent `catch` block (lines 833-835); propagate real API errors

**Test Plan**:
- Given T-004 failing tests, When fetch-compare-swap logic replaces the silent catch, Then all T-004 tests pass

**File**: `plugins/specweave/lib/integrations/ado/ado-spec-sync.ts`
**Dependencies**: T-004

---

## T-006: Run full test suite and verify coverage ≥ 90%
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05

**Test Plan**:
- Given all implementation tasks complete, When `npx vitest run --coverage` runs in `repositories/anton-abyzov/specweave/`, Then all ado-spec-sync tests pass and coverage ≥ 90%
- Given tests pass, Then all 9 ACs in spec.md are marked `[x]`

**Dependencies**: T-003, T-005
